# GuardianLens Frontend

This directory contains the Flutter application for GuardianLens, targeting primarily web and iPad platforms.

## Technology Stack

- **Framework**: Flutter
- **Language**: Dart
- **State Management**: Riverpod/Bloc (to be decided)
- **Navigation**: GoRouter
- **HTTP Client**: Dio
- **Storage**: flutter_secure_storage

## Project Structure

Once initialized, the project will follow this structure:

```
frontend/
├── lib/
│   ├── core/              # Core utilities, constants, themes
│   ├── data/              # Data layer (models, repositories, API clients)
│   ├── features/          # Feature modules
│   │   ├── auth/          # Authentication feature
│   │   ├── profile/       # Child profile management
│   │   ├── dashboard/     # Parent dashboard
│   │   └── youtube/       # YouTube integration
│   ├── navigation/        # App navigation and routing
│   └── main.dart          # Application entry point
├── test/                  # Unit and widget tests
├── integration_test/      # Integration tests
├── assets/                # Static assets (images, fonts)
└── pubspec.yaml           # Dependencies and app metadata
```

## Setup and Development

### Requirements

- Flutter SDK (version to be determined)
- Dart SDK (version to be determined)
- VS Code or Android Studio with Flutter/Dart plugins

### Getting Started

Instructions for setting up the Flutter development environment will be provided once the project is initialized.

### Testing

This project follows a Test-Driven Development (TDD) approach:

1. Write tests first
2. Implement features to make tests pass
3. Refactor code while ensuring tests remain green

## Build and Deployment

Instructions for building and deploying the application will be provided during CI/CD setup.