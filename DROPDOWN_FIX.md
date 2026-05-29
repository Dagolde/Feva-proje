# Dropdown Data Fix

## Problem
The dropdown buttons in the Street and Building forms were empty because the `dropdown_config` table had no data.

## Solution Applied

### Backend (PostgreSQL)
✅ Created and ran `feva-backend/scripts/seed_dropdown_config.sql` to populate the backend database with:
- 9 street types (Avenue, Boulevard, Close, Crescent, Drive, Lane, Road, Street, Way)
- 6 surface types (Asphalt, Concrete, Gravel, Dirt, Paved Blocks, Unpaved)
- 5 street conditions (Excellent, Good, Fair, Poor, Very Poor)
- 10 building types (Residential, Commercial, Industrial, Mixed Use, Institutional, Religious, Educational, Healthcare, Government, Recreational)
- 7 building conditions (Excellent, Good, Fair, Poor, Very Poor, Under Construction, Abandoned)

### Mobile App (SQLite)
✅ Updated `feva-mobile/lib/database/app_database.dart` to automatically seed dropdown data when the database is first created.

## How to Apply the Fix

Since your mobile app database already exists, you need to recreate it to trigger the seed data insertion:

### Option 1: Uninstall and Reinstall (Recommended)
```bash
# Uninstall the app from your device
adb uninstall com.igsl.feva

# Then rebuild and install
cd feva-mobile
flutter run
```

### Option 2: Clear App Data (Faster)
On your Android device:
1. Go to Settings → Apps → FEVA
2. Tap "Storage"
3. Tap "Clear Data" (this will delete the database)
4. Reopen the app

### Option 3: Manual Database Deletion via ADB
```bash
adb shell run-as com.igsl.feva rm /data/data/com.igsl.feva/databases/feva.db
```

## Verification

After applying the fix:
1. Login to the app
2. Navigate to Streets → Add New Street
3. Tap on "Street Type" dropdown - you should see 9 options
4. Tap on "Surface Type" dropdown - you should see 6 options
5. Navigate to Buildings → Add New Building
6. Tap on "Building Type" dropdown - you should see 10 options

## Future Sync

The app also has a `DropdownService.syncFromServer()` method that can download updated dropdown values from the backend API endpoint `/api/v1/sync/config`. This will be useful for updating dropdown options without reinstalling the app.
