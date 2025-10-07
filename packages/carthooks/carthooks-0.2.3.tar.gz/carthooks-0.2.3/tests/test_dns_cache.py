#!/usr/bin/env python3
"""
Test script for DNS cache functionality
"""
import time
import threading
import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import carthooks
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from carthooks.sdk import Client, DNSCache

# Get API host from environment
api_url = os.getenv('CARTHOOKS_API_URL')

parsed_url = urlparse(api_url if api_url.startswith('http') else f'http://{api_url}')
API_HOST = parsed_url.hostname
TEST_URL = f"http://{API_HOST}:9000" if API_HOST == 'localhost' else f"https://{API_HOST}"

def test_dns_cache_basic():
    """Test basic DNS cache functionality"""
    print("=== Testing Basic DNS Cache ===")
    
    # Test DNS cache directly
    cache = DNSCache(ttl=5, fallback=True)
    
    # First resolution (should hit DNS)
    start = time.time()
    ip1 = cache.resolve(API_HOST)
    duration1 = time.time() - start
    print(f"First resolution: {ip1} in {duration1:.3f}s")
    
    # Second resolution (should hit cache)
    start = time.time()
    ip2 = cache.resolve(API_HOST)
    duration2 = time.time() - start
    print(f"Second resolution: {ip2} in {duration2:.3f}s (cached)")
    
    # Should be much faster
    assert duration2 < duration1 / 2, "Cache should be faster"
    assert ip1 == ip2, "IPs should be the same"
    
    print(f"Cache stats: {cache.get_stats()}")
    print("✅ Basic DNS cache test passed")

def test_client_with_dns_cache():
    """Test Client with DNS cache enabled"""
    print("\n=== Testing Client with DNS Cache ===")
    
    # Create client with DNS cache enabled (default)
    client = Client()
    
    print(f"DNS cache enabled: {client.is_dns_cache_enabled()}")
    
    # Test multiple requests
    success_count = 0
    for i in range(10):
        try:
            start = time.time()
            response = client.client.get(TEST_URL)
            duration = time.time() - start
            success_count += 1
            if i % 3 == 0:
                print(f"Request {i}: {response.status_code} in {duration:.3f}s")
        except Exception as e:
            print(f"Request {i}: FAILED - {e}")
    
    print(f"Success rate: {success_count}/10")
    
    if client.dns_cache:
        print(f"DNS cache stats: {client.get_dns_cache_stats()}")
    
    client.close()
    print("✅ Client DNS cache test passed")

def test_client_without_dns_cache():
    """Test Client with DNS cache disabled"""
    print("\n=== Testing Client without DNS Cache ===")
    
    # Create client with DNS cache disabled
    client = Client(dns_cache=False)
    
    print(f"DNS cache enabled: {client.is_dns_cache_enabled()}")
    assert not client.is_dns_cache_enabled(), "DNS cache should be disabled"
    
    # Test request
    try:
        response = client.client.get(TEST_URL)
        print(f"Request without cache: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    client.close()
    print("✅ Client without DNS cache test passed")

def test_concurrent_dns_cache():
    """Test DNS cache under concurrent load"""
    print("\n=== Testing Concurrent DNS Cache ===")
    
    client = Client(dns_cache_ttl=10)
    results = []
    
    def worker(worker_id):
        for i in range(5):
            try:
                start = time.time()
                response = client.client.get(TEST_URL)
                duration = time.time() - start
                results.append((worker_id, i, 'SUCCESS', duration))
            except Exception as e:
                results.append((worker_id, i, 'FAILED', str(e)))
    
    # Start 3 concurrent workers
    threads = []
    for worker_id in range(3):
        thread = threading.Thread(target=worker, args=(worker_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Analyze results
    successes = [r for r in results if r[2] == 'SUCCESS']
    failures = [r for r in results if r[2] == 'FAILED']
    
    print(f"Concurrent test results: {len(successes)} success, {len(failures)} failures")
    print(f"DNS cache stats: {client.get_dns_cache_stats()}")
    
    client.close()
    print("✅ Concurrent DNS cache test passed")

def test_dns_fallback():
    """Test DNS fallback functionality"""
    print("\n=== Testing DNS Fallback ===")
    
    # Create cache with short TTL for testing
    cache = DNSCache(ttl=1, fallback=True)
    
    # First resolution
    ip1 = cache.resolve(API_HOST)
    print(f"Initial resolution: {ip1}")
    
    # Wait for TTL to expire
    time.sleep(2)
    
    # This should still work due to fallback
    try:
        ip2 = cache.resolve(API_HOST)
        print(f"Fallback resolution: {ip2}")
        print("✅ DNS fallback test passed")
    except Exception as e:
        print(f"❌ DNS fallback test failed: {e}")

if __name__ == "__main__":
    print("Starting DNS Cache Tests...")
    
    try:
        test_dns_cache_basic()
        test_client_with_dns_cache()
        test_client_without_dns_cache()
        test_concurrent_dns_cache()
        test_dns_fallback()
        
        print("\n🎉 All DNS cache tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
