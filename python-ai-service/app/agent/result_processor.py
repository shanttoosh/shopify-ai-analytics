"""
Result Processor - Step 5 of agent workflow
Processes raw data into analytics and insights
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict


class ResultProcessor:
    """
    Processes raw Shopify data into meaningful metrics and insights
    """
    
    async def process(
        self,
        raw_data: Dict[str, Any],
        intent: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process raw data based on intent
        
        Returns:
            {
                "summary": Dict[str, Any],
                "calculations": Dict[str, Any],
                "insights": List[str]
            }
        """
        
        data = raw_data.get("data", {})
        intent_type = intent.get("intent", "")
        
        # Route to appropriate processor
        if intent_type in ["inventory_projection", "reorder_recommendations"]:
            return self._process_inventory_projection(data, intent)
        elif intent_type in ["sales_analysis", "top_products"]:
            return self._process_sales_analysis(data, intent)
        elif intent_type in ["customer_behavior", "customer_retention"]:
            return self._process_customer_behavior(data, intent)
        else:
            return self._process_general(data, intent)

    def _process_inventory_projection(
        self, 
        data: Dict[str, Any], 
        intent: Dict
    ) -> Dict[str, Any]:
        """Process inventory projection data"""
        orders = data.get("orders", [])
        inventory = data.get("inventory_levels", [])
        
        # Calculate sales velocity
        if orders:
            total_units = sum(
                item.get("quantity", 0) 
                for order in orders 
                for item in order.get("line_items", [])
            )
            days = self._get_days_from_period(intent.get("time_period", "30 days"))
            daily_rate = total_units / max(days, 1)
        else:
            total_units = 0
            daily_rate = 0
        
        # Current inventory
        current_stock = sum(inv.get("available", 0) for inv in inventory)
        
        # Projection
        projection_days = self._get_projection_days(intent.get("time_period", ""))
        projected_need = daily_rate * projection_days
        shortage = max(0, projected_need - current_stock)
        
        return {
            "summary": {
                "total_units_sold": total_units,
                "daily_sales_rate": round(daily_rate, 2),
                "current_stock": current_stock,
                "days_of_inventory": round(current_stock / daily_rate, 1) if daily_rate > 0 else float('inf')
            },
            "calculations": {
                "projection_period_days": projection_days,
                "projected_units_needed": round(projected_need, 0),
                "shortage": round(shortage, 0),
                "recommendation": "reorder" if shortage > 0 else "sufficient_stock"
            },
            "insights": []
        }

    def _process_sales_analysis(
        self, 
        data: Dict[str, Any], 
        intent: Dict
    ) -> Dict[str, Any]:
        """Process sales analysis data"""
        orders = data.get("orders", [])
        products = data.get("products", [])
        
        if not orders:
            return self._empty_result()
        
        # Aggregate sales by product
        product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
        
        for order in orders:
            for item in order.get("line_items", []):
                product_id = item.get("product_id")
                quantity = item.get("quantity", 0)
                price = item.get("price", 0)
                
                product_sales[product_id]["quantity"] += quantity
                product_sales[product_id]["revenue"] += quantity * price
        
        # Sort by quantity
        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]["quantity"],
            reverse=True
        )[:5]
        
        # Get product names
        product_map = {p.get("id"): p.get("title", "Unknown") for p in products}
        
        top_list = [
            {
                "product": product_map.get(pid, f"Product {pid}"),
                "quantity": data["quantity"],
                "revenue": data["revenue"]
            }
            for pid, data in top_products
        ]
        
        # Summary
        total_orders = len(orders)
        total_revenue = sum(order.get("total_price", 0) for order in orders)
        
        return {
            "summary": {
                "total_orders": total_orders,
                "total_revenue": round(total_revenue, 2),
                "top_products": top_list
            },
            "calculations": {
                "average_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
                "products_analyzed": len(product_sales)
            },
            "insights": []
        }

    def _process_customer_behavior(
        self, 
        data: Dict[str, Any], 
        intent: Dict
    ) -> Dict[str, Any]:
        """Process customer behavior data"""
        customers = data.get("customers", [])
        orders = data.get("orders", [])
        
        # Count repeat customers
        customer_order_counts = defaultdict(int)
        for order in orders:
            customer_id = order.get("customer_id")
            if customer_id:
                customer_order_counts[customer_id] += 1
        
        repeat_customers = sum(1 for count in customer_order_counts.values() if count > 1)
        total_customers = len(customer_order_counts)
        
        return {
            "summary": {
                "total_customers": total_customers,
                "repeat_customers": repeat_customers,
                "repeat_rate": round(repeat_customers / total_customers * 100, 1) if total_customers > 0 else 0
            },
            "calculations": {
                "average_orders_per_customer": round(
                    len(orders) / total_customers, 2
                ) if total_customers > 0 else 0
            },
            "insights": []
        }

    def _process_general(self, data: Dict[str, Any], intent: Dict) -> Dict[str, Any]:
        """Fallback processor for general queries"""
        return {
            "summary": {
                "records_found": sum(len(v) if isinstance(v, list) else 1 for v in data.values())
            },
            "calculations": {},
            "insights": []
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "summary": {"message": "No data found"},
            "calculations": {},
            "insights": []
        }

    def _get_days_from_period(self, period_str: str) -> int:
        """Extract number of days from period string"""
        period_lower = period_str.lower()
        if "week" in period_lower:
            weeks = int(''.join(filter(str.isdigit, period_str)) or 1)
            return weeks * 7
        elif "month" in period_lower:
            months = int(''.join(filter(str.isdigit, period_str)) or 1)
            return months * 30
        elif "day" in period_lower:
            return int(''.join(filter(str.isdigit, period_str)) or 30)
        else:
            return 30  # default

    def _get_projection_days(self, period_str: str) -> int:
        """Get projection period in days"""
        if "next" in period_str.lower():
            return self._get_days_from_period(period_str.replace("next", ""))
        return 7  # default to 1 week
