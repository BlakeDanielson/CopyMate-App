/// Enum representing the status of a photo in the system
enum PhotoStatus {
  /// Photo is pending upload or processing
  pending,

  /// Photo has been uploaded but not yet processed
  uploaded,

  /// Photo is currently being processed
  processing,

  /// Photo processing has completed successfully
  completed,

  /// Photo processing has failed
  failed;

  /// Convert a string to a PhotoStatus enum value
  static PhotoStatus fromString(String status) {
    return PhotoStatus.values.firstWhere(
      (e) => e.name == status.toLowerCase(),
      orElse: () => PhotoStatus.pending,
    );
  }

  /// Convert a PhotoStatus enum value to a string
  String toJson() => name;

  /// Create a PhotoStatus from JSON
  static PhotoStatus fromJson(String json) => fromString(json);
}