import '../database/app_database.dart';
import 'models/reverse_geocode_result.dart';
import 'wkb/wkb_polygon.dart';

/// Provides offline spatial services backed by the local SQLite boundary_zones
/// table.
///
/// Requirements: 2.4, 3.4, 8.2, 8.3, 10.1, 10.2, 10.3
class BoundaryService {
  final AppDatabase db;

  BoundaryService({required this.db});

  /// Tests whether ([lon], [lat]) falls within the zone identified by [zoneId].
  ///
  /// Loads the WKB polygon from the DB and runs a ray-casting PIP test.
  /// Returns `false` if the zone is not found or the geometry cannot be parsed.
  Future<bool> containmentCheck(
      double lon, double lat, String zoneId) async {
    final query = db.select(db.boundaryZones)
      ..where((t) => t.zoneId.equals(zoneId));
    final zone = await query.getSingleOrNull();
    if (zone == null) return false;

    final polygon = WkbPolygon.fromBytes(zone.geometryWkb);
    if (polygon == null) return false;

    return polygon.contains(lon, lat);
  }

  /// Reverse geocodes ([lon], [lat]) against all boundary zones.
  ///
  /// Queries zones by type in order: 'lga', 'ward', 'nipost'.
  /// Sets [ReverseGeocodeResult.postcodeStatus] = 'unresolved' when no NIPOST
  /// polygon matches.
  /// Sets [ReverseGeocodeResult.boundaryFlag] = true when [assignedLgaCode] is
  /// provided and the point does not fall within that LGA.
  ///
  /// [assignedLgaCode] — the LGA code from the user's session.
  Future<ReverseGeocodeResult> reverseGeocode(
    double lon,
    double lat, {
    String? assignedLgaCode,
  }) async {
    final lgaZone = await _findContainingZone(lon, lat, 'lga');
    final wardZone = await _findContainingZone(lon, lat, 'ward');
    final nipostZone = await _findContainingZone(lon, lat, 'nipost');

    final postcodeStatus =
        nipostZone != null ? 'resolved' : 'unresolved';

    // boundary_flag = true when the point is outside the assigned LGA zone.
    final bool boundaryFlag;
    if (assignedLgaCode != null) {
      boundaryFlag = lgaZone?.lgaCode != assignedLgaCode;
    } else {
      boundaryFlag = false;
    }

    return ReverseGeocodeResult(
      zone: lgaZone?.zoneName,
      lga: lgaZone?.zoneName,
      ward: wardZone?.zoneName,
      postcode: nipostZone?.postcode,
      postcodeStatus: postcodeStatus,
      boundaryFlag: boundaryFlag,
    );
  }

  /// Queries all zones of [zoneType] from the DB and returns the first one
  /// whose WKB polygon contains ([lon], [lat]).
  ///
  /// Returns `null` if no matching zone is found.
  Future<BoundaryZone?> _findContainingZone(
      double lon, double lat, String zoneType) async {
    final query = db.select(db.boundaryZones)
      ..where((t) => t.zoneType.equals(zoneType));
    final zones = await query.get();

    for (final zone in zones) {
      final polygon = WkbPolygon.fromBytes(zone.geometryWkb);
      if (polygon != null && polygon.contains(lon, lat)) {
        return zone;
      }
    }
    return null;
  }
}
