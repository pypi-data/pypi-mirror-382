"""
Schwab SDK - Async Accounts Module
Asynchronous account and transaction endpoints.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class AsyncAccounts:
    """
    Async Accounts module for Schwab SDK.
    
    Provides async access to account-related endpoints:
    - get_accounts() - List all accounts
    - get_account_by_id() - Get specific account details
    - get_transactions() - Get account transactions
    - get_transaction() - Get specific transaction
    - get_preferences() - Get account preferences
    """
    
    def __init__(self, client):
        """Initialize with async client."""
        self.client = client
        self.base_url = f"{self.client.trader_base_url}/accounts"
    
    async def get_accounts(self, fields: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all accounts for the authenticated user.
        
        Args:
            fields: Optional fields to include (e.g., "positions")
            
        Returns:
            List of account information
        """
        params = {}
        if fields:
            params['fields'] = fields
            
        return await self.client._make_request(
            method="GET",
            url=self.base_url,
            params=params
        )
    
    async def get_account_by_id(
        self, 
        account_hash: str, 
        fields: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get specific account details.
        
        Args:
            account_hash: Account identifier
            fields: Optional fields to include (e.g., "positions")
            
        Returns:
            Account information
        """
        params = {}
        if fields:
            params['fields'] = fields
            
        return await self.client._make_request(
            method="GET",
            url=f"{self.base_url}/{account_hash}",
            params=params
        )
    
    async def get_transactions(
        self,
        account_hash: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        symbol: Optional[str] = None,
        types: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get account transactions.
        
        Args:
            account_hash: Account identifier
            from_date: Start date (YYYY-MM-DD or ISO format)
            to_date: End date (YYYY-MM-DD or ISO format)
            symbol: Filter by symbol
            types: Filter by transaction types
            
        Returns:
            List of transactions
        """
        # Date normalization logic (same as sync version)
        def _normalize_date(date_str: Optional[str], *, is_end: bool) -> Optional[str]:
            if not date_str:
                return None
            ds = str(date_str).strip()
            import re
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", ds):
                return f"{ds}T23:59:59.000Z" if is_end else f"{ds}T00:00:00.000Z"
            return ds

        start_norm = _normalize_date(from_date, is_end=False) if from_date else None
        end_norm = _normalize_date(to_date, is_end=True) if to_date else None

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
        if start_norm:
            params['startDate'] = start_norm
        if end_norm:
            params['endDate'] = end_norm
        if symbol:
            params['symbol'] = symbol
        if types:
            params['types'] = types
            
        return await self.client._make_request(
            method="GET",
            url=f"{self.base_url}/{account_hash}/transactions",
            params=params
        )
    
    async def get_transaction(
        self, 
        account_hash: str, 
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        Get specific transaction details.
        
        Args:
            account_hash: Account identifier
            transaction_id: Transaction ID
            
        Returns:
            Transaction information
        """
        return await self.client._make_request(
            method="GET",
            url=f"{self.base_url}/{account_hash}/transactions/{transaction_id}"
        )
    
    async def get_preferences(self, account_hash: str) -> Dict[str, Any]:
        """
        Get account preferences.
        
        Args:
            account_hash: Account identifier
            
        Returns:
            Account preferences
        """
        return await self.client._make_request(
            method="GET",
            url=f"{self.base_url}/{account_hash}/preferences"
        )

