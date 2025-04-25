# GuardianLens

A monitoring system for tracking and analyzing social media content, with a focus on protecting younger users from potentially harmful content.

## Project Overview

This application allows parents to:
- Link YouTube accounts through secure OAuth integration
- Monitor children's subscribed channels and view history
- Analyze video content for potentially harmful material using AI-based recognition
- Receive real-time alerts about concerning content
- View detailed reports and analytics

## Tech Stack

- Backend: Python with FastAPI
- Database: SQL-based storage with SQLAlchemy ORM
- Authentication: OAuth 2.0 integration for YouTube account linking
- Task Queue: Celery for asynchronous video analysis
- Frontend: Planned progressive web app implementation

## Development

See `documentation/development-progress.md` for current status and upcoming milestones.

## Documentation

- `documentation/`: Contains detailed guides and specifications
- `projectDocs/`: Contains project requirements and architecture designs

## Git Workflow

This project follows a simplified GitHub Flow. See `projectDocs/gitFlow.md` for detailed instructions.

## Getting Started

1. Clone this repository
2. Set up a Python virtual environment
3. Install dependencies
4. Configure environment variables
5. Run the development server

## Contributing

Contributions are welcome! Please follow our git workflow process and ensure all tests pass before submitting pull requests.