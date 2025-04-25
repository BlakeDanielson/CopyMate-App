import 'package:flutter/material.dart';

/// Widget for displaying error messages on auth screens
class AuthErrorMessage extends StatelessWidget {
  /// Error message to display
  final String message;
  
  /// Whether to show the error
  final bool show;
  
  /// Optional icon
  final IconData icon;
  
  /// Creates a new [AuthErrorMessage] instance
  const AuthErrorMessage({
    super.key,
    required this.message,
    this.show = true,
    this.icon = Icons.error_outline,
  });

  @override
  Widget build(BuildContext context) {
    if (!show || message.isEmpty) {
      return const SizedBox.shrink();
    }
    
    final theme = Theme.of(context);
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 12,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.errorContainer.withOpacity(0.6),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: theme.colorScheme.error,
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            color: theme.colorScheme.error,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onErrorContainer,
              ),
            ),
          ),
        ],
      ),
    );
  }
}