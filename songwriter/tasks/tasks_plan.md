# Task Plan & Backlog - Songwriter Connect v1.0 (MVP)

Based on `techspec.md`.

## Current Status

*   **Project Phase:** Initial Setup & Planning
*   **What Works:** Basic project structure created, core documentation files initialized.
*   **Current Focus:** Finalizing initial setup, planning development sprints/tasks.

## MVP v1.0 Task Backlog (Derived from Key Features - F1-F6)

*(Note: Tasks need further breakdown and estimation)*

*   **[Epic] F1: Songwriter Profiles**
    *   [Task] Design Songwriter Profile page UI.
    *   [Task] Implement Frontend component for Songwriter Profile.
    *   [Task] Implement Backend API endpoint to fetch Songwriter data (bio, photo, credits, awards).
    *   [Task] Implement DB queries (Neo4j) for Songwriter data.
    *   [Task] Implement filtering/sorting for credit lists on profile page (Frontend/Backend).
*   **[Epic] F2: Basic Artist/Song/Album Pages**
    *   [Task] Design basic UI for Artist, Song, Album pages.
    *   [Task] Implement Frontend components for these pages.
    *   [Task] Implement Backend API endpoints for basic data retrieval.
    *   [Task] Implement DB queries (Neo4j) for associated entities.
    *   [Task] Ensure prominent linking to associated Songwriter/Producer profiles.
*   **[Epic] F3: Search Functionality**
    *   [Task] Setup and configure chosen Search Index (Elasticsearch/Algolia).
    *   [Task] Implement Data Ingestion logic to push data from Neo4j to Search Index.
    *   [Task] Implement Backend Search API endpoint utilizing the Search Index.
    *   [Task] Implement Frontend Search Bar UI.
    *   [Task] Implement Frontend Search Results page UI with categorization.
*   **[Epic] F4: Filtering Functionality**
    *   [Task] Define filterable fields for search results (e.g., entity type).
    *   [Task] Define filterable fields for profile page lists (e.g., credits by Artist, Year, Role).
    *   [Task] Implement filtering logic in Backend API (leveraging Search Index where applicable).
    *   [Task] Implement Frontend filtering controls UI (for search results and profile lists).
*   **[Epic] F5: Data Suggestion Form**
    *   [Task] Design simple Data Suggestion Form UI.
    *   [Task] Implement Frontend form component.
    *   [Task] Implement Backend API endpoint to receive and validate form submissions.
    *   [Task] Setup storage mechanism (e.g., DB table) for pending suggestions.
    *   [Task] Define internal process for reviewing/actioning suggestions.
*   **[Epic] F6: Mobile Responsiveness**
    *   [Task] Ensure all Frontend components and pages are fully responsive.
    *   [Task] Test thoroughly across target mobile browsers/devices.
*   **[Epic] Data Ingestion (Initial Setup)**
    *   [Task] Develop scripts/service to ingest data from selected initial API(s) (e.g., MusicBrainz).
    *   [Task] Implement basic data cleaning and mapping.
    *   [Task] (Requires Owner Guidance) Develop initial approved scraping module(s).
*   **[Epic] Deployment (Initial Setup)**
    *   [Task] Choose hosting platform.
    *   [Task] Setup basic CI/CD pipeline.
    *   [Task] Deploy initial version of Frontend, Backend, DB, Search Index.

## Future Enhancements (Post-MVP Backlog - Derived from Section 13)

*   Implement interactive network visualization layer.
*   Introduce user accounts (saving, personalization, enhanced contributions).
*   Expand data scope (genres, eras, deeper credits).
*   Refine data suggestion/verification workflow (user reputation?).
*   Add lyrics display/search.
*   Add annotation features.
*   Implement saving/sharing features.

## Known Issues / Risks (Derived from Section 14)

*   **Risk (High): Data Acquisition & Accuracy:** Sourcing reliable data (esp. producer/awards), vetting, managing suggestions is ongoing effort.
*   **Risk (Medium): Search/Filter Complexity:** Achieving Genius.com-level functionality requires search index expertise.
*   **Risk (Medium): Scraping Compliance:** Ensuring ethical/legal scraping requires careful planning.
*   **Risk (Low): Scope Creep:** Requires discipline to stay focused on MVP. 