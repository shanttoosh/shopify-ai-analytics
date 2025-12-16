# Shopify Analytics App - Quick Start Guide

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python --version`)
- [ ] npm installed (`npm --version`)
- [ ] pip installed (`pip --version`)
- [ ] OpenAI API key (get from https://platform.openai.com/api-keys)

## Step 1: Clone & Navigate

```bash
cd shopify-analytics-app
```

## Step 2: Set Up API Gateway (Node.js)

```bash
cd api-gateway

# Install dependencies
npm install

# The .env file should already exist, update it with your settings
# Key setting: USE_MOCK_DATA=true (for testing without Shopify)

# Start the server
npm run dev
```

The API gateway will start on `http://localhost:3000`

## Step 3: Set Up Python AI Service  

Open a **new terminal** window:

```bash
cd shopify-analytics-app/python-ai-service

# Install dependencies
pip install -r requirements.txt

# The .env file should already exist
# IMPORTANT: Add your OpenAI API key to .env
# Edit the file and replace: OPENAI_API_KEY=your-openai-api-key-here

# Start the service
python -m uvicorn app.main:app --reload --port 8000
```

The Python service will start on `http://localhost:8000`

## Step 4: Test the System

Open a **third terminal** window and try these test requests:

### Test 1: Health Check

```bash
# Check API Gateway
curl http://localhost:3000/health

# Check Python AI Service
curl http://localhost:8000/health
```

### Test 2: Ask a Question

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d "{\"store_id\": \"test-store.myshopify.com\", \"question\": \"What were my top 5 selling products last week?\"}"
```

You should get a detailed response with:
- A business-friendly answer
- Confidence level  
- The generated ShopifyQL query
- Agent reasoning steps
- Metadata

## Troubleshooting

### "Cannot connect to Python AI service"

- Ensure Python service is running on port 8000
- Check `PYTHON_AI_SERVICE_URL` in api-gateway/.env

### "OpenAI API error"

- Verify your `OPENAI_API_KEY` is set correctly in python-ai-service/.env
- Check your OpenAI account has available credits

### "Module not found"

- Ensure you ran `npm install` in api-gateway
- Ensure you ran `pip install -r requirements.txt` in python-ai-service

### Port already in use

- Change `PORT` in .env files to use different ports
- Or stop the process using the port

## Quick Test Script

For convenience, here's a PowerShell script to test the system:

```powershell
# Save this as test-system.ps1

Write-Host "Testing Shopify Analytics App..." -ForegroundColor Green

# Test health endpoints
Write-Host "`nChecking API Gateway..."
curl http://localhost:3000/health

Write-Host "`nChecking Python AI Service..."
curl http://localhost:8000/health

# Test question endpoint
Write-Host "`nAsking a question..."
$body = @{
    store_id = "test-store.myshopify.com"
    question = "How many units will I need next month?"
} | ConvertTo-Json

curl -Method POST -Uri http://localhost:3000/api/v1/questions `
     -Headers @{"Content-Type"="application/json"} `
     -Body $body

Write-Host "`nTests complete!" -ForegroundColor Green
```

Run with: `.\test-system.ps1`

## Next Steps

1. Review `EXAMPLES.md` for more sample questions
2. Check `ARCHITECTURE.md` for system design details
3. See `README.md` for full documentation
4. Try asking your own questions!

## Ready for Production?

To use with a real Shopify store:

1. Set `USE_MOCK_DATA=false` in both .env files
2. Get Shopify API credentials from Shopify Partner Dashboard
3. Update `SHOPIFY_API_KEY` and `SHOPIFY_API_SECRET` in api-gateway/.env
4. Authenticate: Visit `http://localhost:3000/auth/shopify?shop=your-store.myshopify.com`
5. Start querying your real store data!
