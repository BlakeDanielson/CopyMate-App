# Analysis Engine Keyword Management

This document details the process and tooling for managing the keyword lists used by the GuardianLens analysis engine MVP.

## Analysis Technique (MVP)

The MVP analysis engine uses keyword and pattern matching on text metadata only (Channel Title/Description, last 10 Video Titles/Descriptions) (REQ-A01, Section 10.2, `Tech_Spec.md`). It does not analyze video, audio, or image content.

## Risk Categories (Initial Set)

The initial set of risk categories for the MVP includes (Section 10.1, `Tech_Spec.md`):
*   Hate Speech/Extreme Ideology
*   Self-Harm/Suicide Promotion
*   Graphic Violence
*   Explicit/Adult Content
*   Bullying Keywords
*   Dangerous Challenges Keywords
*   Misinformation Keywords (YouTube specific)

## Keyword Management Process

Maintaining internal, updatable lists of keywords and patterns for each risk category is crucial (REQ-A02, Open Issue 10.3, `PRD.md`).
*   A defined process is needed for adding, modifying, and removing keywords.
*   Consider versioning keyword lists to track changes.
*   The process should include how updates are deployed to the analysis engine.

## Testing Keyword Logic

Changes to keyword lists should be tested to ensure they correctly identify relevant content and minimize false positives/negatives. This could involve testing against a dataset of known channel/video metadata.
This testing is part of the overall [Comprehensive Testing Plan](./development-progress.md#comprehensive-testing-plan).

---

*This document requires significant content based on the finalized keyword lists and the implemented management process.*