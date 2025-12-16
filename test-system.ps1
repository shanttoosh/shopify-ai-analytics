# Test Script for Shopify Analytics App
# Save as: test-system.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Shopify Analytics App - Test Suite  " -ForegroundColor Cyan  
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Checks
Write-Host "[TEST 1] Checking API Gateway health..." -ForegroundColor Yellow
try {
    $apiHealth = Invoke-RestMethod -Uri "http://localhost:3000/health" -Method Get
    Write-Host "✓ API Gateway is healthy" -ForegroundColor Green
    Write-Host "  Status: $($apiHealth.status)" -ForegroundColor Gray
} catch {
    Write-Host "✗ API Gateway is not responding" -ForegroundColor Red
    Write-Host "  Make sure it's running on port 3000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[TEST 2] Checking Python AI Service health..." -ForegroundColor Yellow
try {
    $aiHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✓ Python AI Service is healthy" -ForegroundColor Green
    Write-Host "  LLM Provider: $($aiHealth.llm_provider)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Python AI Service is not responding" -ForegroundColor Red
    Write-Host "  Make sure it's running on port 8000" -ForegroundColor Gray
}

# Test 2: Top Products Question
Write-Host ""
Write-Host "[TEST 3] Testing: Top Selling Products..." -ForegroundColor Yellow
$body1 = @{
    store_id = "test-store.myshopify.com"
    question = "What were my top 5 selling products last week?"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" `
                                   -Method Post `
                                   -Headers @{"Content-Type"="application/json"} `
                                   -Body $body1
    
    Write-Host "✓ Query successful" -ForegroundColor Green
    Write-Host "  Answer: $($response1.answer.Substring(0, [Math]::Min(100, $response1.answer.Length)))..." -ForegroundColor Gray
    Write-Host "  Confidence: $($response1.confidence)" -ForegroundColor Gray
    Write-Host "  Data points: $($response1.metadata.data_points_analyzed)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Query failed" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Gray
}

# Test 3: Inventory Projection
Write-Host ""
Write-Host "[TEST 4] Testing: Inventory Projection..." -ForegroundColor Yellow
$body2 = @{
    store_id = "test-store.myshopify.com"
    question = "How many units will I need next month?"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" `
                                   -Method Post `
                                   -Headers @{"Content-Type"="application/json"} `
                                   -Body $body2
    
    Write-Host "✓ Query successful" -ForegroundColor Green
    Write-Host "  Answer: $($response2.answer.Substring(0, [Math]::Min(100, $response2.answer.Length)))..." -ForegroundColor Gray
    Write-Host "  Confidence: $($response2.confidence)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Query failed" -ForegroundColor Red
}

# Test 4: Customer Behavior
Write-Host ""
Write-Host "[TEST 5] Testing: Customer Behavior..." -ForegroundColor Yellow
$body3 = @{
    store_id = "test-store.myshopify.com"
    question = "Which customers placed repeat orders in the last 90 days?"
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" `
                                   -Method Post `
                                   -Headers @{"Content-Type"="application/json"} `
                                   -Body $body3
    
    Write-Host "✓ Query successful" -ForegroundColor Green
    Write-Host "  Answer: $($response3.answer.Substring(0, [Math]::Min(100, $response3.answer.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Query failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Test Suite Complete!                 " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
