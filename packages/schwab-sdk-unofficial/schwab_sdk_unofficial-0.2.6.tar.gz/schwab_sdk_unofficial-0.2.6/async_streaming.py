"""
Schwab SDK - Async Streaming
Asynchronous WebSocket streaming client.
"""

import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import websockets
except ImportError:
    websockets = None


class AsyncStreaming:
    """
    Async WebSocket Streaming client for Schwab.
    
    Provides async access to streaming functionality:
    - connect() / disconnect() - Connection management
    - login() / logout() - Authentication
    - subscribe() / unsubscribe() - Data subscriptions
    - on_data() / on_response() / on_notify() - Callbacks
    """
    
    STREAM_URL = "wss://stream.schwabapi.com/v1/ws"
    
    def __init__(self, client):
        """Initialize with async client."""
        self.client = client
        
        # WebSocket
        self._ws: Optional[websockets.WebSocketServerProtocol] = None
        self._connected = False
        self._is_logged_in = False
        
        # Callbacks
        self._on_data: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_response: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_notify: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # State
        self._subscriptions: List[Dict[str, Any]] = []
        
        # Tasks
        self._receive_task: Optional[asyncio.Task] = None
    
    async def connect(self) -> bool:
        """
        Connect to Schwab WebSocket stream.
        
        Returns:
            True if connected successfully
        """
        if websockets is None:
            raise ImportError("websockets library required for async streaming")
        
        try:
            self._ws = await websockets.connect(self.STREAM_URL)
            self._connected = True
            
            # Start receiving messages
            self._receive_task = asyncio.create_task(self._receive_messages())
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket stream."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self._ws:
            await self._ws.close()
            self._ws = None
        
        self._connected = False
        self._is_logged_in = False
    
    async def login(self) -> bool:
        """
        Login to streaming service.
        
        Returns:
            True if login successful
        """
        if not self._connected:
            raise Exception("Not connected. Call connect() first.")
        
        if not self.client.token_handler.has_valid_tokens():
            raise Exception("No valid tokens. Use client.login() first.")
        
        login_payload = {
            "requests": [{
                "service": "ADMIN",
                "requestid": "1",
                "command": "LOGIN",
                "SchwabClientCustomerId": self.client.client_id,
                "SchwabClientCorrelId": "1",
                "parameters": {
                    "Authorization": f"Bearer {self.client.token_handler.access_token}"
                }
            }]
        }
        
        try:
            await self._send(login_payload)
            self._is_logged_in = True
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    async def logout(self):
        """Logout from streaming service."""
        if not self._is_logged_in:
            return
        
        logout_payload = {
            "requests": [{
                "service": "ADMIN",
                "requestid": "2",
                "command": "LOGOUT"
            }]
        }
        
        try:
            await self._send(logout_payload)
        except Exception:
            pass
        
        self._is_logged_in = False
    
    async def _send(self, payload: Dict[str, Any]):
        """Send payload to WebSocket."""
        if not self._ws:
            raise Exception("Not connected")
        
        message = json.dumps(payload)
        await self._ws.send(message)
    
    async def _receive_messages(self):
        """Receive and process WebSocket messages."""
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {message}")
                except Exception as e:
                    print(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"Receive error: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming messages."""
        if "notify" in data:
            if self._on_notify:
                self._on_notify(data)
        elif "response" in data:
            if self._on_response:
                self._on_response(data)
        else:
            if self._on_data:
                self._on_data(data)
    
    def on_data(self, callback: Callable[[Dict[str, Any]], None]):
        """Set data callback."""
        self._on_data = callback
    
    def on_response(self, callback: Callable[[Dict[str, Any]], None]):
        """Set response callback."""
        self._on_response = callback
    
    def on_notify(self, callback: Callable[[Dict[str, Any]], None]):
        """Set notify callback."""
        self._on_notify = callback
    
    async def subscribe(self, service: str, keys: List[str], fields: Optional[List[str]] = None):
        """
        Subscribe to data stream.
        
        Args:
            service: Service name (e.g., "LEVELONE_EQUITIES")
            keys: List of symbols/keys
            fields: Optional fields to request
        """
        payload = {
            "requests": [{
                "service": service,
                "requestid": str(int(time.time() * 1000)),
                "command": "SUBS",
                "keys": keys
            }]
        }
        
        if fields:
            payload["requests"][0]["fields"] = fields
        
        await self._send(payload)
        self._subscriptions.append(payload)
    
    async def unsubscribe(self, service: str, keys: List[str]):
        """
        Unsubscribe from data stream.
        
        Args:
            service: Service name
            keys: List of symbols/keys to unsubscribe
        """
        payload = {
            "requests": [{
                "service": service,
                "requestid": str(int(time.time() * 1000)),
                "command": "UNSUBS",
                "keys": keys
            }]
        }
        
        await self._send(payload)
    
    # Service-specific helpers
    async def equities_subscribe(self, symbols: List[str], fields: Optional[List[str]] = None):
        """Subscribe to equity quotes."""
        await self.subscribe("LEVELONE_EQUITIES", symbols, fields)
    
    async def options_subscribe(self, option_symbols: List[str], fields: Optional[List[str]] = None):
        """Subscribe to option quotes."""
        await self.subscribe("LEVELONE_OPTIONS", option_symbols, fields)
    
    async def futures_subscribe(self, symbols: List[str], fields: Optional[List[str]] = None):
        """Subscribe to futures quotes."""
        await self.subscribe("LEVELONE_FUTURES", symbols, fields)
    
    async def forex_subscribe(self, pairs: List[str], fields: Optional[List[str]] = None):
        """Subscribe to forex quotes."""
        await self.subscribe("LEVELONE_FOREX", pairs, fields)
    
    async def account_activity_subscribe(self, account_hash: str, fields: Optional[List[str]] = None):
        """Subscribe to account activity."""
        await self.subscribe("ACCT_ACTIVITY", [account_hash], fields)
    
    # Option symbol helper
    @staticmethod
    def create_option_symbol(symbol: str, expiration: str, option_type: str, strike_price: float) -> str:
        """
        Creates a Schwab option symbol from individual components.
        
        Args:
            symbol: Underlying symbol (e.g., "AAPL")
            expiration: Expiration date in format "YYYY-MM-DD" (e.g., "2025-10-03")
            option_type: Option type "C" for Call or "P" for Put
            strike_price: Strike price (e.g., 257.5)
            
        Returns:
            Formatted option symbol for Schwab streaming (e.g., "AAPL  251219C00200000")
        """
        # Parse expiration date
        exp_parts = expiration.split("-")
        if len(exp_parts) != 3:
            raise ValueError("Expiration must be in YYYY-MM-DD format")
        
        year = exp_parts[0][-2:]  # Last 2 digits of year
        month = exp_parts[1]
        day = exp_parts[2]
        exp_formatted = f"{year}{month}{day}"
        
        # Validate option type
        option_type = option_type.upper()
        if option_type not in ["C", "P"]:
            raise ValueError("Option type must be 'C' for Call or 'P' for Put")
        
        # Format strike price according to Schwab standard: WWWWWddd
        # WWWWW = whole portion (5 digits), ddd = decimal portion (3 digits)
        strike_whole = int(strike_price)
        strike_decimal = int((strike_price - strike_whole) * 1000)
        strike_formatted = f"{strike_whole:05d}{strike_decimal:03d}"
        
        # Combine all components: RRRRRRYYMMDDsWWWWWddd
        return f"{symbol:<6}{exp_formatted}{option_type}{strike_formatted}"

