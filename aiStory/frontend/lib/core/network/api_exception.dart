import 'dart:io';

import 'package:dio/dio.dart';

/// Exception class for API errors
class ApiException implements Exception {
  /// HTTP status code
  final int statusCode;
  
  /// Error message
  final String message;
  
  /// Original error object
  final dynamic error;

  /// Creates a new ApiException
  ApiException({
    required this.message,
    this.statusCode = 500,
    this.error,
  });

  /// Create an ApiException from a DioException
  factory ApiException.fromDioError(DioException e) {
    String message;
    int statusCode = 500;

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        message = 'Connection timeout';
        break;
      case DioExceptionType.sendTimeout:
        message = 'Send timeout';
        break;
      case DioExceptionType.receiveTimeout:
        message = 'Receive timeout';
        break;
      case DioExceptionType.badCertificate:
        message = 'Bad certificate';
        break;
      case DioExceptionType.badResponse:
        message = _handleErrorResponse(e.response);
        statusCode = e.response?.statusCode ?? 500;
        break;
      case DioExceptionType.cancel:
        message = 'Request canceled';
        break;
      case DioExceptionType.connectionError:
        message = 'Connection error';
        break;
      case DioExceptionType.unknown:
        if (e.error is SocketException) {
          message = 'No internet connection';
        } else {
          message = 'Unexpected error: ${e.error}';
        }
        break;
    }

    return ApiException(
      message: message,
      statusCode: statusCode,
      error: e,
    );
  }

  /// Formats an error message from response data
  static String _handleErrorResponse(Response? response) {
    if (response == null) {
      return 'Unknown error occurred';
    }

    try {
      if (response.data != null && response.data is Map) {
        // Try to get error message from response
        if (response.data['detail'] != null) {
          return response.data['detail'].toString();
        } else if (response.data['message'] != null) {
          return response.data['message'].toString();
        } else if (response.data['error'] != null) {
          return response.data['error'].toString();
        }
      }
      
      // Fallback to status message
      return 'Error ${response.statusCode}: ${response.statusMessage}';
    } catch (e) {
      return 'Error ${response.statusCode}';
    }
  }

  @override
  String toString() => message;
}