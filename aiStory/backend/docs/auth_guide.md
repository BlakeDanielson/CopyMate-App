# Authentication and Authorization Guide

This guide provides comprehensive documentation for the authentication and authorization system. It covers the authentication flow, authorization mechanisms, security features, examples of protecting endpoints, error handling, and environmental configuration options.

## Authentication Flow

The authentication flow consists of the following steps:

1.  **Registration:** Users register with their email and password.
2.  **Login:** Users log in with their email and password.
3.  **Token Generation:** Upon successful login, the server generates a JWT (JSON Web Token) and a refresh token.
4.  **Token Refresh:** Users can refresh their JWT using the refresh token.

### Registration

To register a new user, send a POST request to the `/auth/register` endpoint with the following data:

```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

A successful registration returns a 201 status code.

### Login

To log in, send a POST request to the `/auth/login` endpoint with the following data:

```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

A successful login returns a 200 status code with the following JSON response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### Token Refresh

To refresh the access token, send a POST request to the `/auth/refresh` endpoint with the following data:

```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

A successful token refresh returns a 200 status code with the following JSON response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

## Authorization Mechanisms

The authorization system uses role-based access control (RBAC). Users are assigned roles, and each role has specific permissions.

### Roles

The following roles are defined:

*   `admin`: Has full access to all resources.
*   `user`: Has access to their own resources.

### Protecting Endpoints

To protect an endpoint, use the `require_role` decorator. For example:

```python
from backend.utils.auth import require_role

@router.get("/admin", dependencies=[Depends(require_role("admin"))])
async def admin_route():
    return {"message": "Admin route"}
```

This endpoint is only accessible to users with the `admin` role.

## Security Features

The authentication system includes the following security features:

*   **Rate Limiting:** Limits the number of requests a user can make in a given time period.
*   **Token Expiration:** JWTs expire after a short period of time (e.g., 15 minutes). Refresh tokens expire after a longer period of time (e.g., 7 days).

### Rate Limiting

Rate limiting is implemented using a middleware that limits the number of requests from a single IP address.

### Token Expiration

JWTs expire after a short period of time to minimize the impact of a compromised token. Refresh tokens expire after a longer period of time to allow users to refresh their access tokens without having to log in again.

## Examples

### Protecting Endpoints with Different Roles

```python
from fastapi import Depends, APIRouter
from backend.utils.auth import require_role

router = APIRouter()

@router.get("/admin", dependencies=[Depends(require_role("admin"))])
async def admin_route():
    return {"message": "Admin route"}

@router.get("/user", dependencies=[Depends(require_role("user"))])
async def user_route():
    return {"message": "User route"}

@router.get("/public")
async def public_route():
    return {"message": "Public route"}
```

## Error Handling and Status Codes

The API returns the following error status codes:

*   `400 Bad Request`: Invalid request data.
*   `401 Unauthorized`: Authentication required.
*   `403 Forbidden`: User does not have permission to access the resource.
*   `404 Not Found`: Resource not found.
*   `500 Internal Server Error`: An unexpected error occurred.

## Environmental Configuration Options

The following environment variables are used to configure the authentication system:

*   `JWT_SECRET_KEY`: The secret key used to sign JWTs.
*   `REFRESH_TOKEN_EXPIRE_MINUTES`: The expiration time for refresh tokens (in minutes).
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: The expiration time for access tokens (in minutes).