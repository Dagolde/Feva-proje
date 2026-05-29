# FEVA Mobile App - Local Backend Connection

## Backend Setup Complete ✅

The backend is running at: `http://192.168.1.106:8000`

### Test Credentials

**Enumerator Account:**
- Username: `test_enum`
- Password: `Test@2026!`

**Admin Account:**
- Username: `admin`
- Password: `Admin@2026!`

## Mobile App Configuration

The mobile app has been configured to connect to your local backend:

1. **Network Security**: Android network security config updated to allow HTTP traffic to `192.168.1.106`
2. **API URLs**: All hardcoded API URLs updated from `https://api.feva.igsl.com` to `http://192.168.1.106:8000`

### Files Modified:
- `feva-mobile/lib/auth/repositories/auth_repository.dart`
- `feva-mobile/lib/sync/sync_engine.dart`
- `feva-mobile/lib/dropdown/dropdown_service.dart`
- `feva-mobile/lib/core/router/app_router.dart`
- `feva-mobile/android/app/src/main/AndroidManifest.xml`
- `feva-mobile/android/app/src/main/res/xml/network_security_config.xml` (created)

## Running the Mobile App

### Prerequisites
1. Ensure your Android device/emulator is on the same network as your PC (192.168.1.x)
2. Backend must be running: `cd feva-backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000`
3. Database containers must be running: `docker compose -f feva-backend/docker-compose.yml up db redis -d`

### Build and Run

```bash
cd feva-mobile

# Clean previous builds
flutter clean

# Get dependencies
flutter pub get

# Generate database code (if needed)
dart run build_runner build --delete-conflicting-outputs

# Run on connected device
flutter run
```

### Testing the Connection

1. Launch the app on your device
2. On the login screen, enter:
   - Username: `test_enum`
   - Password: `Test@2026!`
3. If successful, you should be authenticated and see the main app screen

## Troubleshooting

### "Connection refused" or "Unable to connect"

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok"}
   ```

2. **Check your PC's IP hasn't changed:**
   ```bash
   ipconfig | Select-String -Pattern "IPv4"
   # Look for 192.168.1.x address
   ```
   
   If IP changed, update the mobile app URLs in the files listed above.

3. **Check device is on same network:**
   - Device WiFi should be connected to same router as PC
   - Try pinging from device: `adb shell ping -c 3 192.168.1.106`

4. **Check Windows Firewall:**
   - Ensure port 8000 is allowed for incoming connections
   - Or temporarily disable firewall for testing

### "Invalid username or password"

- Verify credentials are correct (case-sensitive)
- Check backend logs for errors: see terminal running uvicorn

### Database connection errors

```bash
# Restart database containers
docker compose -f feva-backend/docker-compose.yml down
docker compose -f feva-backend/docker-compose.yml up db redis -d

# Wait 15 seconds for health checks, then restart backend
```

## Backend API Endpoints

- Health: `GET http://192.168.1.106:8000/health`
- Login: `POST http://192.168.1.106:8000/api/v1/auth/login`
- Sync: `POST http://192.168.1.106:8000/api/v1/sync/upload`
- Config: `GET http://192.168.1.106:8000/api/v1/sync/config`

## Next Steps

1. **Seed dropdown data**: Run the provision script to add street types, building types, etc.
   ```bash
   cd feva-backend
   python scripts/provision_pilot_devices.py --api-url http://localhost:8000 --admin-user admin --admin-password "Admin@2026!" --lgas TEST_LGA
   ```

2. **Test sync**: Create a street or building record in the mobile app and sync to backend

3. **Upload boundary shapefiles**: Use the admin API to upload LGA/ward boundary files for offline use
