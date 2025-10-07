"""
Schwab SDK - Streaming (initial skeleton)

Admin (connect/login/logout), utilities (subscribe/add/unsubscribe/view),
callbacks (on_data/on_response/on_notify), and basic resubscription.

Service-specific helpers will be added in later iterations.
"""

import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import websocket  # websocket-client
except Exception as _e:  # pragma: no cover
    websocket = None  # type: ignore


class Streaming:
    """
    WebSocket Streaming client for Schwab.

    Initial focus:
    - ADMIN: connect/login/logout
    - Common utilities: subscribe/add/unsubscribe/view
    - Callbacks: on_data/on_response/on_notify
    - Resubscription after reconnect
    """

    STREAM_URL = "wss://stream.schwabapi.com/v1/ws"

    def __init__(self, client) -> None:
        self.client = client

        # WebSocket
        self._ws: Optional[websocket.WebSocketApp] = None  # type: ignore
        self._thread: Optional[threading.Thread] = None
        self._should_run = False
        self._connected_event = threading.Event()

        # Callbacks
        self._on_data: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_response: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_notify: Optional[Callable[[Dict[str, Any]], None]] = None

        # State
        self._is_logged_in = False
        self._subscriptions: List[Dict[str, Any]] = []  # history of SUBS/ADD/VIEW commands
        self._last_login_payload: Optional[Dict[str, Any]] = None
        self._request_counter: int = 1

        # Streamer info (dynamic from userPreference)
        self._streamer_url: Optional[str] = None
        self._schwab_client_customer_id: Optional[str] = None
        self._schwab_client_correl_id: Optional[str] = None
        self._schwab_client_channel: Optional[str] = None
        self._schwab_client_function_id: Optional[str] = None

    # ============================ Streamer info ==============================
    def _ensure_streamer_info(self) -> None:
        if self._streamer_url and self._schwab_client_customer_id and self._schwab_client_channel and self._schwab_client_function_id:
            return

        try:
            prefs = self.client.account.get_user_preferences()
        except Exception:
            # Try to refresh and retry once
            if hasattr(self.client, "refresh_token_now"):
                try:
                    self.client.refresh_token_now()
                except Exception:
                    pass
            prefs = self.client.account.get_user_preferences()

        # Extract streamer URL
        streamer_info = None
        if isinstance(prefs, dict):
            si = prefs.get("streamerInfo") or prefs.get("streamerinfo")
            if isinstance(si, list) and si:
                streamer_info = si[0]
            elif isinstance(si, dict):
                streamer_info = si
        if streamer_info and isinstance(streamer_info, dict):
            self._streamer_url = streamer_info.get("streamerSocketUrl") or prefs.get("streamerSocketUrl")
        else:
            self._streamer_url = prefs.get("streamerSocketUrl") if isinstance(prefs, dict) else None

        # Required IDs
        self._schwab_client_customer_id = (
            prefs.get("schwabClientCustomerId") if isinstance(prefs, dict) else None
        ) or (streamer_info.get("schwabClientCustomerId") if isinstance(streamer_info, dict) else None)
        self._schwab_client_correl_id = (
            (prefs.get("schwabClientCorrelId") if isinstance(prefs, dict) else None)
            or (streamer_info.get("schwabClientCorrelId") if isinstance(streamer_info, dict) else None)
            or f"correl_{int(time.time()*1000)}"
        )
        self._schwab_client_channel = (
            (prefs.get("SchwabClientChannel") if isinstance(prefs, dict) else None)
            or (streamer_info.get("SchwabClientChannel") if isinstance(streamer_info, dict) else None)
            or "N9"
        )
        self._schwab_client_function_id = (
            (prefs.get("SchwabClientFunctionId") if isinstance(prefs, dict) else None)
            or (streamer_info.get("SchwabClientFunctionId") if isinstance(streamer_info, dict) else None)
            or "APIAPP"
        )

        if not self._streamer_url:
            # Fallback to constant if not available (not recommended)
            self._streamer_url = self.STREAM_URL

    # ========================= Callback registration =========================
    def on_data(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._on_data = callback

    def on_response(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._on_response = callback

    def on_notify(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._on_notify = callback

    # =============================== Connection ==============================
    def connect(self) -> None:
        if websocket is None:
            raise RuntimeError("The websocket-client library is not installed. 'pip install websocket-client'")

        if self._ws is not None:
            return

        self._should_run = True
        # Ensure streamer info and dynamic URL
        self._ensure_streamer_info()

        self._ws = websocket.WebSocketApp(
            self._streamer_url or self.STREAM_URL,
            on_open=self._on_open,
            on_close=self._on_close,
            on_error=self._on_error,
            on_message=self._on_message,
        )

        def _runner() -> None:
            while self._should_run:
                try:
                    self._ws.run_forever(ping_interval=20, ping_timeout=10)  # type: ignore
                except Exception:
                    pass
                if self._should_run:
                    time.sleep(2)  # simple backoff before retrying

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()

    def wait_until_connected(self, timeout: float = 10.0) -> bool:
        """Wait until the socket is open or timeout expires."""
        return self._connected_event.wait(timeout)

    def login(
        self,
        authorization: Optional[str] = None,
        *,
        customer_id: Optional[str] = None,
        correl_id: Optional[str] = None,
        channel: Optional[str] = None,
        function_id: Optional[str] = None,
    ) -> None:
        # Prepare authorization: use current access token if not provided
        if authorization is None:
            token = self.client.get_access_token()
            if not token:
                # Try immediate refresh and then obtain token again
                try:
                    refreshed = False
                    if hasattr(self.client, "refresh_token_now"):
                        refreshed = bool(self.client.refresh_token_now())
                    if not refreshed and hasattr(self.client, "refresh_token"):
                        refreshed = bool(self.client.refresh_token())
                    if refreshed:
                        token = self.client.get_access_token()
                except Exception:
                    token = None
            if not token:
                raise RuntimeError("No access token for streaming. Run client.login() to authenticate.")
            # WS LOGIN requires Authorization without 'Bearer' prefix
            authorization = token

        # Allow pulling customer/correl from userPreference if missing
        if not (customer_id and correl_id and channel and function_id):
            # Use cached streamer info
            self._ensure_streamer_info()
            customer_id = customer_id or self._schwab_client_customer_id
            correl_id = correl_id or self._schwab_client_correl_id
            channel = channel or self._schwab_client_channel
            function_id = function_id or self._schwab_client_function_id

        payload = {
            "requests": [
                {
                    "service": "ADMIN",
                    "requestid": str(self._request_counter),
                    "command": "LOGIN",
                    "SchwabClientCustomerId": customer_id,
                    "SchwabClientCorrelId": correl_id,
                    "parameters": {
                        "Authorization": authorization,
                        "SchwabClientChannel": channel,
                        "SchwabClientFunctionId": function_id,
                    },
                }
            ]
        }
        self._request_counter += 1

        self._last_login_payload = payload
        # Ensure the connection is open
        if not self.wait_until_connected(10.0):
            raise RuntimeError("WebSocket did not connect within the expected time")
        self._send(payload)

    def logout(self, *, customer_id: Optional[str] = None, correl_id: Optional[str] = None) -> None:
        if not self._is_logged_in:
            return
        payload = {
            "requests": [
                {
                    "service": "ADMIN",
                    "requestid": "2",
                    "command": "LOGOUT",
                    "account": customer_id or "",
                    "source": "",
                    "parameters": {"correlationid": correl_id or ""},
                }
            ]
        }
        self._send(payload)
        self._is_logged_in = False

    # ================================ Utilities ===============================
    def subscribe(self, service: str, keys: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        self._common_request("SUBS", service, keys, fields, request_id)

    def add(self, service: str, keys: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("ADD", service, keys, None, request_id)

    def unsubscribe(self, service: str, keys: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", service, keys, None, request_id)

    def view(self, service: str, fields: List[int], request_id: Optional[str] = None) -> None:
        self._common_request("VIEW", service, [], fields, request_id)

    # =========================== Helpers per service ==========================
    # LEVELONE_EQUITIES
    def equities_subscribe(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            # Recommended fields (roadmap)
            fields = [0, 1, 2, 3, 4, 5, 8, 10, 18, 42, 33, 34, 35]
        self._common_request("SUBS", "LEVELONE_EQUITIES", symbols, fields, request_id)

    def equities_add(self, symbols: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("ADD", "LEVELONE_EQUITIES", symbols, None, request_id)

    def equities_unsubscribe(self, symbols: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", "LEVELONE_EQUITIES", symbols, None, request_id)

    def equities_view(self, fields: List[int], request_id: Optional[str] = None) -> None:
        self._common_request("VIEW", "LEVELONE_EQUITIES", [], fields, request_id)

    # LEVELONE_OPTIONS
    def options_subscribe(self, option_keys: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            # Recommended fields (roadmap)
            fields = [0, 2, 3, 4, 8, 16, 17, 18, 20, 28, 29, 30, 31, 37, 44]
        self._common_request("SUBS", "LEVELONE_OPTIONS", option_keys, fields, request_id)

    def options_add(self, option_keys: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("ADD", "LEVELONE_OPTIONS", option_keys, None, request_id)

    def options_unsubscribe(self, option_keys: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", "LEVELONE_OPTIONS", option_keys, None, request_id)

    def options_view(self, fields: List[int], request_id: Optional[str] = None) -> None:
        self._common_request("VIEW", "LEVELONE_OPTIONS", [], fields, request_id)

    # LEVELONE_FUTURES
    def futures_subscribe(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3, 4, 5, 8, 12, 13, 18, 19, 20, 24, 33]
        self._common_request("SUBS", "LEVELONE_FUTURES", symbols, fields, request_id)

    def futures_add(self, symbols: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("ADD", "LEVELONE_FUTURES", symbols, None, request_id)

    def futures_unsubscribe(self, symbols: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", "LEVELONE_FUTURES", symbols, None, request_id)

    def futures_view(self, fields: List[int], request_id: Optional[str] = None) -> None:
        self._common_request("VIEW", "LEVELONE_FUTURES", [], fields, request_id)

    # LEVELONE_FUTURES_OPTIONS
    def futures_options_subscribe(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3, 4, 5, 8, 12, 13, 18, 19, 20, 24, 33]
        self._common_request("SUBS", "LEVELONE_FUTURES_OPTIONS", symbols, fields, request_id)

    def futures_options_add(self, symbols: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("ADD", "LEVELONE_FUTURES_OPTIONS", symbols, None, request_id)

    def futures_options_unsubscribe(self, symbols: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", "LEVELONE_FUTURES_OPTIONS", symbols, None, request_id)

    def futures_options_view(self, fields: List[int], request_id: Optional[str] = None) -> None:
        self._common_request("VIEW", "LEVELONE_FUTURES_OPTIONS", [], fields, request_id)

    # LEVELONE_FOREX
    def forex_subscribe(self, pairs: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17, 20, 21, 27, 28, 29]
        self._common_request("SUBS", "LEVELONE_FOREX", pairs, fields, request_id)

    def forex_add(self, pairs: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("ADD", "LEVELONE_FOREX", pairs, None, request_id)

    def forex_unsubscribe(self, pairs: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", "LEVELONE_FOREX", pairs, None, request_id)

    def forex_view(self, fields: List[int], request_id: Optional[str] = None) -> None:
        self._common_request("VIEW", "LEVELONE_FOREX", [], fields, request_id)

    # ===== BOOK (NYSE/NASDAQ/OPTIONS) =====
    def nasdaq_book(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3]
        self._common_request("SUBS", "NASDAQ_BOOK", symbols, fields, request_id)

    def nyse_book(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3]
        self._common_request("SUBS", "NYSE_BOOK", symbols, fields, request_id)

    def options_book(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3]
        self._common_request("SUBS", "OPTIONS_BOOK", symbols, fields, request_id)

    # ===== CHART (EQUITY/FUTURES) =====
    def chart_equity(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            # Recommended on roadmap: 0..7
            fields = [0, 1, 2, 3, 4, 5, 6, 7]
        self._common_request("SUBS", "CHART_EQUITY", symbols, fields, request_id)

    def chart_futures(self, symbols: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            # Recommended on roadmap
            fields = [0, 1, 2, 3, 4, 5]
        self._common_request("SUBS", "CHART_FUTURES", symbols, fields, request_id)

    # ===== SCREENER (EQUITY/OPTION) =====
    def screener_equity(self, keys: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3, 4]
        self._common_request("SUBS", "SCREENER_EQUITY", keys, fields, request_id)

    def screener_options(self, keys: List[str], fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2, 3, 4]
        self._common_request("SUBS", "SCREENER_OPTION", keys, fields, request_id)

    # ===== ACCT_ACTIVITY =====
    def account_activity(self, fields: Optional[List[int]] = None, request_id: Optional[str] = None) -> None:
        if fields is None:
            fields = [0, 1, 2]
        # Obtain account hash if not cached
        account_hash = getattr(self.client, "_account_hash", None)
        if not account_hash:
            try:
                accounts = self.client.account.get_account_numbers()
                if isinstance(accounts, list) and accounts:
                    account_hash = (
                        accounts[0].get("accountHash")
                        or accounts[0].get("hashValue")
                        or accounts[0].get("hash")
                    )
                    self.client._account_hash = account_hash
            except Exception:
                account_hash = None
        if not account_hash:
            raise RuntimeError("Could not obtain account hash for ACCT_ACTIVITY")
        self._common_request("SUBS", "ACCT_ACTIVITY", [account_hash], fields, request_id)

    # ===== UNSUBSCRIBE helper per service =====
    def unsubscribe_service(self, service: str, keys: List[str], request_id: Optional[str] = None) -> None:
        self._common_request("UNSUBS", service, keys, None, request_id)

    def _common_request(
        self,
        command: str,
        service: str,
        keys: List[str],
        fields: Optional[List[int]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        rid = request_id or str(self._request_counter)
        self._request_counter += 1

        # Ensure streamer IDs
        self._ensure_streamer_info()

        # Per-request correl id
        correl = f"{service.lower()}_{int(time.time()*1000)}"
        params: Dict[str, Any] = {"keys": ",".join(keys) if keys else ""}
        if fields is not None:
            params["fields"] = ",".join(map(str, fields))

        payload: Dict[str, Any] = {
            "requests": [
                {
                    "service": service,
                    "command": command,
                    "requestid": rid,
                    "SchwabClientCustomerId": self._schwab_client_customer_id,
                    "SchwabClientCorrelId": correl,
                    "parameters": params,
                }
            ]
        }

        self._subscriptions.append(payload)
        self._send(payload)

    # ================================ Internals ================================
    def _send(self, payload: Dict[str, Any]) -> None:
        msg = json.dumps(payload, separators=(",", ":"))
        if self._ws is None:
            raise RuntimeError("WebSocket not connected. Call connect() first.")
        try:
            self._ws.send(msg)  # type: ignore
        except Exception as e:
            raise RuntimeError(f"Error sending WS message: {e}")

    def _on_open(self, _ws) -> None:  # noqa: N802 (external lib uses camelCase)
        # On open, if there was a pending login, resend it
        self._connected_event.set()
        if self._last_login_payload:
            try:
                self._send(self._last_login_payload)
            except Exception:
                pass

    def _on_close(self, _ws, *_args) -> None:  # noqa: N802
        self._is_logged_in = False
        self._connected_event.clear()

    def _on_error(self, _ws, error) -> None:  # noqa: N802
        # Transport-level errors (serialized ones come via on_response)
        if self._on_response:
            try:
                self._on_response({"service": "SYSTEM", "command": "ERROR", "content": {"message": str(error)}})
            except Exception:
                pass

    def _on_message(self, _ws, message: str) -> None:  # noqa: N802
        try:
            data = json.loads(message)
        except Exception:
            return

        # Schwab server may send different structures
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                if self._on_data:
                    self._on_data(item)
            return

        if isinstance(data, dict) and "notify" in data:
            if self._on_notify:
                self._on_notify(data)
            return

        # List of frames or single frame
        if isinstance(data, list):
            frames = data
        else:
            frames = [data]

        for frame in frames:
            service = str(frame.get("service", "")).upper()
            command = str(frame.get("command", "")).upper()

            # ADMIN responses
            if service == "ADMIN":
                if command == "LOGIN" and frame.get("content", {}).get("code") == 0:
                    self._is_logged_in = True
                    # Send resubscription
                    self._resubscribe_all()
                if self._on_response:
                    self._on_response(frame)
                continue

            # NOTIFY/HEARTBEAT
            if service == "SYSTEM" or command == "NOTIFY":
                if self._on_notify:
                    self._on_notify(frame)
                continue

            # DATA frames
            if self._on_data:
                self._on_data(frame)

    # ============================== Option Symbol Helper =============================
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
            
        Example:
            >>> ws.create_option_symbol("AAPL", "2025-12-19", "C", 200.0)
            "AAPL  251219C00200000"
        """
        # Convert expiration from YYYY-MM-DD to YYMMDD
        exp_parts = expiration.split("-")
        if len(exp_parts) != 3:
            raise ValueError("Expiration must be in YYYY-MM-DD format")
        
        year = exp_parts[0][-2:]  # Last 2 digits of year
        month = exp_parts[1]
        day = exp_parts[2]
        exp_formatted = f"{year}{month}{day}"
        
        # Convert option type to uppercase
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

    # ============================== Resubscription =============================
    def _resubscribe_all(self) -> None:
        # Resend all stored subscriptions (SUBS/ADD/VIEW)
        # Avoid re-LOGOUT/LOGIN here; only resend market commands
        for payload in list(self._subscriptions):
            try:
                self._send(payload)
            except Exception:
                pass
