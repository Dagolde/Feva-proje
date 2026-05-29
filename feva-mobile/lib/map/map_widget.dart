import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:maplibre_gl/maplibre_gl.dart';

import '../core/connectivity_service.dart';

/// MapLibre map widget with offline MBTiles support, boundary layer overlay,
/// and live WMS/WFS fallback when online.
///
/// Requirements: 8.4, 8.6, 9.1, 9.2, 9.3
class MapLibreMapWidget extends StatefulWidget {
  final String? mbtilespath;
  final String? boundaryGeoJson;
  final List<Map<String, dynamic>> capturedPoints;
  final String? wmsUrl;
  final String? wfsUrl;
  final String? accessToken;
  final ConnectivityService? connectivityService;

  const MapLibreMapWidget({
    super.key,
    this.mbtilespath,
    this.boundaryGeoJson,
    this.capturedPoints = const [],
    this.wmsUrl,
    this.wfsUrl,
    this.accessToken,
    this.connectivityService,
  });

  @override
  State<MapLibreMapWidget> createState() => _MapLibreMapWidgetState();
}

class _MapLibreMapWidgetState extends State<MapLibreMapWidget> {
  MapLibreMapController? _controller;
  StreamSubscription<bool>? _connectivitySub;
  bool _isOnline = false;
  String? _currentStyle;

  @override
  void initState() {
    super.initState();
    _isOnline = widget.connectivityService?.isOnline ?? false;
    _currentStyle = _resolveStyle();
    _connectivitySub = widget.connectivityService?.onConnectivityChanged
        .listen(_onConnectivityChanged);
  }

  @override
  void dispose() {
    _connectivitySub?.cancel();
    super.dispose();
  }

  void _onConnectivityChanged(bool online) {
    if (!mounted) return;
    setState(() {
      _isOnline = online;
      _currentStyle = _resolveStyle();
    });
  }

  @override
  Widget build(BuildContext context) {
    return MapLibreMap(
      styleString: _currentStyle ?? _resolveStyle(),
      initialCameraPosition: const CameraPosition(
        target: LatLng(9.0820, 8.6753),
        zoom: 6,
      ),
      onMapCreated: _onMapCreated,
    );
  }

  String _resolveStyle() {
    if (_isOnline && widget.wmsUrl != null) return _buildWmsStyleJson(widget.wmsUrl!);
    if (widget.mbtilespath != null) return _buildOfflineStyleJson(widget.mbtilespath!);
    return _kFallbackStyle;
  }

  Future<void> _onMapCreated(MapLibreMapController controller) async {
    _controller = controller;
    if (_isOnline && widget.wfsUrl != null) {
      await _addWfsBoundaryLayer(widget.wfsUrl!, widget.accessToken);
    } else if (widget.boundaryGeoJson != null) {
      await _addBoundaryLayer(widget.boundaryGeoJson!);
    }
    if (widget.capturedPoints.isNotEmpty) {
      await _addCapturedPointsLayer(widget.capturedPoints);
    }
  }

  Future<void> _addWfsBoundaryLayer(String wfsUrl, String? token) async {
    final controller = _controller;
    if (controller == null) return;
    try {
      final geoJson = await _AuthHttpClient(token: token).get(Uri.parse(wfsUrl));
      await controller.addSource('wfs-boundary-source', GeojsonSourceProperties(data: geoJson));
      await controller.addFillLayer(
        'wfs-boundary-source',
        'wfs-boundary-fill',
        const FillLayerProperties(
          fillColor: '#0080ff',
          fillOpacity: 0.15,
          fillOutlineColor: '#0055cc',
        ),
      );
    } catch (_) {
      // Silent fallback to offline boundary (Requirement 9.3)
      if (widget.boundaryGeoJson != null) await _addBoundaryLayer(widget.boundaryGeoJson!);
    }
  }

  Future<void> _addBoundaryLayer(String geoJson) async {
    final controller = _controller;
    if (controller == null) return;
    await controller.addSource('boundary-source', GeojsonSourceProperties(data: geoJson));
    await controller.addFillLayer(
      'boundary-source',
      'boundary-fill',
      const FillLayerProperties(
        fillColor: '#0080ff',
        fillOpacity: 0.15,
        fillOutlineColor: '#0055cc',
      ),
    );
  }

  Future<void> _addCapturedPointsLayer(List<Map<String, dynamic>> points) async {
    final controller = _controller;
    if (controller == null) return;
    final geoJson = jsonEncode({
      'type': 'FeatureCollection',
      'features': points.map((p) => {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [p['lon'], p['lat']]},
        'properties': {'type': p['type'] ?? 'unknown'},
      }).toList(),
    });
    await controller.addSource('captured-points-source', GeojsonSourceProperties(data: geoJson));
    await controller.addCircleLayer(
      'captured-points-source',
      'captured-points-layer',
      const CircleLayerProperties(
        circleRadius: 6,
        circleColor: '#e63946',
        circleStrokeWidth: 1,
        circleStrokeColor: '#ffffff',
      ),
    );
  }

  String _buildOfflineStyleJson(String path) => jsonEncode({
    'version': 8,
    'sources': {'offline-tiles': {'type': 'raster', 'tiles': ['mbtiles://$path'], 'tileSize': 256}},
    'layers': [{'id': 'background', 'type': 'raster', 'source': 'offline-tiles'}],
  });

  String _buildWmsStyleJson(String url) => jsonEncode({
    'version': 8,
    'sources': {'wms-tiles': {'type': 'raster', 'tiles': [url], 'tileSize': 256}},
    'layers': [{'id': 'background', 'type': 'raster', 'source': 'wms-tiles'}],
  });
}

/// Minimal HTTP client that attaches a Bearer token to GET requests.
class _AuthHttpClient {
  final String? token;
  _AuthHttpClient({this.token});

  Future<String> get(Uri uri) async {
    final client = HttpClient();
    try {
      final request = await client.getUrl(uri);
      if (token != null) request.headers.set('Authorization', 'Bearer $token');
      final response = await request.close();
      return await response.transform(const Utf8Decoder()).join();
    } finally {
      client.close();
    }
  }
}

const _kFallbackStyle = '''
{
  "version": 8,
  "sources": {
    "osm": {
      "type": "raster",
      "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      "tileSize": 256,
      "attribution": "© OpenStreetMap contributors"
    }
  },
  "layers": [{"id": "osm-tiles", "type": "raster", "source": "osm"}]
}
''';
