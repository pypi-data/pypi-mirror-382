# Carthooks Python SDK

Carthooks Python SDK provides comprehensive tools for interacting with the Carthooks platform, including basic HTTP API client functionality and advanced real-time data monitoring capabilities.

## Version 0.2.0 - Integrated Watcher

### Major Changes
- **Integrated Watcher**: Combined the former `cybersailor` package into `carthooks` as the `watcher` module
- **Unified SDK**: Single package for both basic API operations and real-time data monitoring
- **Improved Architecture**: Clean separation between HTTP client (`Client`) and data monitoring (`Watcher`)

### Features
- **HTTP API Client**: Full-featured client for Carthooks REST API
  - HTTP/2 support with connection pooling
  - DNS caching for improved performance
  - IPv6 support (configurable)
  - Comprehensive CRUD operations

- **Real-time Data Watcher**: Advanced monitoring capabilities
  - Real-time data processing via Amazon SQS
  - Automatic monitoring task renewal
  - Single-threaded architecture for simplified execution
  - Flexible message acknowledgment modes

### Installation
```bash
pip install carthooks
```

### Basic API Usage
```python
from carthooks import Client

# Initialize client
client = Client()
client.setAccessToken("your_token")

# Get items from a collection
result = client.getItems(app_id=123456, collection_id=789012)
if result.success:
    print(f"Found {len(result.data)} items")

# Create a new item
result = client.createItem(
    app_id=123456,
    collection_id=789012,
    data={"title": "New Item", "description": "Item description"}
)
```

### Real-time Data Monitoring Usage
```python
from carthooks import Watcher

def handler(ctx, message):
    print(f"Received: {message.item_id}")
    print(f"Event: {message.event_type}")
    print(f"Data: {message.fields}")
    return True

# Initialize watcher
watcher = Watcher(token="your_token")

# Subscribe to data changes
watcher.subscribe(
    handler=handler,
    app_id=123456,
    collection_id=789012,
    sqs_queue_url="https://sqs.region.amazonaws.com/account/queue-name",
    auto_ack=True  # Automatically acknowledge processed messages
)

# Start monitoring
watcher.run()
```

### Manual Message Acknowledgment
```python
def manual_handler(message):
    try:
        # Process message
        print(f"Processing: {message.item_id}")

        # Manually acknowledge on success
        message.ack()
    except Exception as e:
        # Reject message on failure (will be retried)
        message.nack(delay_seconds=30)

watcher.subscribe(
    handler=manual_handler,
    app_id=123456,
    collection_id=789012,
    sqs_queue_url="your_sqs_url",
    auto_ack=False  # Manual acknowledgment mode
)
```

### Advanced Configuration
```python
# Configure HTTP client
client = Client(
    timeout=60.0,
    max_connections=200,
    dns_cache_ttl=600,
    enable_ipv6=True
)

# Configure watcher with filters
watcher.subscribe(
    handler=handler,
    app_id=123456,
    collection_id=789012,
    sqs_queue_url="your_sqs_url",
    filter={"f_1009": {"$eq": 1}},  # Only monitor items where field f_1009 equals 1
    watch_name="custom-watch-name",
    age=86400,  # Monitor for 24 hours
    renewal_interval=1800,  # Renew every 30 minutes
    max_messages=5,  # Process up to 5 messages per batch
    visibility_timeout=300  # 5-minute visibility timeout
)
```

### Environment Variables
```bash
# API Configuration
CARTHOOKS_API_URL=https://api.carthooks.com
CARTHOOKS_TIMEOUT=30.0
CARTHOOKS_MAX_CONNECTIONS=100

# HTTP/2 and DNS Configuration
CARTHOOKS_HTTP2_DISABLED=false
CARTHOOKS_DNS_CACHE_DISABLE=false
CARTHOOKS_DNS_CACHE_TTL=300
CARTHOOKS_ENABLE_IPV6=false

# AWS Configuration (for Watcher)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-southeast-1
```

### Migration from cybersailor
If you were using the `cybersailor` package, migration is straightforward:

```python
# Old cybersailor usage
from cybersailor import Sailor
sailor = Sailor(token="your_token")

# New carthooks usage
from carthooks import Watcher
watcher = Watcher(token="your_token")
```

The API is identical except for the class name change from `Sailor` to `Watcher`.

### License
MIT License