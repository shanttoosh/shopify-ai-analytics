# Quick Setup Checklist

Use this checklist to get your Shopify Analytics App running quickly!

## ✅ Setup Checklist

### Part 1: Get Gemini API Key (2 minutes)
- [ ] Visit https://makersuite.google.com/app/apikey
- [ ] Sign in with Google account
- [ ] Click "Create API Key"
- [ ] Copy the key (starts with `AIzaSy...`)

### Part 2: Configure Python Service (1 minute)
- [ ] Open file: `python-ai-service/.env`
- [ ] Find line: `GOOGLE_API_KEY=your-google-gemini-key-here`
- [ ] Paste your actual API key
- [ ] Save file

### Part 3: Install Dependencies (2 minutes)
```bash
# Python dependencies (includes Gemini)
cd python-ai-service
pip install -r requirements.txt

# Node.js dependencies (already done if you followed initial setup)
cd ../api-gateway
npm install
```

### Part 4: Start Services (1 minute)

**Terminal 1:**
```bash
cd api-gateway
npm run dev
```

**Terminal 2:**
```bash
cd python-ai-service
python -m uvicorn app.main:app --reload --port 8000
```

### Part 5: Test (30 seconds)
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d "{\"store_id\": \"test-store.myshopify.com\", \"question\": \"What were my top selling products?\"}"
```

## 🎯 You're Done!

✅ If you got a response with an "answer" field, everything is working!

## 📚 Next Steps

- **More examples**: See `EXAMPLES.md`
- **Shopify OAuth**: See `SETUP-GUIDE.md` (Optional - only for real stores)
- **Architecture**: See `ARCHITECTURE.md`

## ⚠️ Troubleshooting

**Error: "GOOGLE_API_KEY not set"**
- Make sure you edited the `.env` file (not `.env.example`)
- Restart the Python service after editing

**Error: "Cannot connect to Python AI service"**
- Make sure both services are running
- Check that Python service shows "Uvicorn running on http://0.0.0.0:8000"

**Error: "Module 'google.generativeai' not found"**
- Run: `pip install google-generativeai`

---

**Need detailed help?** See [SETUP-GUIDE.md](SETUP-GUIDE.md) for complete instructions!
