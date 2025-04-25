# GuardianLens

A parent social media monitoring application designed to help parents ensure their children's online safety by monitoring subscribed YouTube channels for potentially inappropriate content.

## Project Overview

GuardianLens is an application that:
- Links to a child's YouTube account (with consent)
- Analyzes subscribed channel metadata via keyword matching
- Presents findings on a parent dashboard
- Handles basic user accounts and child profiles

## Repository Structure

This is a monorepo containing both frontend and backend code:

- `/frontend` - Flutter application (Dart) targeting Web and iOS primarily
- `/backend` - FastAPI application (Python) with Celery for background tasks
- `/docs` - Project documentation

## Technologies

- **Frontend**: Flutter, Dart, Riverpod/Bloc, GoRouter, Dio
- **Backend**: FastAPI, Python, Celery, SQLAlchemy
- **Database**: PostgreSQL, Redis (cache/broker)
- **Integration**: Google OAuth, YouTube Data API v3
- **Deployment**: Docker containers

## Development Methodology

This project follows Test-Driven Development (TDD) methodology for both frontend and backend components, using the Red-Green-Refactor cycle for core logic and UI components.

## Getting Started

Detailed setup instructions will be available after initial development setup is complete.

## License

[License Information]