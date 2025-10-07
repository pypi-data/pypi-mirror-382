#!/usr/bin/env python3
"""
Test script for IPv6 disable functionality
"""
import socket
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import carthooks
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from carthooks.sdk import Client

def test_ipv6_disable():
    """Test IPv6 disable functionality"""
    print("=== Testing IPv6 Disable Functionality ===")
    
    # Test 1: Default behavior (IPv6 disabled)
    print("\n1. Testing default behavior (IPv6 should be disabled):")
    client = Client()
    print(f"   IPv6 enabled: {client.is_ipv6_enabled()}")
    
    # Get API host from environment
    api_url = os.getenv('CARTHOOKS_API_URL')
    
    # Extract hostname from URL
    from urllib.parse import urlparse
    parsed_url = urlparse(api_url if api_url.startswith('http') else f'http://{api_url}')
    api_host = parsed_url.hostname
    
    # Test DNS resolution after IPv6 disable
    try:
        result = socket.getaddrinfo(api_host, 443)
        ipv4_addrs = [r[4][0] for r in result if r[0] == socket.AF_INET]
        ipv6_addrs = [r[4][0] for r in result if r[0] == socket.AF_INET6]
        print(f"   DNS resolution - IPv4: {len(ipv4_addrs)}, IPv6: {len(ipv6_addrs)}")
        print(f"   IPv4 addresses: {ipv4_addrs[:2]}")
        print(f"   IPv6 addresses: {ipv6_addrs[:2]}")
    except Exception as e:
        print(f"   DNS resolution failed: {e}")
    
    # Test HTTP request
    try:
        test_url = f"http://{api_host}:9000" if api_host == 'localhost' else f"https://{api_host}"
        response = client.client.get(test_url)
        print(f"   HTTP request: SUCCESS {response.status_code}")
    except Exception as e:
        print(f"   HTTP request: FAILED - {e}")
    
    client.close()
    
    # Test 2: Explicitly enable IPv6
    print("\n2. Testing with IPv6 explicitly enabled:")
    client_ipv6 = Client(enable_ipv6=True)
    print(f"   IPv6 enabled: {client_ipv6.is_ipv6_enabled()}")
    
    # Test DNS resolution with IPv6 enabled
    try:
        result = socket.getaddrinfo(api_host, 443)
        ipv4_addrs = [r[4][0] for r in result if r[0] == socket.AF_INET]
        ipv6_addrs = [r[4][0] for r in result if r[0] == socket.AF_INET6]
        print(f"   DNS resolution - IPv4: {len(ipv4_addrs)}, IPv6: {len(ipv6_addrs)}")
    except Exception as e:
        print(f"   DNS resolution failed: {e}")
    
    client_ipv6.close()
    
    # Test 3: Environment variable control
    print("\n3. Testing environment variable control:")
    os.environ['CARTHOOKS_ENABLE_IPV6'] = 'true'
    client_env = Client()
    print(f"   IPv6 enabled (via env): {client_env.is_ipv6_enabled()}")
    client_env.close()
    
    # Reset environment
    del os.environ['CARTHOOKS_ENABLE_IPV6']
    
    print("\n✅ IPv6 disable functionality test completed!")

def test_multiple_requests():
    """Test multiple requests to ensure IPv6 disable is stable"""
    print("\n=== Testing Multiple Requests with IPv6 Disabled ===")
    
    client = Client()
    print(f"IPv6 enabled: {client.is_ipv6_enabled()}")
    
    success_count = 0
    # Get API host for testing
    api_url = os.getenv('CARTHOOKS_API_URL')
    
    from urllib.parse import urlparse
    parsed_url = urlparse(api_url if api_url.startswith('http') else f'http://{api_url}')
    api_host = parsed_url.hostname
    test_url = f"http://{api_host}:9000" if api_host == 'localhost' else f"https://{api_host}"
    
    for i in range(10):
        try:
            start = time.time()
            response = client.client.get(test_url)
            duration = time.time() - start
            success_count += 1
            if i % 3 == 0:
                print(f"Request {i+1}: SUCCESS {response.status_code} in {duration:.3f}s")
        except Exception as e:
            print(f"Request {i+1}: FAILED - {str(e)[:50]}")
        time.sleep(0.5)
    
    print(f"\nSuccess rate: {success_count}/10 ({success_count*10}%)")
    client.close()

if __name__ == "__main__":
    print("Starting IPv6 disable tests...")
    
    try:
        test_ipv6_disable()
        test_multiple_requests()
        
        print("\n🎉 All IPv6 disable tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
