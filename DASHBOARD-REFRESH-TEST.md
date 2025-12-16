# Dashboard Refresh Test

## To Debug the Refresh Button:

Open the browser console (F12) and look for any JavaScript errors when clicking refresh.

## Quick Test Script

Run this in PowerShell to test the metrics endpoint directly:

```powershell
# Test dashboard endpoint
Invoke-RestMethod -Uri "http://localhost:3000/metrics/dashboard"

# Test stats endpoint
Invoke-RestMethod -Uri "http://localhost:3000/metrics/stats"
```

If these work, the refresh button should work too.

## Manual Refresh Test:

In the browser console (F12), type:
```javascript
loadMetrics()
```

This will manually trigger the refresh and show any errors.

## Expected Output:

After asking questions, you should see:
- `Total Queries`: 6 (number of questions asked)
- `Active Sessions`: 1
- `Recent Queries`: List with your questions

## If Refresh Still Doesn't Work:

1. Hard refresh: `Ctrl+Shift+R`
2. Clear browser cache
3. Check browser console for errors (F12)
