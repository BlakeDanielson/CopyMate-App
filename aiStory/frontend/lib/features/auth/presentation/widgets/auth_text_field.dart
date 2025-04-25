import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Custom text field for authentication screens
class AuthTextField extends StatefulWidget {
  /// Controller for the text field
  final TextEditingController controller;
  
  /// Label for the text field
  final String label;
  
  /// Hint text 
  final String? hintText;
  
  /// Error text
  final String? errorText;
  
  /// Leading icon
  final IconData? prefixIcon;
  
  /// Whether the field is for passwords (obscured text)
  final bool isPassword;
  
  /// Keyboard type
  final TextInputType? keyboardType;
  
  /// Text input formatters
  final List<TextInputFormatter>? inputFormatters;
  
  /// Text field focus node
  final FocusNode? focusNode;
  
  /// Callback for when the text field is submitted
  final Function(String)? onSubmitted;
  
  /// Maximum lines
  final int? maxLines;
  
  /// Minimum lines
  final int? minLines;
  
  /// Validator function
  final String? Function(String?)? validator;
  
  /// Whether the text field auto-validates
  final bool autoValidate;

  /// Creates a new [AuthTextField] instance
  const AuthTextField({
    super.key,
    required this.controller,
    required this.label,
    this.hintText,
    this.errorText,
    this.prefixIcon,
    this.isPassword = false,
    this.keyboardType,
    this.inputFormatters,
    this.focusNode,
    this.onSubmitted,
    this.maxLines = 1,
    this.minLines,
    this.validator,
    this.autoValidate = false,
  });

  @override
  State<AuthTextField> createState() => _AuthTextFieldState();
}

class _AuthTextFieldState extends State<AuthTextField> {
  late bool _obscureText;
  String? _errorText;
  bool _touched = false;

  @override
  void initState() {
    super.initState();
    _obscureText = widget.isPassword;
    _errorText = widget.errorText;
  }

  @override
  void didUpdateWidget(AuthTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.errorText != widget.errorText) {
      _errorText = widget.errorText;
    }
  }

  void _validate() {
    if (widget.validator != null && widget.autoValidate) {
      setState(() {
        _touched = true;
        _errorText = widget.validator!(widget.controller.text);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.label,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: widget.controller,
          focusNode: widget.focusNode,
          obscureText: _obscureText,
          keyboardType: widget.keyboardType,
          inputFormatters: widget.inputFormatters,
          autovalidateMode: widget.autoValidate
              ? AutovalidateMode.onUserInteraction
              : AutovalidateMode.disabled,
          validator: widget.validator,
          maxLines: widget.isPassword ? 1 : widget.maxLines,
          minLines: widget.minLines,
          onFieldSubmitted: widget.onSubmitted,
          onChanged: (_) => _validate(),
          decoration: InputDecoration(
            hintText: widget.hintText,
            errorText: _touched ? _errorText : null,
            prefixIcon: widget.prefixIcon != null
                ? Icon(widget.prefixIcon, size: 22)
                : null,
            suffixIcon: widget.isPassword
                ? IconButton(
                    icon: Icon(
                      _obscureText ? Icons.visibility : Icons.visibility_off,
                      size: 22,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscureText = !_obscureText;
                      });
                    },
                  )
                : null,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: theme.colorScheme.outline,
                width: 1,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: theme.colorScheme.outline,
                width: 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: theme.colorScheme.primary,
                width: 2,
              ),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: theme.colorScheme.error,
                width: 1,
              ),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: theme.colorScheme.error,
                width: 2,
              ),
            ),
            filled: true,
            fillColor: theme.colorScheme.surface,
          ),
        ),
      ],
    );
  }
}