# Troubleshooting Guide

This document provides guidance on troubleshooting common issues in the GuardianLens project MVP.

## Common Issues and Solutions

*(This section will be populated as common issues are identified during development and operation.)*

## Diagnosing Problems

When encountering issues, use the following techniques:
*   **Check Logs:** Review application logs for error messages and stack traces. Ensure logging levels are configured appropriately in development and production.
*   **Monitoring Dashboards:** Consult monitoring dashboards for system metrics, application performance, and API quota usage.
*   **Tracing:** Implement distributed tracing to follow requests across different components (frontend, backend, database, task queue).

## API Error Handling

Issues related to the YouTube Data API are critical (Risk 12.2, `Tech_Spec.md`).
*   **Identify Error Codes:** Familiarize yourself with common YouTube API error codes and their meanings.
*   **Quota Exceeded:** If quota limits are reached, implement backoff strategies and potentially notify users of delayed scans (REQ-D06).
*   **Rate Limits:** Handle rate limiting errors gracefully with retries and delays.
*   **API Changes:** Be aware of potential YouTube API changes that could break existing functionality. Monitor API documentation and announcements.

## Background Task Failures

Failures in Celery background tasks (e.g., daily scans) need to be investigated.
*   **Check Celery Logs:** Review logs from Celery workers and the message broker (Redis).
*   **Task Retries:** Ensure tasks are configured with appropriate retry mechanisms for transient errors.
*   **Dependencies:** Verify that external dependencies (database, Redis, YouTube API) are accessible and functioning correctly.

## Test Failures

When tests fail, follow these steps to diagnose and resolve issues:
*   **Understand Test Types:** Refer to the [Comprehensive Testing Plan](./development-progress.md#comprehensive-testing-plan) to understand the different types of tests (unit, integration, E2E) and their expected behavior.
*   **Isolate Failures:** Determine if failures are isolated to specific test types, components, or environments.
*   **Check Test Data:** Verify that test data and mocks are correctly set up and current.
*   **Review Recent Changes:** Examine recent code changes that might have affected the failing tests.
*   **Fix and Verify:** After fixing issues, run the tests again to verify the resolution.

---

*This document will evolve as more troubleshooting scenarios are encountered and resolved.*