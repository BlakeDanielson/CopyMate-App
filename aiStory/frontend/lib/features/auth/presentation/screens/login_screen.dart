import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_button.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_error_message.dart';
import 'package:ai_story/features/auth/presentation/widgets/auth_text_field.dart';
import 'package:go_router/go_router.dart';

/// Login screen for user authentication
class LoginScreen extends ConsumerStatefulWidget {
  /// Route name for the login screen
  static const routeName = '/login';

  /// Creates a new [LoginScreen] instance
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
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
          logger.i('User authenticated, redirecting to home');
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
    _passwordController.dispose();
    super.dispose();
  }

  String? _validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your username or email';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your password';
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

  Future<void> _login() async {
    // Clear any previous errors
    setState(() {
      _errorMessage = '';
    });

    // Validate form
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    try {
      await ref.read(authNotifierProvider.notifier).login(
        username: username,
        password: password,
      );
    } catch (e) {
      setState(() {
        _errorMessage = 'Login failed: ${e.toString()}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
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
                  size: 96,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 16),
                Text(
                  'AI Story Creator',
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 48),
                
                // Error message
                if (_errorMessage.isNotEmpty) ...[
                  AuthErrorMessage(message: _errorMessage),
                  const SizedBox(height: 24),
                ],
                
                // Login form
                Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Username/Email field
                      AuthTextField(
                        controller: _usernameController,
                        label: 'Username or Email',
                        hintText: 'Enter your username or email',
                        prefixIcon: Icons.person_outline,
                        keyboardType: TextInputType.emailAddress,
                        validator: _validateUsername,
                        autoValidate: true,
                      ),
                      const SizedBox(height: 16),
                      
                      // Password field
                      AuthTextField(
                        controller: _passwordController,
                        label: 'Password',
                        hintText: 'Enter your password',
                        prefixIcon: Icons.lock_outline,
                        isPassword: true,
                        validator: _validatePassword,
                        autoValidate: true,
                      ),
                      const SizedBox(height: 8),
                      
                      // Forgot password link
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: () {
                            context.push('/forgot-password');
                          },
                          child: Text(
                            'Forgot Password?',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: theme.colorScheme.primary,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      
                      // Login button
                      AuthButton(
                        text: 'Login',
                        onPressed: _login,
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
                      
                      // Register link
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Don\'t have an account?',
                            style: theme.textTheme.bodyMedium,
                          ),
                          TextButton(
                            onPressed: () {
                              context.push('/register');
                            },
                            child: Text(
                              'Register',
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