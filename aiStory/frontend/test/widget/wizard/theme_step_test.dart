import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ai_story/features/wizard/domain/models/wizard_state.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_state_notifier.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';
import 'package:ai_story/features/wizard/presentation/widgets/theme_step.dart';

// Create a mock class for WizardStateNotifier
class MockWizardStateNotifier extends Mock implements WizardStateNotifier {}

void main() {
  group('ThemeStep Widget Tests', () {
    late MockWizardStateNotifier mockWizardStateNotifier;
    late StateNotifierProvider<WizardStateNotifier, WizardState> mockWizardProvider;

    setUp(() {
      mockWizardStateNotifier = MockWizardStateNotifier();
      mockWizardProvider = StateNotifierProvider<WizardStateNotifier, WizardState>((ref) {
        return mockWizardStateNotifier;
      });

      // Set up default state with empty theme
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 2, theme: '')
      );
    });

    testWidgets('ThemeStep renders with theme options', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: ThemeStep(),
            ),
          ),
        ),
      );

      // Assert - Verify the theme options are displayed
      expect(find.text('Choose a theme for your story'), findsOneWidget);
      
      // Should display at least 3 theme options
      expect(find.byType(Card), findsAtLeastNWidgets(3));
      
      // Check for some common theme options
      expect(find.text('Adventure'), findsOneWidget);
      expect(find.text('Fantasy'), findsOneWidget);
      expect(find.text('Space'), findsOneWidget);
    });

    testWidgets('Selecting a theme updates the WizardState', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: ThemeStep(),
            ),
          ),
        ),
      );

      // Find the Adventure theme card
      final adventureCard = find.ancestor(
        of: find.text('Adventure'),
        matching: find.byType(Card),
      );
      
      // Act - Tap the adventure theme
      await tester.tap(adventureCard);
      await tester.pumpAndSettle();
      
      // Verify updateTheme was called with the right argument
      verify(() => mockWizardStateNotifier.updateTheme('Adventure')).called(1);
    });

    testWidgets('Selected theme is highlighted', (WidgetTester tester) async {
      // Arrange - Set up state with a pre-selected theme
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 2, theme: 'Fantasy')
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: ThemeStep(),
            ),
          ),
        ),
      );

      // Find the Fantasy theme card
      final fantasyCard = find.ancestor(
        of: find.text('Fantasy'),
        matching: find.byType(Card),
      );
      
      // Extract the Card widget to check its properties
      final cardWidget = tester.widget<Card>(fantasyCard);
      
      // The selected card should have a different color or elevation
      expect(cardWidget.elevation, greaterThan(1.0));
    });
  });
}