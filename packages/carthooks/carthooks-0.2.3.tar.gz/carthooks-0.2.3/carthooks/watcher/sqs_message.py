from typing import Dict, Any, Optional
from .logger import Logger


class SQSMessage:
    """SQS message wrapper providing developer-friendly API"""
    
    def __init__(self, raw_message: Dict[str, Any], sqs_client, queue_url: str, 
                 app_id: int, collection_id: int, logger: Logger):
        """
        Initialize SQS message object
        
        Args:
            raw_message: Raw SQS message
            sqs_client: SQS client
            queue_url: SQS queue URL  
            app_id: Application ID
            collection_id: Collection ID
            logger: Logger
        """
        self._raw_message = raw_message
        self._sqs_client = sqs_client
        self._queue_url = queue_url
        self._logger = logger
        self._acked = False
        
        # Parse message body
        import json
        self._body = json.loads(raw_message['Body'])
        
        # Extract basic information
        self.app_id = app_id
        self.collection_id = collection_id
        self.receipt_handle = raw_message['ReceiptHandle']
        
        # Extract meta information
        self._meta = self._body.get('meta', {})
        self._payload = self._body.get('payload', {})
        
        # Extract data item information
        self.item_id = self._payload.get('id')
        self.version = self._body.get('version')
        
    @property
    def meta(self) -> Dict[str, Any]:
        """Get message meta information"""
        return self._meta.copy()
        
    @property
    def event_type(self) -> str:
        """Get event type"""
        return self._meta.get('event', '')
        
    @property
    def trigger_name(self) -> str:
        """Get trigger name"""
        return self._meta.get('trigger_name', '')
        
    @property
    def tenant_id(self) -> int:
        """Get tenant ID"""
        return self._meta.get('tenant_id')
        
    @property
    def trigger_type(self) -> str:
        """Get trigger type"""
        return self._meta.get('trigger_type', '')
        
    @property
    def record(self) -> Dict[str, Any]:
        """Get data record body"""
        return self._payload.copy()
        
    @property
    def fields(self) -> Dict[str, Any]:
        """Get field data"""
        return self._payload.get('fields', {})
        
    @property
    def title(self) -> str:
        """Get record title"""
        return self._payload.get('title', '')
        
    @property
    def created_at(self) -> int:
        """Get creation timestamp"""
        return self._payload.get('created_at')
        
    @property
    def updated_at(self) -> int:
        """Get update timestamp"""
        return self._payload.get('updated_at')
        
    @property
    def creator(self) -> int:
        """Get creator ID"""
        return self._payload.get('creator')
        
    def ack(self) -> bool:
        """
        Manually acknowledge message processing completion
        
        Returns:
            bool: Whether acknowledgment was successful
        """
        if self._acked:
            self._logger.warning(f"Message {self.item_id} has already been acknowledged")
            return True
            
        try:
            self._sqs_client.delete_message(
                QueueUrl=self._queue_url,
                ReceiptHandle=self.receipt_handle
            )
            self._acked = True
            self._logger.debug(f"Message acknowledgment successful: {self.item_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Message acknowledgment failed: {e}")
            return False
            
    def nack(self, delay_seconds: int = 0) -> bool:
        """
        Reject message, let it become available again
        
        Args:
            delay_seconds: How many seconds to delay before becoming available again
            
        Returns:
            bool: Whether operation was successful
        """
        if self._acked:
            self._logger.warning(f"Message {self.item_id} has already been acknowledged, cannot reject")
            return False
            
        try:
            # SQS doesn't have direct nack, but can be implemented by modifying visibility timeout
            self._sqs_client.change_message_visibility(
                QueueUrl=self._queue_url,
                ReceiptHandle=self.receipt_handle,
                VisibilityTimeout=delay_seconds
            )
            self._logger.debug(f"Message rejection successful: {self.item_id}, delay: {delay_seconds} seconds")
            return True
            
        except Exception as e:
            self._logger.error(f"Message rejection failed: {e}")
            return False
            
    @property
    def is_acked(self) -> bool:
        """Check if message has been acknowledged"""
        return self._acked
        
    @property
    def raw_message(self) -> Dict[str, Any]:
        """Get raw SQS message (for debugging)"""
        return self._raw_message.copy()
        
    @property
    def subscription_info(self) -> Dict[str, Any]:
        """Get subscription information"""
        return {
            'app_id': self.app_id,
            'collection_id': self.collection_id,
            'trigger_name': self.trigger_name,
            'trigger_type': self.trigger_type,
            'tenant_id': self.tenant_id
        }
        
    def __getitem__(self, key):
        """Support dictionary-style access to payload data"""
        return self._payload.get(key)
        
    def __str__(self) -> str:
        return f"SQSMessage(event={self.event_type}, item_id={self.item_id}, acked={self._acked})"
        
    def __repr__(self) -> str:
        return f"SQSMessage(app_id={self.app_id}, collection_id={self.collection_id}, item_id={self.item_id})"
