#!/usr/bin/env python3
"""
Test script for getting items with filters from collections
Tests the specific API endpoint with filter parameters
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

def test_get_items_with_filter():
    """Test getting items with specific filter parameters"""
    print_separator("GET ITEMS WITH FILTER TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing filtered item retrieval...")
        print(f"📋 API URL: {CARTHOOKS_API_URL}")
        print(f"📋 App ID: {APP_ID}")
        print(f"📋 Collection ID: {COLLECTION_ID}")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        print("✅ OAuth initialized successfully")
        
        # Test 1: Get items with specific filter (f_1001 = EF250920962519)
        # This matches the URL: filters[f_1001][$eq]=EF250920962519&pagination[start]=0&pagination[limit]=1
        filter_params = {
            'filters[f_1001][$eq]': 'EF250920962519'
        }
        
        items_result = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=1,
            start=0,
            **filter_params
        )
        print_result("Get items with f_1001 filter", items_result)
        
        # Test 2: Get items with multiple filter conditions
        multi_filter_params = {
            'filters[f_1001][$eq]': 'EF250920962519',
            'filters[f_1002][$ne]': '',  # Not empty
        }
        
        items_result_multi = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=5,
            start=0,
            **multi_filter_params
        )
        print_result("Get items with multiple filters", items_result_multi)
        
        # Test 3: Get items with different operators
        operator_filter_params = {
            'filters[f_1001][$like]': '%EF2509%'  # Contains pattern
        }
        
        items_result_like = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=3,
            start=0,
            **operator_filter_params
        )
        print_result("Get items with LIKE filter", items_result_like)
        
        # Test 4: Get items with date range filter (if applicable)
        date_filter_params = {
            'filters[created_at][$gte]': '2025-01-01',
            'filters[created_at][$lte]': '2025-12-31'
        }
        
        items_result_date = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=5,
            start=0,
            **date_filter_params
        )
        print_result("Get items with date range filter", items_result_date)

def test_pagination_with_filters():
    """Test pagination combined with filters"""
    print_separator("PAGINATION WITH FILTERS TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing pagination with filters...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # Test pagination with filters
        filter_params = {
            'filters[f_1042][$eq]': 'TMZ'  # Filter by a specific field value
        }
        
        # Page 1
        page1_result = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=2,
            start=0,
            **filter_params
        )
        print_result("Page 1 with filter", page1_result)
        
        # Page 2
        page2_result = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=2,
            start=2,
            **filter_params
        )
        print_result("Page 2 with filter", page2_result)

def test_sorting_with_filters():
    """Test sorting combined with filters"""
    print_separator("SORTING WITH FILTERS TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing sorting with filters...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # Test sorting with filters
        filter_and_sort_params = {
            'filters[f_1042][$ne]': '',  # Non-empty field
            'sort': 'created_at',
            'order': 'desc'
        }
        
        sorted_filtered_result = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=5,
            start=0,
            **filter_and_sort_params
        )
        print_result("Sorted and filtered items", sorted_filtered_result)

def test_field_selection_with_filters():
    """Test field selection combined with filters"""
    print_separator("FIELD SELECTION WITH FILTERS TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print(f"🚀 Testing field selection with filters...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        # Test field selection with filters
        filter_and_fields_params = {
            'filters[f_1001][$like]': '%EF%',  # Items starting with EF
            'fields': 'id,title,f_1001,f_1002,created_at'
        }
        
        fields_filtered_result = client.getItems(
            APP_ID, 
            COLLECTION_ID, 
            limit=3,
            start=0,
            **filter_and_fields_params
        )
        print_result("Filtered items with specific fields", fields_filtered_result)

def main():
    """Run all filter tests"""
    print("🧪 Carthooks Python SDK - Get Items with Filters Testing")
    print("=========================================================")
    print(f"API URL: {CARTHOOKS_API_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"App ID: {APP_ID}")
    print(f"Collection ID: {COLLECTION_ID}")
    
    try:
        # Run all tests
        test_get_items_with_filter()
        test_pagination_with_filters()
        test_sorting_with_filters()
        test_field_selection_with_filters()
        
        print_separator("TESTING COMPLETED")
        print("✅ All filter tests completed")
        print("📝 Check the output above for detailed results")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
