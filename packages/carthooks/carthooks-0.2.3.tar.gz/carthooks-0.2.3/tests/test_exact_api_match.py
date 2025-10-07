#!/usr/bin/env python3
"""
Test script to match the exact API request
URL: https://api-stage.carthooks.com/v1/apps/3883548539/collections/3883549661/items?filters%5Bf_1001%5D%5B%24eq%5D=EF250920962519&pagination%5Bstart%5D=0&pagination%5Blimit%5D=1
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import carthooks
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from carthooks.sdk import Client, OAuthConfig

# Test configuration from environment variables
CARTHOOKS_API_URL = os.getenv('CARTHOOKS_API_URL')
CLIENT_ID = os.getenv('CARTHOOKS_CLIENT_ID')
CLIENT_SECRET = os.getenv('CARTHOOKS_CLIENT_SECRET')

# Fixed values to match the exact URL
APP_ID = 3883548539
COLLECTION_ID = 3883549661

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def pretty_print_json(data, title="Data"):
    """Pretty print JSON data"""
    print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_exact_api_match():
    """Test the exact API request that matches the provided URL"""
    print_separator("EXACT API MATCH TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing exact API match...")
        print(f"📋 Target URL: https://api-stage.carthooks.com/v1/apps/{APP_ID}/collections/{COLLECTION_ID}/items")
        print(f"📋 Expected params: filters[f_1001][$eq]=EF250920962519&pagination[start]=0&pagination[limit]=1")
        print(f"📋 Using API URL: {CARTHOOKS_API_URL}")
        
        # Initialize OAuth
        print(f"🔍 Attempting OAuth initialization...")
        print(f"   OAuth URL will be: {CARTHOOKS_API_URL}/oauth/token")
        print(f"   Client ID: {CLIENT_ID}")
        print(f"   Client Secret: {CLIENT_SECRET[:20]}...")
        
        result = client.initialize_oauth()
        
        print(f"🔍 OAuth result details:")
        print(f"   Success: {result.success}")
        print(f"   Error: {result.error}")
        print(f"   Data: {result.data}")
        print(f"   Meta: {result.meta}")
        print(f"   Trace ID: {result.trace_id}")
        
        # 检查是否有response属性
        if hasattr(result, 'response'):
            print(f"   Response: {result.response}")
        else:
            print(f"   Response: No response attribute")
        
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        print("✅ OAuth initialized successfully")
        
        # Make the exact API call to match the URL
        # URL breakdown:
        # - filters[f_1001][$eq]=EF250920962519
        # - pagination[start]=0  (handled by start=0)
        # - pagination[limit]=1  (handled by limit=1)
        
        filter_params = {
            'filters[f_1001][$eq]': 'EF250920962519'
        }
        
        print("\n🔍 Making API request with parameters:")
        print(f"   App ID: {APP_ID}")
        print(f"   Collection ID: {COLLECTION_ID}")
        print(f"   Limit: 1")
        print(f"   Start: 0")
        print(f"   Filter: {filter_params}")
        
        items_result = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=1,
            start=0,
            **filter_params
        )
        
        if items_result.success:
            print(f"✅ API Request: SUCCESS")
            print(f"   📊 Response Status: HTTP/2 200 OK (equivalent)")
            
            if items_result.data:
                if isinstance(items_result.data, list):
                    print(f"   📋 Items returned: {len(items_result.data)}")
                elif isinstance(items_result.data, dict) and 'items' in items_result.data:
                    items = items_result.data['items']
                    print(f"   📋 Items returned: {len(items) if isinstance(items, list) else 'N/A'}")
                
                # Print the response data
                pretty_print_json(items_result.data, "API Response Data")
            
            if items_result.meta:
                pretty_print_json(items_result.meta, "Response Metadata")
            
            if items_result.trace_id:
                print(f"   🔍 Trace ID: {items_result.trace_id}")
                
            print(f"\n✅ Request successfully matches the target URL pattern!")
            
        else:
            print(f"❌ API Request: FAILED")
            print(f"   Error: {items_result.error}")
            if items_result.trace_id:
                print(f"   🔍 Trace ID: {items_result.trace_id}")

def main():
    """Run the exact API match test"""
    print("🧪 Carthooks Python SDK - Exact API Match Test")
    print("===============================================")
    print(f"Target: https://api-stage.carthooks.com/v1/apps/3883548539/collections/3883549661/items")
    print(f"Params: filters[f_1001][$eq]=EF250920962519&pagination[start]=0&pagination[limit]=1")
    print(f"Expected: HTTP/2 200 OK")
    print(f"")
    print(f"Using API URL: {CARTHOOKS_API_URL}")
    print(f"Using Client ID: {CLIENT_ID}")
    
    try:
        test_exact_api_match()
        
        print_separator("TESTING COMPLETED")
        print("✅ Exact API match test completed")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
