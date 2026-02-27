# API Reference

## Overview

This document provides complete documentation for all API endpoints, including request/response formats, error handling, and authentication details.

**Base URL:** `http://localhost:8000/api`

**Current API Version:** v1

## Authentication

Currently, **no authentication is required** for API requests. All endpoints are publicly accessible.

> **Note:** Authentication may be implemented in future versions. Plan your integration accordingly.

## Response Format

All API responses follow a consistent JSON format:

**Success Response:**
```json
{
  "data": { /* response payload */ },
  "message": "Success message (if applicable)",
  "status": 200
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status": 400,
  "error_code": "ERROR_CODE"
}
```

## Error Responses

### Common HTTP Status Codes

| Status Code | Description |
|------------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource successfully created |
| 400 | Bad Request - Invalid input parameters |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "detail": "Error description",
  "status": 400,
  "error_code": "INVALID_REQUEST"
}
```

---

## Endpoints

### Health Check

#### GET `/health`

Check API health status.

**Request:**
```bash
curl -X GET http://localhost:8000/api/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Prompts

#### GET `/prompts`

Retrieve all prompts with pagination support.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of prompts to skip for pagination |
| limit | integer | 10 | Maximum number of prompts to return |
| collection_id | string | optional | Filter prompts by collection ID |

**Request:**
```bash
curl -X GET "http://localhost:8000/api/prompts?skip=0&limit=10"
```

**Response (200 OK):**
```json
{
  "prompts": [
    {
      "id": "prompt_123abc",
      "title": "Creative Writing Starter",
      "content": "Write a short story about...",
      "description": "A prompt to inspire creative writing",
      "collection_id": "collection_456def",
      "created_at": "2026-02-27T10:30:00Z",
      "updated_at": "2026-02-27T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

#### POST `/prompts`

Create a new prompt.

**Request Body:**
```json
{
  "title": "Creative Writing Starter",
  "content": "Write a short story about an unexpected adventure...",
  "description": "A prompt to inspire creative writing",
  "collection_id": "collection_456def"
}
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Creative Writing Starter",
    "content": "Write a short story about an unexpected adventure...",
    "description": "A prompt to inspire creative writing",
    "collection_id": "collection_456def"
  }'
```

**Response (201 Created):**
```json
{
  "id": "prompt_123abc",
  "title": "Creative Writing Starter",
  "content": "Write a short story about an unexpected adventure...",
  "description": "A prompt to inspire creative writing",
  "collection_id": "collection_456def",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

**Error Response (422 - Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Error Response (400 - Invalid Collection):**
```json
{
  "detail": "Collection not found",
  "status": 400,
  "error_code": "COLLECTION_NOT_FOUND"
}
```

---

#### GET `/prompts/{prompt_id}`

Retrieve a specific prompt by ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| prompt_id | string | The unique identifier of the prompt |

**Request:**
```bash
curl -X GET http://localhost:8000/api/prompts/prompt_123abc
```

**Response (200 OK):**
```json
{
  "id": "prompt_123abc",
  "title": "Creative Writing Starter",
  "content": "Write a short story about an unexpected adventure...",
  "description": "A prompt to inspire creative writing",
  "collection_id": "collection_456def",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

**Error Response (404 - Not Found):**
```json
{
  "detail": "Prompt not found",
  "status": 404,
  "error_code": "PROMPT_NOT_FOUND"
}
```

---

#### PUT `/prompts/{prompt_id}`

Update an existing prompt.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| prompt_id | string | The unique identifier of the prompt |

**Request Body:**
```json
{
  "title": "Updated Creative Writing Starter",
  "content": "Write a short story about an unexpected adventure with a twist...",
  "description": "An updated prompt to inspire creative writing",
  "collection_id": "collection_456def"
}
```

**Request:**
```bash
curl -X PUT http://localhost:8000/api/prompts/prompt_123abc \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Creative Writing Starter",
    "content": "Write a short story about an unexpected adventure with a twist...",
    "description": "An updated prompt to inspire creative writing",
    "collection_id": "collection_456def"
  }'
```

**Response (200 OK):**
```json
{
  "id": "prompt_123abc",
  "title": "Updated Creative Writing Starter",
  "content": "Write a short story about an unexpected adventure with a twist...",
  "description": "An updated prompt to inspire creative writing",
  "collection_id": "collection_456def",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T11:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Prompt not found",
  "status": 404,
  "error_code": "PROMPT_NOT_FOUND"
}
```

**Error Response (422 - Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

#### DELETE `/prompts/{prompt_id}`

Delete a prompt.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| prompt_id | string | The unique identifier of the prompt |

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/prompts/prompt_123abc
```

**Response (204 No Content):**
```
(empty response body)
```

**Error Response (404):**
```json
{
  "detail": "Prompt not found",
  "status": 404,
  "error_code": "PROMPT_NOT_FOUND"
}
```

---

### Collections

#### GET `/collections`

Retrieve all collections with pagination support.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of collections to skip for pagination |
| limit | integer | 10 | Maximum number of collections to return |

**Request:**
```bash
curl -X GET "http://localhost:8000/api/collections?skip=0&limit=10"
```

**Response (200 OK):**
```json
{
  "collections": [
    {
      "id": "collection_456def",
      "name": "Creative Writing",
      "description": "A collection of prompts for creative writing",
      "created_at": "2026-02-27T09:00:00Z"
    }
  ],
  "total": 1
}
```

**Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

#### POST `/collections`

Create a new collection.

**Request Body:**
```json
{
  "name": "Creative Writing",
  "description": "A collection of prompts for creative writing"
}
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Creative Writing",
    "description": "A collection of prompts for creative writing"
  }'
```

**Response (201 Created):**
```json
{
  "id": "collection_456def",
  "name": "Creative Writing",
  "description": "A collection of prompts for creative writing",
  "created_at": "2026-02-27T09:00:00Z"
}
```

**Error Response (422 - Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

#### GET `/collections/{collection_id}`

Retrieve a specific collection by ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| collection_id | string | The unique identifier of the collection |

**Request:**
```bash
curl -X GET http://localhost:8000/api/collections/collection_456def
```

**Response (200 OK):**
```json
{
  "id": "collection_456def",
  "name": "Creative Writing",
  "description": "A collection of prompts for creative writing",
  "created_at": "2026-02-27T09:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Collection not found",
  "status": 404,
  "error_code": "COLLECTION_NOT_FOUND"
}
```

---

#### PUT `/collections/{collection_id}`

Update an existing collection.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| collection_id | string | The unique identifier of the collection |

**Request Body:**
```json
{
  "name": "Creative Writing Prompts",
  "description": "An updated collection of prompts for creative writing"
}
```

**Request:**
```bash
curl -X PUT http://localhost:8000/api/collections/collection_456def \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Creative Writing Prompts",
    "description": "An updated collection of prompts for creative writing"
  }'
```

**Response (200 OK):**
```json
{
  "id": "collection_456def",
  "name": "Creative Writing Prompts",
  "description": "An updated collection of prompts for creative writing",
  "created_at": "2026-02-27T09:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Collection not found",
  "status": 404,
  "error_code": "COLLECTION_NOT_FOUND"
}
```

**Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

#### DELETE `/collections/{collection_id}`

Delete a collection.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| collection_id | string | The unique identifier of the collection |

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/collections/collection_456def
```

**Response (204 No Content):**
```
(empty response body)
```

**Error Response (404):**
```json
{
  "detail": "Collection not found",
  "status": 404,
  "error_code": "COLLECTION_NOT_FOUND"
}
```

---

## Rate Limiting

Currently, **no rate limiting is enforced**. All endpoints accept unlimited requests.

> **Note:** Rate limiting may be implemented in future versions.

## Data Types

| Type | Format | Example |
|------|--------|---------|
| string | UTF-8 text | "Hello World" |
| integer | 32-bit integer | 42 |
| datetime | ISO 8601 | "2026-02-27T10:30:00Z" |

## Field Constraints

| Field | Min Length | Max Length |
|-------|-----------|-----------|
| title (Prompt) | 1 | 200 |
| content (Prompt) | 1 | unlimited |
| description (Prompt) | - | 500 |
| name (Collection) | 1 | 100 |
| description (Collection) | - | 500 |

## Support

For issues, questions, or feature requests, please refer to the project's issue tracker or contact the development team.