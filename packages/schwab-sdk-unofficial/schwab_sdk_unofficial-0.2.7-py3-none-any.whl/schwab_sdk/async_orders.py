"""
Schwab SDK - Async Orders Module
Asynchronous order management endpoints.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class AsyncOrders:
    """
    Async Orders module for Schwab SDK.
    
    Provides async access to order-related endpoints:
    - get_orders() - Get orders for account
    - get_all_orders() - Get all orders
    - place_order() - Place new order
    - get_order() - Get specific order
    - cancel_order() - Cancel order
    - replace_order() - Replace order
    - preview_order() - Preview order
    """
    
    def __init__(self, client):
        """Initialize with async client."""
        self.client = client
        self.base_url = f"{self.client.trader_base_url}/accounts"
    
    async def get_orders(
        self,
        account_hash: str,
        max_results: Optional[int] = None,
        from_entered_time: Optional[str] = None,
        to_entered_time: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get orders for a specific account.
        
        Args:
            account_hash: Account identifier
            max_results: Maximum number of results
            from_entered_time: Start time filter
            to_entered_time: End time filter
            status: Order status filter
            
        Returns:
            List of orders
        """
        # Date normalization logic (same as sync version)
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

        if start_norm and not end_norm:
            import re as _re
            m = _re.match(r"(\d{4}-\d{2}-\d{2})", start_norm)
            base = m.group(1) if m else start_norm[:10]
            end_norm = f"{base}T23:59:59.000Z"
        elif end_norm and not start_norm:
            import re as _re
            m = _re.match(r"(\d{4}-\d{2}-\d{2})", end_norm)
            base = m.group(1) if m else end_norm[:10]
            start_norm = f"{base}T00:00:00.000Z"
        
        params = {}
        if max_results:
            params['maxResults'] = max_results
        if start_norm:
            params['fromEnteredTime'] = start_norm
        if end_norm:
            params['toEnteredTime'] = end_norm
        if status:
            params['status'] = status.strip().upper()
            
        return await self.client._make_request(
            method="GET",
            url=f"{self.base_url}/{account_hash}/orders",
            params=params
        )
    
    async def get_all_orders(
        self,
        max_results: Optional[int] = None,
        from_entered_time: Optional[str] = None,
        to_entered_time: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all orders across all accounts.
        
        Args:
            max_results: Maximum number of results
            from_entered_time: Start time filter
            to_entered_time: End time filter
            status: Order status filter
            
        Returns:
            List of orders
        """
        # Same date normalization logic as get_orders
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

        if start_norm and not end_norm:
            import re as _re
            m = _re.match(r"(\d{4}-\d{2}-\d{2})", start_norm)
            base = m.group(1) if m else start_norm[:10]
            end_norm = f"{base}T23:59:59.000Z"
        elif end_norm and not start_norm:
            import re as _re
            m = _re.match(r"(\d{4}-\d{2}-\d{2})", end_norm)
            base = m.group(1) if m else end_norm[:10]
            start_norm = f"{base}T00:00:00.000Z"
        
        params = {}
        if max_results:
            params['maxResults'] = max_results
        if start_norm:
            params['fromEnteredTime'] = start_norm
        if end_norm:
            params['toEnteredTime'] = end_norm
        if status:
            params['status'] = status.strip().upper()
            
        return await self.client._make_request(
            method="GET",
            url=f"{self.client.trader_base_url}/orders",
            params=params
        )
    
    async def place_order(
        self, 
        account_hash: str, 
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Place a new order.
        
        Args:
            account_hash: Account identifier
            order_data: Order data dictionary
            
        Returns:
            Order response with order ID
        """
        return await self.client._make_request(
            method="POST",
            url=f"{self.base_url}/{account_hash}/orders",
            json_data=order_data
        )
    
    async def get_order(
        self, 
        account_hash: str, 
        order_id: str
    ) -> Dict[str, Any]:
        """
        Get specific order details.
        
        Args:
            account_hash: Account identifier
            order_id: Order ID
            
        Returns:
            Order information
        """
        return await self.client._make_request(
            method="GET",
            url=f"{self.base_url}/{account_hash}/orders/{order_id}"
        )
    
    async def cancel_order(
        self, 
        account_hash: str, 
        order_id: str
    ) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            account_hash: Account identifier
            order_id: Order ID
            
        Returns:
            Cancellation response
        """
        return await self.client._make_request(
            method="DELETE",
            url=f"{self.base_url}/{account_hash}/orders/{order_id}"
        )
    
    async def replace_order(
        self, 
        account_hash: str, 
        order_id: str, 
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Replace an existing order.
        
        Args:
            account_hash: Account identifier
            order_id: Order ID to replace
            order_data: New order data
            
        Returns:
            Replacement response
        """
        return await self.client._make_request(
            method="PUT",
            url=f"{self.base_url}/{account_hash}/orders/{order_id}",
            json_data=order_data
        )
    
    async def preview_order(
        self, 
        account_hash: str, 
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preview an order without placing it.
        
        Args:
            account_hash: Account identifier
            order_data: Order data to preview
            
        Returns:
            Order preview response
        """
        return await self.client._make_request(
            method="POST",
            url=f"{self.base_url}/{account_hash}/orders/preview",
            json_data=order_data
        )

