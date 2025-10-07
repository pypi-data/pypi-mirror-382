"""
Odoo Python Client Library

A Python client for Odoo using the requests library and JSON-RPC.
Based on the odoo-react implementation by Mohamed Helmy.
"""

import requests
from typing import Optional, Dict, List, Any, Union
from datetime import datetime


class OdooPyClient:
    """
    Odoo client for connecting to and interacting with Odoo instances.
    
    Args:
        host: Odoo server address (e.g., 'http://localhost')
        database: Odoo database name
        username: Username for authentication (optional if using session_id)
        password: Password for authentication (optional if using session_id)
        port: Port number (defaults to 80)
        session_id: Session ID for authentication (optional if using username/password)
        context: Additional context like language settings (optional)
    """
    
    def __init__(
        self,
        host: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.session_id = session_id
        self.context = context or {}
        
    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the Odoo server.
        
        Returns:
            Response containing user data and session information.
            
        Raises:
            Exception: If authentication fails.
        """
        url = f"{self.host}:{self.port}/web/session/authenticate"
        
        body = {
            "params": {
                "db": self.database,
                "login": self.username,
                "password": self.password,
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            self.context = data.get("result", {}).get("user_context", {})
            raise Exception(data["error"])
        
        result = data.get("result", {})
        
        # Extract session_id from cookies
        if "session_id" in response.cookies:
            self.session_id = response.cookies["session_id"]
        
        self.context = result.get("user_context", {})
        
        return result
    
    def search(
        self,
        model: str,
        domain: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Search for record IDs matching the domain criteria.
        
        Args:
            model: Odoo model name (e.g., 'res.partner')
            domain: Search domain (e.g., [['name', '=', 'John']])
            
        Returns:
            Response containing matching record IDs.
        """
        params = {
            "kwargs": {
                "context": self.context,
            },
            "model": model,
            "method": "search",
            "args": [domain or []],
        }
        
        return self._request("/web/dataset/call_kw", params)
    
    def read(
        self,
        model: str,
        ids: List[int],
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Read records by IDs.
        
        Args:
            model: Odoo model name (e.g., 'res.partner')
            ids: List of record IDs to read
            fields: List of fields to retrieve (optional)
            
        Returns:
            Response containing record data.
        """
        params = {
            "model": model,
            "method": "read",
            "args": [ids],
            "kwargs": {
                "fields": fields or [],
            },
        }
        
        return self._request("/web/dataset/call_kw", params)
    
    def search_read(
        self,
        model: str,
        domain: Optional[List] = None,
        fields: Optional[List[str]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search and read records in a single call.
        
        Args:
            model: Odoo model name (e.g., 'product.product')
            domain: Search domain for filtering (e.g., [['list_price', '>', '50']])
            fields: List of fields to retrieve
            offset: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            order: Sort order (e.g., 'name DESC')
            
        Returns:
            Response containing matching records with requested fields.
        """
        params = {
            "model": model,
            "method": "search_read",
            "args": [],
            "kwargs": {
                "context": self.context,
                "domain": domain or [],
                "offset": offset,
                "limit": limit,
                "order": order,
                "fields": fields or [],
            },
        }
        
        return self._request("/web/dataset/call_kw", params)
    
    def create(
        self,
        model: str,
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            model: Odoo model name (e.g., 'delivery.order.line')
            values: Dictionary of field values for the new record
            
        Returns:
            Response containing the ID of the created record.
        """
        params = {
            "kwargs": {
                "context": self.context,
            },
            "model": model,
            "method": "create",
            "args": [values],
        }
        
        return self._request("/web/dataset/call_kw", params)
    
    def update(
        self,
        model: str,
        ids: Union[int, List[int]],
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update existing record(s).
        
        Args:
            model: Odoo model name (e.g., 'delivery.order.line')
            ids: Record ID or list of IDs to update
            values: Dictionary of field values to update
            
        Returns:
            Response indicating success or failure.
        """
        if isinstance(ids, int):
            ids = [ids]
        
        if ids:
            params = {
                "kwargs": {
                    "context": self.context,
                },
                "model": model,
                "method": "write",
                "args": [ids, values],
            }
            
            return self._request("/web/dataset/call_kw", params)
        
        return {"error": "No IDs provided"}
    
    def delete(
        self,
        model: str,
        ids: Union[int, List[int]],
    ) -> Dict[str, Any]:
        """
        Delete record(s).
        
        Args:
            model: Odoo model name (e.g., 'delivery.order.line')
            ids: Record ID or list of IDs to delete
            
        Returns:
            Response indicating success or failure.
        """
        if isinstance(ids, int):
            ids = [ids]
        
        params = {
            "kwargs": {
                "context": self.context,
            },
            "model": model,
            "method": "unlink",
            "args": [ids],
        }
        
        return self._request("/web/dataset/call_kw", params)
    
    def rpc_call(
        self,
        endpoint: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Make a generic RPC call to any Odoo endpoint.
        
        Args:
            endpoint: API endpoint path (e.g., '/web/dataset/call_kw')
            params: Parameters for the RPC call
            
        Returns:
            Response from the endpoint.
        """
        return self._request(endpoint, params)
    
    def _request(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Internal method to make HTTP requests to Odoo.
        
        Args:
            path: API endpoint path
            params: Request parameters
            
        Returns:
            Response data from Odoo.
            
        Raises:
            Exception: If the request fails or returns an error.
        """
        params = params or {}
        url = f"{self.host}:{self.port}{path}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add session cookie if available
        cookies = {}
        if self.session_id:
            cookies["session_id"] = self.session_id
        
        # Prepare JSON-RPC request body
        body = {
            "jsonrpc": "2.0",
            "id": int(datetime.utcnow().timestamp() * 1000) % 1000,
            "method": "call",
            "params": params,
        }
        
        response = requests.post(
            url,
            json=body,
            headers=headers,
            cookies=cookies
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            raise Exception(data["error"])
        
        return data.get("result")


# Convenience function for creating an Odoo client
def connect(
    host: str,
    database: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    port: int = 80,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> OdooPyClient:
    """
    Create and return an Odoo client instance.
    
    Args:
        host: Odoo server address
        database: Odoo database name
        username: Username for authentication (optional if using session_id)
        password: Password for authentication (optional if using session_id)
        port: Port number (defaults to 80)
        session_id: Session ID for authentication (optional if using username/password)
        context: Additional context like language settings (optional)
        
    Returns:
        OdooPyClient instance.
    """
    return OdooPyClient(
        host=host,
        database=database,
        username=username,
        password=password,
        port=port,
        session_id=session_id,
        context=context,
    )
