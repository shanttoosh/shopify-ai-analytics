# Simple Direct Test
Write-Host "Testing API Gateway..." -ForegroundColor Cyan

# Test health endpoint first
try {
    $health = Invoke-RestMethod -Uri "http://localhost:3000/health" -Method Get
    Write-Host "✓ API Gateway Health: $($health.status)" -ForegroundColor Green
}
catch {
    Write-Host "✗ API Gateway not responding" -ForegroundColor Red
    exit
}

# Build request properly
$headers = @{
    "Content-Type" = "application/json"
}

$bodyObject = @{
    store_id = "analytics-test-store123.myshopify.com"
    question = "What products are in my store?"
}

$jsonBody = $bodyObject | ConvertTo-Json

Write-Host ""
Write-Host "Sending request to: http://localhost:3000/api/v1/questions" -ForegroundColor Yellow
Write-Host "Body: $jsonBody" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" `
        -Method POST `
        -Headers $headers `
        -Body $jsonBody
    
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Full Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
}
catch {
    Write-Host "✗ ERROR!" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Full Error:" -ForegroundColor Yellow
    $_ | Format-List * | Write-Host
}
