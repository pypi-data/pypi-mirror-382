import boto3
import json
import time
import os
from typing import Callable, Optional, Dict, Any
from .logger import Logger
from .sqs_message import SQSMessage


class SQSListener:
    """Amazon SQS message listener - single threaded"""
    
    def __init__(self, queue_url: str, handler: Callable, app_id: int, collection_id: int,
                 auto_ack: bool = True, max_messages: int = 10, visibility_timeout: int = None,
                 aws_access_key_id: str = None, aws_secret_access_key: str = None, 
                 region_name: str = None):
        """
        Initialize SQS listener
        
        Args:
            queue_url: SQS queue URL
            handler: Message processing function
            app_id: Application ID
            collection_id: Collection ID
            auto_ack: Whether to automatically acknowledge messages (default True)
            max_messages: Maximum number of messages to retrieve in one batch (1-10, default 10)
            visibility_timeout: Message visibility timeout in seconds (None uses queue default)
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region
        """
        self.queue_url = queue_url
        self.handler = handler
        self.app_id = app_id
        self.collection_id = collection_id
        self.auto_ack = auto_ack
        self.max_messages = max(1, min(10, max_messages))  # Ensure 1-10 range
        self.visibility_timeout = visibility_timeout
        self.running = False
        self.logger = Logger("sqs_listener")
        
        # Get AWS configuration from environment variables
        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = region_name or os.getenv('AWS_REGION', 'ap-southeast-1')
        
        # Initialize SQS client
        self.sqs = boto3.client(
            'sqs',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )
        
    def start(self):
        """Start SQS listening"""
        if self.running:
            self.logger.warning("SQS listener is already running")
            return
            
        self.running = True
        self.logger.info(f"SQS listener started, queue: {self.queue_url}")
        
    def stop(self):
        """Stop SQS listening"""
        self.running = False
        self.logger.info("SQS listener stopped")
        
    def process_messages(self):
        """Process SQS messages - called from main thread"""
        if not self.running:
            return
            
        try:
            # Build receive_message parameters
            receive_params = {
                'QueueUrl': self.queue_url,
                'MaxNumberOfMessages': self.max_messages,
                'WaitTimeSeconds': 1,  # Short polling for main thread
                'MessageAttributeNames': ['All']
            }
            
            # Add visibility timeout if specified
            if self.visibility_timeout is not None:
                receive_params['VisibilityTimeout'] = self.visibility_timeout
            
            # Long polling to receive messages
            response = self.sqs.receive_message(**receive_params)
            
            messages = response.get('Messages', [])
            if not messages:
                return
                
            # Process received messages
            for message in messages:
                if not self.running:
                    break
                    
                try:
                    result = self._process_message(message)
                    
                    # Decide whether to automatically acknowledge based on auto_ack setting
                    if self.auto_ack and result:
                        self.sqs.delete_message(
                            QueueUrl=self.queue_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        self.logger.debug(f"Message auto-acknowledged: {message.get('MessageId')}")
                    elif not self.auto_ack:
                        # In manual ACK mode, user decides whether to acknowledge
                        self.logger.debug(f"Manual ACK mode, waiting for user acknowledgment: {message.get('MessageId')}")
                    else:
                        # Processing failed and in auto ACK mode, don't delete message
                        self.logger.warning(f"Message processing failed, not acknowledging: {message.get('MessageId')}")
                    
                except Exception as e:
                    self.logger.error(f"Message processing failed: {e}")
                    # Don't delete message when processing fails, let it become available again
                    
        except Exception as e:
            if self.running:  # Only log errors when running
                self.logger.error(f"SQS listening error: {e}")
                time.sleep(1)  # Wait 1 second before retry on error
                    
    def _process_message(self, raw_message: Dict[str, Any]) -> bool:
        """Process single SQS message"""
        try:
            # Create SQSMessage object
            sqs_message = SQSMessage(
                raw_message=raw_message,
                sqs_client=self.sqs,
                queue_url=self.queue_url,
                app_id=self.app_id,
                collection_id=self.collection_id,
                logger=self.logger
            )
            
            if not sqs_message.item_id:
                self.logger.error(f"Incorrect message format, missing payload.id: {raw_message}")
                return False
                
            # Import Context class
            from .watcher import Context
            
            # Create Context object
            context = Context(
                watcher=getattr(self, 'watcher', None),
                task=None,    # No task in SQS mode
                logger=self.logger
            )
            
            self.logger.info(f"Processing message: {sqs_message.event_type}, item_id: {sqs_message.item_id}")
            
            # Call user's handler function, passing context and SQSMessage
            if self.auto_ack:
                # Auto ACK mode: pass compatible parameters
                result = self.handler(context, sqs_message)
            else:
                # Manual ACK mode: only pass SQSMessage, user needs to manually call ack()
                result = self.handler(sqs_message)
            
            if result:
                self.logger.debug(f"Message processing successful: {sqs_message.item_id}")
                return True
            else:
                self.logger.warning(f"Message processing returned False: {sqs_message.item_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Message parsing failed: {e}")
            raise
            
    def set_watcher(self, watcher):
        """Set watcher instance (for Record and Context)"""
        self.watcher = watcher
