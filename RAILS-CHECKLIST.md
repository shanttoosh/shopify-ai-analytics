# Rails API Gateway - Build Checklist

## Phase 1: Environment Setup
- [ ] Download Ruby installer (rubyinstaller.org)
- [ ] Install Ruby 3.2.6 with DevKit
- [ ] Run MSYS2 setup (option 1)
- [ ] Verify: `ruby --version`
- [ ] Install Rails: `gem install rails`
- [ ] Verify: `rails --version`

## Phase 2: Create Rails App
- [ ] Create new Rails API: `rails new rails-api-gateway --api`
- [ ] Test server: `rails server -p 4000`
- [ ] Add dependencies to Gemfile
- [ ] Run: `bundle install`

## Phase 3: Database Setup
- [ ] Create Store model
- [ ] Create QueryLog model
- [ ] Run migrations
- [ ] Add token encryption

## Phase 4: Controllers
- [ ] Health controller (`/health`)
- [ ] Questions controller (`/api/v1/questions`)
- [ ] Shopify auth controller (`/auth/shopify`)
- [ ] Add input validation

## Phase 5: Services
- [ ] Python AI client service
- [ ] Store service
- [ ] Query log service

## Phase 6: Configuration
- [ ] Setup CORS
- [ ] Environment variables (.env)
- [ ] Routes configuration
- [ ] Session management

## Phase 7: Testing
- [ ] Test health endpoint
- [ ] Test questions endpoint
- [ ] Test with Python AI service
- [ ] Verify all example questions

## Phase 8: Documentation
- [ ] Update README
- [ ] Add Rails-specific setup
- [ ] Update architecture docs
