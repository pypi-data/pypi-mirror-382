import os
import sys
import logging
import time
from dotenv import load_dotenv
load_dotenv()

# 添加本地开发代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from carthooks.watcher import Watcher
from carthooks.sdk import Client, OAuthConfig

# 获取 access token
oauth_config = OAuthConfig(
    client_id=os.getenv('CARTHOOKS_CLIENT_ID').strip('"'),
    client_secret=os.getenv('CARTHOOKS_CLIENT_SECRET').strip('"'),
    auto_refresh=True
)

os.environ['CARTHOOKS_API_URL'] = os.getenv('CARTHOOKS_API_URL')

with Client(oauth_config=oauth_config) as client:
    result = client.initialize_oauth()
    if result.success:
        accesstoken = client.get_current_tokens().access_token
    else:
        accesstoken = None

def process_handler(ctx, record):
    """
    简化的处理函数，只打印当前数据
    """
    print("=" * 50)
    print("New data item received:")
    print(f"  - Event: {record.app_id}")
    print(f"  - Collection: {record.collection_id}")
    print(f"  - Item ID: {record.item_id}")
    print(f"  - Title: {record.title}")
    print(f"  - Creator: {record.creator}")
    print(f"  - Created at: {record.created_at}")
    print("-" * 50)
    print("=" * 50)

    time.sleep(10)
    
    return True

def main():
    watcher_id = f"subscribe-test-{os.getenv('HOSTNAME','test')}"
    watcher = Watcher(token=accesstoken, watcher_id=watcher_id)
    watcher.logger.setLevel(logging.INFO)
    watcher.logger.info(f"watcher_id: {watcher_id}")
    
    watcher.subscribe(
        handler=process_handler, 
        app_id=3883548539,
        collection_id=3883548560,
        sqs_queue_url=os.getenv('SQS_QUEUE_URL'),
        filter={
            "f_1013": {
                "$eq": "停机维护"  # 使用字符串常量
            }
        },

    )
    
    print("Starting to listen for data...")
    watcher.run()

if __name__ == '__main__':
    main()
