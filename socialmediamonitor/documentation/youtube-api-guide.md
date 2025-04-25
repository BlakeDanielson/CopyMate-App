# YouTube API Integration Guide

This document details the interaction with the YouTube Data API for the GuardianLens project MVP.

## API Interaction Overview

The GuardianLens backend interacts with the YouTube Data API v3 using the `youtube.readonly` OAuth scope to fetch public data for subscribed channels.

Key API calls:
*   `subscriptions.list`: Fetches the list of channel IDs a linked account is subscribed to (REQ-D02).
*   `channels.list`: Fetches channel details (snippet, statistics, topicDetails) for subscribed channels (REQ-D03).
*   `playlistItems.list`: Fetches video IDs from a channel's uploads playlist (REQ-D05).
*   `videos.list`: Fetches video details (snippet) for recent videos (REQ-D06).

API calls are orchestrated by the Python/FastAPI backend, triggered by the Celery background task system (REQ-D01).

## Caching Strategy

Aggressive caching is implemented to minimize redundant API calls and manage quota usage (REQ-D05). Redis is used as the caching layer (`Tech_Stack.md`).

*   Channel metadata (snippet, statistics, topicDetails) is cached.
*   Recent video metadata (title, description) is cached.
*   Cache TTL (Time To Live) is set to approximately 24 hours (REQ-D05).

The caching layer sits between the backend logic and the YouTube API calls.

## Quota Management

YouTube Data API quotas are a critical constraint (Risk 12.1, `Tech_Spec.md`). The system addresses this through:
*   **Aggressive Caching:** Reduces the number of API calls needed.
*   **Efficient Call Patterns:** Designing backend logic to fetch only necessary data.
*   **Monitoring:** Tracking API quota consumption.
*   **Quota Increase Request:** Initiating a request to Google for increased quota is a critical immediate action (Section 14, `Tech_Spec.md`).

Robust error handling is implemented for API errors, rate limits, and quota exhaustion (REQ-D06).

## Error Handling

The backend implements graceful handling for YouTube API errors, rate limits, and quota issues (REQ-D06). This includes logging errors and potentially notifying the parent if a scan fails due to API problems.

---

*This document will be updated based on the results of the technical spike on API interactions and caching.*