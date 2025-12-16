# Rails API Gateway - Step-by-Step Setup Guide

## Phase 1: Install Ruby & Rails (30-60 minutes)

### Step 1: Download Ruby Installer

1. **Go to:** https://rubyinstaller.org/downloads/
2. **Download:** Ruby+Devkit 3.2.6-1 (x64) - RECOMMENDED
   - Look for: `rubyinstaller-devkit-3.2.6-1-x64.exe`
3. **Run the installer**

### Step 2: Install Ruby

During installation:
- ✅ Check: "Add Ruby executables to your PATH"
- ✅ Check: "Associate .rb and .rbw files"
- ✅ Select: "MSYS2 development toolchain"
- Click "Install"

At the end:
- ✅ Check: "Run 'ridk install'"
- Click "Finish"

### Step 3: Complete MSYS2 Setup

A terminal window will appear asking which components to install:
- Type: **`1`** (MSYS2 base installation)
- Press **Enter**
- Wait for installation to complete
- Press **Enter** again to close

### Step 4: Verify Ruby Installation

Open a **NEW PowerShell terminal** and run:
```powershell
ruby --version
# Should show: ruby 3.2.6

gem --version
# Should show: 3.4.x or higher
```

### Step 5: Install Rails

```powershell
gem install rails
```

This will take 3-5 minutes. You'll see lots of gems being installed.

### Step 6: Verify Rails

```powershell
rails --version
# Should show: Rails 7.x.x
```

✅ **Ruby & Rails installed!**

---

## Phase 2: Create Rails API (15 minutes)

### Step 1: Navigate to Project

```powershell
cd c:\Users\DELL\Downloads\cafe-nostalgia\shopify-analytics-app
```

### Step 2: Create Rails API-only App

```powershell
rails new rails-api-gateway --api --database=sqlite3 --skip-test
```

This creates a minimal Rails API (no views, no asset pipeline).

### Step 3: Navigate to Rails App

```powershell
cd rails-api-gateway
```

### Step 4: Test Rails Server

```powershell
rails server -p 4000
```

Visit: http://localhost:4000
You should see a Rails welcome page!

Press **Ctrl+C** to stop.

✅ **Rails app created!**

---

## Phase 3: Add Dependencies (5 minutes)

### Step 1: Edit Gemfile

Open: `rails-api-gateway/Gemfile`

Add these gems:
```ruby
# HTTP client for Python AI service
gem 'httparty'

# CORS support
gem 'rack-cors'

# Environment variables
gem 'dotenv-rails', groups: [:development, :test]

# Input validation
gem 'active_model_serializers'
```

### Step 2: Install Gems

```powershell
bundle install
```

✅ **Dependencies installed!**

---

## Phase 4: Port Functionality (I'll guide you through each file)

We'll create:
1. **Models** - Store, QueryLog
2. **Controllers** - Questions, Auth, Health
3. **Services** - PythonAIClient
4. **Routes** - API endpoints
5. **Config** - CORS, environment

**Ready to start Phase 1 (Install Ruby)?**

Let me know when you've:
1. Downloaded Ruby installer
2. Completed installation
3. Verified `ruby --version` works

Then I'll guide you through Phase 2!
