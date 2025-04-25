GuardianLens - Technical Specification Document
Project: Parent Social Media Monitor (GuardianLens)
Version: 1.0 (YouTube-Only MVP + TDD)
Date: April 22, 2025
Status: Initial Draft

Table of Contents:

Introduction

Architecture Overview

Phase 1 (MVP) Detailed Specifications

3.1. Common Setup & Tooling

3.2. Backend Development (FastAPI + Celery - TDD)

3.3. Frontend Development (Flutter - TDD)

3.4. Database & Cache Setup (PostgreSQL + Redis)

3.5. Analysis Engine (MVP - Keyword Based)

3.6. Third-Party Integrations (MVP Setup)

3.7. Security & Compliance Implementation (MVP Basics)

3.8. Deployment & CI/CD (MVP Setup)

3.9. Integration Testing & QA

Phase 2 Enhancements (High-Level Outline)

Phase 3 Advanced Features (High-Level Outline)

Appendices (API Contracts, DB Schema Details, Risk Categories)

1. Introduction

1.1. Overview: This document provides detailed technical specifications for building the Minimum Viable Product (MVP) of GuardianLens. It specifies the architecture, technologies (Flutter frontend, Python/FastAPI backend), development tasks (Phase 1), and incorporates a Test-Driven Development (TDD) methodology. This spec is based on the provided PRD, Tech Stack, and initial Tech Spec documents.

1.2. Goals (Technical): Deliver a functional, rigorously tested, and deployable MVP application capable of linking a child's YouTube account (with consent), analyzing subscribed channel metadata via keyword matching, presenting findings on a parent dashboard, and handling basic user accounts. Establish a robust foundation for future expansion, prioritizing efficient YouTube API usage.

1.3. Target Platforms (MVP): Flutter Web, Flutter iOS (iPad primary focus). Secondary: Flutter Android, Flutter iOS (iPhone).

1.4. Core Technologies: Flutter (Dart), FastAPI (Python), Celery, PostgreSQL, Redis, Google OAuth, YouTube Data API v3, Docker. (Refer to uploaded Tech Stack doc for specific library recommendations like Riverpod/Bloc, GoRouter, dio, Celery, spaCy/NLTK potential).

1.5. Development Methodology: Test-Driven Development (TDD) for both frontend and backend components. Red-Green-Refactor cycle mandatory for core logic and UI components.

2. Architecture Overview

2.1. Frontend: Flutter application handling UI, state management (Riverpod/Bloc), navigation (GoRouter), user interaction, and secure storage (flutter_secure_storage). Communicates via REST API with the backend.

2.2. Backend: FastAPI (Python) application serving the REST API. Handles parent authentication (JWT), child profile management, YouTube OAuth flow, API interactions (YouTube, Email Service), database operations, and triggers background tasks.

2.3. Background Processing: Celery (Python) workers handle asynchronous tasks: fetching YouTube subscriptions/metadata, running analysis engine, potentially sending notifications. Uses Redis/RabbitMQ as a broker.

2.4. Analysis Engine (MVP): Python module (initially integrated within backend or Celery task) performing keyword/pattern matching on text metadata against internal lists.

2.5. Database: PostgreSQL for persistent relational data (users, profiles, channels, analysis results).

2.6. Cache: Redis for caching YouTube API responses (channel/video metadata) to manage quotas and improve performance. Also serves as Celery broker.

2.7. Deployment: Flutter Web to static hosting. Backend API & Celery workers as Docker containers (PaaS/K8s). Managed PostgreSQL & Redis instances.

3. Phase 1 (MVP) Detailed Specifications

(TDD Cycle: Write Test -> Fail -> Write Code -> Pass -> Refactor)

3.1. Common Setup & Tooling
* Task 1.1 (DevOps/Lead): Set up Git repository (Monorepo recommended: frontend (Flutter), backend (FastAPI/Celery)). Define branching strategy (Gitflow).
* Task 1.2 (DevOps/Lead): Set up Notion workspace/database for project management. Populate with Phase 1 epics/stories based on this spec. Define task tracking workflow.
* Task 1.3 (DevOps/Backend): Set up local development environment using Docker Compose (docker-compose.yml) including services for: PostgreSQL, Redis, Backend API, Celery Worker.
* Task 1.4 (DevOps/FE): Ensure consistent Flutter/Dart SDK versions across the frontend team.
* Task 1.5 (DevOps/BE): Ensure consistent Python versions. Set up venv. Manage dependencies (requirements.txt or Poetry/PDM).
* Task 1.6 (All Devs): Set up IDEs (VS Code/Android Studio/IntelliJ) with extensions for Dart/Flutter, Python, Docker, TDD frameworks (pytest, flutter_test).

3.2. Backend Development (FastAPI + Celery - TDD)
* Task 2.1 (BE Dev): Initialize FastAPI project structure. Basic configuration (BaseSettings). Celery app initialization.
* Task 2.2 (BE Dev): Implement /health endpoint for API and potentially a Celery worker health check mechanism.
* TDD Cycle: Test API endpoint. Test basic Celery task execution (e.g., simple add task).
* Task 2.3 (BE Dev): Set up SQLAlchemy ORM, Alembic, async DB connection (asyncpg). Define base models.
* TDD Cycle: Test DB connection setup.
* Task 2.4 (BE Dev): Implement ParentUser Model & Auth Endpoints (POST /v1/users/register, POST /v1/auth/token).
* TDD Cycle: Test user creation (validation, passlib hashing). Test login (credential validation, python-jose JWT generation). Test JWT validation/decoding logic. Test protected route decorator (Depends).
* Task 2.5 (BE Dev): Implement ChildProfile Model & CRUD API Endpoints (POST /v1/profiles, GET /v1/profiles, PUT /v1/profiles/{id}, DELETE /v1/profiles/{id}). Ensure endpoints are protected and scoped to the logged-in parent.
* TDD Cycle: Test each CRUD operation logic and API endpoint behavior (auth, validation, DB interaction - mocked for unit tests).
* Task 2.6 (BE Dev): Implement YouTube OAuth Flow Endpoints (GET /v1/youtube/auth/url, GET /v1/youtube/auth/callback). Handle state parameter for security. Securely store refresh/access tokens associated with ChildProfile upon successful callback (encrypt tokens at rest). Implement token refresh logic (potentially background task).
* TDD Cycle: Test URL generation. Test callback handling (code exchange - mocked Google API call, token storage - mocked DB). Test token refresh logic (mocked Google API, DB update).
* Task 2.7 (BE Dev): Implement Account Unlinking Endpoint (POST /v1/profiles/{id}/youtube/unlink). Revoke/delete stored tokens.
* TDD Cycle: Test token deletion logic (mocked DB). Test Google token revocation API call (mocked).
* Task 2.8 (BE Dev): Define Celery Task for Fetching Subscriptions (tasks.fetch_subscriptions). Takes child_profile_id. Uses stored OAuth token to call YouTube subscriptions.list. Stores/updates channel IDs associated with profile. Handles token expiry/refresh. Handles API errors/quota issues.
* TDD Cycle: Test task logic mocking YouTube API client and DB interactions. Test error handling paths.
* Task 2.9 (BE Dev): Define Celery Task for Fetching Channel/Video Metadata (tasks.fetch_channel_metadata). Takes channel_id. Calls YouTube channels.list & playlistItems.list & videos.list. Implement aggressive caching using Redis (check cache before API call, store results on success). Handles API errors/quota issues.
* TDD Cycle: Test caching logic (cache hit/miss). Test task logic mocking YouTube API client, Redis client, and DB interactions. Test parsing of API responses.
* Task 2.10 (BE Dev): Define Celery Task for Running Analysis (tasks.analyze_channel). Takes channel_id. Retrieves cached/fetched metadata (channel desc, video titles/descs). Runs keyword analysis engine (Task 3.5.1). Stores AnalysisResult.
* TDD Cycle: Test task logic, mocking metadata retrieval and analysis engine function. Test DB storage of results.
* Task 2.11 (BE Dev): Implement Orchestration Logic/Scheduler. Trigger fetch_subscriptions daily per active linked profile. Trigger fetch_channel_metadata for new/updated subscriptions. Trigger analyze_channel after metadata fetch. (Can use Celery Beat or simple cron/scheduler).
* TDD Cycle: Test scheduling logic (mocking task triggers).
* Task 2.12 (BE Dev): Implement Dashboard API Endpoint (GET /v1/dashboard/{profile_id}). Retrieves subscribed channels, latest analysis results/flags, context (sub count), "newly flagged" status. Implement sorting/filtering based on query params.
* TDD Cycle: Test endpoint logic, mocking DB interactions. Test sorting/filtering logic. Test "newly flagged" calculation.
* Task 2.13 (BE Dev): Implement Feedback Endpoint (POST /v1/analysis/{result_id}/feedback). Allows parent to mark as "Not Harmful". Store feedback.
* TDD Cycle: Test endpoint logic, mocking DB update.
* Task 2.14 (BE Dev): Implement Notification Trigger Logic. After analysis task completes, check for new high-priority flags. If found, trigger notification task (Task 2.15).
* TDD Cycle: Test logic for detecting new flags and triggering notification task.
* Task 2.15 (BE Dev): Define Celery Task for Sending Notifications (tasks.send_notification). Takes user ID, message type. Uses Email Service client (SES/SendGrid) or triggers FCM push via backend admin SDK (if needed).
* TDD Cycle: Test task logic mocking Email/FCM clients.
* Task 2.16 (Ops/BE Dev): Configure structured logging for API endpoints and Celery tasks. Critical for debugging background jobs.

3.3. Frontend Development (Flutter - TDD)
* Task 3.1 (FE Dev): Initialize Flutter project. Configure targets. Add dependencies (provider/flutter_bloc, go_router, dio, flutter_secure_storage, image_picker, file_picker, firebase_messaging, etc.). Set up basic project structure (features/layers).
* Task 3.2 (FE Dev): Set up State Management (Riverpod/Bloc). Define providers/blocs for Auth, Child Profiles, YouTube Linking State, Dashboard Data, API Client.
* TDD Cycle: Unit test state logic (initial states, transitions, event handling). Mock dependencies.
* Task 3.3 (FE Dev): Implement API Client Service (using dio). Wrapper methods for all backend endpoints. Handle JWT token injection (interceptors), error handling, response parsing.
* TDD Cycle: Unit test service methods mocking dio client. Verify requests/responses/error handling.
* Task 3.4 (FE Dev): Implement Authentication Screens (Register, Login).
* TDD Cycle: Widget test UI elements, form validation, interactions, calls to Auth Bloc/Provider & API service. Mock dependencies.
* Task 3.5 (FE Dev): Implement Core App Navigation (GoRouter). Define routes (Auth, Dashboard, Profile Management, Linking Flow). Handle auth guarding.
* TDD Cycle: Widget test navigation logic.
* Task 3.6 (FE Dev): Implement Child Profile Management Screens (List, Create/Edit Form).
* TDD Cycle: Widget test UI, form handling, interaction with Profile Bloc/Provider & API service.
* Task 3.7 (FE Dev): Implement YouTube Account Linking Flow UI. Display instructions, consent info. Trigger backend URL endpoint. Handle redirect/callback (requires platform-specific setup for deep linking or web redirect handling). Update linking state via Bloc/Provider.
* TDD Cycle: Widget test UI elements, consent display. Unit/Widget test state updates based on linking steps. Mock API service calls. Testing OAuth callback flow might require integration tests or careful mocking.
* Task 3.8 (FE Dev): Implement Dashboard Screen. Fetch data via API service. Display summary, list of subscribed channels with flags/thumbnails/names. Implement sorting/filtering UI controls. Show "newly flagged" indicator.
* TDD Cycle: Widget test data fetching states (loading/error/success). Test list display, sorting/filtering logic, flag indicators based on mocked data. Mock API service.
* Task 3.9 (FE Dev): Implement Flagged Channel Detail View (Modal or separate screen). Display context (sub count, reason, snippet?). Provide YouTube link. Implement "Mark as Not Harmful" button.
* TDD Cycle: Widget test display logic based on mocked data. Test button interaction calls API service.
* Task 3.10 (FE Dev): Implement Account Unlinking Button/Action. Trigger backend endpoint. Update UI state.
* TDD Cycle: Widget test button interaction, confirmation dialog (if any), calls to API service, state updates.
* Task 3.11 (FE Dev): Implement Parent Onboarding Flow (simple multi-screen tutorial on first login).
* TDD Cycle: Widget test screen content and navigation.
* Task 3.12 (FE Dev): Set up FCM for push notifications (if mobile target active). Handle receiving/displaying simple notifications.
* TDD Cycle: Unit test notification handling logic (mocking FCM plugin).
* Task 3.13 (FE Dev): Implement Responsive Layouts for Dashboard/Detail views to adapt between iPad and Web.
* TDD Cycle: Widget test layouts render correctly at different simulated screen sizes.

3.4. Database & Cache Setup (PostgreSQL + Redis)
* Task 4.1 (Ops/BE Dev): Provision managed PostgreSQL & Redis instances (or configure local Docker). Ensure network connectivity between API/Celery containers and DB/Cache.
* Task 4.2 (BE Dev): Use Alembic to generate initial migration scripts based on SQLAlchemy models (ParentUser, ChildProfile, LinkedAccount, SubscribedChannel, AnalyzedVideo, AnalysisResult, etc.). Define detailed schema in Appendix.
* Task 4.3 (Ops/BE Dev): Apply initial migrations. Set up backup/restore strategy. Configure Redis for caching TTLs and potentially as Celery broker.

3.5. Analysis Engine (MVP - Keyword Based)
* Task 5.1 (BE Dev/Analyst): Develop/Refine initial keyword lists & patterns for MVP risk categories (Hate Speech, Self-Harm, etc.). Store in a configurable format (e.g., JSON/YAML file).
* Task 5.2 (BE Dev): Implement core analysis function/module in Python. Takes text inputs (channel/video metadata), applies keyword matching logic, returns list of found categories/flags. Consider using spaCy/NLTK for basic tokenization/lemmatization if needed.
* TDD Cycle: Unit test the analysis function with various text inputs and expected keyword matches/non-matches. Test handling of edge cases (empty text, special characters).
* Task 5.3 (BE Dev): Integrate analysis function into the tasks.analyze_channel Celery task (Task 2.10).

3.6. Third-Party Integrations (MVP Setup)
* Task 6.1 (BE Dev/Lead): Set up Google Cloud Project. Enable YouTube Data API v3. Create OAuth 2.0 Credentials (Client ID/Secret for Web/iOS/Android as needed). CRITICAL: Initiate YouTube Data API Quota Increase Request ASAP, providing detailed justification based on planned usage (daily scans per user).
* Task 6.2 (BE Dev/Lead): Set up Email Service (AWS SES/SendGrid). Obtain API keys. Configure sending domain/addresses.
* Task 6.3 (FE Dev/Lead): Set up Firebase project for FCM (if mobile notifications are used). Configure Flutter app with necessary Firebase files.

3.7. Security & Compliance Implementation (MVP Basics)
* Task 7.1 (BE Dev): Implement JWT Auth, password hashing (Task 2.4, 2.5).
* Task 7.2 (FE Dev): Use flutter_secure_storage for JWT token persistence.
* Task 7.3 (BE Dev): Implement Pydantic input validation rigorously.
* Task 7.4 (FE/BE Dev): Implement Consent Flows: CRITICAL
* Develop clear consent language/UI for parent & child (Task 5.3 PRD).
* Implement technical mechanism for Verifiable Parental Consent (VPC) if targeting <13 (requires specific solution research - e.g., email verification loop, small payment verification - consult legal).
* Ensure Google OAuth flow serves as child consent mechanism for >=13.
* Task 7.5 (Ops): Enforce HTTPS.
* Task 7.6 (Ops): Securely manage all secrets (API keys, DB creds, JWT secret, OAuth secrets).
* Task 7.7 (Ops/BE Dev): Implement basic rate limiting (optional but recommended for auth).
* Task 7.8 (Ops/Lead): Configure CORS correctly.
* Task 7.9 (Lead/Legal): Final legal review of consent flows, privacy policy, ToS adherence (YouTube/Google), COPPA/GDPR/AZ compliance.

3.8. Deployment & CI/CD (MVP Setup)
* Task 8.1 (Ops): Set up cloud hosting (Static for Flutter Web, PaaS/K8s for Backend/Celery). Provision managed DB/Cache.
* Task 8.2 (Ops): Create CI/CD pipeline for Backend (Docker): Lint -> Pytest Tests -> Build -> Push -> Deploy Staging.
* Task 8.3 (Ops): Create CI/CD pipeline for Frontend (Flutter): Lint -> Flutter Tests -> Build Web -> Deploy Web Staging. (Add steps for native builds if needed for internal testing).

3.9. Integration Testing & QA
* Task 9.1 (QA/Dev): Execute Flutter integration_test suite against staging backend. Test core flows (Link Account -> See Dashboard -> View Detail -> Mark Safe).
* Task 9.2 (QA): Manual exploratory testing on target platforms (iPad/Web). Focus on YouTube linking edge cases, consent flows, dashboard accuracy, responsiveness.
* Task 9.3 (QA/Security): Basic security checks. Verify consent mechanisms.
* Task 9.4 (QA/Product): Review analysis results for accuracy (MVP keyword level). Check context display.
* Task 9.5 (All): Bug Bash on staging.

4. Phase 2 Enhancements (High-Level Outline)

(Based on PRD Future Considerations & requires separate detailed spec)

Support Additional Platforms (Instagram/TikTok): Major effort - requires new API integrations, consent flows, analysis adaptations.

Deeper Analysis (LLMs, Image/Video): Integrate external LLM APIs or potentially fine-tune models. Requires significant backend changes, prompt engineering, cost analysis. TDD for new analysis modules.

Parent Customization: UI/Backend changes (TDD).

5. Phase 3 Advanced Features (High-Level Outline)

(Based on PRD Future Considerations & requires separate detailed spec)

Real-time Alerting: Requires different architecture (WebSockets, event streaming?).

Child's Own Content Analysis: Major privacy/consent implications. Requires different API scopes.

Enhanced Reporting: Backend aggregation, frontend charting libraries (TDD).

6. Appendices

6.1. API Contract Definitions: (Placeholder - Link to generated OpenAPI/Swagger documentation).

6.2. Database Schema (Detailed): (Placeholder - Link to schema diagram or Alembic migration files).

6.3. Risk Categories & Keywords (MVP): (Placeholder - Link to internal document/repository managing keyword lists).

6.4. Key Configuration Variables: (Placeholder - List essential env vars).