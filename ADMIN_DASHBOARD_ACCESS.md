# FEVA Admin Dashboard Access

## Dashboard URL

**Local Development:** http://localhost:8000/dashboard/

## Admin Credentials

- **Username:** `admin`
- **Password:** `Admin@2026!`

## How to Access

### Option 1: Browser with Session Cookie (Recommended)

1. **Login via API first to get a token:**
   ```bash
   # PowerShell
   $body = '{"username":"admin","password":"Admin@2026!"}'
   $response = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method POST -Body $body -ContentType 'application/json'
   $token = $response.access_token
   Write-Output $token
   ```

2. **Access dashboard with Bearer token:**
   - Open your browser
   - Install a browser extension like "ModHeader" or "Simple Modify Headers"
   - Add header: `Authorization: Bearer YOUR_TOKEN_HERE`
   - Navigate to: http://localhost:8000/dashboard/

### Option 2: Using curl/PowerShell

```powershell
# Get token
$body = '{"username":"admin","password":"Admin@2026!"}'
$response = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method POST -Body $body -ContentType 'application/json'
$token = $response.access_token

# Access dashboard
$headers = @{Authorization = "Bearer $token"}
Invoke-WebRequest -Uri http://localhost:8000/dashboard/ -Headers $headers -UseBasicParsing
```

### Option 3: Quick Browser Access (No Auth Extension)

The dashboard requires authentication. To make it easier for local development, you can temporarily modify the dashboard route to skip auth:

**File:** `feva-backend/app/api/dashboard.py`

Change:
```python
@router.get("/dashboard/", response_class=HTMLResponse)
async def qa_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("supervisor", "admin")),  # <-- Remove this line
):
```

To:
```python
@router.get("/dashboard/", response_class=HTMLResponse)
async def qa_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_role("supervisor", "admin")),  # <-- Commented out
):
```

Then just open: http://localhost:8000/dashboard/

**⚠️ Remember to re-enable auth before deploying to production!**

## Dashboard Features

The QA Dashboard provides:
- **Metrics Overview:** Total records, pending reviews, flagged items
- **Flagged Records:** Buildings and streets with QA issues
  - Boundary violations
  - GPS accuracy problems
  - Duplicate detections
- **Record Details:** View and manage flagged items

## Troubleshooting

### "401 Unauthorized"
- Token expired (tokens expire after 1 hour)
- Get a new token using the login endpoint

### "403 Forbidden"
- User doesn't have admin or supervisor role
- Verify role: `SELECT username, role_id FROM users WHERE username='admin';`
- Admin should have role_id = 1

### "500 Internal Server Error"
- Check backend logs in the uvicorn terminal
- Ensure database is running: `docker ps | grep feva_db`

## API Endpoints for Dashboard Data

If you want to access the data programmatically:

- **QA Metrics:** `GET /api/v1/qa/metrics`
- **Flagged Records:** `GET /api/v1/qa/flagged`

Both require Bearer token authentication.

## Next Steps

1. **Seed test data:** Create some buildings/streets with QA flags to see them in the dashboard
2. **Test QA workflows:** Review, approve, or reject flagged records
3. **Export data:** Use the export endpoints to download GeoJSON/CSV
