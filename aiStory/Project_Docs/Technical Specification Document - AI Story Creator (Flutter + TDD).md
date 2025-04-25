# **Technical Specification Document - AI Story Creator**

**Project:** AI Bedtime Story Creator **Version:** 1.1 (Based on Plan v1 - Flutter Pivot + TDD, Stack Detail Added) **Date:** April 22, 2025 **Status:** Revised Draft

**Table of Contents:**

1. Introduction
2. Architecture Overview
3. Phase 1 (MVP) Detailed Specifications
   * 3.1. Common Setup & Tooling
   * 3.2. Backend Development (FastAPI - TDD)
   * 3.3. Frontend Development (Flutter - TDD)
   * 3.4. Database Setup (PostgreSQL)
   * 3.5. AI Integration (MVP)
   * 3.6. Third-Party Integrations (MVP Setup)
   * 3.7. Security Implementation (MVP Basics)
   * 3.8. Deployment & CI/CD (MVP Setup)
   * 3.9. Integration Testing & QA
4. Phase 2 Enhancements (High-Level Outline)
5. Phase 3 Advanced Features (High-Level Outline)
6. Appendices (API Contracts, DB Schema Details)

**1. Introduction**

*   **1.1. Overview:** This document provides detailed technical specifications for building the Minimum Viable Product (MVP) of the AI Bedtime Story Creator, following the plan outlined in `story_wizard_plan_v1`. It specifies the architecture, technologies (including specific libraries and versions), development tasks, and testing approach (TDD) for Phase 1.
*   **1.2. Goals (Technical):** Deliver a functional, tested, and deployable MVP application (Flutter targeting iPad/Web, FastAPI backend) capable of generating personalized stories with images and handling basic user accounts and orders. Establish a solid foundation for future phases.
*   **1.3. Target Platforms (MVP):** iPad (via Flutter iOS build), Web (via Flutter Web build). Secondary: iPhone, Android (build targets enabled, but primary testing/optimization focused on iPad/Web).
*   **1.4. Core Technologies & Libraries (Target Versions as of 2025-04-22):**
    *   **Frontend:**
        *   Runtime/SDK: Flutter SDK (Latest Stable), Dart SDK (Latest Stable)
        *   State Management: `riverpod` / `flutter_riverpod` (Latest Stable) or `bloc` / `flutter_bloc` (Latest Stable) - *Team to finalize choice.*
        *   Routing: `go_router` (Latest Stable)
        *   HTTP Client: `dio` (Latest Stable)
        *   Image/File Picking: `image_picker` (Latest Stable), `file_picker` (Latest Stable)
        *   Secure Storage: `flutter_secure_storage` (Latest Stable)
        *   UI Components: Flutter Material Widgets, potentially `shadcn_flutter` if adapted/available, or custom components.
        *   Testing: `flutter_test` (Widget/Unit), `integration_test`
    *   **Backend:**
        *   Runtime: Python (`~3.12.10` or `~3.11.12`)
        *   Framework: FastAPI (`~0.111.0`)
        *   Data Validation: Pydantic (`~2.7.1`)
        *   ORM: SQLAlchemy (`~2.0.40`)
        *   Async DB Driver: `asyncpg` (Latest Stable)
        *   HTTP Client: `httpx` (`~0.27.0`)
        *   Password Hashing: `passlib[bcrypt]` (Latest Stable)
        *   JWT Handling: `python-jose[cryptography]` (Latest Stable)
        *   Migrations: Alembic (Latest Stable)
        *   Rate Limiting (Optional): `slowapi` (Latest Stable)
        *   Testing: `pytest`, `pytest-asyncio`, FastAPI `TestClient`
        *   Dependency Management: Poetry
    *   **AI Services Clients:**
        *   Replicate: `replicate` (`~0.29.1`)
        *   OpenAI: `openai` (`~1.25.1`)
        *   Google Gemini: `google-generativeai` (`~1.11.0`)
        *   *(Use clients relevant to chosen provider)*
    *   **Cloud Storage Clients:**
        *   AWS S3: `boto3` (`~1.34.88`)
        *   GCS: `google-cloud-storage` (`~2.17.0`)
    *   **Payments Client:**
        *   Stripe: `stripe` (`~9.10.0`)
    *   **Database:** PostgreSQL (`~16.x`)
    *   **Infrastructure:** Docker, Docker Compose, Git
*   **1.5. Development Methodology:** Test-Driven Development (TDD) for both frontend and backend components.

**2. Architecture Overview**

*   **2.1. Frontend:** Flutter application (single codebase) using Riverpod/Bloc for state, GoRouter for navigation, Dio for HTTP calls.
*   **2.2. Backend:** FastAPI (Python) application using Pydantic for validation, SQLAlchemy/asyncpg for DB, httpx/specific clients for external APIs.
*   **2.3. Database:** PostgreSQL.
*   **2.4. AI Services:** Replicate API, OpenAI/Gemini/Claude API.
*   **2.5. File Storage:** AWS S3 or GCS.
*   **2.6. Deployment:** Flutter Web (Static Hosting), FastAPI (Docker on PaaS/Cloud Run).

**3. Phase 1 (MVP) Detailed Specifications**

*(TDD Cycle: Write Test -> Fail -> Write Code -> Pass -> Refactor)*

**3.1. Common Setup & Tooling**
*   Task 1.1 (DevOps/Lead): Set up Git repository (Monorepo recommended: `frontend` (Flutter), `backend` (Python)). Define branching strategy (Gitflow).
*   Task 1.2 (DevOps/Lead): Set up **Notion** workspace/database for project management. Populate with Phase 1 epics/stories based on this spec. Define task tracking workflow.
*   Task 1.3 (DevOps/Backend): Set up local development environment using Docker Compose (`docker-compose.yml`) including services for: PostgreSQL (`postgres:16`), Backend API (building from local Dockerfile). Add Redis (`redis:latest`) if needed later.
*   Task 1.4 (DevOps/FE): Ensure consistent Flutter SDK (latest stable) and Dart SDK versions across the frontend team. Standardize Flutter project setup (`flutter create`).
*   Task 1.5 (DevOps/BE): Ensure consistent Python versions (`~3.12` recommended). Use Poetry for dependency management.
*   Task 1.6 (All Devs): Set up IDEs (VS Code/Android Studio/IntelliJ) with extensions for Dart/Flutter, Python, Docker, `pytest`, `flutter_test`.

**3.2. Backend Development (FastAPI - TDD)**
*   Task 2.1 (BE Dev): Initialize FastAPI project. Basic config (`pydantic-settings`). Add `pytest`, `pytest-asyncio`.
*   Task 2.2 (BE Dev): Implement `/health` endpoint.
    *   TDD Cycle: Use `TestClient`.
*   Task 2.3 (BE Dev): Set up SQLAlchemy (`~2.0.40`), Alembic, `asyncpg`. Define base models.
    *   TDD Cycle: Test DB connection setup.
*   Task 2.4 (BE Dev): Implement User Model/Schemas (Pydantic `~2.7.1`). Implement `POST /v1/users` (signup).
    *   TDD Cycle: Test validation, hashing (`passlib[bcrypt]`), endpoint. Mock DB.
*   Task 2.5 (BE Dev): Implement Authentication (`POST /v1/auth/token`). JWT handling (`python-jose[cryptography]`). Protected route decorator (`Depends`).
    *   TDD Cycle: Test hashing/verify (`passlib`), token gen/verify (`python-jose`), login endpoint, protected decorator.
*   Task 2.6 (BE Dev): Implement Photo Metadata Model/Schemas.
*   Task 2.7 (BE Dev): Implement `POST /v1/photos/upload-url` endpoint. Use `boto3` or `google-cloud-storage` client.
    *   TDD Cycle: Mock cloud client. Test auth, URL structure.
*   Task 2.8 (BE Dev): Implement Story/StoryPage Models/Schemas. Define MVP wizard input/output schemas.
*   Task 2.9 (BE Dev): Implement `POST /v1/stories` endpoint (Core Orchestration).
    *   TDD Cycle: Test Pydantic validation. Test prompt template logic. Test mocked AI client calls (`openai`/`google-generativeai`, `replicate`). Test page segmentation logic. Test mocked Personalization call (`replicate`), including fallback. Test DB saving (mocked). Test success/failure responses.
*   Task 2.10 (BE Dev): Implement `GET /v1/stories`, `GET /v1/stories/{story_id}` endpoints.
    *   TDD Cycle: Test auth, DB retrieval (mocked), not found errors.
*   Task 2.11 (BE Dev): Implement Order Model/Schemas.
*   Task 2.12 (BE Dev): Implement `POST /v1/orders` endpoint (Create Payment Intent). Use `stripe` client (`~9.10.0`).
    *   TDD Cycle: Mock Stripe client. Test payload, DB save (pending), client secret return.
*   Task 2.13 (BE Dev): Implement `POST /v1/webhooks/stripe` endpoint. Verify signature. Handle `payment_intent.succeeded`.
    *   TDD Cycle: Test signature verify (mock request). Test event handling logic (mock DB update, mock task trigger).
*   Task 2.14 (BE Dev): Implement Order Confirmation Logic (Trigger POD). Use `httpx` (`~0.27.0`) to call POD API.
    *   TDD Cycle: Test logic (triggered by webhook test). Mock POD API (`httpx` mock). Verify payload, DB update (POD ID, status).
*   Task 2.15 (BE Dev): Implement `GET /v1/orders`, `GET /v1/orders/{order_id}` endpoints.
    *   TDD Cycle: Test auth, DB retrieval (mocked), not found.
*   Task 2.16 (Ops/BE Dev): Configure structured logging (`logging` module).

**3.3. Frontend Development (Flutter - TDD)**
*   Task 3.1 (FE Dev): Initialize Flutter project. Add dependencies: `flutter_riverpod` (or `flutter_bloc`), `go_router`, `dio`, `image_picker`, `file_picker`, `flutter_secure_storage`.
*   Task 3.2 (FE Dev): Set up State Management (`Riverpod`/`Bloc`). Define providers/blocs for Auth, Wizard, API Services.
    *   TDD Cycle: Unit test state logic (`flutter_test`). Mock dependencies.
*   Task 3.3 (FE Dev): Implement API Client Service layer (using `dio`). Define methods. Handle JWT injection (`dio` Interceptor), errors.
    *   TDD Cycle: Unit test service methods mocking `dio`.
*   Task 3.4 (FE Dev): Implement Auth Screens (Sign Up, Login).
    *   TDD Cycle: Widget test (`flutter_test`) UI (`TextField`, `Button`), validation, interactions, state updates, API calls (mocked service).
*   Task 3.5 (FE Dev): Implement App Navigation (`go_router`). Define routes. Handle auth guarding.
    *   TDD Cycle: Widget test navigation logic.
*   Task 3.6 (FE Dev): Implement Wizard Multi-Step Structure/Shell (`Stepper` or custom). Manage step state.
    *   TDD Cycle: Widget test step transitions.
*   Task 3.7 (FE Dev): Implement Wizard Step 1: Welcome Screen.
    *   TDD Cycle: Widget test static content, navigation.
*   Task 3.8 (FE Dev): Implement Wizard Step 2: Child's Name Input (`TextField`).
    *   TDD Cycle: Widget test interaction, state updates.
*   Task 3.9 (FE Dev): Implement Wizard Step 3: Age Range Selection (`ChoiceChip`/`SegmentedButton`).
    *   TDD Cycle: Widget test interaction, state updates.
*   Task 3.10 (FE Dev): Implement Wizard Step 4: Theme Selection (Visual `Card` + `GestureDetector`).
    *   TDD Cycle: Widget test display, tap interaction, state updates.
*   Task 3.11 (FE Dev): Implement Wizard Step 5: Photo Upload (`image_picker`/`file_picker`). Consent checkbox logic. Pre-signed URL flow.
    *   TDD Cycle: Widget test consent logic. Unit/Widget test platform channel mocking, API service interaction (mocked), state updates (progress).
*   Task 3.12 (FE Dev): Implement Wizard Step 6: Generate Button (`ElevatedButton`) & Loading State (`CircularProgressIndicator`).
    *   TDD Cycle: Widget test button state, tap action -> API call (mocked), UI state transitions (loading/success/error).
*   Task 3.13 (FE Dev): Implement Story Preview Screen (`PageView`?). Fetch data via API service. Display text/images.
    *   TDD Cycle: Widget test data fetching states, display logic (mocked data), navigation.
*   Task 3.14 (FE Dev): Implement Checkout Flow Screens (Shipping Address Form, Payment Form - integrate with backend intent using `stripe_flutter` potentially, or custom UI calling backend).
    *   TDD Cycle: Widget test forms, validation, state, API calls (mocked service/Stripe).
*   Task 3.15 (FE Dev): Implement Order Confirmation Screen.
    *   TDD Cycle: Widget test display logic.
*   Task 3.16 (FE Dev): Implement Order History Screen (`ListView`). Fetch orders via API service.
    *   TDD Cycle: Widget test data fetching states, list display.
*   Task 3.17 (FE Dev): Implement Responsive Layouts (`LayoutBuilder`/`MediaQuery`) for Wizard/Preview.
    *   TDD Cycle: Widget test layouts at different simulated sizes.

**3.4. Database Setup (PostgreSQL)**
*   Task 4.1 (Ops/BE Dev): Provision managed PostgreSQL (`~16.x`). Configure local Docker (`postgres:16`).
*   Task 4.2 (BE Dev): Use Alembic to generate initial migration script from SQLAlchemy models.
*   Task 4.3 (Ops/BE Dev): Apply migration. Set up backups.

**3.5. AI Integration (MVP)**
*   Task 5.1 (BE Dev): Obtain API keys (Text Gen AI, Replicate). Store securely.
*   Task 5.2 (BE Dev): Implement client logic (`openai`/`google-generativeai`, `replicate`) tested via mocking (Task 2.9).
*   Task 5.3 (Product/AI Spec): Define exact MVP prompt templates.
*   Task 5.4 (Product/AI Spec): Identify specific Replicate models (base image gen, personalization).

**3.6. Third-Party Integrations (MVP Setup)**
*   Task 6.1 (BE Dev/Lead): Set up Stripe account. Obtain/store keys.
*   Task 6.2 (BE Dev/Lead): Set up POD provider account. Obtain/store keys. Review API docs.
*   Task 6.3 (BE Dev): Implement client logic (`stripe`, `httpx` for POD) tested via mocking (Tasks 2.12, 2.14).

**3.7. Security Implementation (MVP Basics)**
*   Task 7.1 (BE Dev): Implement JWT auth (`python-jose`), route protection (`Depends`) (Task 2.5).
*   Task 7.2 (BE Dev): Implement password hashing (`passlib`) (Task 2.4).
*   Task 7.3 (BE Dev): Ensure Pydantic validation on all endpoints.
*   Task 7.4 (FE Dev): Implement secure photo consent flow (`Checkbox` logic) (Task 3.11). Use `flutter_secure_storage` for JWT.
*   Task 7.5 (Ops): Configure HTTPS.
*   Task 7.6 (Ops): Securely store secrets (env vars/secrets manager).
*   Task 7.7 (Ops/BE Dev): Set up basic rate limiting (`slowapi`) (Task 2.5 related).
*   Task 7.8 (Ops/Lead): Configure CORS policy (FastAPI CORS Middleware).

**3.8. Deployment & CI/CD (MVP Setup)**
*   Task 8.1 (Ops): Set up cloud hosting (Render/GCP/AWS).
*   Task 8.2 (Ops): Create Backend CI/CD (GitHub Actions/etc.): Lint -> **Pytest** -> Build Docker -> Push -> Deploy Staging.
*   Task 8.3 (Ops): Create Frontend CI/CD: Lint (`dart analyze`) -> **Flutter Test** -> Build Web (`flutter build web`) -> Deploy Web Staging. (Add native build steps if needed).

**3.9. Integration Testing & QA**
*   Task 9.1 (QA/Dev): Execute Flutter `integration_test` suite against staging backend.
*   Task 9.2 (QA): Manual exploratory testing (iPad/Web focus).
*   Task 9.3 (QA/Security): Basic security checks.
*   Task 9.4 (QA/Product): Review generated story quality.
*   Task 9.5 (All): Bug Bash on staging.

**4. Phase 2 Enhancements (High-Level Outline)**

*   (Requires TDD for new Flutter widgets, state, backend logic, prompt engineering tests)

**5. Phase 3 Advanced Features (High-Level Outline)**

*   (Requires TDD for Profiles, Controls, Suggestions UI/State/Backend logic)

**6. Appendices**

*   **6.1. API Contract Definitions:** (Link to OpenAPI/Swagger Doc)
*   **6.2. Database Schema (Detailed):** (Link to Schema Diagram/Alembic Migrations)
*   **6.3. Key Configuration Variables:** (List of ENV VARS)