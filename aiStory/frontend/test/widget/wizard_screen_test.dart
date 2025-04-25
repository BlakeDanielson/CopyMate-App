import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ai_story/features/wizard/presentation/screens/wizard_screen.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_state_notifier.dart';
import 'package:ai_story/features/wizard/domain/models/wizard_state.dart';
import 'package:ai_story/features/wizard/presentation/widgets/name_step.dart';
import 'package:ai_story/features/wizard/presentation/widgets/age_step.dart';
import 'package:ai_story/features/wizard/presentation/widgets/theme_step.dart';

// Create mock for WizardStateNotifier
class MockWizardStateNotifier extends Mock implements WizardStateNotifier {}

void main() {
  group('WizardScreen Widget Tests', () {
    late MockWizardStateNotifier mockWizardStateNotifier;
    late StateNotifierProvider<WizardStateNotifier, WizardState> mockWizardProvider;
    
    setUp(() {
      // Create a mock wizard provider to control the state during tests
      mockWizardStateNotifier = MockWizardStateNotifier();
      mockWizardProvider = StateNotifierProvider<WizardStateNotifier, WizardState>((ref) {
        return mockWizardStateNotifier;
      });

      // Set up default state
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 0)
      );
      
      // Set up canGoNext and canGoPrevious methods
      when(() => mockWizardStateNotifier.canGoNext()).thenReturn(true);
      when(() => mockWizardStateNotifier.canGoPrevious()).thenReturn(false);
    });
    
    testWidgets('WizardScreen should display stepper with steps', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Assert - verify the structure is present
      expect(find.byType(Stepper), findsOneWidget);
      
      // Verify the stepper has steps (at least the initial one)
      final stepperWidget = tester.widget<Stepper>(find.byType(Stepper));
      expect(stepperWidget.steps.isNotEmpty, true);
      
      // Verify the app bar has the correct title
      expect(find.text('Create Your Story'), findsOneWidget);
    });
    
    testWidgets('WizardScreen should display the initial step content', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Assert - verify that initial step content is visible
      expect(find.text('Character Name'), findsOneWidget);
      // Verify the NameStep widget is present
      expect(find.byType(NameStep), findsOneWidget);
    });
    
    testWidgets('Next button should be enabled at first step and Back button disabled', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Assert - verify next button is enabled and back is disabled
      expect(find.text('Next'), findsOneWidget);
      expect(find.text('Back'), findsOneWidget);
      
      // The next button should be enabled at the first step
      final nextButton = tester.widget<ElevatedButton>(
        find.ancestor(
          of: find.text('Next'),
          matching: find.byType(ElevatedButton),
        ),
      );
      expect(nextButton.onPressed != null, true);
      
      // The back button should be disabled at the first step
      final backButton = tester.widget<ElevatedButton>(
        find.ancestor(
          of: find.text('Back'),
          matching: find.byType(ElevatedButton),
        ),
      );
      expect(backButton.onPressed == null, true);
    });
    
    testWidgets('Next button should advance to next step when clicked', 
        (WidgetTester tester) async {
      // Arrange - start at first step
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Act - tap the next button
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
      
      // Verify nextStep was called
      verify(() => mockWizardStateNotifier.nextStep()).called(1);
    });
    
    testWidgets('Second step shows AgeStep content when currentStep is 1', 
        (WidgetTester tester) async {
      // Arrange - Use a wizard notifier starting at step 2
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 1)
      );
      when(() => mockWizardStateNotifier.canGoPrevious()).thenReturn(true);
      
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Assert - verify that second step content is visible
      expect(find.text('Character Age'), findsOneWidget);
      // Verify the AgeStep widget is present
      expect(find.byType(AgeStep), findsOneWidget);
      
      // Back button should now be enabled
      final backButton = tester.widget<ElevatedButton>(
        find.ancestor(
          of: find.text('Back'),
          matching: find.byType(ElevatedButton),
        ),
      );
      expect(backButton.onPressed != null, true);
    });
    
    testWidgets('Third step shows ThemeStep content when currentStep is 2', 
        (WidgetTester tester) async {
      // Arrange - Use a wizard notifier starting at step 3
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 2)
      );
      when(() => mockWizardStateNotifier.canGoPrevious()).thenReturn(true);
      
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Assert - verify that third step content is visible
      expect(find.text('Story Theme'), findsOneWidget);
      // Verify the ThemeStep widget is present
      expect(find.byType(ThemeStep), findsOneWidget);
    });
    
    testWidgets('Back button should return to previous step when clicked', 
        (WidgetTester tester) async {
      // Arrange - Use a wizard notifier starting at step 2
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 1)
      );
      when(() => mockWizardStateNotifier.canGoPrevious()).thenReturn(true);
      
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: WizardScreen(),
          ),
        ),
      );
      
      // Act - tap the back button
      await tester.tap(find.text('Back'));
      await tester.pumpAndSettle();
      
      // Verify previousStep was called
      verify(() => mockWizardStateNotifier.previousStep()).called(1);
    });
  });
}