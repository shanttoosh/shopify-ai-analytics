$body = '{"store_id": "analytics-test-store123.myshopify.com", "question": "What products are in my store?"}'

Invoke-RestMethod -Uri "http://localhost:3000/api/v1/questions" -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 10
