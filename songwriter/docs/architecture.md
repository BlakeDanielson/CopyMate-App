# System Architecture - Songwriter Connect v1.0 (MVP)

This document outlines the planned architecture based on `techspec.md`.

## 1. Overview

*   **How it Works:** Standard client-server web application architecture.
*   **Component Relationships:** A React/Next.js frontend interacts with a Python (Flask/Django) backend API. The backend fetches data from a Neo4j database and a dedicated Search Index (Elasticsearch/Algolia). Data ingestion scripts/services populate the database and index.
*   **Dependencies:**
    *   Frontend depends on Backend API.
    *   Backend API depends on Neo4j Database and Search Index.
    *   Data Ingestion depends on external APIs and potentially scraped sources.

## 2. Components

*   **Web Application:** Standard client-server model.
*   **Frontend:**
    *   Technology: Single Page Application (SPA) built with React/Next.js (preferred).
    *   Responsibilities: UI, data fetching via Backend API, search/filter interface.
    *   Design: Mobile-first responsive design.
*   **Backend:**
    *   Technology: API server built with Python (Flask/Django preferred).
    *   Responsibilities:
        *   Serving data to the frontend.
        *   Interfacing with the database (Neo4j).
        *   Interfacing with the search index (Elasticsearch/Algolia).
        *   Handling data ingestion pipelines (from APIs, scrapers).
        *   Receiving and storing data suggestions from the user form.
*   **Database:**
    *   Technology: Neo4j Graph Database.
    *   Purpose: Stores entities (Songwriters, Artists, Songs, Albums, Producers, Awards) and their relationships (WROTE, PERFORMED, PRODUCED, APPEARS_ON, RECEIVED_AWARD, etc.).
*   **Search Index:**
    *   Technology: Elasticsearch or Algolia (or similar).
    *   Purpose: Required for performant, faceted search across multiple entity types (G4). Data from Neo4j will be indexed here.
*   **Data Ingestion:**
    *   Type: Separate services or scripts.
    *   Responsibilities:
        *   Fetching data from approved APIs (MusicBrainz, Spotify, etc.).
        *   Performing approved public scraping tasks (Requires specific guidance and approval).
        *   Processing and verifying data before insertion into Neo4j/Search Index.
*   **Data Suggestion Handling:**
    *   Mechanism: A backend endpoint receives submissions from a basic frontend form.
    *   Storage: Submissions stored (e.g., in a separate table/database) for an internal team review/verification queue.

## 3. Data Flow (Simplified)

1.  **Ingestion:** External Data (APIs, Scrapes) -> Data Ingestion Scripts -> Neo4j DB & Search Index.
2.  **User Request:** User -> Frontend -> Backend API.
3.  **Data Retrieval:** Backend API -> Neo4j DB (for relationship/profile data) & Search Index (for search/filter).
4.  **Response:** Backend API -> Frontend -> User.
5.  **Suggestion:** User -> Frontend Form -> Backend API -> Suggestion Queue.

## 4. Key Architectural Decisions

*   Use of a Graph Database (Neo4j) for relationship data (G2).
*   Separation of Search functionality into a dedicated Search Index (G4).
*   Client-Server architecture with a distinct Frontend and Backend.
*   Dedicated Data Ingestion pipeline. 