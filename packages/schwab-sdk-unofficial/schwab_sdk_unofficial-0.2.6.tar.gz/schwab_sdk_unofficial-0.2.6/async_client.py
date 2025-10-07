"""
Schwab SDK - Async Client
Asynchronous version of the main SDK client.
"""

import asyncio
import aiohttp
import json
import os
import time
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta

try:
    from .token_handler import TokenHandler
    from .authentication import Authentication
except ImportError:
    # Fallback for direct testing
    from token_handler import TokenHandler
    from authentication import Authentication

# Forward declarations for type hints
if TYPE_CHECKING:
    try:
        from .accounts import Accounts
        from .orders import Orders
        from .market import Market
        from .streaming import Streaming
    except ImportError:
        from accounts import Accounts
        from orders import Orders
        from market import Market
        from streaming import Streaming


class AsyncClient:
    """
    Asynchronous Schwab SDK client.
    
    Provides async access to all functionality:
    - client.account.* - Account, transactions, and preferences endpoints
    - client.orders.* - Order endpoints
    - client.market.* - Market data endpoints
    - client.streaming.* - WebSocket streaming
    
    Usage:
        client = AsyncClient(client_id, client_secret, redirect_uri)
        await client.login()  # Only if there are no valid tokens
        
        # Use submodules
        accounts = await client.account.get_accounts()
        quote = await client.market.get_quote("AAPL")
        await client.orders.place_order(account_hash, order_data)
    """
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        redirect_uri: str = "https://localhost:8080/callback",
        save_token: bool = True,
        token_data: Optional[dict] = None
    ):
        """
        Initializes the Async Schwab SDK client.
        
        Args:
            client_id: Schwab application Client ID
            client_secret: Schwab application Client Secret
            redirect_uri: OAuth redirect URI (default: https://localhost:8080/callback)
            save_token: Si True, guarda tokens en archivo JSON; si False, solo en memoria
            token_data: Dict opcional para inicializar tokens en memoria (refresh/boot)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Schwab API base URLs
        self.trader_base_url = "https://api.schwabapi.com/trader/v1"
        self.market_base_url = "https://api.schwabapi.com/marketdata/v1"
        
        # Initialize core components
        token_path = "schwab_tokens.json" if save_token else ":memory:"
        self.token_handler = TokenHandler(client_id, client_secret, redirect_uri, token_path, token_data)
        self.authentication = Authentication(client_id, client_secret, redirect_uri, self.token_handler)
        
        # Configure callback for automatic re-login when refresh token expires
        self.token_handler.on_refresh_token_expired = self._handle_refresh_token_expired
        
        # Initialize submodules (lazy loading to avoid circular imports)
        self._account = None
        self._orders = None
        self._market = None
        self._streaming = None
        
        # Async session for HTTP requests
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the async session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an async HTTP request with automatic token management.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Request URL
            headers: Request headers
            params: Query parameters
            data: Form data
            json_data: JSON data
            
        Returns:
            Response JSON data
        """
        await self._ensure_session()
        
        # Ensure we have valid tokens
        if not self.token_handler.has_valid_tokens():
            raise Exception("No valid tokens found. Use client.login() to authenticate.")
        
        # Add authorization header
        if headers is None:
            headers = {}
        headers['Authorization'] = f'Bearer {self.token_handler.access_token}'
        
        # Make the request
        async with self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        ) as response:
            if response.status == 401:
                # Token expired, try to refresh
                if await self._refresh_tokens():
                    # Retry with new token
                    headers['Authorization'] = f'Bearer {self.token_handler.access_token}'
                    async with self._session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        data=data,
                        json=json_data
                    ) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.json()
                else:
                    raise Exception("Authentication failed. Please login again.")
            
            response.raise_for_status()
            return await response.json()
    
    async def _refresh_tokens(self) -> bool:
        """Refresh access and refresh tokens."""
        try:
            # Use the synchronous token handler for now
            # In a full async implementation, this would be async too
            return self.token_handler.refresh_tokens()
        except Exception:
            return False
    
    def _handle_refresh_token_expired(self):
        """Handle refresh token expiration."""
        print("Refresh token expired. Please login again.")
    
    async def login(self, timeout: int = 300, auto_open_browser: bool = True) -> tuple[bool, Optional[dict]]:
        """
        Executes the OAuth authentication flow (async wrapper).
        
        Args:
            timeout: Maximum time to wait for the callback (default: 300s)
            auto_open_browser: Open browser automatically (default: True)
            
        Returns:
            Tuple of (success: bool, tokens: dict or None)
            - success: True if authentication succeeded, False otherwise
            - tokens: Dict with token data if successful, None if failed
        """
        # For now, use the synchronous login
        # In a full implementation, this would be async
        success = self.authentication.login(timeout, auto_open_browser)
        tokens = self.token_handler.get_token_payload() if success else None
        return success, tokens
    
    @property
    def account(self):
        """Access to account endpoints."""
        if self._account is None:
            from .async_accounts import AsyncAccounts
            self._account = AsyncAccounts(self)
        return self._account
    
    @property
    def orders(self):
        """Access to order endpoints."""
        if self._orders is None:
            from .async_orders import AsyncOrders
            self._orders = AsyncOrders(self)
        return self._orders
    
    @property
    def market(self):
        """Access to market data endpoints."""
        if self._market is None:
            from .async_market import AsyncMarket
            self._market = AsyncMarket(self)
        return self._market
    
    @property
    def streaming(self):
        """Access to streaming endpoints."""
        if self._streaming is None:
            try:
                from .async_streaming import AsyncStreaming
            except ImportError:
                from async_streaming import AsyncStreaming
            self._streaming = AsyncStreaming(self)
        return self._streaming
