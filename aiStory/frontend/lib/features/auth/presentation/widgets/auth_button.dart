import 'package:flutter/material.dart';

/// Custom button for authentication screens
class AuthButton extends StatelessWidget {
  /// Button text
  final String text;
  
  /// Button onPressed callback
  final VoidCallback onPressed;
  
  /// Loading state
  final bool isLoading;
  
  /// Button color
  final Color? color;
  
  /// Text color
  final Color? textColor;

  /// Creates a new [AuthButton] instance
  const AuthButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isLoading = false,
    this.color,
    this.textColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: color ?? theme.colorScheme.primary,
          foregroundColor: textColor ?? theme.colorScheme.onPrimary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          elevation: 2,
        ),
        child: isLoading
            ? SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 3,
                  color: textColor ?? theme.colorScheme.onPrimary,
                ),
              )
            : Text(
                text,
                style: theme.textTheme.titleMedium?.copyWith(
                  color: textColor ?? theme.colorScheme.onPrimary,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }
}