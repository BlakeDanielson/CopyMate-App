import 'package:json_annotation/json_annotation.dart';

import '../../domain/models/photo_status.dart';

part 'photo_list_filters.g.dart';

/// Filters for retrieving photos
@JsonSerializable()
class PhotoListFilters {
  /// Filter by photo status
  final PhotoStatus? status;
  
  /// Filter by start date
  @JsonKey(name: 'from_date')
  final String? fromDate;
  
  /// Filter by end date
  @JsonKey(name: 'to_date')
  final String? toDate;
  
  /// Filter by tags
  final List<String>? tags;
  
  /// Page number (1-based)
  final int page;
  
  /// Number of items per page
  @JsonKey(name: 'page_size')
  final int pageSize;

  /// Creates a new PhotoListFilters
  const PhotoListFilters({
    this.status,
    this.fromDate,
    this.toDate,
    this.tags,
    this.page = 1,
    this.pageSize = 20,
  });

  /// Creates a PhotoListFilters from JSON
  factory PhotoListFilters.fromJson(Map<String, dynamic> json) => 
      _$PhotoListFiltersFromJson(json);

  /// Converts this PhotoListFilters to JSON
  Map<String, dynamic> toJson() => _$PhotoListFiltersToJson(this);
  
  /// Converts this filter to query parameters
  Map<String, String> toQueryParameters() {
    final Map<String, String> params = {};
    
    if (status != null) {
      params['status'] = status!.name;
    }
    
    if (fromDate != null) {
      params['from_date'] = fromDate!;
    }
    
    if (toDate != null) {
      params['to_date'] = toDate!;
    }
    
    if (tags != null && tags!.isNotEmpty) {
      params['tags'] = tags!.join(',');
    }
    
    params['page'] = page.toString();
    params['page_size'] = pageSize.toString();
    
    return params;
  }
}