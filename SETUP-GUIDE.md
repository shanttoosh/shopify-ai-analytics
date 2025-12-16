# 🚀 Setup Guide - Google Gemini & Shopify OAuth

This guide will help you set up the Shopify Analytics App using **Google Gemini** (free!) instead of OpenAI, and configure Shopify OAuth.

---

## Part 1: Setting Up Google Gemini (5 minutes)

### Step 1: Get Your Free Gemini API Key

1. **Visit Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. Click **"Create API Key"**
4. **Copy the key** (it looks like: `AIzaSyC...`)

> 💡 **Note**: Gemini is FREE with generous rate limits! Perfect for this project.

### Step 2: Configure Python Service

1. Open the file: `python-ai-service/.env`
2. Find the line with `GOOGLE_API_KEY=`
3. Replace `your-google-gemini-key-here` with your actual key:

```bash
# LLM Provider Configuration
GOOGLE_API_KEY=AIzaSyC-your-actual-key-here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro
```

4. **Save the file**

### Step 3: Install Gemini Package

```bash
cd python-ai-service
pip install google-generativeai
```

✅ **That's it!** Gemini is now configured and ready to use.

---

## Part 2: Shopify OAuth Setup (Optional - for Real Store)

You have **two options**:

### Option A: Use Mock Data (No Shopify Account Needed) - RECOMMENDED FOR TESTING

**Already configured!** Just keep this setting in both `.env` files:

```bash
USE_MOCK_DATA=true
```

You can test the entire system without any Shopify credentials. Skip to "Testing Your Setup" below.

---

### Option B: Connect to Real Shopify Store

If you want to connect to a real Shopify store, follow these steps:

#### Step 1: Create Shopify Partner Account

1. Go to: https://partners.shopify.com/signup
2. Sign up for a **free Partner account**
3. Confirm your email

#### Step 2: Create a Development Store

1. In Shopify Partners, click **"Stores"** → **"Add store"**
2. Select **"Development store"**
3. Fill in details:
   - Store name: `your-test-store`
   - Purpose: Development
4. Note your store URL: `your-test-store.myshopify.com`

#### Step 3: Create a Custom App

1. Go to your **Partner Dashboard**
2. Click **"Apps"** → **"Create app"**
3. Select **"Create app manually"**
4. Fill in:
   - App name: `Shopify Analytics AI`
   - App URL: `http://localhost:3000`
   - Allowed redirection URL(s): `http://localhost:3000/auth/shopify/callback`

5. **Get your API credentials:**
   - Click on your app
   - Go to **"App credentials"** tab
   - Copy **"API key"** (Client ID)
   - Copy **"API secret key"** (Client secret)

#### Step 4: Set Required Scopes/Permissions

In your app settings, go to **"Configuration"** → **"Admin API access scopes"**

Select these scopes:
- ✅ `read_products`
- ✅ `read_orders`
- ✅ `read_customers`
- ✅ `read_inventory`

Save the configuration.

#### Step 5: Configure API Gateway

1. Open: `api-gateway/.env`
2. Update these values:

```bash
# Shopify OAuth
SHOPIFY_API_KEY=your-api-key-from-step-3
SHOPIFY_API_SECRET=your-api-secret-from-step-3
SHOPIFY_SCOPES=read_products,read_orders,read_customers,read_inventory
SHOPIFY_CALLBACK_URL=http://localhost:3000/auth/shopify/callback

# Disable mock mode to use real data
USE_MOCK_DATA=false
```

3. Also update in `python-ai-service/.env`:

```bash
USE_MOCK_DATA=false
```

#### Step 6: Install Your App on Development Store

1. **Start your services** (see "Testing Your Setup" below)
2. **Open your browser** and visit:
   ```
   http://localhost:3000/auth/shopify?shop=your-test-store.myshopify.com
   ```
   (Replace `your-test-store` with your actual store name)

3. You'll be redirected to Shopify to **approve permissions**
4. Click **"Install app"**
5. You'll be redirected back with a success message

✅ **Your app is now connected to Shopify!**

---

## Testing Your Setup

### 1. Start the Services

**Terminal 1 - API Gateway:**
```bash
cd api-gateway
npm run dev
```

You should see:
```
🚀 API Gateway running on port 3000
📝 Environment: development
🤖 Python AI Service: http://localhost:8000
🔧 Mock Mode: ON (or OFF if using real Shopify)
```

**Terminal 2 - Python AI Service:**
```bash
cd python-ai-service
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Test Health Checks

Open a **third terminal** and run:

```bash
# Test API Gateway
curl http://localhost:3000/health

# Test Python AI Service (should show "gemini" as provider)
curl http://localhost:8000/health
```

### 3. Ask Your First Question!

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d "{\"store_id\": \"test-store.myshopify.com\", \"question\": \"What were my top 5 selling products last week?\"}"
```

You should get a detailed response with:
- ✅ Business-friendly answer
- ✅ Confidence level
- ✅ Generated ShopifyQL query
- ✅ Agent reasoning steps

### 4. Try More Questions

```bash
# Inventory projection
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d "{\"store_id\": \"test-store.myshopify.com\", \"question\": \"How much inventory should I reorder for next week?\"}"

# Customer behavior
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d "{\"store_id\": \"test-store.myshopify.com\", \"question\": \"Which customers made repeat purchases?\"}"
```

---

## Troubleshooting

### "GOOGLE_API_KEY not set in environment"

**Fix:**
1. Make sure you edited `python-ai-service/.env` (not `.env.example`)
2. Verify your API key is correct
3. Restart the Python service

### "Cannot connect to Python AI service"

**Fix:**
1. Make sure Python service is running on port 8000
2. Check no other process is using port 8000:
   ```bash
   netstat -ano | findstr :8000
   ```
3. Verify `PYTHON_AI_SERVICE_URL` in `api-gateway/.env` is set to `http://localhost:8000`

### "Gemini API error: ..."

**Common issues:**
- **Quota exceeded**: You've hit the free tier limit (wait a bit, or reduce requests)
- **Invalid API key**: Double-check your key from Google AI Studio
- **Package not installed**: Run `pip install google-generativeai`

### Shopify OAuth Issues

**"Invalid shop domain"**
- Make sure shop URL ends with `.myshopify.com`
- Use the exact domain from your Partner dashboard

**"Store not found"**
- You need to complete OAuth flow first
- Visit: `http://localhost:3000/auth/shopify?shop=your-store.myshopify.com`

---

## Quick Reference

### Current Configuration

**LLM Provider:** Google Gemini (FREE!)  
**API Key Location:** `python-ai-service/.env`  
**Data Mode:** Mock (no Shopify account needed)

### File Locations

- **Gemini Config**: `python-ai-service/.env`
- **Shopify Config**: `api-gateway/.env`
- **Test Script**: `test-system.ps1`

### Important URLs

- **Get Gemini Key**: https://makersuite.google.com/app/apikey
- **Shopify Partners**: https://partners.shopify.com
- **API Gateway**: http://localhost:3000
- **Python Service**: http://localhost:8000

---

## Next Steps

1. ✅ Get Gemini API key (5 minutes)
2. ✅ Configure `.env` files
3. ✅ Install dependencies: `pip install google-generativeai`
4. ✅ Start both services
5. ✅ Test with sample questions
6. 🎯 (Optional) Connect to real Shopify store

**Need more examples?** Check `EXAMPLES.md` for 6 detailed sample queries!

**Questions?** Review `QUICKSTART.md` or `README.md` for more details.

---

## Why Gemini?

✅ **Free** - No credit card required  
✅ **Fast** - Quick response times  
✅ **Capable** - Handles all our analytics tasks  
✅ **Easy** - Just one API key needed  
✅ **Generous limits** - Plenty for development

You can always switch to OpenAI or Claude later by just changing 3 lines in the `.env` file!
