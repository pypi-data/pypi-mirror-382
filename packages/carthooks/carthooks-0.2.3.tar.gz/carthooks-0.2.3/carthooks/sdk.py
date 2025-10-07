import httpx
import os
import socket
import time
import threading
from urllib.parse import urlparse
from typing import Dict, Tuple, Optional, List, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

# OAuth related classes and types

@dataclass
class OAuthConfig:
    """OAuth configuration"""
    client_id: str
    client_secret: str
    refresh_token: Optional[str] = None
    auto_refresh: bool = True
    on_token_refresh: Optional[Callable[['OAuthTokens'], None]] = None

@dataclass
class OAuthTokens:
    """OAuth token response"""
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    refresh_token: Optional[str] = None

@dataclass
class OAuthTokenRequest:
    """OAuth token request"""
    grant_type: str
    client_id: str
    client_secret: str
    user_access_token: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None

@dataclass
class OAuthAuthorizeCodeRequest:
    """OAuth authorization code request"""
    client_id: str
    redirect_uri: str
    state: str
    target_tenant_id: Optional[int] = None

@dataclass
class OAuthAuthorizeCodeResponse:
    """OAuth authorization code response"""
    redirect_url: str

@dataclass
class UserInfo:
    """Current user information"""
    user_id: int
    username: str
    email: str
    tenant_id: int
    tenant_name: str
    is_admin: bool
    scope: List[str]

class DNSCache:
    """Thread-safe DNS cache with fallback support"""

    def __init__(self, ttl: int = 300, fallback: bool = True):
        self.ttl = ttl
        self.fallback = fallback
        self._cache: Dict[str, Tuple[List[str], float]] = {}
        self._lock = threading.RLock()

    def resolve(self, hostname: str) -> str:
        """Resolve hostname to IP address with caching and fallback"""
        with self._lock:
            # Check cache first
            if hostname in self._cache:
                ips, timestamp = self._cache[hostname]
                if time.time() - timestamp < self.ttl:
                    # Cache is fresh, return first IP
                    return ips[0] if ips else self._resolve_system(hostname)
                elif self.fallback:
                    # Cache is stale but we have fallback data
                    stale_ips = ips
                else:
                    stale_ips = None
            else:
                stale_ips = None

            # Try fresh DNS resolution
            try:
                ip = self._resolve_system(hostname)
                # Update cache with successful resolution
                self._cache[hostname] = ([ip], time.time())
                return ip
            except Exception as e:
                # DNS resolution failed
                if stale_ips and self.fallback:
                    # Use stale cache as fallback
                    return stale_ips[0]
                # No fallback available, re-raise the exception
                raise e

    def _resolve_system(self, hostname: str) -> str:
        """Perform system DNS resolution"""
        return socket.gethostbyname(hostname)

    def clear(self):
        """Clear the DNS cache"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        with self._lock:
            fresh_count = 0
            stale_count = 0
            current_time = time.time()

            for hostname, (ips, timestamp) in self._cache.items():
                if current_time - timestamp < self.ttl:
                    fresh_count += 1
                else:
                    stale_count += 1

            return {
                'total_entries': len(self._cache),
                'fresh_entries': fresh_count,
                'stale_entries': stale_count
            }

class DNSCachedHTTPTransport(httpx.HTTPTransport):
    """Custom HTTP transport with DNS caching"""

    def __init__(self, dns_cache: Optional[DNSCache] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dns_cache = dns_cache

    def handle_request(self, request):
        """Handle request with DNS caching if enabled"""
        if self.dns_cache and request.url.host:
            try:
                # Resolve hostname using DNS cache
                cached_ip = self.dns_cache.resolve(request.url.host)

                # Create new URL with resolved IP
                original_host = request.url.host
                url_with_ip = request.url.copy_with(host=cached_ip)
                request = request.copy_with(url=url_with_ip)

                # Add Host header to maintain proper HTTP/1.1 behavior
                if 'host' not in request.headers:
                    request.headers['host'] = original_host

            except Exception:
                # DNS resolution failed, proceed with original request
                # This allows httpx to handle DNS resolution normally
                pass

        return super().handle_request(request)

class Result:
    def __init__(self, response):
        self.trace_id = None
        self.meta = None
        try:
            self.response = response.json()
            self.data = self.response.get('data')
            self.error = self.response.get("error")
            self.trace_id = self.response.get("traceId")
            self.meta = self.response.get("meta")
            if self.error:
                self.data = None
                self.success = False
            else:
                self.success = True
        except:
            self.data = None
            self.error = response.text
            self.success = False

    def __getitem__(self, key):
        return self.data.get(key)

    def __str__(self) -> str:
        return f"CarthooksResult(success={self.success}, data={self.data}, error={self.error})"

class Client:
    def __init__(self, timeout=None, max_connections=None, max_keepalive_connections=None, http2=None,
                 dns_cache=None, dns_cache_ttl=None, dns_fallback=None, enable_ipv6=None, 
                 oauth_config=None, access_token=None):
        """
        Initialize Carthooks client with HTTP/2 support, connection pooling, DNS caching, and OAuth support

        Args:
            timeout: Request timeout in seconds (default: 30.0, env: CARTHOOKS_TIMEOUT)
            max_connections: Maximum number of connections in the pool (default: 100, env: CARTHOOKS_MAX_CONNECTIONS)
            max_keepalive_connections: Maximum number of keep-alive connections (default: 20, env: CARTHOOKS_MAX_KEEPALIVE_CONNECTIONS)
            http2: Enable HTTP/2 support (default: True, env: CARTHOOKS_HTTP2_DISABLED to disable)
            dns_cache: Enable DNS caching (default: True, env: CARTHOOKS_DNS_CACHE_DISABLE to disable)
            dns_cache_ttl: DNS cache TTL in seconds (default: 300, env: CARTHOOKS_DNS_CACHE_TTL)
            dns_fallback: Use stale DNS cache on resolution failure (default: True, env: CARTHOOKS_DNS_FALLBACK_DISABLE to disable)
            enable_ipv6: Enable IPv6 support (default: False, env: CARTHOOKS_ENABLE_IPV6 to enable)
            oauth_config: OAuth configuration (OAuthConfig instance)
            access_token: Direct access token (alternative to OAuth, env: CARTHOOKS_ACCESS_TOKEN)
        """
        self.base_url = os.getenv('CARTHOOKS_API_URL')
        if self.base_url == None:
            self.base_url = "https://api.carthooks.com"
        self.headers = {
            'Content-Type': 'application/json',
        }

        # OAuth configuration and state
        self.oauth_config = oauth_config
        self.current_tokens: Optional[OAuthTokens] = None
        self.token_expires_at: Optional[datetime] = None

        # Set access token from parameter or environment
        if access_token is None:
            access_token = os.getenv('CARTHOOKS_ACCESS_TOKEN')
        
        if access_token:
            self.setAccessToken(access_token)

        # Get configuration from environment variables with fallbacks
        if timeout is None:
            timeout = float(os.getenv('CARTHOOKS_TIMEOUT', '30.0'))

        if max_connections is None:
            max_connections = int(os.getenv('CARTHOOKS_MAX_CONNECTIONS', '100'))

        if max_keepalive_connections is None:
            max_keepalive_connections = int(os.getenv('CARTHOOKS_MAX_KEEPALIVE_CONNECTIONS', '20'))

        if http2 is None:
            http2_disabled = os.getenv('CARTHOOKS_HTTP2_DISABLED', 'false').lower()
            http2 = not (http2_disabled in ('true', '1', 'yes', 'on'))

        # DNS cache configuration
        if dns_cache is None:
            dns_cache_disabled = os.getenv('CARTHOOKS_DNS_CACHE_DISABLE', 'false').lower()
            dns_cache = not (dns_cache_disabled in ('true', '1', 'yes', 'on'))

        if dns_cache_ttl is None:
            dns_cache_ttl = int(os.getenv('CARTHOOKS_DNS_CACHE_TTL', '300'))

        if dns_fallback is None:
            dns_fallback_disabled = os.getenv('CARTHOOKS_DNS_FALLBACK_DISABLE', 'false').lower()
            dns_fallback = not (dns_fallback_disabled in ('true', '1', 'yes', 'on'))

        # IPv6 configuration (default: disabled)
        if enable_ipv6 is None:
            enable_ipv6_env = os.getenv('CARTHOOKS_ENABLE_IPV6', 'false').lower()
            enable_ipv6 = enable_ipv6_env in ('true', '1', 'yes', 'on')

        # Force IPv4-only if IPv6 is disabled
        if not enable_ipv6:
            self._setup_ipv4_only()

        # Store IPv6 setting for reference
        self.ipv6_enabled = enable_ipv6

        # Configure connection pool limits
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections
        )

        # Initialize DNS cache if enabled
        self.dns_cache = None
        if dns_cache:
            self.dns_cache = DNSCache(ttl=dns_cache_ttl, fallback=dns_fallback)

        # Create custom transport with DNS caching
        transport = DNSCachedHTTPTransport(
            dns_cache=self.dns_cache,
            limits=limits,
            http2=http2
        )

        # Create HTTP client with HTTP/2 support, connection pooling, and DNS caching
        self.client = httpx.Client(
            timeout=timeout,
            transport=transport
        )

    def setAccessToken(self, access_token):
        """Set the access token for API authentication"""
        self.headers['Authorization'] = f'Bearer {access_token}'
        # Update client headers
        self.client.headers.update(self.headers)

    def getItems(self, app_id, collection_id, limit=20, start=0, **options):
        """Get items from a collection with pagination"""
        # Ensure valid token before making request
        self.ensure_valid_token()

        options['pagination[start]'] = start
        options['pagination[limit]'] = limit
        url = f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items'
        response = self.client.get(url, headers=self.headers, params=options)
        return Result(response)

    def getItemById(self, app_id, collection_id, item_id, fields=None):
        """Get a specific item by ID"""
        params = {}
        if fields:
            params['fields'] = fields
        response = self.client.get(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}',
            headers=self.headers,
            params=params if params else None
        )
        return Result(response)
    

# POST    /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/     OpenAPI.CreateSubItem
# PUT     /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/items/:sub_row_id/:sub_row_id     OpenAPI.UpdateSubItem
# DELETE  /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/items/:sub_row_id/:sub_row_id     OpenAPI.DeleteSubItem
    def createSubItem(self, app_id, collection_id, item_id, field_id, data):
        """Create a sub-item in a subform field"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)

    def updateSubItem(self, app_id, collection_id, item_id, field_id, sub_item_id, data):
        """Update a sub-item in a subform field"""
        print("data", data)
        response = self.client.put(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}/items/{sub_item_id}',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)

    def deleteSubItem(self, app_id, collection_id, item_id, field_id, sub_item_id):
        """Delete a sub-item from a subform field"""
        response = self.client.delete(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}/items/{sub_item_id}',
            headers=self.headers
        )
        return Result(response)
    
    def getSubmissionToken(self, app_id, collection_id, options):
        """Get a submission token for creating items"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/submission-token',
            headers=self.headers,
            json=options
        )
        return Result(response)

    def updateSubmissionToken(self, app_id, collection_id, item_id, options):
        """Update a submission token for an existing item"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/update-token',
            headers=self.headers,
            json=options
        )
        return Result(response)

    def createItem(self, app_id, collection_id, data):
        """Create a new item in a collection"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)

    def updateItem(self, app_id, collection_id, item_id, data):
        """Update an existing item"""
        response = self.client.put(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)
    
    def lockItem(self, app_id, collection_id, item_id, lock_timeout=600, lock_id=None, subject=None):
        """Lock an item to prevent concurrent modifications"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/lock',
            headers=self.headers,
            json={'lockTimeout': lock_timeout, 'lockId': lock_id, 'lockSubject': subject}
        )
        return Result(response)

    def unlockItem(self, app_id, collection_id, item_id, lock_id=None):
        """Unlock a previously locked item"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/unlock',
            headers=self.headers,
            json={'lockId': lock_id}
        )
        return Result(response)

    def deleteItem(self, app_id, collection_id, item_id):
        """Delete an item from a collection"""
        response = self.client.delete(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}',
            headers=self.headers
        )
        return Result(response)

    def getUploadToken(self):
        """Get a token for file uploads"""
        response = self.client.post(
            f'{self.base_url}/v1/uploads/token',
            headers=self.headers
        )
        return Result(response)

    def getUser(self, user_id):
        """Get user information by user ID"""
        response = self.client.get(
            f'{self.base_url}/v1/users/{user_id}',
            headers=self.headers
        )
        return Result(response)

    def getUserByToken(self, token):
        """Get user information by token"""
        response = self.client.get(
            f'{self.base_url}/v1/user-token/{token}',
            headers=self.headers
        )
        return Result(response)

    def close(self):
        """Close the client and release connection pool resources"""
        if hasattr(self, 'client'):
            self.client.close()

    def clear_dns_cache(self):
        """Clear the DNS cache"""
        if self.dns_cache:
            self.dns_cache.clear()

    def get_dns_cache_stats(self) -> Optional[Dict[str, int]]:
        """Get DNS cache statistics"""
        if self.dns_cache:
            return self.dns_cache.get_stats()
        return None

    def is_dns_cache_enabled(self) -> bool:
        """Check if DNS cache is enabled"""
        return self.dns_cache is not None

    def _setup_ipv4_only(self):
        """Force IPv4-only connections by modifying socket.getaddrinfo"""
        import socket

        # Store original getaddrinfo if not already stored
        if not hasattr(socket, '_carthooks_original_getaddrinfo'):
            socket._carthooks_original_getaddrinfo = socket.getaddrinfo

        def ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            """Custom getaddrinfo that only returns IPv4 addresses"""
            return socket._carthooks_original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

        # Replace system getaddrinfo with IPv4-only version
        socket.getaddrinfo = ipv4_only_getaddrinfo

    def is_ipv6_enabled(self) -> bool:
        """Check if IPv6 is enabled"""
        return getattr(self, 'ipv6_enabled', False)
    
    def start_watch_data(self, endpoint_url, name, app_id, collection_id, filters=None, age=432000, watch_start_time=None):
        """
        Start data monitoring
        
        Args:
            endpoint_url: SQS queue URL
            name: Monitoring task name
            app_id: Application ID
            collection_id: Collection ID
            filters: Filter conditions (optional)
            age: Monitoring validity period in seconds, default 5 days (5*24*3600)
            watch_start_time: Monitoring start timestamp (optional)
        
        Returns:
            Monitoring task information
        """
        data = {
            "endpoint_url": endpoint_url,
            "endpoint_type": "sqs",
            "name": name,
            "app_id": app_id,
            "collection_id": collection_id,
            "age": age
        }
        
        if watch_start_time:
            data["watch_start_time"] = watch_start_time
            
        if filters:
            data["filters"] = filters
            
        response = self.client.post(
            f'{self.base_url}/v1/watch-data',
            headers=self.headers,
            json=data
        )
        return Result(response)

    # OAuth Methods

    def get_oauth_token(self, request: OAuthTokenRequest) -> Result:
        """Get OAuth token using various grant types"""
        # Use form-encoded data for OAuth token requests (OAuth 2.0 standard)
        form_data = {
            'grant_type': request.grant_type,
            'client_id': request.client_id,
            'client_secret': request.client_secret,
        }
        
        if request.user_access_token:
            form_data['user_access_token'] = request.user_access_token
        if request.code:
            form_data['code'] = request.code
        if request.redirect_uri:
            form_data['redirect_uri'] = request.redirect_uri
        if request.refresh_token:
            form_data['refresh_token'] = request.refresh_token

        # Create headers for form request
        form_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        response = self.client.post(
            f'{self.base_url}/oauth/token',
            headers=form_headers,
            data=form_data
        )
        
        result = Result(response)
        
        # Store tokens if this is our client and request was successful
        if result.success and self.oauth_config and request.client_id == self.oauth_config.client_id:
            if result.data:
                tokens = OAuthTokens(
                    access_token=result.data.get('access_token', ''),
                    token_type=result.data.get('token_type', 'Bearer'),
                    expires_in=result.data.get('expires_in', 0),
                    scope=result.data.get('scope', ''),
                    refresh_token=result.data.get('refresh_token')
                )
                
                # Store tokens and expiration time
                self.current_tokens = tokens
                if tokens.expires_in > 0:
                    self.token_expires_at = datetime.now() + timedelta(seconds=tokens.expires_in)
                
                # Update authorization header
                self.setAccessToken(tokens.access_token)
                
                # Call refresh callback if provided
                if self.oauth_config.on_token_refresh:
                    self.oauth_config.on_token_refresh(tokens)
        
        return result

    def refresh_oauth_token(self, refresh_token: Optional[str] = None) -> Result:
        """Refresh OAuth token using refresh token"""
        if not self.oauth_config:
            return Result(type('MockResponse', (), {
                'json': lambda: {'error': 'OAuth configuration not provided'},
                'text': 'OAuth configuration not provided'
            })())

        token_to_use = (
            refresh_token or 
            (self.oauth_config.refresh_token if self.oauth_config else None) or
            (self.current_tokens.refresh_token if self.current_tokens else None)
        )

        if not token_to_use:
            return Result(type('MockResponse', (), {
                'json': lambda: {'error': 'No refresh token available'},
                'text': 'No refresh token available'
            })())

        request = OAuthTokenRequest(
            grant_type='refresh_token',
            client_id=self.oauth_config.client_id,
            client_secret=self.oauth_config.client_secret,
            refresh_token=token_to_use
        )

        return self.get_oauth_token(request)

    def initialize_oauth(self, user_access_token: Optional[str] = None) -> Result:
        """Initialize OAuth with client credentials"""
        if not self.oauth_config:
            return Result(type('MockResponse', (), {
                'json': lambda: {'error': 'OAuth configuration not provided'},
                'text': 'OAuth configuration not provided'
            })())

        request = OAuthTokenRequest(
            grant_type='client_credentials',
            client_id=self.oauth_config.client_id,
            client_secret=self.oauth_config.client_secret,
            user_access_token=user_access_token,
            refresh_token=self.oauth_config.refresh_token,

        )

        return self.get_oauth_token(request)

    def exchange_authorization_code(self, code: str, redirect_uri: str) -> Result:
        """Exchange authorization code for tokens"""
        if not self.oauth_config:
            return Result(type('MockResponse', (), {
                'json': lambda: {'error': 'OAuth configuration not provided'},
                'text': 'OAuth configuration not provided'
            })())

        request = OAuthTokenRequest(
            grant_type='authorization_code',
            client_id=self.oauth_config.client_id,
            client_secret=self.oauth_config.client_secret,
            code=code,
            redirect_uri=redirect_uri
        )

        return self.get_oauth_token(request)

    def get_oauth_authorize_code(self, request: OAuthAuthorizeCodeRequest) -> Result:
        """Get OAuth authorization code (requires authentication)"""
        data = {
            'client_id': request.client_id,
            'redirect_uri': request.redirect_uri,
            'state': request.state,
        }
        
        if request.target_tenant_id:
            data['target_tenant_id'] = request.target_tenant_id

        response = self.client.post(
            f'{self.base_url}/../api/oauth/get-authorize-code',
            headers=self.headers,
            json=data
        )
        return Result(response)

    def get_current_user(self) -> Result:
        """Get current user information (requires OAuth token)"""
        response = self.client.get(
            f'{self.base_url}/v1/me',
            headers=self.headers
        )
        return Result(response)

    def ensure_valid_token(self) -> bool:
        """Check if token needs refresh and refresh if necessary"""
        if (not self.oauth_config or 
            not self.oauth_config.auto_refresh or 
            not self.token_expires_at):
            return True

        # Check if token expires within 5 minutes
        five_minutes_from_now = datetime.now() + timedelta(minutes=5)
        if self.token_expires_at > five_minutes_from_now:
            return True

        refresh_token_available = False
        if self.oauth_config and self.oauth_config.refresh_token:
            refresh_token_available = True
        elif self.current_tokens and self.current_tokens.refresh_token:
            refresh_token_available = True

        if not refresh_token_available:
            result = self.initialize_oauth()
        else:
            result = self.refresh_oauth_token()
        return result.success

    def get_current_tokens(self) -> Optional[OAuthTokens]:
        """Get current OAuth tokens"""
        return self.current_tokens

    def set_oauth_config(self, config: OAuthConfig) -> None:
        """Set OAuth configuration"""
        self.oauth_config = config

    def get_oauth_config(self) -> Optional[OAuthConfig]:
        """Get OAuth configuration"""
        return self.oauth_config

    # Context manager support
    def __enter__(self):
        """Enter context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        self.close()
