# AI-Powered Shopify Analytics App

An intelligent analytics application that connects to Shopify stores and answers natural language questions about sales, inventory, and customer data using LLM-powered agents.

## Architecture

This application uses a multi-tier architecture:

- **Node.js API Gateway** (Port 3000): Entry point handling authentication, validation, and request orchestration
- **Python AI Service** (Port 8000): LLM-powered agent that interprets questions, generates ShopifyQL, and explains results
- **Shopify Admin API**: Data source for store analytics

## Features

- 🔐 **Shopify OAuth Integration**: Secure store authentication
- 🤖 **AI-Powered Query Generation**: Converts natural language to ShopifyQL
- 📊 **Analytics Insights**: Inventory projections, sales trends, customer behavior
- 💬 **Business-Friendly Explanations**: Technical data converted to actionable insights
- ⚡ **Agentic Workflow**: Multi-step reasoning with validation

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Gateway | Node.js + Express |
| AI Service | Python + FastAPI |
| LLM | **Google Gemini (Free!)** or OpenAI GPT-4 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Shopify OAuth 2.0 |

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- **Google Gemini API key (FREE!)** - Get it here: https://makersuite.google.com/app/apikey
  - OR OpenAI API key (if you prefer)
- Shopify Partner account (optional - mock mode available)

## Quick Start

> 📘 **New to setup?** Check out our detailed **[SETUP-GUIDE.md](SETUP-GUIDE.md)** for step-by-step instructions on:
> - Getting a FREE Google Gemini API key
> - Configuring Shopify OAuth (optional)
> - Troubleshooting common issues

### 1. Clone and Install

```bash
cd shopify-analytics-app

# Install Node.js dependencies
cd api-gateway
npm install

# Install Python dependencies
cd ../python-ai-service
pip install -r requirements.txt
```

### 2. Configure Environment

**Important:** Get your FREE Gemini API key from https://makersuite.google.com/app/apikey

```bash
# Edit python-ai-service/.env
# Replace with your actual Gemini key:
GOOGLE_API_KEY=your-key-here
LLM_PROVIDER=gemini

# api-gateway/.env is already configured for mock mode
```

For detailed Shopify OAuth setup, see **[SETUP-GUIDE.md](SETUP-GUIDE.md)**.

### 3. Run Services

```bash
# Terminal 1: Start API Gateway
cd api-gateway
npm run dev

# Terminal 2: Start Python AI Service
cd python-ai-service
uvicorn app.main:app --reload --port 8000
```

The API gateway will be available at `http://localhost:3000`

## Example Usage

### Ask a Question

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
  "answer": "Based on the last 30 days, you sell around 10 units per day. You should reorder at least 300 units to avoid stockouts next month.",
  "confidence": "high",
  "shopify_query": "SELECT product_id, SUM(quantity) FROM orders WHERE created_at >= '2024-11-16' GROUP BY product_id",
  "metadata": {
    "execution_time": "1.2s",
    "data_points_analyzed": 150
  }
}
```

## Supported Question Types

| Category | Example Questions |
|----------|------------------|
| **Inventory** | "How many units of Product X will I need next month?"<br>"Which products are likely to go out of stock in 7 days?" |
| **Sales** | "What were my top 5 selling products last week?"<br>"What's my sales trend for the last 30 days?" |
| **Customers** | "Which customers placed repeat orders in the last 90 days?"<br>"What's my customer retention rate?" |
| **Reordering** | "How much inventory should I reorder based on last 30 days sales?" |

## API Documentation

### POST /api/v1/questions

Analyzes a natural language question about store data.

**Request:**
```json
{
  "store_id": "your-store.myshopify.com",
  "question": "Your question here"
}
```

**Response:**
```json
{
  "answer": "Business-friendly explanation",
  "confidence": "low|medium|high",
  "shopify_query": "Generated ShopifyQL",
  "reasoning": ["Step 1: ...", "Step 2: ..."],
  "metadata": {
    "execution_time": "1.5s",
    "data_points_analyzed": 200
  }
}
```

### GET /auth/shopify

Initiates Shopify OAuth flow.

### GET /auth/shopify/callback

Handles OAuth callback and stores access token.

## Agent Workflow

The Python AI service implements a 6-step agentic workflow:

1. **Intent Classification**: Understand what the user is asking
2. **Query Planning**: Determine required Shopify data sources
3. **ShopifyQL Generation**: Create appropriate query using LLM
4. **Query Execution**: Fetch data from Shopify Admin API
5. **Result Processing**: Analyze and extract insights
6. **Natural Language Explanation**: Convert to business-friendly language

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed workflow diagrams.

## Project Structure

```
shopify-analytics-app/
├── api-gateway/                  # Node.js Express API
│   ├── src/
│   │   ├── controllers/          # Request handlers
│   │   ├── services/             # Business logic
│   │   ├── models/               # Database models
│   │   └── middleware/           # Auth, validation
│   ├── package.json
│   └── .env.example
├── python-ai-service/            # Python FastAPI service
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── agent/               # Agent components
│   │   ├── llm/                 # LLM integration
│   │   └── shopify/             # Shopify API client
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests

```bash
# API Gateway tests
cd api-gateway
npm test

# Python AI Service tests
cd python-ai-service
pytest
```

### Mock Mode

For development without a Shopify store:

```bash
# Set in .env
USE_MOCK_DATA=true
```

## Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

Services will be available:
- API Gateway: http://localhost:3000
- Python AI: http://localhost:8000

## Security Considerations

- Shopify access tokens are encrypted at rest
- API keys stored in environment variables
- Request validation and sanitization
- Rate limiting on API endpoints
- HTTPS required in production

## Troubleshooting

### LLM Not Responding
- Check `OPENAI_API_KEY` is set correctly
- Verify OpenAI API quota/billing

### Shopify API Errors
- Ensure OAuth permissions include: `read_products`, `read_orders`, `read_customers`, `read_inventory`
- Check rate limits (2 requests/second for REST API)

### Connection Refused
- Ensure both services are running
- Check `PYTHON_AI_SERVICE_URL` in API gateway .env

## Architecture Diagrams

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system architecture, data flow diagrams, and agent workflow visualizations.

## License

MIT License - Built for educational/interview purposes
