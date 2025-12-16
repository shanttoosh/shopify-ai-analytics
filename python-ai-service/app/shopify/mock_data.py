"""
Mock Data Provider - Generates realistic test data for development
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class MockDataProvider:
    """
    Provides mock Shopify data for testing without a real store
    """
    
    def __init__(self):
        self.products = self._generate_products()
        self.orders = self._generate_orders()
        self.inventory = self._generate_inventory()
        self.customers = self._generate_customers()

    def get_orders(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get mock orders"""
        return self.orders

    def get_products(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get mock products"""
        return self.products

    def get_inventory(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get mock inventory levels"""
        return self.inventory

    def get_customers(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get mock customers"""
        return self.customers

    def _generate_products(self) -> List[Dict[str, Any]]:
        """Generate realistic product data"""
        products = [
            {
                "id": 1001,
                "title": "Premium Organic Coffee Beans",
                "price": 24.99,
                "sku": "COFFEE-001"
            },
            {
                "id": 1002,
                "title": "Stainless Steel Travel Mug",
                "price": 19.99,
                "sku": "MUG-002"
            },
            {
                "id": 1003,
                "title": "Artisan Dark Chocolate Bar",
                "price": 8.99,
                "sku": "CHOC-003"
            },
            {
                "id": 1004,
                "title": "Organic Green Tea Set",
                "price": 32.99,
                "sku": "TEA-004"
            },
            {
                "id": 1005,
                "title": "Ceramic Coffee Grinder",
                "price": 45.99,
                "sku": "GRIND-005"
            }
        ]
        return products

    def _generate_orders(self) -> List[Dict[str, Any]]:
        """Generate realistic order data for last 30 days"""
        orders = []
        base_date = datetime.now()
        
        # Generate 30-50 orders over last 30 days
        for i in range(45):
            days_ago = random.randint(0, 30)
            order_date = base_date - timedelta(days=days_ago)
            
            # Random products in order
            num_items = random.randint(1, 3)
            line_items = []
            total_price = 0
            
            for _ in range(num_items):
                product = random.choice(self.products)
                quantity = random.randint(1, 5)
                price = product["price"]
                
                line_items.append({
                    "product_id": product["id"],
                    "title": product["title"],
                    "quantity": quantity,
                    "price": price
                })
                
                total_price += price * quantity
            
            orders.append({
                "id": 2000 + i,
                "created_at": order_date.isoformat(),
                "total_price": round(total_price, 2),
                "customer_id": random.randint(3000, 3020),  # 20 different customers
                "line_items": line_items
            })
        
        return orders

    def _generate_inventory(self) -> List[Dict[str, Any]]:
        """Generate inventory levels"""
        inventory = []
        
        for product in self.products:
            # Random current stock (some low, some high)
            available = random.choice([5, 12, 25, 45, 100, 15, 8, 30])
            
            inventory.append({
                "product_id": product["id"],
                "location_id": 5000,
                "available": available
            })
        
        return inventory

    def _generate_customers(self) -> List[Dict[str, Any]]:
        """Generate customer data"""
        customers = []
        
        first_names = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        
        for i in range(20):
            customers.append({
                "id": 3000 + i,
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "email": f"customer{i}@example.com",
                "orders_count": random.randint(1, 5)
            })
        
        return customers


# Singleton instance
_mock_provider = None


def get_mock_provider() -> MockDataProvider:
    """Get singleton mock provider"""
    global _mock_provider
    if _mock_provider is None:
        _mock_provider = MockDataProvider()
    return _mock_provider
