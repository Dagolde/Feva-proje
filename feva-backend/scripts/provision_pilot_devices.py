#!/usr/bin/env python3
"""Field pilot device provisioning script.

Usage:
    python scripts/provision_pilot_devices.py --api-url http://localhost:8000 \
        --admin-user admin --admin-password <password> \
        --lgas ABUJA KANO

What this script does:
  1. Authenticates as Admin and obtains a JWT.
  2. Creates Enumerator and Supervisor test accounts for each pilot LGA.
  3. Seeds dropdown config (street_type, surface_type, etc.) via Admin API.
  4. Uploads boundary Shapefiles for the pilot LGAs (if --shapefile-dir provided).
  5. Prints an ADB install command for the pilot APK (if --apk provided).

Requirements: 8.1, 18.1, 19.1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Provision FEVA pilot devices")
    p.add_argument("--api-url", default="http://localhost:8000", help="Backend base URL")
    p.add_argument("--admin-user", required=True)
    p.add_argument("--admin-password", required=True)
    p.add_argument("--lgas", nargs="+", required=True, help="LGA codes to provision, e.g. ABUJA KANO")
    p.add_argument("--shapefile-dir", type=Path, help="Directory containing .zip boundary files per LGA")
    p.add_argument("--apk", type=Path, help="Path to pilot APK to install via ADB")
    p.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    return p.parse_args()


# ── Default seed data ─────────────────────────────────────────────────────────

DROPDOWN_SEED: list[dict] = [
    # street_type
    {"category": "street_type", "value": "residential", "label": "Residential", "sort_order": 1},
    {"category": "street_type", "value": "commercial", "label": "Commercial", "sort_order": 2},
    {"category": "street_type", "value": "arterial", "label": "Arterial", "sort_order": 3},
    {"category": "street_type", "value": "collector", "label": "Collector", "sort_order": 4},
    # surface_type
    {"category": "surface_type", "value": "asphalt", "label": "Asphalt", "sort_order": 1},
    {"category": "surface_type", "value": "concrete", "label": "Concrete", "sort_order": 2},
    {"category": "surface_type", "value": "gravel", "label": "Gravel", "sort_order": 3},
    {"category": "surface_type", "value": "earth", "label": "Earth/Unpaved", "sort_order": 4},
    # street_condition
    {"category": "street_condition", "value": "good", "label": "Good", "sort_order": 1},
    {"category": "street_condition", "value": "fair", "label": "Fair", "sort_order": 2},
    {"category": "street_condition", "value": "poor", "label": "Poor", "sort_order": 3},
    # building_type
    {"category": "building_type", "value": "residential", "label": "Residential", "sort_order": 1},
    {"category": "building_type", "value": "commercial", "label": "Commercial", "sort_order": 2},
    {"category": "building_type", "value": "mixed", "label": "Mixed Use", "sort_order": 3},
    {"category": "building_type", "value": "industrial", "label": "Industrial", "sort_order": 4},
    {"category": "building_type", "value": "institutional", "label": "Institutional", "sort_order": 5},
    # building_condition
    {"category": "building_condition", "value": "good", "label": "Good", "sort_order": 1},
    {"category": "building_condition", "value": "fair", "label": "Fair", "sort_order": 2},
    {"category": "building_condition", "value": "poor", "label": "Poor", "sort_order": 3},
    {"category": "building_condition", "value": "dilapidated", "label": "Dilapidated", "sort_order": 4},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _log(msg: str, dry_run: bool = False) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"{prefix}{msg}")


def _login(client: httpx.Client, api_url: str, username: str, password: str) -> str:
    resp = client.post(
        f"{api_url}/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    resp.raise_for_status()
    token: str = resp.json()["access_token"]
    return token


def _create_user(
    client: httpx.Client,
    api_url: str,
    token: str,
    username: str,
    email: str,
    password: str,
    role_id: int,
    lga: str,
    dry_run: bool,
) -> None:
    _log(f"  Creating user '{username}' (role_id={role_id}, lga={lga})", dry_run)
    if dry_run:
        return
    resp = client.post(
        f"{api_url}/api/v1/admin/users",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role_id": role_id,
            "lga_assignment": [lga],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 201:
        _log(f"    → created id={resp.json()['id']}")
    elif resp.status_code == 409:
        _log(f"    → already exists, skipping")
    else:
        _log(f"    → WARNING: {resp.status_code} {resp.text}")


def _seed_dropdowns(
    client: httpx.Client, api_url: str, token: str, dry_run: bool
) -> None:
    _log("Seeding dropdown config…", dry_run)
    for item in DROPDOWN_SEED:
        _log(f"  {item['category']}/{item['value']}", dry_run)
        if dry_run:
            continue
        resp = client.post(
            f"{api_url}/api/v1/admin/dropdown-config",
            json=item,
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code not in (201, 409):
            _log(f"    → WARNING: {resp.status_code} {resp.text}")


def _upload_shapefile(
    client: httpx.Client,
    api_url: str,
    token: str,
    zip_path: Path,
    layer_name: str,
    dry_run: bool,
) -> None:
    _log(f"  Uploading shapefile {zip_path.name} as layer '{layer_name}'…", dry_run)
    if dry_run:
        return
    with zip_path.open("rb") as fh:
        resp = client.post(
            f"{api_url}/api/v1/admin/shapefiles",
            data={"layer_name": layer_name, "version_tag": "pilot-2026"},
            files={"file": (zip_path.name, fh, "application/zip")},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120,
        )
    if resp.status_code == 201:
        _log(f"    → ingested {resp.json().get('features_written', '?')} features")
    else:
        _log(f"    → WARNING: {resp.status_code} {resp.text}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    dry_run: bool = args.dry_run

    _log(f"=== FEVA Pilot Provisioning ({'DRY RUN' if dry_run else 'LIVE'}) ===")
    _log(f"API: {args.api_url}")
    _log(f"LGAs: {', '.join(args.lgas)}")

    with httpx.Client(timeout=30) as client:
        # 1. Admin login
        _log("\n[1/4] Authenticating as admin…")
        if not dry_run:
            token = _login(client, args.api_url, args.admin_user, args.admin_password)
            _log("  → authenticated")
        else:
            token = "dry-run-token"

        # 2. Create test accounts per LGA
        # role_id 2 = enumerator, role_id 3 = supervisor (matches seed data)
        _log("\n[2/4] Creating test accounts…")
        for lga in args.lgas:
            lga_lower = lga.lower()
            _create_user(
                client, args.api_url, token,
                username=f"enum_{lga_lower}_01",
                email=f"enum_{lga_lower}_01@pilot.feva.test",
                password=f"Pilot@{lga}2026!",
                role_id=2,
                lga=lga,
                dry_run=dry_run,
            )
            _create_user(
                client, args.api_url, token,
                username=f"super_{lga_lower}_01",
                email=f"super_{lga_lower}_01@pilot.feva.test",
                password=f"Pilot@{lga}2026!",
                role_id=3,
                lga=lga,
                dry_run=dry_run,
            )

        # 3. Seed dropdown config
        _log("\n[3/4] Seeding dropdown config…")
        _seed_dropdowns(client, args.api_url, token, dry_run)

        # 4. Upload boundary shapefiles
        _log("\n[4/4] Uploading boundary shapefiles…")
        if args.shapefile_dir:
            for lga in args.lgas:
                zip_path = args.shapefile_dir / f"{lga.lower()}_boundaries.zip"
                if zip_path.exists():
                    _upload_shapefile(client, args.api_url, token, zip_path, lga.lower(), dry_run)
                else:
                    _log(f"  WARNING: {zip_path} not found — skipping")
        else:
            _log("  --shapefile-dir not provided, skipping")

    # 5. APK install hint
    if args.apk:
        _log(f"\nTo install APK on connected devices:")
        _log(f"  adb devices | tail -n +2 | awk '{{print $1}}' | xargs -I{{}} adb -s {{}} install -r {args.apk}")

    _log("\n=== Provisioning complete ===")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error: {exc.response.status_code} {exc.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
