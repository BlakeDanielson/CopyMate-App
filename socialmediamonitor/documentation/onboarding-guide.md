# Technical Onboarding Guide

This document serves as a guide for new technical team members joining the GuardianLens project.

## Project Overview

GuardianLens is a platform aimed at helping parents monitor their children's online activity and safety, starting with a YouTube-Only MVP. The goal is to provide parents with actionable insights into potential risks associated with the YouTube channels their children subscribe to, based on analysis of public channel and video metadata (Section 1, `Tech_Spec.md`, Section 1, `PRD.md`).

## Architecture Overview

The system follows a standard architecture pattern:
*   **Frontend:** Flutter-based web and mobile UI for parents (Section 1, `Tech_Stack.md`).
*   **Backend API:** Python with FastAPI, handling business logic, data fetching orchestration, and analysis (Section 2, `Tech_Stack.md`).
*   **Database:** PostgreSQL for primary data storage (Section 3, `Tech_Stack.md`).
*   **Caching/Task Queue Broker:** Redis used for caching and as the message broker for Celery (Section 3, 5, `Tech_Stack.md`).
*   **Analysis Engine:** Integrated within the backend for MVP, performing keyword matching on text metadata (Section 4, `Tech_Stack.md`).
*   **Asynchronous Tasks:** Celery handles background jobs like daily data fetching and analysis (Section 5, `Tech_Stack.md`).

## Tech Stack Setup

To set up the development environment:
*   Install Flutter and Dart for frontend development.
*   Set up a Python environment for backend development, installing FastAPI and other dependencies (e.g., Celery, database driver, HTTP client).
*   Set up local instances of PostgreSQL and Redis, or obtain credentials for development instances.
*   Configure environment variables for database connections, API keys, and other secrets.

Refer to project-specific setup instructions for detailed steps.

## Key Workflows

Important development workflows include:
*   **Feature Development:** Implementing new functional requirements based on the PRD and Tech Spec.
*   **API Integration:** Working with the YouTube Data API, including handling quotas and caching.
*   **Analysis Logic Development:** Updating and testing the keyword matching logic.
*   **Background Task Management:** Developing and monitoring Celery tasks.
*   **Testing:** Writing and running unit, integration, and end-to-end tests as detailed in the [Comprehensive Testing Plan](./development-progress.md#comprehensive-testing-plan).
*   **CI/CD:** Utilizing the CI/CD pipeline for automated builds and deployments.

---

*This document should be expanded with specific setup instructions and details on key development processes.*