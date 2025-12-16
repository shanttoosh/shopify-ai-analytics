# Sample API Requests and Responses

This document provides example API requests and expected responses for the Shopify Analytics App.

## Base URL

```
http://localhost:3000
```

## Example 1: Inventory Projection

### Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "example-store.myshopify.com",
    "question": "How many units of Product X will I need next month?"
  }'
```

### Response

```json
{
  "answer": "Based on your recent sales data, you sell approximately 10.5 units per day. To meet demand for the next month (30 days), you'll need about 315 units. You should reorder at least 290 units to avoid stockouts.",
  "confidence": "medium",
  "shopify_query": "SELECT product_id, SUM(quantity) FROM orders JOIN inventory_levels WHERE created_at >= date_sub(NOW(), INTERVAL 30 DAY) GROUP BY product_id",
  "reasoning": [
    "Classified as: inventory_projection",
    "Need data from: orders, products, inventory_levels",
    "Generated query plan",
    "Retrieved 45 data points",
    "Calculated metrics and insights"
  ],
  "metadata": {
    "execution_time": "2.34s",
    "data_points_analyzed": 45,
    "intent": "inventory_projection",
    "confidence_reason": "Based on 30 days of sales history"
  }
}
```

---

## Example 2: Top Selling Products

### Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "example-store.myshopify.com",
    "question": "What were my top 5 selling products last week?"
  }'
```

### Response

```json
{
  "answer": "Based on 38 orders totaling $1,245.50 last week, your top selling products are: Premium Organic Coffee Beans (42 units), Artisan Dark Chocolate Bar (28 units), and Stainless Steel Travel Mug (25 units).",
  "confidence": "high",
  "shopify_query": "SELECT product_id, product_title, SUM(quantity) as total_qty FROM orders WHERE created_at >= date_sub(NOW(), INTERVAL 7 DAY) GROUP BY product_id ORDER BY total_qty DESC LIMIT 5",
  "reasoning": [
    "Classified as: top_products",
    "Need data from: orders, products",
    "Generated query plan",
    "Retrieved 38 data points",
    "Calculated metrics and insights"
  ],
  "metadata": {
    "execution_time": "1.87s",
    "data_points_analyzed": 38,
    "intent": "top_products",
    "confidence_reason": "High confidence with 38 orders analyzed"
  }
}
```

---

## Example 3: Stock Out Prediction

### Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "example-store.myshopify.com",
    "question": "Which products are likely to go out of stock in 7 days?"
  }'
```

### Response

```json
{
  "answer": "Based on current inventory levels and recent sales rates, the following products may run out of stock within 7 days: Artisan Dark Chocolate Bar (5 units remaining, selling 2.3/day) and Organic Green Tea Set (8 units remaining, selling 1.8/day). Consider reordering these items soon.",
  "confidence": "medium",
  "shopify_query": "SELECT p.id, p.title, i.available, AVG(daily_sales) FROM products p JOIN inventory_levels i JOIN (SELECT product_id, COUNT(*)/30 as daily_sales FROM orders) s WHERE i.available / s.daily_sales < 7",
  "reasoning": [
    "Classified as: inventory_status",
    "Need data from: products, orders, inventory_levels",
    "Generated query plan",
    "Retrieved 52 data points",
    "Calculated metrics and insights"
  ],
  "metadata": {
    "execution_time": "2.12s",
    "data_points_analyzed": 52,
    "intent": "inventory_status",
    "confidence_reason": "Medium confidence based on 30-day average"
  }
}
```

---

## Example 4: Repeat Customers

### Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "example-store.myshopify.com",
    "question": "Which customers placed repeat orders in the last 90 days?"
  }'
```

### Response

```json
{
  "answer": "You have 12 repeat customers from the last 90 days, representing 35.3% of your customer base. These loyal customers placed an average of 2.5 orders each.",
  "confidence": "high",
  "shopify_query": "SELECT customer_id, COUNT(*) as order_count FROM orders WHERE created_at >= date_sub(NOW(), INTERVAL 90 DAY) GROUP BY customer_id HAVING order_count > 1",
  "reasoning": [
    "Classified as: customer_behavior",
    "Need data from: orders, customers",
    "Generated query plan",
    "Retrieved 68 data points",
    "Calculated metrics and insights"
  ],
  "metadata": {
    "execution_time": "1.95s",
    "data_points_analyzed": 68,
    "intent": "customer_behavior",
    "confidence_reason": "High confidence with comprehensive customer data"
  }
}
```

---

## Example 5: Reorder Recommendations

### Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "example-store.myshopify.com",
    "question": "How much inventory should I reorder based on last 30 days sales?"
  }'
```

### Response

```json
{
  "answer": "Based on the last 30 days of sales data, I recommend reordering: Premium Organic Coffee Beans (300 units), Stainless Steel Travel Mug (150 units), and Artisan Dark Chocolate Bar (200 units). These quantities should cover approximately 2 weeks of demand at current sales rates.",
  "confidence": "high",
  "shopify_query": "SELECT product_id, product_title, SUM(quantity) * 0.5 as recommended_reorder FROM orders WHERE created_at >= date_sub(NOW(), INTERVAL 30 DAY) GROUP BY product_id ORDER BY recommended_reorder DESC",
  "reasoning": [
    "Classified as: reorder_recommendations",
    "Need data from: orders, products, inventory_levels",
    "Generated query plan",
    "Retrieved 85 data points",
    "Calculated metrics and insights"
  ],
  "metadata": {
    "execution_time": "2.45s",
    "data_points_analyzed": 85,
    "intent": "reorder_recommendations",
    "confidence_reason": "High confidence based on 30 days of consistent sales data"
  }
}
```

---

## Example 6: Ambiguous Question (Low Confidence)

### Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "example-store.myshopify.com",
    "question": "How is business?"
  }'
```

### Response

```json
{
  "answer": "I'd like to help, but I need a bit more information. Could you clarify:\n- What time period are you interested in?\n- Which products should I analyze?\n\nFor example: 'What were the top 5 selling products last month?'",
  "confidence": "low",
  "shopify_query": null,
  "reasoning": [
    "Question too ambiguous for confident analysis"
  ],
  "metadata": {
    "requires_clarification": true
  }
}
```

---

## Error Response Example

### Invalid Store ID

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "non-existent-store.myshopify.com",
    "question": "What are my sales?"
  }'
```

### Response

```json
{
  "error": "Store not found. Please authenticate first via /auth/shopify"
}
```

---

## Testing with Mock Data

By default, the application runs in mock mode (`USE_MOCK_DATA=true`). This allows you to test all endpoints without a real Shopify store. The mock data includes:

- 5 sample products (coffee, mugs, chocolate, tea, grinder)
- 45 sample orders over the last 30 days
- 20 sample customers
- Realistic inventory levels

To test with a real Shopify store:

1. Set `USE_MOCK_DATA=false` in `.env`
2. Complete OAuth flow: `/auth/shopify?shop=your-store.myshopify.com`
3. Send requests with your actual store ID

---

## Agent Reasoning Trail

Each response includes a `reasoning` array showing the agent's step-by-step thought process:

1. **Intent Classification**: What category the question falls into
2. **Data Planning**: Which resources are needed
3. **Query Generation**: Query plan created
4. **Data Retrieval**: Number of records fetched
5. **Analysis**: Metrics calculated

This transparency helps understand how the AI arrived at its answer.

---

## Confidence Levels

- **`high`**: Strong data support, clear question, 30+ data points
- **`medium`**: Adequate data, some assumptions made, 10-30 data points
- **`low`**: Limited data, ambiguous question, or requires clarification

The `confidence_reason` field in metadata explains why a particular confidence level was assigned.
