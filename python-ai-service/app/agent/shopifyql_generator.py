"""
ShopifyQL Generator - Step 3 of agent workflow  
Generates ShopifyQL queries from the plan
"""

from typing import Dict, Any
from app.llm.client import LLMClient


class ShopifyQLGenerator:
    """
    Generates ShopifyQL queries and converts them to API-compatible query specifications
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def generate(
        self, 
        plan: Dict[str, Any], 
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a query specification from the plan
        
        Returns:
            {
                "shopifyql": str,
                "api_calls": List[Dict],
                "filters": Dict,
                "aggregations": List[str]
            }
        """
        
        # For this implementation, we'll convert the plan into API calls
        # In a production system, you might use the LLM to refine the query further
        
        shopifyql = plan.get("shopifyql", "")
        resources = plan.get("resources_needed", [])
        fields = plan.get("fields_required", {})
        
        # Convert ShopifyQL-style plan to API call specifications
        api_calls = self._plan_to_api_calls(resources, fields, intent)
        
        # Extract any filters from intent
        filters = self._extract_filters(intent)
        
        return {
            "shopifyql": shopifyql,
            "api_calls": api_calls,
            "filters": filters,
            "aggregations": self._determine_aggregations(intent),
            "post_processing": plan.get("post_processing", "")
        }

    def _plan_to_api_calls(
        self, 
        resources: list, 
        fields: Dict[str, list],
        intent: Dict
    ) -> list:
        """Convert resource requirements to API call specifications"""
        api_calls = []
        
        for resource in resources:
            call = {
                "resource": resource,
                "method": "list",  # GET list of resources
                "fields": fields.get(resource, []),
                "filters": {}
            }
            
            # Add time filters if applicable
            time_period = intent.get("time_period", "")
            if time_period and resource in ["orders", "customers"]:
                call["filters"]["time_filter"] = time_period
            
            api_calls.append(call)
        
        return api_calls

    def _extract_filters(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Extract filters from intent"""
        filters = {}
        
        # Time period filter
        if intent.get("time_period"):
            filters["time_period"] = intent["time_period"]
        
        # Product filter
        products = intent.get("products", "all")
        if products != "all":
            filters["products"] = products
        
        return filters

    def _determine_aggregations(self, intent: Dict[str, Any]) -> list:
        """Determine what aggregations are needed"""
        intent_type = intent.get("intent", "")
        
        aggregation_map = {
            "inventory_projection": ["sum", "average", "trend"],
            "sales_analysis": ["sum", "count", "average"],
            "top_products": ["sum", "count", "rank"],
            "customer_behavior": ["count", "frequency"],
            "reorder_recommendations": ["average", "projection"]
        }
        
        return aggregation_map.get(intent_type, ["sum", "count"])

    def validate_query(self, query_spec: Dict[str, Any]) -> bool:
        """
        Validate that the generated query is safe and well-formed
        This is where you'd add query validation logic
        """
        # Check that we have API calls
        if not query_spec.get("api_calls"):
            return False
        
        # Check each API call is well-formed
        for call in query_spec["api_calls"]:
            if "resource" not in call:
                return False
        
        return True
