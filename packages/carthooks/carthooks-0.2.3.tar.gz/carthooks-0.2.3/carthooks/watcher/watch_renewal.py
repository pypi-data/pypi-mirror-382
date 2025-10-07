import time
from typing import Dict, Any, Optional
from .logger import Logger


class WatchRenewal:
    """Monitoring task renewal manager - single threaded"""
    
    def __init__(self, carthooks_client, watch_config: Dict[str, Any], renewal_interval: int = 3600):
        """
        Initialize renewal manager
        
        Args:
            carthooks_client: CartHooks client instance
            watch_config: Monitoring configuration parameters
            renewal_interval: Renewal interval (seconds), default 1 hour
        """
        self.carthooks_client = carthooks_client
        self.watch_config = watch_config.copy()  # Copy config to avoid modifying original
        self.renewal_interval = renewal_interval
        self.running = False
        self.last_renewal = 0
        self.logger = Logger("watch_renewal")
        
    def start_renewal(self):
        """Start renewal"""
        if self.running:
            self.logger.warning("Renewal task is already running")
            return
            
        self.running = True
        self.last_renewal = time.time()
        self.logger.info(f"Monitoring task renewal started, renewal interval: {self.renewal_interval} seconds")
        
    def stop_renewal(self):
        """Stop renewal"""
        self.running = False
        self.logger.info("Monitoring task renewal stopped")
        
    def check_renewal(self):
        """Check if renewal is needed - called from main thread"""
        if not self.running:
            return
            
        current_time = time.time()
        if current_time - self.last_renewal >= self.renewal_interval:
            try:
                # Re-call start_watch_data for renewal
                result = self.carthooks_client.start_watch_data(**self.watch_config)
                
                if result.success:
                    self.logger.info(f"Monitoring task renewal successful: {self.watch_config.get('name', 'Unknown')}")
                    self.last_renewal = current_time
                else:
                    self.logger.error(f"Monitoring task renewal failed: {result.error}")
                    # Consider retry mechanism when renewal fails
                    self._handle_renewal_failure(result.error)
                    
            except Exception as e:
                self.logger.error(f"Monitoring task renewal exception: {e}")
                self._handle_renewal_failure(str(e))
                    
    def _handle_renewal_failure(self, error: str):
        """Handle renewal failure"""
        # Can implement retry logic or other error handling
        # Currently simply log error, renewal thread will retry in next cycle
        self.logger.warning(f"Renewal failed, will retry in next cycle: {error}")
        
    def update_config(self, new_config: Dict[str, Any]):
        """Update monitoring configuration"""
        self.watch_config = new_config.copy()
        self.logger.info("Monitoring configuration updated")
        
    def get_config(self) -> Dict[str, Any]:
        """Get current monitoring configuration"""
        return self.watch_config.copy()
        
    def is_running(self) -> bool:
        """Check if renewal is running"""
        return self.running
