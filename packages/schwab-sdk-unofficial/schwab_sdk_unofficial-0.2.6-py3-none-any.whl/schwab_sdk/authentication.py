"""
Schwab SDK - Authentication Handler
Handles the full OAuth flow with Schwab API.
"""

import webbrowser
import time
from typing import Optional, Dict, Any, Callable
from urllib.parse import urlencode
import requests

try:
    from .callback import CallbackServer
    from .token_handler import TokenHandler
except ImportError:
    # Fallback for direct testing
    from callback import CallbackServer
    from token_handler import TokenHandler

class Authentication:
    """
    Handles OAuth authentication with Schwab API.
    
    - Builds authorization URL
    - Starts callback server to receive authorization code
    - Exchanges code for tokens
    - Integrates with TokenHandler for persistent handling
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, token_handler: TokenHandler):
        """
        Initializes the Authentication handler.
        
        Args:
            client_id: Schwab application Client ID
            client_secret: Schwab application Client Secret
            redirect_uri: OAuth redirect URI (must match the callback server)
            token_handler: TokenHandler instance for token management
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_handler = token_handler
        
        # Schwab OAuth URLs
        self.auth_url_base = "https://api.schwabapi.com/v1/oauth/authorize"
        self.token_url = "https://api.schwabapi.com/v1/oauth/token"
        
        # Callback server
        self.callback_server: Optional[CallbackServer] = None
        
        # Last login state
        self.last_login_result: Optional[Dict[str, Any]] = None
    
    def login(self, timeout: int = 300, auto_open_browser: bool = True) -> bool:
        """
        Executes the full OAuth flow to obtain tokens.
        
        First checks whether valid tokens already exist before starting the flow.
        
        Args:
            timeout: Maximum time in seconds to wait for the callback (default: 300)
            auto_open_browser: If True, automatically opens the browser (default: True)
            
        Returns:
            True if authentication succeeded, False otherwise
        """
        # Check if we already have valid tokens
        if self.token_handler.has_valid_token():
            print("You already have valid tokens; login is not necessary")
            return True
        
        print("Starting OAuth authentication flow...")
        
        try:
            # 1. Start callback server
            if not self._start_callback_server():
                return False
            
            # 2. Build authorization URL and open browser
            auth_url = self._build_auth_url()
            print(f"Authorization URL: {auth_url}")
            
            if auto_open_browser:
                print("Opening browser automatically...")
                webbrowser.open(auth_url)
            else:
                print("Please open the URL above in your browser")
            
            # 3. Wait for callback with authorization code
            print(f"Waiting for callback (timeout: {timeout}s)...")
            callback_result = self.callback_server.wait(timeout)
            
            # 4. Stop callback server
            self._stop_callback_server()
            
            # 5. Process callback result
            if not callback_result:
                print("Timeout waiting for authorization callback")
                return False
            
            # Parameters are inside the "params" key
            params = callback_result.get("params", {})
            
            if params.get("error"):
                error = params["error"]
                error_desc = params.get("error_description", "")
                print(f"OAuth error: {error} - {error_desc}")
                return False
            
            # 6. Extract authorization code
            auth_code = params.get("code")
            if not auth_code:
                print("Authorization code not received in the callback")
                print(f"Callback received: {callback_result}")
                return False
            
            print("Authorization code received, exchanging for tokens...")
            
            # 7. Exchange code for tokens
            if self._exchange_code_for_tokens(auth_code):
                print("Authentication completed successfully!")
                return True
            else:
                print("Failed to exchange code for tokens")
                return False
                
        except Exception as e:
            print(f"Error during authentication: {e}")
            self._stop_callback_server()
            return False
    
    def _build_auth_url(self) -> str:
        """
        Builds Schwab's authorization URL.
        
        Returns:
            Full authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "api"  # Scope required by Schwab
        }
        
        return f"{self.auth_url_base}?{urlencode(params)}"
    
    def _start_callback_server(self) -> bool:
        """
        Starts the callback server to receive the authorization code.
        
        Returns:
            True if the server started successfully, False otherwise
        """
        try:
            # Extract information from redirect_uri to configure the server
            # Example: https://127.0.0.1:8443/callback -> host=127.0.0.1, port 8443
            import urllib.parse
            parsed = urllib.parse.urlparse(self.redirect_uri)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            path = parsed.path or "/callback"
            
            # Initialize callback server with full configuration
            self.callback_server = CallbackServer(
                host=host,
                port=port,
                path=path,
                force_https=True,
                adhoc_ssl=True,
                server="auto"
            )
            
            # Start the server (does not return a boolean; raises an exception if it fails)
            self.callback_server.start()
            
            print(f"Callback server started at https://{host}:{port}{path}")
            return True
                
        except Exception as e:
            print(f"Error starting callback server: {e}")
            return False
    
    def _stop_callback_server(self) -> None:
        """
        Stops the callback server.
        """
        if self.callback_server:
            try:
                self.callback_server.shutdown()
                print("Callback server stopped")
            except Exception as e:
                print(f"Error stopping callback server: {e}")
            finally:
                self.callback_server = None
    
    def _exchange_code_for_tokens(self, auth_code: str) -> bool:
        """
        Exchanges the authorization code for access and refresh tokens.
        
        Args:
            auth_code: Authorization code received from the callback
            
        Returns:
            True if the exchange was successful, False otherwise
        """
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Use Basic Authentication as is common in OAuth
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded_credentials}"
        
        try:
            print("Exchanging authorization code for tokens...")
            
            response = requests.post(
                self.token_url,
                data=urlencode(payload),
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Extract tokens
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in", 1800)  # Default 30 min
                
                if not access_token or not refresh_token:
                    print("Incomplete token response")
                    return False
                
                # Save tokens using TokenHandler
                self.token_handler.save_tokens(access_token, refresh_token, expires_in)
                
                print("Tokens saved successfully")
                return True
            
            else:
                try:
                    error_data = response.json()
                    error = error_data.get("error", "unknown_error")
                    error_desc = error_data.get("error_description", "")
                    print(f"Error exchanging tokens: {error} - {error_desc}")
                except:
                    print(f"Error exchanging tokens: HTTP {response.status_code}")
                
                return False
                
        except requests.RequestException as e:
            print(f"Network error exchanging tokens: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error exchanging tokens: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Checks if the user is authenticated with valid tokens.
        
        Returns:
            True if there are valid tokens, False otherwise
        """
        return self.token_handler.has_valid_token()
    
    def get_access_token(self) -> Optional[str]:
        """
        Gets the current access token.
        
        Returns:
            Valid access token or None if unavailable
        """
        return self.token_handler.get_access_token()
    
    def logout(self) -> None:
        """
        Signs out by deleting all tokens.
        """
        print("Signing out...")
        self.token_handler._clear_tokens()
        print("Session closed successfully")
    
    def __del__(self):
        """
        Destructor to ensure the callback server is closed.
        """
        self._stop_callback_server()
