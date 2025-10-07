from typing import Any, Optional, Dict
from ..sdk import Client
from .logger import Logger
from .sqs_listener import SQSListener
from .watch_renewal import WatchRenewal
import traceback
import os
import time
import json


class Record:
    def __init__(self, watcher, app_id, collection_id, item_id, data):
        self.watcher = watcher
        self.app_id = app_id
        self.collection_id = collection_id
        self.item_id = item_id
        self.__record = data
        self.id = data.get("id", item_id)
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.creator = data.get("creator")
        self.title = data.get("title")
        self.data = data.get("fields", {})  # Safe field access
        
        # Debug information
        if watcher and watcher.logger:
            watcher.logger.debug(f"Creating Record: {self.item_id}")
    
    def __getitem__(self, key):
        return self.__record.get(key)

    def __str__(self) -> str:
        return f"Record(title={self.__record.get('title')}, item_id={self.item_id})"
    
    def __repr__(self) -> str:
        return f"Record(app_id={self.app_id}, collection_id={self.collection_id}, item_id={self.item_id})"
    
    def lock(self, **kwargs):
        if self.watcher:
            return self.watcher.lock(self, **kwargs)
        else:
            raise Exception("Record has no associated watcher instance")
    
    def unlock(self):
        if self.watcher:
            return self.watcher.unlock(self)
        else:
            raise Exception("Record has no associated watcher instance")
    
    def update(self, map):
        if self.watcher:
            return self.watcher.update(self, map)
        else:
            raise Exception("Record has no associated watcher instance")

    
class Context:
    def __init__(self, watcher, task, logger):
        self.task = task
        self.watcher = watcher
        self.logger = logger

class Watcher:
    def __init__(self, token=None, watcher_id=None):
        # Add debug info to confirm using local version
        print("=" * 60)
        print("🚀 Using Carthooks Watcher SDK")
        print(f"📁 File path: {__file__}")
        print(f"📦 Module path: {__name__}")
        print("=" * 60)
        
        self.logger = Logger("watcher")
        self.client = Client()
        self.client.setAccessToken(token)
        
        # SQS related properties
        self.sqs_listener = None
        self.watch_renewal = None
        self._running = False
        
        if watcher_id == None:
            self.watcher_id = os.uname().nodename
        else:
            self.watcher_id = watcher_id

    def subscribe(self, handler, app_id, collection_id, filter=None, 
                 sqs_queue_url=None, watch_name=None, age=432000, 
                 renewal_interval=3600, auto_ack=True, max_messages=10,
                 visibility_timeout=None, **kwargs):
        """
        Subscribe to data changes via SQS
        
        Args:
            handler: Data processing function
            app_id: Application ID
            collection_id: Collection ID
            filter: Filter conditions
            sqs_queue_url: SQS queue URL (required)
            watch_name: Monitoring task name
            age: Monitoring validity period (seconds), default 5 days
            renewal_interval: Renewal interval (seconds), default 1 hour
            auto_ack: Auto acknowledge messages (default True), False requires manual msg.ack()
            max_messages: Maximum number of messages to retrieve in one batch (1-10), default 10
            visibility_timeout: Message visibility timeout in seconds, None uses queue default
        """
        if not sqs_queue_url:
            raise ValueError("SQS queue URL is required for subscription")
            
        print("🔔 Watcher SDK: Setting up SQS subscription...")
        print(f"📋 Subscription params: app_id={app_id}, collection_id={collection_id}")
        print(f"🎯 ACK mode: {'Auto' if auto_ack else 'Manual'}")
        
        self._setup_sqs_subscription(
            handler=handler,
            app_id=app_id,
            collection_id=collection_id,
            filter=filter,
            sqs_queue_url=sqs_queue_url,
            watch_name=watch_name or f"watch-{app_id}-{collection_id}",
            age=age,
            renewal_interval=renewal_interval,
            auto_ack=auto_ack,
            max_messages=max_messages,
            visibility_timeout=visibility_timeout
        )
            
    def _setup_sqs_subscription(self, handler, app_id, collection_id, filter, 
                               sqs_queue_url, watch_name, age, renewal_interval, auto_ack,
                               max_messages, visibility_timeout):
        """Setup SQS subscription mode"""
        try:
            # 1. Convert filter format
            filters = self._convert_filter_to_watch_format(filter) if filter else None
            
            # 2. Call start_watch_data to register monitoring
            watch_config = {
                'endpoint_url': sqs_queue_url,
                'name': watch_name,
                'app_id': app_id,
                'collection_id': collection_id,
                'filters': filters,
                'age': age
            }
            
            result = self.client.start_watch_data(**watch_config)
            
            if not result.success:
                raise Exception(f"Failed to register monitoring: {result.error}")
                
            print(f"✅ Monitoring task registered successfully: {watch_name}")
            
            # 3. Initialize SQS listener
            self.sqs_listener = SQSListener(
                queue_url=sqs_queue_url, 
                handler=handler,
                app_id=app_id,
                collection_id=collection_id,
                auto_ack=auto_ack,
                max_messages=max_messages,
                visibility_timeout=visibility_timeout
            )
            self.sqs_listener.set_watcher(self)  # Set watcher instance
            self.sqs_listener.start()
            
            # 4. Initialize renewal task
            self.watch_renewal = WatchRenewal(
                self.client, 
                watch_config, 
                renewal_interval
            )
            self.watch_renewal.start_renewal()
            
            print(f"✅ SQS subscription setup completed")

        except Exception as e:
            self.logger.error(f"SQS subscription setup failed: {e}")
            print(f"❌ SQS subscription setup failed: {e}")
            # Could consider fallback to polling mode
            raise


    def _convert_filter_to_watch_format(self, filter_dict: Dict) -> Optional[Dict]:
        """
        Convert subscribe filter format to watch API filters format

        Original format: {"f_1009": {"$eq": 1}}
        Target format: {"f_1009": {"$eq": 1}}  # Direct format, no need for conditions wrapper
        """
        if not filter_dict:
            return None

        # Based on curl example, return filter conditions directly, no need for mode and conditions wrapper
        return filter_dict

    def lock(self, record, lock_timeout=600, subject=None):
        self.logger.debug(f"Locking task: {record}")
        return self.client.lockItem(record.app_id, record.collection_id, record.item_id, lock_timeout=lock_timeout, lock_id=self.watcher_id, subject=subject)

    def unlock(self, record):
        self.logger.debug(f"Unlocking task: {record}")
        return self.client.unlockItem(record.app_id, record.collection_id, record.item_id, lock_id=self.watcher_id)

    def update(self, task, map):
        self.logger.info(f"Updating task: {task} with map: {map}")
        return self.client.updateItem(task.app_id, task.collection_id, task.item_id, map)

    def create(self, app_id, collection_id, data):
        self.logger.info(f"Creating record in app_id: {app_id}, collection_id: {collection_id} with data: {data}")
        result = self.client.createItem(app_id, collection_id, data)
        return result

    def run(self):
        """Run Watcher"""
        print("🏃 Watcher SDK: Starting to run...")
        self.logger.debug("Running...")
        self._running = True

        if not self.sqs_listener:
            raise ValueError("No SQS listener configured. Please call subscribe() first.")

        try:
            print("🎯 SQS mode running...")
            while self._running:
                # Process SQS messages
                self.sqs_listener.process_messages()

                # Check for renewal
                if self.watch_renewal:
                    self.watch_renewal.check_renewal()

                # Small sleep to prevent busy waiting
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n⏹️  Received interrupt signal, stopping...")
            self.stop()
        except Exception as e:
            self.logger.error(f"Runtime error: {e}")
            self.stop()

    def stop(self):
        """Stop Watcher and all related services"""
        print("🛑 Stopping Watcher...")
        self._running = False

        # Stop SQS listener
        if self.sqs_listener:
            self.sqs_listener.stop()
            print("✅ SQS listener stopped")

        # Stop renewal task
        if self.watch_renewal:
            self.watch_renewal.stop_renewal()
            print("✅ Renewal task stopped")

        print("✅ Watcher stopped")
