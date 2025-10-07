"""
Schwab SDK - Client Principal
Main class that orchestrates all SDK modules.
"""

import os
import time
from typing import Optional, TYPE_CHECKING
import requests

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


class Client:
    """
    Main Schwab SDK client.
    
    Provides access to all functionality:
    - client.account.* - Account, transactions, and preferences endpoints
    - client.orders.* - Order endpoints
    - client.market.* - Market data endpoints
    - client.streaming.* - WebSocket streaming
    
    Usage:
        client = Client(client_id, client_secret, redirect_uri)
        client.login()  # Only if there are no valid tokens
        
        # Use submodules
        accounts = client.account.get_accounts()
        quote = client.market.get_quote("AAPL")
        client.orders.place_order(account_hash, order_data)
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
        Initializes the Schwab SDK client.
        
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
        self._account_module: Optional['Accounts'] = None
        self._orders_module: Optional['Orders'] = None  
        self._market_module: Optional['Market'] = None
        self._streaming_module: Optional['Streaming'] = None
        
        # Auto-login if there are no valid tokens
        self._auto_authenticate()
    
    @property
    def account(self) -> 'Accounts':
        """
        Access to the accounts, transactions, and preferences module.
        
        Returns:
            Instance of the Accounts module
        """
        if self._account_module is None:
            try:
                from .accounts import Accounts
            except ImportError:
                from accounts import Accounts
            self._account_module = Accounts(self)
        return self._account_module
    
    @property 
    def orders(self) -> 'Orders':
        """
        Access to the orders module.
        
        Returns:
            Instance of the Orders module
        """
        if self._orders_module is None:
            try:
                from .orders import Orders
            except ImportError:
                from orders import Orders
            self._orders_module = Orders(self)
        return self._orders_module
    
    @property
    def market(self) -> 'Market':
        """
        Access to the market data module.
        
        Returns:
            Instance of the Market module
        """
        if self._market_module is None:
            try:
                from .market import Market
            except ImportError:
                from market import Market
            self._market_module = Market(self)
        return self._market_module
    
    @property
    def streaming(self) -> 'Streaming':
        """
        Access to the WebSocket streaming module.
        
        Returns:
            Instance of the Streaming module
        """
        if self._streaming_module is None:
            try:
                from .streaming import Streaming
            except ImportError:
                from streaming import Streaming
            self._streaming_module = Streaming(self)
        return self._streaming_module
    
    def login(self, timeout: int = 300, auto_open_browser: bool = True) -> tuple[bool, Optional[dict]]:
        """
        Executes the OAuth authentication flow.
        
        Args:
            timeout: Maximum time to wait for the callback (default: 300s)
            auto_open_browser: Open browser automatically (default: True)
            
        Returns:
            Tuple of (success: bool, tokens: dict or None)
            - success: True if authentication succeeded, False otherwise
            - tokens: Dict with token data if successful, None if failed
        """
        success = self.authentication.login(timeout, auto_open_browser)
        tokens = self.token_handler.get_token_payload() if success else None
        return success, tokens
    
    def has_valid_token(self) -> bool:
        """
        Checks whether there are valid access tokens.
        
        Returns:
            True if tokens are valid, False otherwise
        """
        return self.token_handler.has_valid_token()
    
    def refresh_token(self) -> bool:
        """
        Automatically refreshes the access token.
        
        Automatic rotation is handled internally every 29 minutes.
        This method is primarily informational.
        
        Returns:
            True if there are valid tokens or refresh succeeded, False otherwise
        """
        if self.has_valid_token():
            return True
        return self.token_handler.refresh_token_now()
    
    def refresh_token_now(self) -> bool:
        """
        Forces an immediate access token refresh.
        
        Returns:
            True if the refresh succeeded, False otherwise
        """
        return self.token_handler.refresh_token_now()
    
    def logout(self) -> None:
        """
        Signs out by deleting all tokens.
        """
        self.authentication.logout()
    
    def get_access_token(self) -> Optional[str]:
        """
        Retrieves the current access token for use in requests.
        
        Returns:
            Valid access token or None if unavailable
        """
        return self.token_handler.get_access_token()
    
    def get_auth_headers(self) -> dict:
        """
        Retrieves authentication headers for API requests.
        
        Returns:
            Dict with Authorization headers, or an empty dict if no token
        """
        token = self.get_access_token()
        if token:
            return {
                "Authorization": f"Bearer {token}"
            }
        return {}

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: int = 15,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> requests.Response:
        """
        Performs an HTTP request with:
        - Automatic Authorization headers
        - Token refresh on 401 (once)
        - Retries with backoff for 429/5xx
        
        Returns:
            requests.Response
        """
        # Merge headers
        req_headers = {**self.get_auth_headers(), **(headers or {})}

        def _send() -> requests.Response:
            return requests.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                headers=req_headers,
                timeout=timeout,
            )

        last_exc: Optional[Exception] = None
        attempt = 0
        while attempt < max_retries:
            try:
                resp = _send()
                # Handle 401: try refresh once and retry immediately
                if resp.status_code == 401:
                    try:
                        if self.refresh_token_now():
                            req_headers = {**self.get_auth_headers(), **(headers or {})}
                            resp = _send()
                            if resp.status_code != 401:
                                return resp
                    except Exception:
                        pass
                    # If still 401, return response for caller to handle
                    return resp

                # Retries for 429 and 5xx
                if resp.status_code in (429, 500, 502, 503, 504):
                    sleep_s = backoff_factor * (2 ** attempt)
                    time.sleep(sleep_s)
                    attempt += 1
                    continue
                return resp
            except requests.RequestException as e:
                last_exc = e
                sleep_s = backoff_factor * (2 ** attempt)
                time.sleep(sleep_s)
                attempt += 1

        # If we exhausted retries and had an exception, re-raise; otherwise, send once more
        if last_exc:
            raise last_exc
        # Unlikely case: no exception but nothing returned
        return _send()
    
    def is_authenticated(self) -> bool:
        """
        Checks whether the client is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.authentication.is_authenticated()
    
    def _auto_authenticate(self) -> None:
        """
        Attempts automatic authentication if there are no valid tokens.
        """
        if not self.has_valid_token():
            print("No valid tokens found. Use client.login() to authenticate.")
        else:
            print("Client authenticated with valid tokens")
    
    def _handle_refresh_token_expired(self) -> None:
        """
        Callback executed when the refresh token expires.
        
        Notifies the user that re-login is required.
        """
        print("Refresh token expired. Please run client.login() to re-authenticate.")
    
    def __enter__(self):
        """
        Context manager entry.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - clean up resources.
        """
        if hasattr(self, 'token_handler'):
            self.token_handler.cleanup()
    
    def __del__(self):
        """
        Destructor - clean up resources.
        """
        if hasattr(self, 'token_handler'):
            self.token_handler.cleanup()
    
    def __repr__(self) -> str:
        """
        String representation of the client.
        """
        status = "authenticated" if self.is_authenticated() else "not authenticated"
        return f"SchwabClient(client_id='{self.client_id[:8]}...', status='{status}')"
