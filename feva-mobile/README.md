# FEVA Mobile

**Field Enumeration and Verification App — Flutter Mobile Client**

FEVA is an offline-first mobile data collection application commissioned by Inspired Global Systems Ltd (IGSL) on behalf of a Nigerian State Government as part of a statewide Addressing Infrastructure Programme.

## Overview

The FEVA mobile app enables systematic enumeration of all streets and buildings across all Local Government Areas (LGAs) in the State. It supports:

- Offline-first data capture with SQLite/SQLCipher local storage
- GPS acquisition with accuracy monitoring and EXIF-tagged photo capture
- Shapefile boundary layer validation (point-in-polygon, reverse geocode)
- Incremental background sync to the FEVA backend over TLS 1.2+
- Role-based access control (Enumerator, Supervisor, Admin)
- Phase 3 QR code scanning for physical building verification

## Platform Requirements

- Android 8.0 (API level 26) or higher (mandatory)
- iOS 14 or higher (optional)

## Tech Stack

- **Framework**: Flutter (Dart)
- **Local DB**: SQLite via Drift ORM + SQLCipher (AES-256 at rest)
- **Maps**: MapLibre GL (offline MBTiles + GeoJSON boundary layers)
- **State Management**: flutter_bloc / Cubit
- **Sync**: flutter_workmanager (background isolate)

## Getting Started

```bash
flutter pub get
flutter run
```

## Branch Strategy

| Branch    | Purpose                          |
|-----------|----------------------------------|
| `main`    | Production releases only         |
| `develop` | Integration branch for features  |
| `feature/*` | Individual feature branches    |
| `hotfix/*`  | Production hotfix branches     |

## Ownership

Maintained by [@igsl/feva-dev](https://github.com/orgs/igsl/teams/feva-dev).  
All source code is the property of IGSL and the commissioning State Government.
