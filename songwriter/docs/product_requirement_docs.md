# Product Requirement Document (PRD) - Songwriter Connect v1.0 (MVP)

This document is derived from the `techspec.md` file.

## 1. Why This Project Exists / Problem It Solves (Overview)

This document outlines the technical specifications for the Minimum Viable Product (MVP) of "Songwriter Connect" (tentative name). This web application will serve as a high-accuracy information portal focused on mainstream pop songwriters active from 2000 onwards. It aims to provide detailed songwriter profiles including credits, awards, and production information, powered by a robust search and filtering engine.

The application will prioritize data accuracy and mobile responsiveness.

## 2. Core Requirements and Goals (MVP v1.0)

*   **(G1 - Core Content):** Deliver dedicated, detailed pages for mainstream pop (2000+) Songwriters, including comprehensive credits (writers, producers), awards/nominations, and basic biographical information.
*   **(G2 - Data Structure):** Store relationship data in a Graph Database (Neo4j) to support future visualization features.
*   **(G3 - Data Accuracy):** Achieve a high level of accuracy for credits and associated metadata through a combination of vetted API sources, permissible public scraping (with guidance), and a verified user suggestion system.
*   **(G4 - Search & Filter):** Implement robust search and filtering capabilities comparable to Genius.com (excluding lyric search), allowing users to effectively find and filter songwriters, songs, artists, and albums.
*   **(G5 - Associated Entities):** Provide basic pages for Artists, Songs, and Albums primarily as linking hubs to showcase songwriter involvement.
*   **(G6 - User Experience):** Offer a clean, intuitive, mobile-responsive user interface for accessing information.
*   **(G7 - Data Suggestion):** Provide a simple mechanism for users to suggest data additions/corrections without requiring user accounts.
*   **(G8 - Platform):** Launch a web application accessible via modern browsers.

## 3. Non-Goals (for MVP v1.0)

*   Graphical network visualization UI.
*   User accounts and authentication.
*   Saving or sharing specific searches or pages.
*   Displaying or searching song lyrics.
*   User annotation features (like Genius).
*   Including detailed credits beyond primary songwriters and producers (e.g., engineers, instrumentalists).
*   Covering genres outside mainstream pop or eras before 2000 extensively.
*   Monetization features.
*   Linux support for any potential related tooling (web app is platform agnostic).

## 4. Target Audience (MVP)

*   Music enthusiasts focused on mainstream pop from 2000 onwards.
*   Industry professionals, journalists, and researchers interested in songwriter credits and relationships within this specific scope.

## 5. Source of Truth

This document serves as the primary source of truth for the project scope and requirements for the MVP v1.0, derived from `techspec.md`. 