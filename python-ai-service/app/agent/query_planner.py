"""
Query Planner - Step 2 of agent workflow
Determines what Shopify data is needed to answer the question
"""

import json
from typing import Dict, Any
from app.llm.client import LLMClient
from app.llm.prompts import QUERY_GENERATOR_SYSTEM, QUERY_GENERATOR_PROMPT


class QueryPlanner:
    """
    Plans what Shopify resources and fields are needed to answer the question
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def plan(self, intent: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Create a plan for data retrieval
        
        Returns:
            {
                "shopifyql": str,
                "resources_needed": List[str],
                "fields_required": Dict[str, List[str]],
                "post_processing": str
            }
        """
        prompt = QUERY_GENERATOR_PROMPT.format(
            intent=intent["intent"],
            time_period=intent.get("time_period", "recent"),
            products=intent.get("products", "all"),
            metrics=", ".join(intent.get("metrics", [])),
            question=question
        )
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=QUERY_GENERATOR_SYSTEM,
                temperature=0.4
            )
            
            # Parse JSON response
            plan = self._parse_json_response(response)
            
            # Validate and enrich
            return self._validate_plan(plan, intent)
            
        except Exception as e:
            print(f"Query planning error: {e}")
            # Return minimal safe plan
            return self._fallback_plan(intent)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse query plan as JSON")

    def _validate_plan(self, plan: Dict[str, Any], intent: Dict) -> Dict[str, Any]:
        """Validate and ensure plan has required fields"""
        
        # Ensure required fields
        plan.setdefault("shopifyql", "SELECT * FROM orders")
        plan.setdefault("resources_needed", ["orders"])
        plan.setdefault("fields_required", {})
        plan.setdefault("post_processing", "Aggregate and analyze data")
        
        return plan

    def _fallback_plan(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a fallback plan based on intent"""
        intent_type = intent.get("intent", "general_query")
        
        # Simple mapping of intents to data needs
        plans = {
            "inventory_projection": {
                "shopifyql": "SELECT * FROM orders JOIN inventory_levels",
                "resources_needed": ["orders", "products", "inventory_levels"],
                "fields_required": {
                    "orders": ["created_at", "line_items", "quantity"],
                    "inventory_levels": ["available", "product_id"]
                },
                "post_processing": "Calculate daily sales rate and project future needs"
            },
            "sales_analysis": {
                "shopifyql": "SELECT * FROM orders",
                "resources_needed": ["orders"],
                "fields_required": {
                    "orders": ["created_at", "total_price", "line_items"]
                },
                "post_processing": "Aggregate sales by time period"
            },
            "top_products": {
                "shopifyql": "SELECT product_id, SUM(quantity) FROM orders GROUP BY product_id",
                "resources_needed": ["orders", "products"],
                "fields_required": {
                    "orders": ["line_items", "created_at"],
                    "products": ["title", "id"]
                },
                "post_processing": "Sum quantities and rank products"
            }
        }
        
        return plans.get(intent_type, plans["sales_analysis"])
