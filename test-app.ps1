# Test Your Shopify Analytics App
Write-Host "Testing Shopify Analytics App..." -ForegroundColor Cyan
Write-Host ""

# Test 1: What products are in my store?
Write-Host "[TEST 1] Asking: What products are in my store?" -ForegroundColor Yellow

$body = @{
    store_id = "analytics-test-store123.myshopify.com"
    question = "What products are in my store?"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" `
        -Method Post `
        -Headers @{"Content-Type" = "application/json" } `
        -Body $body
    
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Answer:" -ForegroundColor Cyan
    Write-Host $response.answer -ForegroundColor White
    Write-Host ""
    Write-Host "Confidence: $($response.confidence)" -ForegroundColor Gray
    Write-Host "Data points analyzed: $($response.metadata.data_points_analyzed)" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "✗ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test 2: Inventory projection
Write-Host "[TEST 2] Asking: How much inventory will I need next week?" -ForegroundColor Yellow

$body2 = @{
    store_id = "analytics-test-store123.myshopify.com"
    question = "How much inventory will I need next week?"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" `
        -Method Post `
        -Headers @{"Content-Type" = "application/json" } `
        -Body $body2
    
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Answer:" -ForegroundColor Cyan
    Write-Host $response2.answer -ForegroundColor White
    Write-Host ""
}
catch {
    Write-Host "✗ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Tests Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
