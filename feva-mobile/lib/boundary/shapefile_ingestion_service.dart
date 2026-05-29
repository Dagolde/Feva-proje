import 'dart:convert';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';
import 'package:drift/drift.dart' show Value;
import 'package:http/http.dart' as http;

import '../database/app_database.dart';

/// Downloads GeoJSON boundary layers from the backend and upserts them into
/// the local [boundary_zones] SQLite table.
///
/// Requirements: 8.1, 8.5
class ShapefileIngestionService {
  final AppDatabase db;
  final String baseUrl;
  final String accessToken;

  ShapefileIngestionService({
    required this.db,
    required this.baseUrl,
    required this.accessToken,
  });

  /// Downloads and ingests a boundary layer from the backend.
  ///
  /// Steps:
  /// 1. GET `$baseUrl/api/v1/sync/shapefiles/$layer` with Bearer token.
  /// 2. Compute SHA-256 of the response body.
  /// 3. If a row with that checksum already exists in [boundary_zones], skip.
  /// 4. Parse the GeoJSON FeatureCollection.
  /// 5. Convert each Polygon feature to WKB and upsert into [boundary_zones].
  ///
  /// Returns the count of zones upserted, or 0 if skipped (checksum match).
  Future<int> ingestLayer(String layer) async {
    final uri = Uri.parse('$baseUrl/api/v1/sync/shapefiles/$layer');
    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $accessToken'},
    );

    if (response.statusCode != 200) {
      throw Exception(
          'Shapefile download failed: HTTP ${response.statusCode}');
    }

    // Compute SHA-256 checksum of the raw response body.
    final checksum = sha256.convert(response.bodyBytes).toString();

    // Skip if we already have this version stored.
    final existing = await (db.select(db.boundaryZones)
          ..where((t) => t.shapefileVersion.equals(checksum))
          ..limit(1))
        .getSingleOrNull();
    if (existing != null) return 0;

    // Parse GeoJSON FeatureCollection.
    final fc = jsonDecode(response.body) as Map<String, dynamic>;
    final features = fc['features'] as List<dynamic>;

    int count = 0;
    for (final feature in features) {
      final props = feature['properties'] as Map<String, dynamic>;
      final geometry = feature['geometry'] as Map<String, dynamic>;

      if (geometry['type'] != 'Polygon') continue;

      final coordinates = geometry['coordinates'] as List<dynamic>;
      final wkb = _polygonToWkb(coordinates);

      final companion = BoundaryZonesCompanion.insert(
        zoneId: (props['zone_id'] as String?) ?? '',
        zoneName: (props['zone_name'] as String?) ?? '',
        zoneType: (props['zone_type'] as String?) ?? 'admin',
        lgaCode: Value(props['lga_code'] as String?),
        wardCode: Value(props['ward_code'] as String?),
        postcode: Value(props['postcode'] as String?),
        geometryWkb: wkb,
        shapefileVersion: checksum,
        createdAt: Value(DateTime.now().millisecondsSinceEpoch),
      );

      await db.into(db.boundaryZones).insertOnConflictUpdate(companion);
      count++;
    }

    return count;
  }

  /// Converts a GeoJSON Polygon coordinate array to little-endian WKB bytes.
  ///
  /// [coordinates] is the full `geometry.coordinates` array, i.e.
  /// `[ [[lon, lat], ...], ... ]` where index 0 is the exterior ring.
  Uint8List _polygonToWkb(List<dynamic> coordinates) {
    // Use the exterior ring only (index 0).
    final exteriorRing = coordinates[0] as List<dynamic>;
    final numPoints = exteriorRing.length;

    // WKB layout (little-endian):
    //   1 byte  — byte order (0x01)
    //   4 bytes — geometry type (3 = Polygon)
    //   4 bytes — number of rings (1)
    //   4 bytes — number of points in ring
    //   numPoints × 16 bytes — (float64 lon, float64 lat) pairs
    final byteLength = 1 + 4 + 4 + 4 + numPoints * 16;
    final buffer = ByteData(byteLength);
    int offset = 0;

    // Byte order: little-endian
    buffer.setUint8(offset, 0x01);
    offset += 1;

    // Geometry type: Polygon = 3
    buffer.setUint32(offset, 3, Endian.little);
    offset += 4;

    // Number of rings: 1
    buffer.setUint32(offset, 1, Endian.little);
    offset += 4;

    // Number of points
    buffer.setUint32(offset, numPoints, Endian.little);
    offset += 4;

    // Coordinate pairs
    for (final point in exteriorRing) {
      final coords = point as List<dynamic>;
      final lon = (coords[0] as num).toDouble();
      final lat = (coords[1] as num).toDouble();
      buffer.setFloat64(offset, lon, Endian.little);
      offset += 8;
      buffer.setFloat64(offset, lat, Endian.little);
      offset += 8;
    }

    return buffer.buffer.asUint8List();
  }
}
