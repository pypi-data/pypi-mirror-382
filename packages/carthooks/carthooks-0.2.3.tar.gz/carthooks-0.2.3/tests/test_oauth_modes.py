#!/usr/bin/env python3
"""
Test script for Carthooks Python SDK OAuth functionality
Tests all 3 OAuth modes with automatic token management
"""

import os
import sys
import time
from typing import Optional
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

def print_result(operation, result):
    """Print operation result"""
    if result.success:
        print(f"✅ {operation}: SUCCESS")
        if result.data:
            print(f"   Data: {result.data}")
        if result.trace_id:
            print(f"   Trace ID: {result.trace_id}")
    else:
        print(f"❌ {operation}: FAILED")
        print(f"   Error: {result.error}")
        if result.trace_id:
            print(f"   Trace ID: {result.trace_id}")

def test_api_calls(client, mode_name):
    """Test basic API calls with the client"""
    print(f"\n--- Testing API calls in {mode_name} mode ---")
    
    # Test 1: Get current user info
    user_result = client.get_current_user()
    print_result("Get current user", user_result)
    
    # Test 2: Get items from collection
    items_result = client.getItems(APP_ID, COLLECTION_ID, limit=5)
    print_result("Get items", items_result)
    
    # Test 3: Create a test item
    test_data = {
        "title": f"Test Item - {mode_name} - {int(time.time())}",
        "description": f"Created via Python SDK in {mode_name} mode"
    }
    create_result = client.createItem(APP_ID, COLLECTION_ID, test_data)
    print_result("Create item", create_result)
    
    # If item was created successfully, try to update and delete it
    if create_result.success and create_result.data:
        item_id = create_result.data.get('id')
        if item_id:
            # Test 4: Update the item
            update_data = {
                "title": f"Updated Test Item - {mode_name}",
                "description": f"Updated via Python SDK in {mode_name} mode"
            }
            update_result = client.updateItem(APP_ID, COLLECTION_ID, item_id, update_data)
            print_result("Update item", update_result)
            
            # Test 5: Get the specific item
            get_result = client.getItemById(APP_ID, COLLECTION_ID, item_id)
            print_result("Get item by ID", get_result)
            
            # Test 6: Delete the item
            delete_result = client.deleteItem(APP_ID, COLLECTION_ID, item_id)
            print_result("Delete item", delete_result)

def test_mode_1_client_credentials():
    """Test Mode 1: Client Credentials (Machine-to-Machine)"""
    print_separator("MODE 1: Client Credentials (Machine-to-Machine)")

    def on_token_refresh(tokens: OAuthTokens):
        print(f"🔄 Token refreshed automatically: {tokens.access_token[:20]}...")

    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True,
        on_token_refresh=on_token_refresh
    )

    # Set API URL via environment variable
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL

    with Client(oauth_config=oauth_config) as client:
        print("🚀 Initializing OAuth with client credentials...")
        print(f"📋 Using API URL: {CARTHOOKS_API_URL}")
        print(f"📋 OAuth Token URL: {CARTHOOKS_API_URL}api/oauth/token")

        # Initialize OAuth - this should get the access token transparently
        result = client.initialize_oauth()
        print_result("Initialize OAuth", result)

        if result.success:
            # Show current tokens
            tokens = client.get_current_tokens()
            if tokens:
                print(f"📋 Access Token: {tokens.access_token[:20]}...")
                print(f"📋 Token Type: {tokens.token_type}")
                print(f"📋 Expires In: {tokens.expires_in} seconds")
                print(f"📋 Scope: {tokens.scope}")

            # Test API calls
            test_api_calls(client, "Client Credentials")

            # Test automatic token refresh by forcing a refresh
            print("\n--- Testing automatic token refresh ---")
            refresh_result = client.refresh_oauth_token()
            print_result("Manual token refresh", refresh_result)
        else:
            print("ℹ️  Make sure the backend server is running on http://localhost:9000")
            print("ℹ️  Check if the client credentials are valid")

def test_mode_2_client_credentials_with_user():
    """Test Mode 2: Client Credentials with User Token"""
    print_separator("MODE 2: Client Credentials with User Token")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Initializing OAuth with client credentials + user token...")
        
        # For this test, we'll use a placeholder user access token
        # In a real scenario, this would come from your frontend/user authentication
        user_access_token = "user-token-placeholder"  # This would be a real user token
        
        # Note: This might fail if we don't have a valid user token, but we'll test the flow
        result = client.initialize_oauth(user_access_token)
        print_result("Initialize OAuth with user token", result)
        
        if result.success:
            tokens = client.get_current_tokens()
            if tokens:
                print(f"📋 User-context Access Token: {tokens.access_token[:20]}...")
                print(f"📋 Scope: {tokens.scope}")
            
            test_api_calls(client, "Client Credentials + User")
        else:
            print("ℹ️  This mode requires a valid user access token from frontend authentication")

def test_mode_3_authorization_code():
    """Test Mode 3: Authorization Code Flow"""
    print_separator("MODE 3: Authorization Code Flow")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Testing Authorization Code Flow...")
        
        # This mode is typically used in web applications
        # We'll demonstrate the flow but won't complete it since it requires user interaction
        
        from carthooks.sdk import OAuthAuthorizeCodeRequest
        
        auth_request = OAuthAuthorizeCodeRequest(
            client_id=CLIENT_ID,
            redirect_uri="http://localhost:3000/callback",
            state="test-state-123",
            target_tenant_id=None  # Optional
        )
        
        # Get authorization URL (this requires authentication)
        # Note: This might fail if we don't have proper authentication
        auth_result = client.get_oauth_authorize_code(auth_request)
        print_result("Get authorization code URL", auth_result)
        
        if auth_result.success and auth_result.data:
            redirect_url = auth_result.data.get('redirect_url')
            print(f"📋 Authorization URL: {redirect_url}")
            print("ℹ️  In a real application, you would redirect the user to this URL")
            print("ℹ️  After user authorization, you would exchange the code for tokens")
        else:
            print("ℹ️  Authorization code flow requires proper authentication setup")
            print("ℹ️  This is typically used in web applications with user interaction")

def test_token_expiration_handling():
    """Test automatic token expiration handling"""
    print_separator("TOKEN EXPIRATION HANDLING TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Testing automatic token expiration handling...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if result.success:
            print("✅ Initial token obtained")
            
            # Make an API call
            items_result = client.getItems(APP_ID, COLLECTION_ID, limit=1)
            print_result("API call with fresh token", items_result)
            
            # Check if token needs refresh (this will automatically refresh if needed)
            print("\n🔍 Checking token validity...")
            is_valid = client.ensure_valid_token()
            print(f"📋 Token is valid: {is_valid}")
            
            # Make another API call (token should be automatically refreshed if needed)
            items_result2 = client.getItems(APP_ID, COLLECTION_ID, limit=1)
            print_result("API call with auto-refreshed token", items_result2)

def main():
    """Run all OAuth mode tests"""
    print("🧪 Carthooks Python SDK OAuth Testing")
    print("=====================================")
    print(f"API URL: {CARTHOOKS_API_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"App ID: {APP_ID}")
    print(f"Collection ID: {COLLECTION_ID}")
    
    try:
        # Test all OAuth modes
        test_mode_1_client_credentials()
        test_mode_2_client_credentials_with_user()
        test_mode_3_authorization_code()
        test_token_expiration_handling()
        
        print_separator("TESTING COMPLETED")
        print("✅ All OAuth modes have been tested")
        print("📝 Check the output above for detailed results")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
