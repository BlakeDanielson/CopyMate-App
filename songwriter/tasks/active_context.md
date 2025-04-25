# Active Context - Songwriter Connect v1.0 (MVP)

*As of: 2025-04-17*

*   **Current Work Focus:** Beginning implementation of Feature F1: Songwriter Profiles (Frontend - Next.js + ShadCN UI).
*   **Active Decisions/Considerations:**
    *   Confirming choice between Flask/Django for Backend.
    *   Evaluating Elasticsearch vs. Algolia for Search Index.
    *   Planning initial data source selection (APIs, approved scrapes).
*   **Recent Changes:**
    *   Created project directory structure (`docs`, `tasks`, `src`, etc.).
    *   Created core documentation files (`product_requirement_docs.md`, `architecture.md`, `technical.md`, `tasks_plan.md`, `active_context.md`).
    *   Populated core documentation files based on `techspec.md`.
*   **Next Steps:**
    *   Set up Next.js project (if needed) and integrate ShadCN UI.
    *   Create initial Songwriter Profile page component (`src/app/songwriters/[id]/page.tsx`).
    *   Design and implement basic layout using ShadCN components with placeholder data.
    *   Break down MVP features in `tasks/tasks_plan.md` into smaller, actionable development tasks.
    *   Begin setting up development environment (Backend, DB, Search Index).
    *   Start development on core features, likely beginning with data modeling in Neo4j and basic backend/frontend setup. 