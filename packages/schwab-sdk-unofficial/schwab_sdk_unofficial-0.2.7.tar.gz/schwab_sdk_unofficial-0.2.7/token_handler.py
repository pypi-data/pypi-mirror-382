"""
Schwab SDK - Token Handler
Handles automatic rotation of access and refresh tokens.
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlencode

class TokenHandler:
    """
    Manages access and refresh tokens with automatic rotation.
    
    - Automatic rotation of access token every 29 minutes
    - Automatic rotation of refresh token every 6 days 23 hours
    - Manual refresh available
    - Robust error handling
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, token_path: str, token_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the TokenHandler.
        
        Args:
            client_id: Schwab application Client ID
            client_secret: Schwab application Client Secret
            redirect_uri: Redirect URI for OAuth
            token_path: Path to token file or ":memory:" for in-memory mode
            token_data: Optional token payload dict to initialize tokens in-memory
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Schwab URLs
        self.token_url = "https://api.schwabapi.com/v1/oauth/token"
        
        # Tokens and metadata
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.access_token_expires_at: Optional[datetime] = None
        self.refresh_token_expires_at: Optional[datetime] = None
        
        # Persistence mode
        self._in_memory_mode = (token_path == ":memory:")
        # File path to persist tokens when not in-memory
        self.token_file = None if self._in_memory_mode else token_path
        # In-memory payload mirror (used when _in_memory_mode = True)
        self._last_token_payload: Optional[Dict[str, Any]] = None
        
        # Threading for auto-refresh
        self._refresh_timer: Optional[threading.Timer] = None
        self._refresh_token_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        
        # Callback for re-login when the refresh token expires
        self.on_refresh_token_expired = None
        
        # Initialize tokens either from provided dict or from disk
        initialized = False
        if token_data:
            try:
                self._init_from_dict(token_data)
                initialized = True
            except Exception as e:
                print(f"Error initializing tokens from token_data: {e}")
        if not initialized and not self._in_memory_mode:
            # Load existing tokens if present on disk
            self.load_tokens()
        elif not initialized and self._in_memory_mode:
            # In-memory mode without token_data: start empty
            pass

    def _init_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Initialize tokens from a provided dictionary.

        Accepted keys:
        - access_token (str)
        - refresh_token (str)
        - expires_in (int seconds) OR access_token_expires_at (ISO string)
        - refresh_token_expires_at (ISO string, optional)
        """
        with self._lock:
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")

            now = datetime.now()

            # Access token expiry
            access_expires_at_iso = data.get("access_token_expires_at")
            expires_in = data.get("expires_in")
            if access_expires_at_iso:
                try:
                    self.access_token_expires_at = datetime.fromisoformat(access_expires_at_iso)
                except Exception:
                    # Fallback: treat as seconds from now if parsing fails
                    if isinstance(access_expires_at_iso, (int, float)):
                        self.access_token_expires_at = now + timedelta(seconds=int(access_expires_at_iso))
            elif isinstance(expires_in, (int, float)):
                self.access_token_expires_at = now + timedelta(seconds=int(expires_in))
            else:
                # Default 30 minutes if not provided
                self.access_token_expires_at = now + timedelta(minutes=30)

            # Refresh token expiry
            refresh_expires_at_iso = data.get("refresh_token_expires_at")
            if refresh_expires_at_iso:
                try:
                    self.refresh_token_expires_at = datetime.fromisoformat(refresh_expires_at_iso)
                except Exception:
                    # Default ~7 days from now if parsing fails
                    self.refresh_token_expires_at = now + timedelta(days=6, hours=23)
            else:
                # Default ~7 days from now if not provided
                self.refresh_token_expires_at = now + timedelta(days=6, hours=23)

            # Schedule auto-refresh if we have at least a refresh token
            if self.refresh_token:
                self._schedule_auto_refresh()
    
    def save_tokens(self, access_token: str, refresh_token: str, expires_in: int = 1800) -> None:
        """
        Persist tokens securely.
        
        Args:
            access_token: Access token
            refresh_token: Refresh token
            expires_in: Seconds until the access token expires (default 1800 = 30 min)
        """
        with self._lock:
            self.access_token = access_token
            self.refresh_token = refresh_token
            
            # Compute expiration timestamps
            now = datetime.now()
            self.access_token_expires_at = now + timedelta(seconds=expires_in)
            # Refresh token expires in ~7 days; schedule at 6d 23h to be safe
            self.refresh_token_expires_at = now + timedelta(days=6, hours=23)
            
            # Prepare payload
            token_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_token_expires_at": self.access_token_expires_at.isoformat(),
                "refresh_token_expires_at": self.refresh_token_expires_at.isoformat()
            }
            
            if self._in_memory_mode:
                # Store only in-memory
                self._last_token_payload = token_data
            else:
                # Persist to disk
                try:
                    if not self.token_file:
                        raise ValueError("token_file is not set")
                    with open(self.token_file, 'w') as f:
                        json.dump(token_data, f, indent=2)
                except Exception as e:
                    print(f"Error saving tokens: {e}")
            
            # Schedule auto-refresh
            self._schedule_auto_refresh()
    
    def load_tokens(self) -> bool:
        """
        Load existing tokens from disk.
        
        Returns:
            True if valid tokens were loaded, False otherwise
        """
        if self._in_memory_mode:
            # Nothing to load from disk in memory mode
            return False
        if not os.path.exists(self.token_file):
            return False
        
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            # Parse expiration timestamps
            if token_data.get("access_token_expires_at"):
                self.access_token_expires_at = datetime.fromisoformat(
                    token_data["access_token_expires_at"]
                )
            
            if token_data.get("refresh_token_expires_at"):
                self.refresh_token_expires_at = datetime.fromisoformat(
                    token_data["refresh_token_expires_at"]
                )
            
            # Verify the refresh token is still valid
            if self.refresh_token_expires_at and datetime.now() >= self.refresh_token_expires_at:
                print("Refresh token expired, clearing tokens")
                self._clear_tokens()
                return False
            
            # Schedule auto-refresh if we have valid tokens
            if self.refresh_token:
                self._schedule_auto_refresh()
                return True
                
            return False
            
        except Exception as e:
            print(f"Error loading tokens: {e}")
            return False
    
    def has_valid_token(self) -> bool:
        """
        Check if we have a valid access token.
        
        Returns:
            True if the access token is valid, False otherwise
        """
        if not self.access_token or not self.access_token_expires_at:
            return False
        
        # Consider valid if more than 1 minute remains before expiry
        return datetime.now() < (self.access_token_expires_at - timedelta(minutes=1))
    
    def get_access_token(self) -> Optional[str]:
        """
        Get the current access token (without automatic refresh).
        
        Returns:
            Access token if valid, None otherwise
        """
        if self.has_valid_token():
            return self.access_token
        return None
    
    def refresh_token_now(self) -> bool:
        """
        Immediately refresh the access token using the refresh token.
        
        Returns:
            True if the refresh succeeded, False otherwise
        """
        if not self.refresh_token:
            print("No refresh token available")
            return False
        
        return self._refresh_access_token()
    
    def _refresh_access_token(self) -> bool:
        """
        Refresh the access token using grant_type=refresh_token.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            return False
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=urlencode(payload),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Save new tokens
                self.save_tokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token", self.refresh_token),
                    expires_in=token_data.get("expires_in", 1800)
                )
                
                print("Access token refreshed successfully")
                return True
            
            else:
                error_data = response.json() if response.content else {}
                error = error_data.get("error", "unknown_error")
                
                # Specific error handling
                if error in ["invalid_grant", "invalid_client"]:
                    print(f"Refresh token expired or invalid ({error}), re-login required")
                    self._clear_tokens()
                    # Trigger callback for re-login if configured
                    if self.on_refresh_token_expired:
                        self.on_refresh_token_expired()
                else:
                    print(f"Error refreshing token: {error}")
                
                return False
                
        except Exception as e:
            print(f"Exception while refreshing token: {e}")
            return False
    
    def _schedule_auto_refresh(self) -> None:
        """
        Schedule automatic token rotation.
        """
        # Cancel existing timers
        if self._refresh_timer:
            self._refresh_timer.cancel()
        if self._refresh_token_timer:
            self._refresh_token_timer.cancel()
        
        if not self.access_token_expires_at or not self.refresh_token_expires_at:
            return
        
        now = datetime.now()
        
        # Schedule access token refresh (29 minutes from now)
        access_refresh_seconds = 29 * 60  # 29 minutes
        if self.access_token_expires_at > now:
            # If the current token hasn't expired, compute remaining time - 1 minute buffer
            time_until_expires = (self.access_token_expires_at - now).total_seconds()
            access_refresh_seconds = max(60, time_until_expires - 60)  # Minimum 1 minute
        
        self._refresh_timer = threading.Timer(access_refresh_seconds, self._auto_refresh_access_token)
        self._refresh_timer.daemon = True
        self._refresh_timer.start()
        
        # Schedule refresh token handler (6 days 23 hours from creation)
        refresh_token_seconds = (self.refresh_token_expires_at - now).total_seconds()
        if refresh_token_seconds > 0:
            self._refresh_token_timer = threading.Timer(refresh_token_seconds, self._auto_refresh_refresh_token)
            self._refresh_token_timer.daemon = True
            self._refresh_token_timer.start()
        
        print(f"Auto-refresh scheduled: access token in {access_refresh_seconds/60:.1f} min, refresh token in {refresh_token_seconds/3600:.1f} hours")
    
    def _auto_refresh_access_token(self) -> None:
        """
        Callback for automatic access token refresh every 29 minutes.
        """
        print("Running automatic access token refresh...")
        success = self._refresh_access_token()
        
        if success:
            # Schedule the next refresh in 29 minutes
            self._refresh_timer = threading.Timer(29 * 60, self._auto_refresh_access_token)
            self._refresh_timer.daemon = True
            self._refresh_timer.start()
        else:
            print("Auto-refresh failed; manual re-login required")
    
    def _auto_refresh_refresh_token(self) -> None:
        """
        Callback when the refresh token is about to expire.
        Triggers re-login if a callback is configured.
        """
        print("Refresh token expiring; re-login required")
        self._clear_tokens()
        
        if self.on_refresh_token_expired:
            self.on_refresh_token_expired()
    
    def _clear_tokens(self) -> None:
        """
        Clear all tokens and cancel timers.
        """
        with self._lock:
            self.access_token = None
            self.refresh_token = None
            self.access_token_expires_at = None
            self.refresh_token_expires_at = None
            
            # Cancel timers
            if self._refresh_timer:
                self._refresh_timer.cancel()
                self._refresh_timer = None
            if self._refresh_token_timer:
                self._refresh_token_timer.cancel()
                self._refresh_token_timer = None
            
            # Remove token file (file mode only)
            if not self._in_memory_mode and self.token_file:
                try:
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                except Exception as e:
                    print(f"Error deleting token file: {e}")
            # Clear in-memory payload
            self._last_token_payload = None
    
    def cleanup(self) -> None:
        """
        Clean up resources (timers) when the object is destroyed.
        """
        if self._refresh_timer:
            self._refresh_timer.cancel()
        if self._refresh_token_timer:
            self._refresh_token_timer.cancel()

    def get_token_payload(self) -> Optional[Dict[str, Any]]:
        """
        Return the current token payload as a dict. In file mode this mirrors
        the last saved state; in memory mode this is the authoritative store.
        
        Returns:
            Dict with access_token, refresh_token, access_token_expires_at, refresh_token_expires_at
            or None if no tokens are available.
        """
        if self.access_token and self.refresh_token and self.access_token_expires_at and self.refresh_token_expires_at:
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "access_token_expires_at": self.access_token_expires_at.isoformat(),
                "refresh_token_expires_at": self.refresh_token_expires_at.isoformat(),
            }
        return self._last_token_payload
    
    def __del__(self):
        """
        Destructor to clean up resources.
        """
        self.cleanup()
