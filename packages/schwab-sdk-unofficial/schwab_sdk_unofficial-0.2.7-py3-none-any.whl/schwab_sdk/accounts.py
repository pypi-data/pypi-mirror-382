"""
Schwab SDK - Accounts Module
Handles account endpoints, transactions, and user preferences.
"""

import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode


class Accounts:
    """
    Module for account-related endpoints.
    
    Includes:
    - Account information (numbers, balances, positions)
    - Transactions
    - User preferences
    """
    
    def __init__(self, client):
        """
        Initializes the Accounts module.
        
        Args:
            client: Instance of the main client
        """
        self.client = client
        self.base_url = client.trader_base_url
    
    def get_account_numbers(self) -> Dict[str, Any]:
        """
        Gets a list of account numbers and their encrypted values.
        
        GET /accounts/accountNumbers
        
        Returns:
            JSON response with accountNumber and accountHash for each account
        """
        endpoint = f"{self.base_url}/accounts/accountNumbers"
        response = self.client._request("GET", endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_accounts(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves balances and positions for all linked accounts.
        
        GET /accounts
        
        Returns:
            JSON response with complete information for all accounts
        """
        endpoint = f"{self.base_url}/accounts"
        response = self.client._request("GET", endpoint, params=params or {}, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_account_by_id(self, account_hash: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves balance and positions for a specific account.
        
        GET /accounts/{accountNumber}
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            
        Returns:
            JSON response with information for the specified account
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}"
        response = self.client._request("GET", endpoint, params=params or {}, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def find_account(self, last_4_digits: str) -> Optional[Dict[str, Any]]:
        """
        Finds an account by the last 4 digits of the account number.
        
        Helper method that fetches all accounts and filters by the last 4 digits.
        
        Args:
            last_4_digits: Last 4 digits of the account number
            
        Returns:
            Information for the matched account, or None if not found
        """
        # Get account numbers
        account_numbers = self.get_account_numbers()
        # Look for an account whose number ends with the specified digits
        for account_info in account_numbers:
            account_number = account_info.get("accountNumber", "")
            if account_number.endswith(last_4_digits):
                # Retrieve full information for this account
                account_hash = account_info.get("hashValue", account_number)
                return self.get_account_by_id(account_hash)
        return None
    
    def get_transactions(self, account_hash: str, from_date: str = None, to_date: str = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves all transactions for a specific account.
        
        GET /accounts/{accountNumber}/transactions
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            from_date: Start date in short format 'YYYY-MM-DD' or ISO UTC 'YYYY-MM-DDTHH:MM:SS.ffffffZ'
            to_date: End date in short format 'YYYY-MM-DD' or ISO UTC 'YYYY-MM-DDTHH:MM:SS.ffffffZ'
            filters: Additional optional query filters
            
        Returns:
            JSON response with the account's transactions
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/transactions"
        # Build query parameters (accepts 'YYYY-MM-DD' or full ISO UTC)
        params: Dict[str, Any] = {}

        def _normalize_date(date_str: Optional[str], *, is_end: bool) -> Optional[str]:
            """Normalizes dates:
            - 'YYYY-MM-DD' -> 'YYYY-MM-DDT00:00:00.000Z' (start) or 'YYYY-MM-DDT23:59:59.000Z' (end)
            - If already ISO-like -> passed through as-is
            """
            if not date_str:
                return None
            ds = str(date_str).strip()
            # Short format YYYY-MM-DD
            import re
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", ds):
                return f"{ds}T23:59:59.000Z" if is_end else f"{ds}T00:00:00.000Z"
            # If it looks like ISO, return as is
            return ds

        start_norm = _normalize_date(from_date, is_end=False) if from_date else None
        end_norm = _normalize_date(to_date, is_end=True) if to_date else None

        # If only one date is provided, fill the other with the same day
        if start_norm and not end_norm:
            # Derive base date from start
            import re as _re
            m = _re.match(r"(\d{4}-\d{2}-\d{2})", start_norm)
            base = m.group(1) if m else start_norm[:10]
            end_norm = f"{base}T23:59:59.000Z"
        elif end_norm and not start_norm:
            import re as _re
            m = _re.match(r"(\d{4}-\d{2}-\d{2})", end_norm)
            base = m.group(1) if m else end_norm[:10]
            start_norm = f"{base}T00:00:00.000Z"

        if start_norm:
            params['startDate'] = start_norm
        if end_norm:
            params['endDate'] = end_norm
        if filters:
            params.update(filters)
        response = self.client._request("GET", endpoint, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    
    def get_transaction(self, account_hash: str, transaction_id: str) -> Dict[str, Any]:
        """
        Retrieves specific information for a transaction.
        
        GET /accounts/{accountNumber}/transactions/{transactionId}
        
        Args:
            account_hash: Encrypted account identifier (hashValue)
            transaction_id: ID of the specific transaction
            
        Returns:
            JSON response with information for the specific transaction
        """
        endpoint = f"{self.base_url}/accounts/{account_hash}/transactions/{transaction_id}"
        response = self.client._request("GET", endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Retrieves preference information for the authenticated user.
        
        GET /userPreference
        
        This includes streaming-related data such as:
        - schwabClientCustomerId
        - schwabClientCorrelId
        - SchwabClientChannel
        - SchwabClientFunctionId
        
        Returns:
            JSON response with the user's preferences
        """
        endpoint = f"{self.base_url}/userPreference"
        response = self.client._request("GET", endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
