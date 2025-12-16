"""
Query Executor - Step 4 of agent workflow
Executes queries against Shopify API or mock data
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.shopify.api_client import ShopifyAPIClient
from app.shopify.mock_data import MockDataProvider


class QueryExecutor:
    """
    Executes query specifications against Shopify API or mock data
    """
    
    def __init__(self):
        self.shopify_client = ShopifyAPIClient()
        self.mock_provider = MockDataProvider()

    async def execute(
        self,
        query_spec: Dict[str, Any],
        store_id: str,
        access_token: Optional[str] = None,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the query specification and return raw data
        
        Returns:
            {
                "data": {...},
                "record_count": int,
                "resources": {...}
            }
        """
        
        if use_mock or not access_token:
            print("📦 Using mock data")
            return await self._execute_mock(query_spec)
        else:
            print("🌐 Querying Shopify API")
            return await self._execute_shopify(query_spec, store_id, access_token)

    async def _execute_mock(self, query_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using mock data"""
        api_calls = query_spec.get("api_calls", [])
        filters = query_spec.get("filters", {})
        
        data = {}
        total_records = 0
        
        for call in api_calls:
            resource = call["resource"]
            
            # Get mock data for this resource
            if resource == "orders":
                mock_data = self.mock_provider.get_orders(filters)
            elif resource == "products":
                mock_data = self.mock_provider.get_products(filters)
            elif resource == "inventory_levels":
                mock_data = self.mock_provider.get_inventory(filters)
            elif resource == "customers":
                mock_data = self.mock_provider.get_customers(filters)
            else:
                mock_data = []
            
            data[resource] = mock_data
            total_records += len(mock_data)
        
        return {
            "data": data,
            "record_count": total_records,
            "resources": list(data.keys()),
            "is_mock": True
        }

    async def _execute_shopify(
        self,
        query_spec: Dict[str, Any],
        store_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Execute using real Shopify API"""
        api_calls = query_spec.get("api_calls", [])
        
        data = {}
        total_records = 0
        
        for call in api_calls:
            resource = call["resource"]
            filters = call.get("filters", {})
            
            # Make API call
            try:
                result = await self.shopify_client.fetch(
                    store_id=store_id,
                    access_token=access_token,
                    resource=resource,
                    filters=filters
                )
                
                data[resource] = result
                total_records += len(result) if isinstance(result, list) else 1
                
            except Exception as e:
                print(f"Error fetching {resource}: {e}")
                data[resource] = []
        
        return {
            "data": data,
            "record_count": total_records,
            "resources": list(data.keys()),
            "is_mock": False
        }
