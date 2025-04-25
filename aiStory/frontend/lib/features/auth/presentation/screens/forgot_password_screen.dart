import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_button.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_error_message.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_text_field.dart';
import 'package:go_router/go_router.dart';

/// Password reset request screen
class ForgotPasswordScreen extends ConsumerStatefulWidget {
  /// Route name for the forgot password screen
  static const routeName = '/forgot-password';

  /// Creates a new [ForgotPasswordScreen] instance
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';
  bool _requestSent = false;

  @override
  void initState() {
    super.initState();
    // Listen for auth state changes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.listenManual(authNotifierProvider, (previous, next) {
        if (next is LoadingAuthState) {
          setState(() {
            _isLoading = true;
            _errorMessage = '';
          });
        } else if (next is ErrorAuthState) {
          setState(() {
            _isLoading = false;
            _errorMessage = next.message;
          });
        } else if (next is UnauthenticatedState) {
          setState(() {
            _isLoading = false;
            // If we were loading before, and now we're unauthenticated,
            // the password reset request likely succeeded
            if (previous is LoadingAuthState) {
              _requestSent = true;
            }
          });
        }
      });
    });
  }

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your email';
    }
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) {
      return 'Please enter a valid email address';
    }
    return null;
  }

  Future<void> _requestPasswordReset() async {
    // Clear any previous errors
    setState(() {
      _errorMessage = '';
    });

    // Validate form
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    final email = _emailController.text.trim();

    try {
      await ref.read(authNotifierProvider.notifier).requestPasswordReset(email);
      setState(() {
        _requestSent = true;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Password reset request failed: ${e.toString()}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Forgot Password'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: _requestSent 
                ? _buildSuccessContent(theme)
                : _buildRequestForm(theme),
          ),
        ),
      ),
    );
  }

  Widget _buildSuccessContent(ThemeData theme) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Icon(
          Icons.check_circle_outline,
          size: 80,
          color: theme.colorScheme.primary,
        ),
        const SizedBox(height: 24),
        Text(
          'Reset Email Sent',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.primary,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'We have sent password reset instructions to your email address. Please check your inbox.',
          style: theme.textTheme.bodyLarge,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),
        AuthButton(
          text: 'Back to Login',
          onPressed: () => context.go('/login'),
        ),
      ],
    );
  }

  Widget _buildRequestForm(ThemeData theme) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Icon(
          Icons.lock_reset_outlined,
          size: 80,
          color: theme.colorScheme.primary,
        ),
        const SizedBox(height: 16),
        Text(
          'Forgot Password?',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.primary,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Enter your email address and we\'ll send you instructions to reset your password.',
          style: theme.textTheme.bodyLarge,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),
        
        // Error message
        if (_errorMessage.isNotEmpty) ...[
          AuthErrorMessage(message: _errorMessage),
          const SizedBox(height: 24),
        ],
        
        // Form
        Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Email field
              AuthTextField(
                controller: _emailController,
                label: 'Email Address',
                hintText: 'Enter your email address',
                prefixIcon: Icons.email_outlined,
                keyboardType: TextInputType.emailAddress,
                validator: _validateEmail,
                autoValidate: true,
              ),
              const SizedBox(height: 24),
              
              // Submit button
              AuthButton(
                text: 'Send Reset Instructions',
                onPressed: _requestPasswordReset,
                isLoading: _isLoading,
              ),
              const SizedBox(height: 16),
              
              // Back to login link
              Align(
                alignment: Alignment.center,
                child: TextButton(
                  onPressed: () {
                    context.go('/login');
                  },
                  child: Text(
                    'Back to Login',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}