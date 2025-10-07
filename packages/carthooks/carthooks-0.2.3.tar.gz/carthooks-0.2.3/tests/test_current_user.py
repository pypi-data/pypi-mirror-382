#!/usr/bin/env python3
"""
Test script to examine current user information
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

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def pretty_print_json(data, title="Data"):
    """Pretty print JSON data"""
    print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_current_user_info():
    """Test and examine current user information"""
    print_separator("CURRENT USER INFORMATION TEST")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Getting current user information...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"❌ Failed to initialize OAuth: {result.error}")
            return
        
        print("✅ OAuth initialized successfully")
        
        # Get current user information
        user_result = client.get_current_user()
        
        if user_result.success:
            print("✅ Successfully retrieved current user information")
            
            # Print raw response
            pretty_print_json(user_result.response, "Raw Response")
            
            # Print user data
            if user_result.data:
                pretty_print_json(user_result.data, "User Data")
                
                # Analyze each field
                print("\n📊 Field Analysis:")
                for key, value in user_result.data.items():
                    print(f"   {key}: {value} ({type(value).__name__})")
            
            # Print metadata
            if user_result.meta:
                pretty_print_json(user_result.meta, "Metadata")
            
            # Print trace ID
            if user_result.trace_id:
                print(f"\n🔍 Trace ID: {user_result.trace_id}")
            
        else:
            print(f"❌ Failed to get current user: {user_result.error}")
            if user_result.trace_id:
                print(f"🔍 Trace ID: {user_result.trace_id}")

def test_oauth_token_info():
    """Test and examine OAuth token information"""
    print_separator("OAUTH TOKEN INFORMATION")
    
    oauth_config = OAuthConfig(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auto_refresh=True
    )
    
    os.environ['CARTHOOKS_API_URL'] = CARTHOOKS_API_URL
    
    with Client(oauth_config=oauth_config) as client:
        print("🚀 Getting OAuth token information...")
        
        # Initialize OAuth
        result = client.initialize_oauth()
        if result.success:
            print("✅ OAuth token obtained successfully")
            
            # Print token response
            pretty_print_json(result.response, "OAuth Token Response")
            
            if result.data:
                pretty_print_json(result.data, "Token Data")
                
                # Analyze token fields
                print("\n📊 Token Field Analysis:")
                for key, value in result.data.items():
                    print(f"   {key}: {value} ({type(value).__name__})")
            
            # Get current tokens from client
            current_tokens = client.get_current_tokens()
            if current_tokens:
                print("\n📋 Current Tokens Object:")
                print(f"   Access Token: {current_tokens.access_token[:50]}...")
                print(f"   Token Type: {current_tokens.token_type}")
                print(f"   Expires In: {current_tokens.expires_in}")
                print(f"   Scope: {current_tokens.scope}")
                print(f"   Refresh Token: {current_tokens.refresh_token}")
        else:
            print(f"❌ Failed to get OAuth token: {result.error}")

def main():
    """Run current user information tests"""
    print("🧪 Carthooks Python SDK Current User Information")
    print("===============================================")
    print(f"API URL: {CARTHOOKS_API_URL}")
    print(f"Client ID: {CLIENT_ID}")
    
    try:
        test_oauth_token_info()
        test_current_user_info()
        
        print_separator("TESTING COMPLETED")
        print("✅ Current user information tests completed")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
