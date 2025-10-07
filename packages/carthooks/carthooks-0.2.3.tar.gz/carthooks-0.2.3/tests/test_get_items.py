#!/usr/bin/env python3
"""
Test script for getting items from collections
Tests various scenarios for retrieving items using the Carthooks Python SDK
"""

import os
import sys
import json
import time
from typing import Optional
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
APP_ID = int(os.getenv('CARTHOOKS_APP_ID'))
COLLECTION_ID = int(os.getenv('CARTHOOKS_COLLECTION_ID'))

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def pretty_print_json(data, title="Data"):
    """Pretty print JSON data"""
    print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def print_result(operation, result):
    """Print operation result with detailed information"""
    if result.success:
        print(f"✅ {operation}: SUCCESS")
        if result.data:
            # Print data structure info
            if isinstance(result.data, dict):
                print(f"   📊 Data type: dict with {len(result.data)} keys")
                if 'items' in result.data:
                    items = result.data['items']
                    print(f"   📋 Items count: {len(items) if isinstance(items, list) else 'N/A'}")
                elif 'id' in result.data:
                    print(f"   🆔 Item ID: {result.data['id']}")
            elif isinstance(result.data, list):
                print(f"   📊 Data type: list with {len(result.data)} items")
            
            # Print first few items for inspection
            pretty_print_json(result.data, f"{operation} Response Data")
        
        if result.meta:
            pretty_print_json(result.meta, "Metadata")
        
        if result.trace_id:
            print(f"   🔍 Trace ID: {result.trace_id}")
    else:
        print(f"❌ {operation}: FAILED")
        print(f"   Error: {result.error}")
        if result.trace_id:
            print(f"   🔍 Trace ID: {result.trace_id}")

def test_get_items_basic():
    """Test basic item retrieval"""
    print_separator("BASIC ITEM RETRIEVAL TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Getting items from collection {COLLECTION_ID} in app {APP_ID}...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        print("✅ OAuth initialized successfully")
        
        # Test 1: Get items with default pagination
        items_result = client.getItems(APP_ID, COLLECTION_ID)
        print_result("Get items (default pagination)", items_result)
        
        # Test 2: Get items with custom limit
        items_result_limited = client.getItems(APP_ID, COLLECTION_ID, limit=5)
        print_result("Get items (limit=5)", items_result_limited)
        
        # Test 3: Get items with pagination
        items_result_page1 = client.getItems(APP_ID, COLLECTION_ID, limit=3, start=0)
        print_result("Get items (page 1: limit=3, start=0)", items_result_page1)
        
        items_result_page2 = client.getItems(APP_ID, COLLECTION_ID, limit=3, start=3)
        print_result("Get items (page 2: limit=3, start=3)", items_result_page2)

def test_get_items_with_options():
    """Test item retrieval with various options"""
    print_separator("ITEM RETRIEVAL WITH OPTIONS TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing item retrieval with various options...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # Test with sorting options (if supported)
        items_result_sorted = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=5,
            sort_field="created_at",
            sort_order="desc"
        )
        print_result("Get items (with sorting)", items_result_sorted)
        
        # Test with field filtering (if supported)
        items_result_fields = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=5,
            fields="id,title,created_at"
        )
        print_result("Get items (with field filtering)", items_result_fields)

def test_get_item_by_id():
    """Test getting specific items by ID"""
    print_separator("GET ITEM BY ID TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing item retrieval by ID...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # First, get some items to find valid IDs
        items_result = client.getItems(APP_ID, COLLECTION_ID, limit=3)
        print_result("Get items to find IDs", items_result)
        
        if items_result.success and items_result.data:
            # Try to extract item IDs from the response
            items = None
            if isinstance(items_result.data, dict) and 'items' in items_result.data:
                items = items_result.data['items']
            elif isinstance(items_result.data, list):
                items = items_result.data
            
            if items and len(items) > 0:
                # Test getting first item by ID
                first_item = items[0]
                item_id = first_item.get('id') or first_item.get('ID')
                
                if item_id:
                    print(f"\n🎯 Testing getItemById with ID: {item_id}")
                    
                    # Test 1: Get item without field filtering
                    item_result = client.getItemById(APP_ID, COLLECTION_ID, item_id)
                    print_result(f"Get item by ID ({item_id})", item_result)
                    
                    # Test 2: Get item with specific fields
                    item_result_fields = client.getItemById(
                        APP_ID, 
                        COLLECTION_ID, 
                        item_id, 
                        fields="id,title,created_at"
                    )
                    print_result(f"Get item by ID with fields ({item_id})", item_result_fields)
                else:
                    print("⚠️  Could not find item ID in the response")
            else:
                print("⚠️  No items found to test getItemById")

def test_create_and_get_item():
    """Test creating an item and then retrieving it"""
    print_separator("CREATE AND GET ITEM TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing create and retrieve cycle...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # Create a test item
        test_data = {
            "title": f"Test Item for Get - {int(time.time())}",
            "description": "Created specifically for testing item retrieval",
            "test_field": "test_value",
            "created_by_test": True
        }
        
        print(f"📝 Creating test item with data:")
        pretty_print_json(test_data, "Test Item Data")
        
        create_result = client.createItem(APP_ID, COLLECTION_ID, test_data)
        print_result("Create test item", create_result)
        
        if create_result.success and create_result.data:
            # Extract the created item ID
            item_id = create_result.data.get('id') or create_result.data.get('ID')
            
            if item_id:
                print(f"\n🎯 Created item with ID: {item_id}")
                
                # Test getting the created item by ID
                get_result = client.getItemById(APP_ID, COLLECTION_ID, item_id)
                print_result(f"Get created item by ID ({item_id})", get_result)
                
                # Test getting items list to verify the item appears
                items_result = client.getItems(APP_ID, COLLECTION_ID, limit=10)
                print_result("Get items list (should include new item)", items_result)
                
                # Verify the item exists in the list
                if items_result.success and items_result.data:
                    items = None
                    if isinstance(items_result.data, dict) and 'items' in items_result.data:
                        items = items_result.data['items']
                    elif isinstance(items_result.data, list):
                        items = items_result.data
                    
                    if items:
                        found_item = None
                        for item in items:
                            if (item.get('id') == item_id or item.get('ID') == item_id):
                                found_item = item
                                break
                        
                        if found_item:
                            print(f"✅ Created item found in items list")
                            pretty_print_json(found_item, "Found Item in List")
                        else:
                            print(f"⚠️  Created item not found in items list")
                
                # Clean up: delete the test item
                print(f"\n🧹 Cleaning up: deleting test item {item_id}")
                delete_result = client.deleteItem(APP_ID, COLLECTION_ID, item_id)
                print_result(f"Delete test item ({item_id})", delete_result)
            else:
                print("⚠️  Could not extract item ID from create response")

def test_error_scenarios():
    """Test error scenarios for item retrieval"""
    print_separator("ERROR SCENARIOS TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing error scenarios...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # Test 1: Invalid app ID
        invalid_app_result = client.getItems(999999999, COLLECTION_ID, limit=5)
        print_result("Get items with invalid app ID", invalid_app_result)
        
        # Test 2: Invalid collection ID
        invalid_collection_result = client.getItems(APP_ID, 999999999, limit=5)
        print_result("Get items with invalid collection ID", invalid_collection_result)
        
        # Test 3: Invalid item ID
        invalid_item_result = client.getItemById(APP_ID, COLLECTION_ID, 999999999)
        print_result("Get item with invalid item ID", invalid_item_result)
        
        # Test 4: Extreme pagination values
        extreme_pagination_result = client.getItems(APP_ID, COLLECTION_ID, limit=1000, start=999999)
        print_result("Get items with extreme pagination", extreme_pagination_result)

def main():
    """Run all get items tests"""
    print("🧪 Carthooks Python SDK - Get Items Testing")
    print("===========================================")
    print(f"API URL: {CARTHOOKS_API_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"App ID: {APP_ID}")
    print(f"Collection ID: {COLLECTION_ID}")
    
    try:
        # Run all tests
        test_get_items_basic()
        test_get_items_with_options()
        test_get_item_by_id()
        test_create_and_get_item()
        test_error_scenarios()
        
        print_separator("TESTING COMPLETED")
        print("✅ All get items tests completed")
        print("📝 Check the output above for detailed results")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
