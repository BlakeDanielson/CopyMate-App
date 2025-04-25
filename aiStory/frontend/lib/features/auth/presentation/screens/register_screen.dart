import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_button.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_error_message.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_text_field.dart';
import 'package:go_router/go_router.dart';

/// Registration screen for new users
class RegisterScreen extends ConsumerStatefulWidget {
  /// Route name for the registration screen
  static const routeName = '/register';

  /// Creates a new [RegisterScreen] instance
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';
  bool _passwordVisible = false;

  @override
  void initState() {
    super.initState();
    // Listen for auth state changes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.listenManual(authNotifierProvider, (previous, next) {
        if (next is AuthenticatedState) {
          logger.i('User registered and authenticated, redirecting to home');
          context.go('/home');
        } else if (next is ErrorAuthState) {
          setState(() {
            _isLoading = false;
            _errorMessage = next.message;
          });
        } else if (next is LoadingAuthState) {
          setState(() {
            _isLoading = true;
            _errorMessage = '';
          });
        } else if (next is UnauthenticatedState) {
          setState(() {
            _isLoading = false;
          });
        }
      });
    });
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    super.dispose();
  }

  String? _validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter a username';
    }
    if (value.length < 3) {
      return 'Username must be at least 3 characters';
    }
    return null;
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

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter a password';
    }
    if (value.length < 6) {
      return 'Password must be at least 6 characters';
    }
    return null;
  }

  void _togglePasswordVisibility() {
    setState(() {
      _passwordVisible = !_passwordVisible;
    });
  }

  Future<void> _register() async {
    // Clear any previous errors
    setState(() {
      _errorMessage = '';
    });

    // Validate form
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    final username = _usernameController.text.trim();
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    final firstName = _firstNameController.text.trim();
    final lastName = _lastNameController.text.trim();

    try {
      await ref.read(authNotifierProvider.notifier).register(
        username: username,
        email: email,
        password: password,
        firstName: firstName.isNotEmpty ? firstName : null,
        lastName: lastName.isNotEmpty ? lastName : null,
      );
    } catch (e) {
      setState(() {
        _errorMessage = 'Registration failed: ${e.toString()}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Account'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // App logo or branding
                Icon(
                  Icons.auto_stories_rounded,
                  size: 64,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 8),
                Text(
                  'Join AI Story Creator',
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 32),
                
                // Error message
                if (_errorMessage.isNotEmpty) ...[
                  AuthErrorMessage(message: _errorMessage),
                  const SizedBox(height: 24),
                ],
                
                // Registration form
                Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Username field
                      AuthTextField(
                        controller: _usernameController,
                        label: 'Username',
                        hintText: 'Choose a unique username',
                        prefixIcon: Icons.person_outline,
                        validator: _validateUsername,
                        autoValidate: true,
                      ),
                      const SizedBox(height: 16),
                      
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
                      const SizedBox(height: 16),
                      
                      // Password field
                      AuthTextField(
                        controller: _passwordController,
                        label: 'Password',
                        hintText: 'Create a password',
                        prefixIcon: Icons.lock_outline,
                        isPassword: !_passwordVisible,
                        validator: _validatePassword,
                        autoValidate: true,
                      ),
                      const SizedBox(height: 16),
                      
                      // First name field
                      AuthTextField(
                        controller: _firstNameController,
                        label: 'First Name (Optional)',
                        hintText: 'Enter your first name',
                        prefixIcon: Icons.badge_outlined,
                      ),
                      const SizedBox(height: 16),
                      
                      // Last name field
                      AuthTextField(
                        controller: _lastNameController,
                        label: 'Last Name (Optional)',
                        hintText: 'Enter your last name',
                        prefixIcon: Icons.badge_outlined,
                      ),
                      const SizedBox(height: 24),
                      
                      // Register button
                      AuthButton(
                        text: 'Create Account',
                        onPressed: _register,
                        isLoading: _isLoading,
                      ),
                      const SizedBox(height: 16),
                      
                      // Test mode button
                      OutlinedButton(
                        onPressed: () {
                          ref.read(authNotifierProvider.notifier).enterTestMode();
                        },
                        style: OutlinedButton.styleFrom(
                          minimumSize: const Size(double.infinity, 48),
                          side: BorderSide(color: theme.colorScheme.primary),
                        ),
                        child: Text(
                          'Test without Authentication',
                          style: TextStyle(color: theme.colorScheme.primary),
                        ),
                      ),
                      const SizedBox(height: 24),
                      
                      // Login link
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Already have an account?',
                            style: theme.textTheme.bodyMedium,
                          ),
                          TextButton(
                            onPressed: () {
                              context.go('/login');
                            },
                            child: Text(
                              'Login',
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: theme.colorScheme.primary,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}