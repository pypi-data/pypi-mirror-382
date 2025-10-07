"""
Schwab SDK - Orders Module
Handles all endpoints related to orders.
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from datetime import datetime, timedelta
import re


class Orders:
    """
    Module for endpoints related to orders.
    
    Includes functionality to:
    - Retrieve existing orders
    - Place new orders
    - Cancel orders
    - Replace orders
    - Order preview
    
    All methods that create/modify orders extract the order_id
    from the Location header and add it to the JSON response.
    """
    
    def __init__(self, client):
        """
        Initializes the Orders module.
        
        Args:
            client: Instance of the main client
        """
        self.client = client
        self.base_url = client.trader_base_url
        # Allowed values (case-insensitive) for the 'status' query param
        self._allowed_status_values = {
            "AWAITING_PARENT_ORDER",
            "AWAITING_CONDITION",
            "AWAITING_STOP_CONDITION",
            "AWAITING_MANUAL_REVIEW",
            "ACCEPTED",
            "AWAITING_UR_OUT",
            "PENDING_ACTIVATION",
            "QUEUED",
            "WORKING",
            "REJECTED",
            "PENDING_CANCEL",
            "CANCELED",
            "PENDING_REPLACE",
            "REPLACED",
            "FILLED",
            "EXPIRED",
            "NEW",
            "AWAITING_RELEASE_TIME",
            "PENDING_ACKNOWLEDGEMENT",
            "PENDING_RECALL",
            "UNKNOWN",
        }
    
    def get_orders(
        self,
        account_hash: str,
        from_entered_time: str = None,
        to_entered_time: str = None,
        status: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves all orders for a specific account.
        
        GET /accounts/{accountNumber}/orders
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            from_entered_time: Date from which to retrieve orders (ISO format). If not specified, uses 60 days back.
            to_entered_time: Date up to which to retrieve orders (ISO format). If not specified, uses current date.
            
        Returns:
            Dict with full HTTP metadata + native response:
            {
                'status_code': 200,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': [...]  # Schwab native list of orders
            }
        """
        # Date normalization: accepts 'YYYY-MM-DD' or full ISO.
        def _normalize_dt(dt: Optional[str], *, is_end: bool) -> Optional[str]:
            if not dt:
                return None
            s = str(dt).strip()
            import re as _re
            if _re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
                return f"{s}T23:59:59.000Z" if is_end else f"{s}T00:00:00.000Z"
            return s

        start_norm = _normalize_dt(from_entered_time, is_end=False) if from_entered_time else None
        end_norm = _normalize_dt(to_entered_time, is_end=True) if to_entered_time else None

        # If both are missing, default to the last 60 days
        if not start_norm and not end_norm:
            from datetime import datetime, timedelta
            to_date = datetime.now()
            from_date = to_date - timedelta(days=60)
            start_norm = from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            end_norm = to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        # If only one is present, derive the other for the same day
        elif start_norm and not end_norm:
            import re as _re
            m = _re.search(r"(\d{4}-\d{2}-\d{2})", start_norm)
            base = m.group(1) if m else start_norm[:10]
            end_norm = f"{base}T23:59:59.000Z"
        elif end_norm and not start_norm:
            import re as _re
            m = _re.search(r"(\d{4}-\d{2}-\d{2})", end_norm)
            base = m.group(1) if m else end_norm[:10]
            start_norm = f"{base}T00:00:00.000Z"
        
        endpoint = f"{self.base_url}/accounts/{account_hash}/orders"
        # Add required parameters
        params = {
            'fromEnteredTime': start_norm,
            'toEnteredTime': end_norm,
        }
        if status:
            # Normalize to uppercase (case-insensitive). Strict validation is not enforced.
            norm_status = str(status).strip().upper()
            params['status'] = norm_status
        if max_results is not None:
            params['maxResults'] = max_results
        try:
            response = self.client._request("GET", endpoint, params=params, timeout=30)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'GET',
                'params': params
            }
            
            # Process data based on status
            if result['success']:
                try:
                    schwab_data = response.json()
                except:
                    schwab_data = []
                result['data'] = schwab_data
                
            else:
                # Handle errors
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'GET',
                'params': params,
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def place_order(self, account_hash: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Places a new order for a specific account.
        
        POST /accounts/{accountNumber}/orders
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            order_data: Order payload in JSON format
            
        Returns:
            Dict with full HTTP metadata + native response + order_id:
            {
                'status_code': 201,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': {...},  # Schwab native response
                'order_id': '123456'
            }
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/orders"
        headers = {"Content-Type": "application/json"}
        try:
            response = self.client._request("POST", endpoint, json=order_data, headers=headers, timeout=15)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'POST'
            }
            
            # Process data based on status
            if result['success']:
                # Get Schwab native JSON response
                try:
                    schwab_data = response.json() if response.text else {}
                except:
                    schwab_data = {}
                
                result['data'] = schwab_data
                
                # Extract order_id from the Location header
                order_id = self._extract_order_id_from_location(response.headers.get("Location"))
                if order_id:
                    result['order_id'] = order_id
                
            else:
                # Handle errors - include error info
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'POST',
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def get_order(self, account_hash: str, order_id: str) -> Dict[str, Any]:
        """
        Retrieves a specific order by its ID.
        
        GET /accounts/{accountNumber}/orders/{orderId}
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            order_id: Order ID
            
        Returns:
            Dict with full HTTP metadata + native response:
            {
                'status_code': 200,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': {...}  # Specific order information
            }
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/orders/{order_id}"
        try:
            response = self.client._request("GET", endpoint, timeout=10)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'GET',
                'order_id': order_id
            }
            
            # Process data based on status
            if result['success']:
                try:
                    schwab_data = response.json()
                except:
                    schwab_data = {}
                result['data'] = schwab_data
                
            else:
                # Handle errors
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'GET',
                'order_id': order_id,
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def cancel_order(self, account_hash: str, order_id: str) -> Dict[str, Any]:
        """
        Cancels a specific order.
        
        DELETE /accounts/{accountNumber}/orders/{orderId}
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            order_id: ID of the order to cancel
            
        Returns:
            Dict with full HTTP metadata + native response:
            {
                'status_code': 200,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': {...},  # Schwab native response
                'order_id': '123456'
            }
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/orders/{order_id}"
        try:
            response = self.client._request("DELETE", endpoint, timeout=10)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'DELETE',
                'order_id': order_id
            }
            
            # Process data based on status
            if result['success']:
                try:
                    schwab_data = response.json()
                except:
                    schwab_data = {}
                result['data'] = schwab_data
                # Try to extract order_id from the Location header if present
                extracted_id = self._extract_order_id_from_location(response.headers.get("Location"))
                if extracted_id:
                    result['order_id'] = extracted_id
                
            else:
                # Handle errors
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'DELETE',
                'order_id': order_id,
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def replace_order(self, account_hash: str, order_id: str, new_order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replaces an existing order with new information.
        
        PUT /accounts/{accountNumber}/orders/{orderId}
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            order_id: ID of the order to replace
            new_order_data: New order payload in JSON format
            
        Returns:
            Dict with full HTTP metadata + native response + order_id:
            {
                'status_code': 201,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': {...},  # Schwab native response
                'order_id': '123456'
            }
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/orders/{order_id}"
        headers = {"Content-Type": "application/json"}
        try:
            response = self.client._request("PUT", endpoint, json=new_order_data, headers=headers, timeout=15)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'PUT',
                'original_order_id': order_id
            }
            
            # Process data based on status
            if result['success']:
                # Get Schwab native JSON response
                try:
                    schwab_data = response.json() if response.text else {}
                except:
                    schwab_data = {}
                
                result['data'] = schwab_data
                
                # Extract new order_id from the Location header
                new_order_id = self._extract_order_id_from_location(response.headers.get("Location"))
                if new_order_id:
                    result['order_id'] = new_order_id
                
            else:
                # Handle errors
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'PUT',
                'original_order_id': order_id,
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def get_all_orders(
        self,
        from_entered_time: str = None,
        to_entered_time: str = None,
        status: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves all orders for all accounts.
        
        GET /orders
        
        Args:
            from_entered_time: Date from which to retrieve orders (ISO format). If not specified, uses 60 days back.
            to_entered_time: Date up to which to retrieve orders (ISO format). If not specified, uses current date.
        
        Returns:
            Dict with full HTTP metadata + native response:
            {
                'status_code': 200,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': [...]  # Orders from all accounts
            }
        """
        # Date normalization: accepts 'YYYY-MM-DD' or full ISO.
        def _normalize_dt(dt: Optional[str], *, is_end: bool) -> Optional[str]:
            if not dt:
                return None
            s = str(dt).strip()
            import re as _re
            if _re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
                return f"{s}T23:59:59.000Z" if is_end else f"{s}T00:00:00.000Z"
            return s

        start_norm = _normalize_dt(from_entered_time, is_end=False) if from_entered_time else None
        end_norm = _normalize_dt(to_entered_time, is_end=True) if to_entered_time else None

        # If both are missing, default to the last 60 days
        if not start_norm and not end_norm:
            from datetime import datetime, timedelta
            to_date = datetime.now()
            from_date = to_date - timedelta(days=60)
            start_norm = from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            end_norm = to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        # If only one is present, derive the other for the same day
        elif start_norm and not end_norm:
            import re as _re
            m = _re.search(r"(\d{4}-\d{2}-\d{2})", start_norm)
            base = m.group(1) if m else start_norm[:10]
            end_norm = f"{base}T23:59:59.000Z"
        elif end_norm and not start_norm:
            import re as _re
            m = _re.search(r"(\d{4}-\d{2}-\d{2})", end_norm)
            base = m.group(1) if m else end_norm[:10]
            start_norm = f"{base}T00:00:00.000Z"
        
        endpoint = f"{self.base_url}/orders"
        # Add required parameters
        params = {
            'fromEnteredTime': start_norm,
            'toEnteredTime': end_norm,
        }
        if status:
            norm_status = str(status).strip().upper()
            params['status'] = norm_status
        if max_results is not None:
            params['maxResults'] = max_results
        try:
            response = self.client._request("GET", endpoint, params=params, timeout=30)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'GET',
                'params': params
            }
            
            # Process data based on status
            if result['success']:
                try:
                    schwab_data = response.json()
                except:
                    schwab_data = []
                result['data'] = schwab_data
                
            else:
                # Handle errors
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'GET',
                'params': params,
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def preview_order(self, account_hash: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Previews an order without placing it.
        
        POST /accounts/{accountNumber}/previewOrder
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            order_data: Order payload to preview
            
        Returns:
            Dict with full HTTP metadata + native response:
            {
                'status_code': 200,
                'success': True,
                'headers': {...},
                'url': 'https://...',
                'elapsed_seconds': 0.5,
                'data': {...}  # Schwab native preview information
            }
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/previewOrder"
        headers = {"Content-Type": "application/json"}
        try:
            response = self.client._request("POST", endpoint, json=order_data, headers=headers, timeout=15)
            
            # Prepare response with full metadata
            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'url': str(response.url),
                'elapsed_seconds': response.elapsed.total_seconds(),
                'method': 'POST'
            }
            
            # Process data based on status
            if result['success']:
                try:
                    schwab_data = response.json()
                except:
                    schwab_data = {}
                result['data'] = schwab_data
                # Try to extract order_id from the Location header if present
                extracted_id = self._extract_order_id_from_location(response.headers.get("Location"))
                if extracted_id:
                    result['order_id'] = extracted_id
                
            else:
                # Handle errors
                try:
                    error_data = response.json() if response.text else {}
                except:
                    error_data = {'error': response.text or 'No error details'}
                
                result['data'] = error_data
                result['error_message'] = f"{response.status_code} {response.reason} for url: {response.url}"
                
                # Raise exception as before to maintain compatibility
                response.raise_for_status()
            
            return result
            
        except requests.RequestException as e:
            # On exception, return error metadata
            return {
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'success': False,
                'headers': dict(getattr(e.response, 'headers', {})) if hasattr(e, 'response') else {},
                'url': str(getattr(e.response, 'url', endpoint)) if hasattr(e, 'response') else endpoint,
                'elapsed_seconds': 0,
                'method': 'POST',
                'data': {'error': str(e)},
                'error_message': str(e)
            }
    
    def _extract_order_id_from_location(self, location_header: Optional[str]) -> Optional[str]:
        """
        Extracts the order_id from the Location header.
        
        The Location header typically has the format:
        https://api.schwabapi.com/trader/v1/accounts/{accountHash}/orders/{orderId}
        
        Args:
            location_header: Location header value
            
        Returns:
            Extracted Order ID or None if it could not be extracted
        """
        if not location_header:
            return None
        
        try:
            # Look for pattern /orders/{order_id} at the end of the URL
            match = re.search(r'/orders/([^/]+)(?:/.*)?$', location_header)
            if match:
                return match.group(1)
            
            # Fallback: take the last segment of the URL
            segments = location_header.rstrip('/').split('/')
            if len(segments) > 0:
                return segments[-1]
            
        except Exception as e:
            print(f"Error extracting order_id from Location header: {e}")
        
        return None

    # ===== Helpers to build common orders =====
    @staticmethod
    def build_limit_order(symbol: str, quantity: int, price: float, instruction: str = "BUY") -> Dict[str, Any]:
        return {
            "orderType": "LIMIT",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": instruction,
                    "quantity": quantity,
                    "instrument": {"symbol": symbol, "assetType": "EQUITY"},
                }
            ],
            "price": price,
        }

    @staticmethod
    def build_market_order(symbol: str, quantity: int, instruction: str = "BUY") -> Dict[str, Any]:
        return {
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": instruction,
                    "quantity": quantity,
                    "instrument": {"symbol": symbol, "assetType": "EQUITY"},
                }
            ],
        }

    @staticmethod
    def build_bracket_order(symbol: str, quantity: int, entry_price: float, take_profit_price: float, stop_loss_price: float) -> Dict[str, Any]:
        return {
            "orderType": "LIMIT",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "TRIGGER",
            "orderLegCollection": [
                {
                    "instruction": "BUY",
                    "quantity": quantity,
                    "instrument": {"symbol": symbol, "assetType": "EQUITY"},
                }
            ],
            "price": entry_price,
            "childOrderStrategies": [
                {
                    "orderStrategyType": "OCO",
                    "childOrderStrategies": [
                        {
                            "orderType": "LIMIT",
                            "session": "NORMAL",
                            "duration": "DAY",
                            "orderStrategyType": "SINGLE",
                            "orderLegCollection": [
                                {
                                    "instruction": "SELL",
                                    "quantity": quantity,
                                    "instrument": {"symbol": symbol, "assetType": "EQUITY"},
                                }
                            ],
                            "price": take_profit_price,
                        },
                        {
                            "orderType": "STOP",
                            "session": "NORMAL",
                            "duration": "DAY",
                            "orderStrategyType": "SINGLE",
                            "orderLegCollection": [
                                {
                                    "instruction": "SELL",
                                    "quantity": quantity,
                                    "instrument": {"symbol": symbol, "assetType": "EQUITY"},
                                }
                            ],
                            "stopPrice": stop_loss_price,
                        },
                    ],
                }
            ],
        }
