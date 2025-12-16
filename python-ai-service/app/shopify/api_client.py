"""
Shopify API Client - Wrapper for Shopify Admin API
"""

import httpx
from typing import Dict, Any, List, Optional
import os


class ShopifyAPIClient:
    """
    Client for interacting with Shopify Admin API (REST and GraphQL)
    """
    
    def __init__(self):
        self.api_version = os.getenv("SHOPIFY_API_VERSION", "2024-01")
        self.timeout = 30.0

    async def fetch(
        self,
        store_id: str,
        access_token: str,
        resource: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from Shopify Admin API
        
        Args:
            store_id: Store domain (e.g., "example.myshopify.com")
            access_token: Shopify access token
            resource: Resource type (orders, products, etc.)
            filters: Optional filters to apply
            
        Returns:
            List of resource objects
        """
        
        # Build API URL
        base_url = f"https://{store_id}/admin/api/{self.api_version}"
        
        # Map resource to endpoint
        endpoint_map = {
            "orders": "/orders.json",
            "products": "/products.json",
            "inventory_levels": "/inventory_levels.json",
            "customers": "/customers.json"
        }
        
        endpoint = endpoint_map.get(resource)
        if not endpoint:
            raise ValueError(f"Unsupported resource: {resource}")
        
        url = base_url + endpoint
        
        # Build query parameters
        params = self._build_params(filters or {})
        
        # Make request
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract resource array from response
                # Shopify wraps responses like {"orders": [...]}
                resource_key = resource
                return data.get(resource_key, [])
                
            except httpx.HTTPStatusError as e:
                print(f"Shopify API error: {e.response.status_code}")
                raise Exception(f"Shopify API returned {e.response.status_code}")
            except httpx.RequestError as e:
                print(f"Request error: {e}")
                raise Exception("Failed to connect to Shopify API")

    def _build_params(self, filters: Dict[str, Any]) -> Dict[str, str]:
        """Build query parameters from filters"""
        params = {}
        
        # Time filter
        if "time_filter" in filters:
            time_str = filters["time_filter"]
            # Convert to Shopify's created_at_min/max format
            # This is simplified - production would parse the time string properly
            params["limit"] = "250"
        
        # Product filter
        if "products" in filters and filters["products"] != "all":
            # This would filter by product IDs
            pass
        
        # Default limit
        params.setdefault("limit", "250")
        
        return params

    async def fetch_graphql(
        self,
        store_id: str,
        access_token: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute GraphQL query against Shopify Admin API
        
        This is more powerful than REST for complex queries
        """
        url = f"https://{store_id}/admin/api/{self.api_version}/graphql.json"
        
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                if "errors" in data:
                    raise Exception(f"GraphQL errors: {data['errors']}")
                
                return data.get("data", {})
                
            except httpx.HTTPStatusError as e:
                raise Exception(f"Shopify GraphQL error: {e.response.status_code}")
