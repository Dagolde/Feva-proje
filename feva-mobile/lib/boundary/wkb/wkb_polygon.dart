import 'dart:typed_data';

/// Parses a WKB (Well-Known Binary) Polygon and provides a ray-casting
/// point-in-polygon test.
///
/// Supports ISO WKB geometry type 3 (Polygon) in both little-endian and
/// big-endian byte order.
class WkbPolygon {
  /// Exterior ring as a list of [lon, lat] pairs.
  final List<List<double>> ring;

  WkbPolygon(this.ring);

  /// Parses a WKB BLOB into a [WkbPolygon].
  ///
  /// Returns `null` if:
  /// - [bytes] is too short to be a valid WKB Polygon
  /// - The geometry type is not 3 (Polygon)
  /// - The polygon has no rings or no points
  static WkbPolygon? fromBytes(Uint8List bytes) {
    if (bytes.length < 9) return null;

    // Byte 0: byte order marker
    final byteOrder = bytes[0];
    final isLittleEndian = byteOrder == 0x01;

    final bd = ByteData.sublistView(bytes);

    int readUint32(int offset) {
      return isLittleEndian
          ? bd.getUint32(offset, Endian.little)
          : bd.getUint32(offset, Endian.big);
    }

    double readFloat64(int offset) {
      return isLittleEndian
          ? bd.getFloat64(offset, Endian.little)
          : bd.getFloat64(offset, Endian.big);
    }

    // Bytes 1–4: geometry type (must be 3 = Polygon)
    final geomType = readUint32(1);
    if (geomType != 3) return null;

    // Bytes 5–8: number of rings
    final numRings = readUint32(5);
    if (numRings == 0) return null;

    // Bytes 9–12: number of points in the first (exterior) ring
    final numPoints = readUint32(9);
    if (numPoints == 0) return null;

    // Minimum required length: 13 header bytes + numPoints * 16 bytes (2 × float64)
    final requiredLength = 13 + numPoints * 16;
    if (bytes.length < requiredLength) return null;

    final ring = <List<double>>[];
    int offset = 13;
    for (int i = 0; i < numPoints; i++) {
      final lon = readFloat64(offset);
      final lat = readFloat64(offset + 8);
      ring.add([lon, lat]);
      offset += 16;
    }

    return WkbPolygon(ring);
  }

  /// Ray-casting point-in-polygon test.
  ///
  /// Returns `true` if ([lon], [lat]) is inside this polygon's exterior ring.
  bool contains(double lon, double lat) {
    bool inside = false;
    final n = ring.length;
    for (int i = 0, j = n - 1; i < n; j = i++) {
      final xi = ring[i][0], yi = ring[i][1];
      final xj = ring[j][0], yj = ring[j][1];
      if (((yi > lat) != (yj > lat)) &&
          (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi)) {
        inside = !inside;
      }
    }
    return inside;
  }
}
