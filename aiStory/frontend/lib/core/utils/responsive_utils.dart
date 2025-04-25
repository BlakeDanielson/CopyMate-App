import 'package:flutter/material.dart';

/// Utility class for responsive design
class ResponsiveUtils {
  static const double _mobileBreakpoint = 600;
  static const double _tabletBreakpoint = 900;
  static const double _desktopBreakpoint = 1200;
  
  /// Private constructor for singleton
  ResponsiveUtils._();
  
  /// Check if current screen size is mobile
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < _mobileBreakpoint;
  }
  
  /// Check if current screen size is tablet
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= _mobileBreakpoint && width < _desktopBreakpoint;
  }
  
  /// Check if current screen size is desktop
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= _desktopBreakpoint;
  }
  
  /// Get the current device type
  static DeviceType getDeviceType(BuildContext context) {
    if (isMobile(context)) {
      return DeviceType.mobile;
    } else if (isTablet(context)) {
      return DeviceType.tablet;
    } else {
      return DeviceType.desktop;
    }
  }
  
  /// Get a value based on the screen size
  static T responsiveValue<T>({
    required BuildContext context,
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.desktop:
        return desktop ?? tablet ?? mobile;
      case DeviceType.tablet:
        return tablet ?? mobile;
      case DeviceType.mobile:
        return mobile;
    }
  }
  
  /// Get a padding value based on the screen size
  static EdgeInsets responsivePadding(BuildContext context) {
    return responsiveValue(
      context: context,
      mobile: const EdgeInsets.all(16),
      tablet: const EdgeInsets.all(24),
      desktop: const EdgeInsets.all(32),
    );
  }
  
  /// Get a responsive width for containers based on screen size
  static double responsiveWidth(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width >= _desktopBreakpoint) {
      // Desktop: 75% of screen width up to max 1200px
      return width * 0.75 > 1200 ? 1200 : width * 0.75;
    } else if (width >= _tabletBreakpoint) {
      // Tablet: 85% of screen width
      return width * 0.85;
    } else {
      // Mobile: 95% of screen width
      return width * 0.95;
    }
  }
  
  /// Get a responsive number of grid columns based on screen size
  static int responsiveGridCount(BuildContext context) {
    return responsiveValue(
      context: context,
      mobile: 1,
      tablet: 2,
      desktop: 3,
    );
  }
  
  /// Get a responsive font size based on screen size
  static double responsiveFontSize(
    BuildContext context, {
    required double baseFontSize,
  }) {
    return responsiveValue(
      context: context,
      mobile: baseFontSize,
      tablet: baseFontSize * 1.1,
      desktop: baseFontSize * 1.2,
    );
  }
}

/// Enum for device types
enum DeviceType {
  mobile,
  tablet,
  desktop,
}

/// Extension on BuildContext for responsive utilities
extension ResponsiveContext on BuildContext {
  /// Check if current screen size is mobile
  bool get isMobile => ResponsiveUtils.isMobile(this);
  
  /// Check if current screen size is tablet
  bool get isTablet => ResponsiveUtils.isTablet(this);
  
  /// Check if current screen size is desktop
  bool get isDesktop => ResponsiveUtils.isDesktop(this);
  
  /// Get the current device type
  DeviceType get deviceType => ResponsiveUtils.getDeviceType(this);
  
  /// Get a responsive padding value
  EdgeInsets get responsivePadding => ResponsiveUtils.responsivePadding(this);
  
  /// Get a responsive width
  double get responsiveWidth => ResponsiveUtils.responsiveWidth(this);
  
  /// Get a responsive number of grid columns
  int get responsiveGridCount => ResponsiveUtils.responsiveGridCount(this);
}