import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_notifier.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';
import 'package:ai_story/features/auth/presentation/screens/login_screen.dart';
import 'package:ai_story/features/auth/domain/repositories/auth_repository.dart';

@GenerateNiceMocks([MockSpec<AuthNotifier>(), MockSpec<GoRouter>()])
import 'login_screen_test_mode_test.mocks.dart';

void main() {
  group('LoginScreen Test Mode Tests', () {
    late MockAuthNotifier mockAuthNotifier;
    late ProviderContainer container;
    late GoRouter mockRouter;

    setUp(() {
      mockAuthNotifier = MockAuthNotifier();
      mockRouter = MockGoRouter();
      
      container = ProviderContainer(
        overrides: [
          authNotifierProvider.overrideWith((ref) => mockAuthNotifier),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    testWidgets('should display "Test without Authentication" button', (WidgetTester tester) async {
      // ARRANGE
      when(mockAuthNotifier.state).thenReturn(const AuthState.unauthenticated());
      
      // ACT
      await tester.pumpWidget(
        ProviderScope(
          parent: container,
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );
      
      // ASSERT
      expect(find.text('Test without Authentication'), findsOneWidget);
      expect(find.byType(OutlinedButton), findsOneWidget);
    });

    testWidgets('tapping "Test without Authentication" button should call enterTestMode', (WidgetTester tester) async {
      // ARRANGE
      when(mockAuthNotifier.state).thenReturn(const AuthState.unauthenticated());
      
      // ACT
      await tester.pumpWidget(
        ProviderScope(
          parent: container,
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );
      
      // Find and tap the test mode button
      await tester.tap(find.text('Test without Authentication'));
      await tester.pump();
      
      // ASSERT
      verify(mockAuthNotifier.enterTestMode()).called(1);
    });

    testWidgets('should navigate to home screen after entering test mode', (WidgetTester tester) async {
      // ARRANGE
      final mockUser = MockUserData.getMockUser();
      
      // First return unauthenticated, then switch to test mode after button press
      when(mockAuthNotifier.state).thenReturn(const AuthState.unauthenticated());
      
      // Mock the state to change to test mode after enterTestMode is called
      when(mockAuthNotifier.enterTestMode()).thenAnswer((_) async {
        when(mockAuthNotifier.state).thenReturn(AuthState.testMode(user: mockUser));
      });
      
      // Builder to create a widget with GoRouter access
      Widget createWidgetUnderTest() {
        return ProviderScope(
          parent: container,
          child: MaterialApp.router(
            routerConfig: mockRouter,
            builder: (context, child) {
              return child!;
            },
          ),
        );
      }
      
      // ACT
      await tester.pumpWidget(createWidgetUnderTest());
      
      // ASSERT - Verify navigation occurs when state changes to test mode
      // This test will be implemented once we set up the proper navigation mocking
      // with GoRouter, which is more complex than simple navigation
    });
  });
}