#!/usr/bin/env python3
"""
Test script for automatic token refresh functionality
"""

import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import carthooks
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from carthooks.sdk import Client, OAuthConfig, OAuthTokens

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

def print_token_info(client, label):
    """Print current token information"""
    tokens = client.get_current_tokens()
    if tokens:
        print(f"📋 {label}:")
        print(f"   Access Token: {tokens.access_token[:30]}...")
        print(f"   Token Type: {tokens.token_type}")
        print(f"   Expires In: {tokens.expires_in} seconds")
        print(f"   Scope: {tokens.scope}")
        if hasattr(client, 'token_expires_at') and client.token_expires_at:
            remaining = (client.token_expires_at - datetime.now()).total_seconds()
            print(f"   Time until expiry: {remaining:.0f} seconds")
    else:
        print(f"📋 {label}: No tokens available")

def test_automatic_token_refresh():
    """Test automatic token refresh functionality"""
    print_separator("AUTOMATIC TOKEN REFRESH TEST")
    
    refresh_count = 0
    
    def on_token_refresh(tokens: OAuthTokens):
        nonlocal refresh_count
        refresh_count += 1
        print(f"🔄 Token refresh #{refresh_count} triggered!")
        print(f"   New Access Token: {tokens.access_token[:30]}...")
        print(f"   New Expires In: {tokens.expires_in} seconds")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True,
        on_token_refresh=on_token_refresh
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Testing automatic token refresh...")
        
        # Step 1: Get initial token
        print("\n--- Step 1: Get initial token ---")
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to get initial token: {result.error}")
            return
        
        print_token_info(client, "Initial Token")
        
        # Step 2: Make some API calls to verify token works
        print("\n--- Step 2: Test API calls with initial token ---")
        user_result = client.get_current_user()
        if user_result.success:
            print("✅ API call successful with initial token")
        else:
            print(f"❌ API call failed: {user_result.error}")
            return
        
        # Step 3: Force token refresh by calling refresh_oauth_token
        print("\n--- Step 3: Force token refresh ---")
        refresh_result = client.refresh_oauth_token()
        if refresh_result.success:
            print("✅ Manual token refresh successful")
            print_token_info(client, "Refreshed Token")
        else:
            print(f"❌ Manual token refresh failed: {refresh_result.error}")
        
        # Step 4: Test API calls with refreshed token
        print("\n--- Step 4: Test API calls with refreshed token ---")
        items_result = client.getItems(APP_ID, COLLECTION_ID, limit=2)
        if items_result.success:
            print(f"✅ API call successful with refreshed token")
            print(f"   Retrieved {len(items_result.data)} items")
        else:
            print(f"❌ API call failed: {items_result.error}")
        
        # Step 5: Test ensure_valid_token method
        print("\n--- Step 5: Test ensure_valid_token method ---")
        is_valid_before = client.ensure_valid_token()
        print(f"📋 Token validity check: {is_valid_before}")
        
        # Step 6: Simulate token near expiry by manually setting expiry time
        print("\n--- Step 6: Simulate token near expiry ---")
        if hasattr(client, 'token_expires_at'):
            # Set token to expire in 2 minutes (should trigger auto-refresh)
            client.token_expires_at = datetime.now() + timedelta(minutes=2)
            print("⏰ Set token to expire in 2 minutes")
            
            # Call ensure_valid_token - should trigger refresh
            is_valid_after = client.ensure_valid_token()
            print(f"� Token validity after simulated near-expiry: {is_valid_after}")
            
            # Make an API call - should use refreshed token
            user_result2 = client.get_current_user()
            if user_result2.success:
                print("✅ API call successful after auto-refresh")
            else:
                print(f"❌ API call failed after auto-refresh: {user_result2.error}")
        
        print(f"\n📊 Total refresh count: {refresh_count}")

def test_token_refresh_with_multiple_calls():
    """Test token refresh behavior with multiple API calls"""
    print_separator("MULTIPLE API CALLS WITH TOKEN REFRESH")
    
    refresh_count = 0
    
    def on_token_refresh(tokens: OAuthTokens):
        nonlocal refresh_count
        refresh_count += 1
        print(f"🔄 Auto-refresh #{refresh_count}: {tokens.access_token[:20]}...")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True,
        on_token_refresh=on_token_refresh
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Testing token refresh with multiple API calls...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        print_token_info(client, "Initial Token")
        
        # Make multiple API calls
        api_calls = [
            ("Get current user", lambda: client.get_current_user()),
            ("Get items (page 1)", lambda: client.getItems(APP_ID, COLLECTION_ID, limit=2, start=0)),
            ("Get items (page 2)", lambda: client.getItems(APP_ID, COLLECTION_ID, limit=2, start=2)),
            ("Get current user again", lambda: client.get_current_user()),
        ]
        
        for i, (description, api_call) in enumerate(api_calls, 1):
            print(f"\n--- API Call {i}: {description} ---")
            
            # Check token validity before each call
            is_valid = client.ensure_valid_token()
            print(f"📋 Token valid before call: {is_valid}")
            
            # Make the API call
            result = api_call()
            if result.success:
                print(f"✅ {description}: SUCCESS")
            else:
                print(f"❌ {description}: FAILED - {result.error}")
            
            # Small delay between calls
            time.sleep(1)
        
        print(f"\n📊 Total refresh count during multiple calls: {refresh_count}")

def test_token_expiry_edge_cases():
    """Test edge cases around token expiry"""
    print_separator("TOKEN EXPIRY EDGE CASES")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Testing token expiry edge cases...")
        
        # Get initial token
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to get initial token: {result.error}")
            return
        
        print_token_info(client, "Initial Token")
        
        # Test 1: Token expires in exactly 5 minutes (should not refresh)
        print("\n--- Test 1: Token expires in 6 minutes (should not refresh) ---")
        if hasattr(client, 'token_expires_at'):
            client.token_expires_at = datetime.now() + timedelta(minutes=6)
            is_valid = client.ensure_valid_token()
            print(f"📋 Token valid (6 min remaining): {is_valid}")
        
        # Test 2: Token expires in 4 minutes (should refresh)
        print("\n--- Test 2: Token expires in 4 minutes (should refresh) ---")
        if hasattr(client, 'token_expires_at'):
            client.token_expires_at = datetime.now() + timedelta(minutes=4)
            is_valid = client.ensure_valid_token()
            print(f"📋 Token valid (4 min remaining): {is_valid}")
        
        # Test 3: Token already expired (should refresh)
        print("\n--- Test 3: Token already expired (should refresh) ---")
        if hasattr(client, 'token_expires_at'):
            client.token_expires_at = datetime.now() - timedelta(minutes=1)
            is_valid = client.ensure_valid_token()
            print(f"📋 Token valid (expired): {is_valid}")
        
        # Final API call to verify everything still works
        print("\n--- Final verification ---")
        user_result = client.get_current_user()
        if user_result.success:
            print("✅ Final API call successful")
        else:
            print(f"❌ Final API call failed: {user_result.error}")

def main():
    """Run all token refresh tests"""
    print("🧪 Carthooks Python SDK Token Refresh Testing")
    print("==============================================")
    print(f"API URL: {CARTHOOKS_API_URL}")
    print(f"Client ID: {CLIENT_ID}")
    
    try:
        test_automatic_token_refresh()
        test_token_refresh_with_multiple_calls()
        test_token_expiry_edge_cases()
        
        print_separator("TESTING COMPLETED")
        print("✅ All token refresh tests completed")
        print("📝 Check the output above for detailed results")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
