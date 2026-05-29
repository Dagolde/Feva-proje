/// Result of a reverse geocode lookup against boundary zones.
class ReverseGeocodeResult {
  /// Zone name from the matching 'admin' or 'lga' zone, if any.
  final String? zone;

  /// LGA name from the matching 'lga' zone, if any.
  final String? lga;

  /// Ward name from the matching 'ward' zone, if any.
  final String? ward;

  /// Postcode from the matching 'nipost' zone, if any.
  final String? postcode;

  /// 'resolved' if a NIPOST polygon matched, 'unresolved' otherwise.
  final String postcodeStatus;

  /// true = point falls outside the Enumerator's assigned LGA zone.
  final bool boundaryFlag;

  const ReverseGeocodeResult({
    this.zone,
    this.lga,
    this.ward,
    this.postcode,
    required this.postcodeStatus,
    required this.boundaryFlag,
  });
}
