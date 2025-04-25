# AI Story Creator - Flutter Frontend

## Overview
The AI Story Creator application is a Flutter-based mobile and web application that allows users to create AI-generated stories from prompts and images. This is the frontend component of the project, built using Flutter with clean architecture principles.

## Architecture

The project follows clean architecture principles with a feature-based organization:

```
lib/
├── config/              # Application configuration
├── core/                # Core utilities and common components
│   ├── constants/       # Application constants
│   ├── errors/          # Error handling
│   ├── network/         # Network-related utilities
│   ├── theme/           # Application theming
│   └── utils/           # Utility functions
├── features/            # Feature-based modules
│   ├── auth/            # Authentication feature
│   ├── home/            # Home screen feature
│   ├── settings/        # Settings feature
│   └── story/           # Story creation and viewing feature
├── shared/              # Shared components
│   ├── models/          # Shared data models
│   ├── services/        # Shared services
│   └── widgets/         # Shared UI widgets
└── main.dart            # Application entry point
```

### Layers (per feature)
Each feature follows a layered architecture:

- **Data**: repositories, data sources, and models for API interactions
- **Domain**: business logic, entities, and use cases
- **Presentation**: UI components, screens, and state management

## State Management

The application uses [Riverpod](https://riverpod.dev/) for state management, which provides:

- Dependency injection
- State management
- Side-effect handling
- Reactive programming support

## Navigation

Routing is handled by [go_router](https://pub.dev/packages/go_router), which provides:

- Declarative routing
- Deep linking support
- Nested routing
- Path parameters

## Setup

### Prerequisites
- Flutter SDK (>= 3.7.2)
- Dart SDK (>= 3.0.0)
- Android Studio or VS Code with Flutter extensions

### Installation

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies
   ```bash
   flutter pub get
   ```
4. Run the application
   ```bash
   flutter run
   ```

## Environment Configuration

The application supports different environments:

- Development
- Staging
- Production

Environment-specific configurations are stored in `.env` files:

- `.env.development`
- `.env.staging`
- `.env.production`

To switch between environments, modify the environment parameter in the `EnvConfig.initialize()` call in `main.dart`.

## Testing

The project includes:

- Unit tests: `test/unit/`
- Widget tests: `test/widget/`
- Integration tests: `test/integration/`

Run tests with:
```bash
flutter test
```

## Building for Production

Build for production with:

```bash
# Android
flutter build apk --release
flutter build appbundle --release

# iOS
flutter build ios --release

# Web
flutter build web --release
```

## Code Generation

The project uses build_runner for code generation. After making changes to models or providers, run:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## Contributing

1. Create a feature branch from the development branch
2. Make your changes
3. Write tests for your changes
4. Run tests to ensure they pass
5. Submit a pull request
