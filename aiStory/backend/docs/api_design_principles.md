# API Design Principles & Standards

This document outlines the API design principles and standards for the AI Story Creator application. Adhering to these guidelines ensures a consistent, maintainable, and developer-friendly API.

## RESTful API Conventions

### URI Structure

- Use nouns to represent resources, not verbs
- Use plural nouns for collections
- Use kebab-case for multi-word resource names
- Nest resources logically to show relationships

Examples:
- ✅ `/stories` (for a collection of stories)
- ✅ `/stories/{story_id}/pages` (for pages within a story)
- ❌ `/getStories` (uses verb)
- ❌ `/story` (uses singular noun for collection)

### HTTP Methods

Use appropriate HTTP methods based on the operation:

| Method | Purpose | Examples |
|--------|---------|----------|
| GET | Retrieve resources | GET /stories, GET /stories/{id} |
| POST | Create new resources | POST /stories |
| PUT | Replace a resource completely | PUT /stories/{id} |
| PATCH | Partial update of a resource | PATCH /stories/{id} |
| DELETE | Remove a resource | DELETE /stories/{id} |

### Resource Naming

- Use clear, descriptive resource names
- Be consistent with naming patterns
- Use lowercase letters
- Use hyphens (-) for multi-word resources

Examples:
- ✅ `/user-profiles`
- ❌ `/userProfiles` or `/user_profiles`

## API Versioning

We will use URI path versioning for API versioning to ensure backward compatibility while evolving the API.

Format: `/api/v{major_version}/{resource}`

Examples:
- `/api/v1/stories`
- `/api/v1/users`

This allows us to:
- Introduce breaking changes in newer versions
- Support clients using older versions
- Deprecate and eventually remove older versions

## Response Formats

### Success Responses

All API responses will use JSON format with a consistent structure:

```json
{
  "data": {
    // Resource data
  },
  "meta": {
    "total": 50,
    "page": 1,
    "per_page": 10
  },
  "links": {
    "self": "/api/v1/stories?page=1",
    "next": "/api/v1/stories?page=2",
    "prev": null
  }
}
```

For list endpoints, wrap the results in a data array:

```json
{
  "data": [
    { "id": 1, "title": "Story 1" },
    { "id": 2, "title": "Story 2" }
  ],
  "meta": {...},
  "links": {...}
}
```

### Error Responses

Error responses will follow a consistent structure:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {
      "resource": "story",
      "id": "123"
    }
  }
}
```

## HTTP Status Codes

Use appropriate HTTP status codes to indicate the result of operations:

| Code | Status | Usage |
|------|--------|-------|
| 200 | OK | Successful GET, PUT, or PATCH |
| 201 | Created | Successful POST that created a resource |
| 204 | No Content | Successful operation with no content to return (e.g., DELETE) |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Request conflicts with current state |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Pagination

For list endpoints, use cursor-based or offset-based pagination:

### Offset Pagination

Query parameters:
- `page`: Page number (starting at 1)
- `per_page`: Number of items per page (default: 10, max: 100)

Example: `/api/v1/stories?page=2&per_page=20`

### Cursor Pagination

Query parameters:
- `cursor`: Opaque cursor value from previous response
- `limit`: Number of items to return (default: 10, max: 100)

Example: `/api/v1/stories?cursor=eyJpZCI6MTAwfQ&limit=20`

## Filtering, Sorting, and Fields Selection

### Filtering

Use query parameters to filter collections:

Example: `/api/v1/stories?status=published&category=fantasy`

### Sorting

Use the `sort` parameter with field name and order:

Example: `/api/v1/stories?sort=created_at:desc,title:asc`

### Field Selection

Use the `fields` parameter to request specific fields:

Example: `/api/v1/stories?fields=id,title,created_at`

## Authentication & Authorization

### Authentication

The API will use JWT (JSON Web Tokens) for authentication:

1. Client authenticates via `/auth/login` to receive a JWT
2. Client includes the JWT in subsequent requests:
   - As a Bearer token in the Authorization header: `Authorization: Bearer {token}`

### Authorization

Authorization will be role-based:
- User roles: `user`, `admin`
- Resource-based permissions
- Ownership-based access

## Rate Limiting

API requests will be rate-limited to prevent abuse:

- Rate limits vary by endpoint and authentication status
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Total requests allowed in period
  - `X-RateLimit-Remaining`: Requests remaining in period
  - `X-RateLimit-Reset`: Time (in UTC) when the limit resets

## API Documentation

The API will be documented using OpenAPI 3.0 (via FastAPI's built-in support):

- Interactive documentation available at `/docs`
- Complete OpenAPI spec available at `/openapi.json`
- Each endpoint includes detailed descriptions, parameters, request bodies, responses, and examples

## Versioning & Deprecation

When deprecating an endpoint or feature:

1. Announce deprecation in advance
2. Include a `Deprecation` header in responses
3. Include a `Sunset` header indicating when it will be removed
4. Provide migration documentation to the new endpoint/feature

Example:
```
Deprecation: true
Sunset: Sat, 31 Dec 2023 23:59:59 GMT
Link: <https://api.example.com/docs/migration>; rel="deprecation"
```

## Cross-Origin Resource Sharing (CORS)

The API will support CORS to allow browser-based clients from approved origins:

- Allowed origins defined in configuration
- Support for credentials
- Support for standard and preflight requests

## Webhooks (Future Consideration)

For event-driven integrations, we will provide webhooks:

- Clients can register webhook URLs for specific events
- Events delivered via HTTP POST with a consistent payload format
- Retry logic for failed webhook deliveries
- Webhook signatures for security verification