# ReWear API Documentation

**Version:** 1.0.0  
**Generated:** 2025-07-12 12:59:46

Community Clothing Exchange Platform with Real-time Features

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require JWT Bearer token authentication:
```
Authorization: Bearer <your_jwt_token>
```

---

## Other

### GET /

**Root**

Health check endpoint

#### Responses

**200** - Successful Response

#### Example

```bash
curl -X GET "http://localhost:8000/"
```
---

### GET /health

**Health Check**

Detailed health check

#### Responses

**200** - Successful Response

#### Example

```bash
curl -X GET "http://localhost:8000/health"
```
---

## Authentication

### POST /api/v1/auth/register

**Register User**

Register a new user with welcome notifications

#### Request Body

**Content-Type:** `application/json`

```json
{
  "email": "user@example.com",
  "username": "string",
  "first_name": "example_value",
  "last_name": "example_value",
  "bio": "example_value",
  "city": "example_value",
  "state": "example_value",
  "country": "example_value",
  "password": "string"
}
```

#### Responses

**201** - Successful Response

```json
{
  "email": "user@example.com",
  "username": "string",
  "first_name": "example_value",
  "last_name": "example_value",
  "bio": "example_value",
  "city": "example_value",
  "state": "example_value",
  "country": "example_value",
  "id": 123,
  "points_balance": 123,
  "total_points_earned": 123,
  "total_points_spent": 123,
  "is_active": true,
  "is_verified": true,
  "is_admin": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "last_login": "example_value",
  "profile_image_url": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### POST /api/v1/auth/login

**Login User**

OAuth2 compatible token login, get an access token for future requests

#### Request Body

**Content-Type:** `application/x-www-form-urlencoded`

```json
{
  "grant_type": "example_value",
  "username": "string",
  "password": "string",
  "scope": "string",
  "client_id": "example_value",
  "client_secret": "example_value"
}
```

#### Responses

**200** - Successful Response

```json
{
  "access_token": "string",
  "token_type": "string",
  "expires_in": 123
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### POST /api/v1/auth/login-json

**Login User Json**

JSON login endpoint (alternative to OAuth2 form)

#### Request Body

**Content-Type:** `application/json`

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

#### Responses

**200** - Successful Response

```json
{
  "access_token": "string",
  "token_type": "string",
  "expires_in": 123
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### GET /api/v1/auth/me

**Get Current User Profile**

Get current user profile

#### Responses

**200** - Successful Response

```json
{
  "email": "user@example.com",
  "username": "string",
  "first_name": "example_value",
  "last_name": "example_value",
  "bio": "example_value",
  "city": "example_value",
  "state": "example_value",
  "country": "example_value",
  "id": 123,
  "points_balance": 123,
  "total_points_earned": 123,
  "total_points_spent": 123,
  "is_active": true,
  "is_verified": true,
  "is_admin": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "last_login": "example_value",
  "profile_image_url": "example_value"
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### PUT /api/v1/auth/me

**Update Current User Profile**

Update current user profile

#### Request Body

**Content-Type:** `application/json`

```json
{
  "first_name": "example_value",
  "last_name": "example_value",
  "bio": "example_value",
  "city": "example_value",
  "state": "example_value",
  "country": "example_value"
}
```

#### Responses

**200** - Successful Response

```json
{
  "email": "user@example.com",
  "username": "string",
  "first_name": "example_value",
  "last_name": "example_value",
  "bio": "example_value",
  "city": "example_value",
  "state": "example_value",
  "country": "example_value",
  "id": 123,
  "points_balance": 123,
  "total_points_earned": 123,
  "total_points_spent": 123,
  "is_active": true,
  "is_verified": true,
  "is_admin": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "last_login": "example_value",
  "profile_image_url": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### POST /api/v1/auth/refresh

**Refresh Token**

Refresh access token

#### Responses

**200** - Successful Response

```json
{
  "access_token": "string",
  "token_type": "string",
  "expires_in": 123
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### POST /api/v1/auth/logout

**Logout User**

Logout user (client should discard the token)

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### POST /api/v1/auth/resend-welcome

**Resend Welcome Email**

Resend welcome email (for testing or if user didn't receive it)

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/resend-welcome" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### POST /api/v1/auth/test-welcome-email

**Test Welcome Email**

Send test welcome email to specified address (for development)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `test_email` | string | query | ✅ |  |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/test-welcome-email" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

## Users

### GET /api/v1/users/me/dashboard

**Get User Dashboard**

Get user dashboard data

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/dashboard" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/users/me/items

**Get User Items**

Get current user's items

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `status_filter` | string | query | ❌ | Filter by item status |
| `limit` | integer | query | ❌ | Number of items to return |
| `offset` | integer | query | ❌ | Number of items to skip |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "title": "string",
    "brand": "example_value",
    "size": "string",
    "condition": "string",
    "points_value": 123,
    "primary_image_url": "example_value",
    "created_at": "2023-12-01T10:00:00Z"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/users/me/swaps

**Get User Swaps**

Get current user's swaps (sent and received)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_type` | string | query | ❌ | Filter by 'sent' or 'received' |
| `status_filter` | string | query | ❌ | Filter by swap status |
| `limit` | integer | query | ❌ | Number of swaps to return |
| `offset` | integer | query | ❌ | Number of swaps to skip |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "swap_type": "string",
    "status": "string",
    "points_offered": "example_value",
    "created_at": "2023-12-01T10:00:00Z",
    "item": "...",
    "offered_item": "example_value"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/swaps" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/users/me/points

**Get User Point History**

Get current user's point transaction history

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `transaction_type` | string | query | ❌ | Filter by transaction type |
| `limit` | integer | query | ❌ | Number of transactions to return |
| `offset` | integer | query | ❌ | Number of transactions to skip |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "amount": 123,
    "transaction_type": "string",
    "description": "string",
    "created_at": "2023-12-01T10:00:00Z"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/points" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/users/{user_id}

**Get User Public Profile**

Get public user profile

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `user_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
{
  "id": 123,
  "username": "string",
  "first_name": "example_value",
  "last_name": "example_value",
  "profile_image_url": "example_value",
  "city": "example_value",
  "state": "example_value",
  "country": "example_value",
  "created_at": "2023-12-01T10:00:00Z"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/123"
```
---

### GET /api/v1/users/{user_id}/items

**Get User Public Items**

Get public user's available items

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `user_id` | integer | path | ✅ |  |
| `limit` | integer | query | ❌ | Number of items to return |
| `offset` | integer | query | ❌ | Number of items to skip |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "title": "string",
    "brand": "example_value",
    "size": "string",
    "condition": "string",
    "points_value": 123,
    "primary_image_url": "example_value",
    "created_at": "2023-12-01T10:00:00Z"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/123/items"
```
---

## Items

### POST /api/v1/items/

**Create Item**

Create a new item listing with enhanced validation and notifications

#### Request Body

**Content-Type:** `application/json`

```json
{
  "title": "string",
  "description": "string",
  "brand": "example_value",
  "size": "string",
  "condition": "string",
  "color": "example_value",
  "material": "example_value",
  "tags": "example_value",
  "pickup_location": "example_value",
  "shipping_available": true,
  "original_price": "example_value",
  "category_id": 123,
  "points_value": "example_value"
}
```

#### Responses

**201** - Successful Response

```json
{
  "title": "string",
  "description": "string",
  "brand": "example_value",
  "size": "string",
  "condition": "string",
  "color": "example_value",
  "material": "example_value",
  "tags": "example_value",
  "pickup_location": "example_value",
  "shipping_available": true,
  "original_price": "example_value",
  "id": 123,
  "category_id": 123,
  "owner_id": 123,
  "status": "string",
  "points_value": 123,
  "image_urls": "example_value",
  "primary_image_url": "example_value",
  "is_active": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "published_at": "example_value",
  "owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "category": {
    "id": "...",
    "name": "...",
    "slug": "...",
    "description": "...",
    "icon_name": "...",
    "color_code": "...",
    "is_active": "...",
    "created_at": "..."
  }
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### GET /api/v1/items/

**List Items**

Enhanced item listing with integrated search and filtering

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `q` | string | query | ❌ | Search query |
| `category_id` | string | query | ❌ | Filter by category |
| `size` | string | query | ❌ | Filter by size |
| `condition` | string | query | ❌ | Filter by condition |
| `min_points` | string | query | ❌ | Minimum points value |
| `max_points` | string | query | ❌ | Maximum points value |
| `brand` | string | query | ❌ | Filter by brand |
| `color` | string | query | ❌ | Filter by color |
| `material` | string | query | ❌ | Filter by material |
| `tags` | string | query | ❌ | Comma-separated tags |
| `location` | string | query | ❌ | Filter by location |
| `sort_by` | string | query | ❌ | Sort by: created_at, points_value, title, relevance |
| `sort_order` | string | query | ❌ | Sort order: asc, desc |
| `limit` | integer | query | ❌ | Number of items to return |
| `offset` | integer | query | ❌ | Number of items to skip |
| `include_shipping` | string | query | ❌ | Include items with shipping |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "title": "string",
    "description": "string",
    "brand": "example_value",
    "size": "string",
    "condition": "string",
    "color": "example_value",
    "material": "example_value",
    "tags": "example_value",
    "points_value": 123,
    "primary_image_url": "example_value",
    "image_urls": "example_value",
    "shipping_available": true,
    "created_at": "2023-12-01T10:00:00Z",
    "owner": "...",
    "category": "..."
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/items/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/items/trending

**Get Trending Items**

Get trending items based on recent swap activity and views

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `limit` | integer | query | ❌ | Number of trending items |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/items/trending" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/items/{item_id}

**Get Item**

Get item details with enhanced information

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
{
  "title": "string",
  "description": "string",
  "brand": "example_value",
  "size": "string",
  "condition": "string",
  "color": "example_value",
  "material": "example_value",
  "tags": "example_value",
  "pickup_location": "example_value",
  "shipping_available": true,
  "original_price": "example_value",
  "id": 123,
  "category_id": 123,
  "owner_id": 123,
  "status": "string",
  "points_value": 123,
  "image_urls": "example_value",
  "primary_image_url": "example_value",
  "is_active": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "published_at": "example_value",
  "owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "category": {
    "id": "...",
    "name": "...",
    "slug": "...",
    "description": "...",
    "icon_name": "...",
    "color_code": "...",
    "is_active": "...",
    "created_at": "..."
  }
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/items/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### PUT /api/v1/items/{item_id}

**Update Item**

Update item (only by owner) with validation

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |

#### Request Body

**Content-Type:** `application/json`

```json
{
  "title": "example_value",
  "description": "example_value",
  "brand": "example_value",
  "size": "example_value",
  "condition": "example_value",
  "color": "example_value",
  "material": "example_value",
  "tags": "example_value",
  "pickup_location": "example_value",
  "shipping_available": "example_value",
  "original_price": "example_value"
}
```

#### Responses

**200** - Successful Response

```json
{
  "title": "string",
  "description": "string",
  "brand": "example_value",
  "size": "string",
  "condition": "string",
  "color": "example_value",
  "material": "example_value",
  "tags": "example_value",
  "pickup_location": "example_value",
  "shipping_available": true,
  "original_price": "example_value",
  "id": 123,
  "category_id": 123,
  "owner_id": 123,
  "status": "string",
  "points_value": 123,
  "image_urls": "example_value",
  "primary_image_url": "example_value",
  "is_active": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "published_at": "example_value",
  "owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "category": {
    "id": "...",
    "name": "...",
    "slug": "...",
    "description": "...",
    "icon_name": "...",
    "color_code": "...",
    "is_active": "...",
    "created_at": "..."
  }
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/items/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### DELETE /api/v1/items/{item_id}

**Delete Item**

Delete/deactivate item (only by owner)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X DELETE "http://localhost:8000/api/v1/items/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/items/{item_id}/similar

**Get Similar Items**

Get items similar to the specified item

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |
| `limit` | integer | query | ❌ | Number of similar items |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/items/123/similar" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/items/categories/

**List Categories**

List all categories with optional item counts

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `include_inactive` | boolean | query | ❌ | Include inactive categories |
| `with_counts` | boolean | query | ❌ | Include item counts per category |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "name": "string",
    "slug": "string",
    "description": "example_value",
    "icon_name": "example_value",
    "color_code": "example_value",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/items/categories/"
```
---

### GET /api/v1/items/categories/{category_id}/items

**List Category Items**

List items in a specific category with enhanced sorting

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `category_id` | integer | path | ✅ |  |
| `sort_by` | string | query | ❌ | Sort by: created_at, points_value, title |
| `limit` | integer | query | ❌ | Number of items to return |
| `offset` | integer | query | ❌ | Number of items to skip |

#### Responses

**200** - Successful Response

```json
[
  {
    "id": 123,
    "title": "string",
    "description": "string",
    "brand": "example_value",
    "size": "string",
    "condition": "string",
    "color": "example_value",
    "material": "example_value",
    "tags": "example_value",
    "points_value": 123,
    "primary_image_url": "example_value",
    "image_urls": "example_value",
    "shipping_available": true,
    "created_at": "2023-12-01T10:00:00Z",
    "owner": "...",
    "category": "..."
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/items/categories/123/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

## Swaps

### POST /api/v1/swaps/

**Create Swap Request**

Create a new swap request with real-time notification

#### Request Body

**Content-Type:** `application/json`

```json
{
  "requester_message": "example_value",
  "item_id": 123,
  "swap_type": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value"
}
```

#### Responses

**201** - Successful Response

```json
{
  "requester_message": "example_value",
  "id": 123,
  "requester_id": 123,
  "item_id": 123,
  "item_owner_id": 123,
  "swap_type": "string",
  "status": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value",
  "owner_response": "example_value",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "expires_at": "example_value",
  "responded_at": "example_value",
  "completed_at": "example_value",
  "requester": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item_owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item": {
    "id": "...",
    "title": "...",
    "brand": "...",
    "size": "...",
    "condition": "...",
    "points_value": "...",
    "primary_image_url": "...",
    "created_at": "..."
  },
  "offered_item": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/swaps/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### GET /api/v1/swaps/

**List User Swaps**

List current user's swaps (sent and received)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_type` | string | query | ❌ | Filter by 'sent' or 'received' |
| `status_filter` | string | query | ❌ | Filter by swap status |
| `limit` | integer | query | ❌ |  |
| `offset` | integer | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
[
  {
    "requester_message": "example_value",
    "id": 123,
    "requester_id": 123,
    "item_id": 123,
    "item_owner_id": 123,
    "swap_type": "string",
    "status": "string",
    "offered_item_id": "example_value",
    "points_offered": "example_value",
    "owner_response": "example_value",
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z",
    "expires_at": "example_value",
    "responded_at": "example_value",
    "completed_at": "example_value",
    "requester": "...",
    "item_owner": "...",
    "item": "...",
    "offered_item": "example_value"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/swaps/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### PUT /api/v1/swaps/{swap_id}/accept

**Accept Swap**

Accept a swap request with real-time notification

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_id` | integer | path | ✅ |  |
| `owner_response` | string | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
{
  "requester_message": "example_value",
  "id": 123,
  "requester_id": 123,
  "item_id": 123,
  "item_owner_id": 123,
  "swap_type": "string",
  "status": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value",
  "owner_response": "example_value",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "expires_at": "example_value",
  "responded_at": "example_value",
  "completed_at": "example_value",
  "requester": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item_owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item": {
    "id": "...",
    "title": "...",
    "brand": "...",
    "size": "...",
    "condition": "...",
    "points_value": "...",
    "primary_image_url": "...",
    "created_at": "..."
  },
  "offered_item": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/swaps/123/accept" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### PUT /api/v1/swaps/{swap_id}/reject

**Reject Swap**

Reject a swap request with real-time notification

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_id` | integer | path | ✅ |  |
| `owner_response` | string | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
{
  "requester_message": "example_value",
  "id": 123,
  "requester_id": 123,
  "item_id": 123,
  "item_owner_id": 123,
  "swap_type": "string",
  "status": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value",
  "owner_response": "example_value",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "expires_at": "example_value",
  "responded_at": "example_value",
  "completed_at": "example_value",
  "requester": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item_owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item": {
    "id": "...",
    "title": "...",
    "brand": "...",
    "size": "...",
    "condition": "...",
    "points_value": "...",
    "primary_image_url": "...",
    "created_at": "..."
  },
  "offered_item": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/swaps/123/reject" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### PUT /api/v1/swaps/{swap_id}/complete

**Complete Swap**

Mark swap as completed with real-time notifications and points handling

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
{
  "requester_message": "example_value",
  "id": 123,
  "requester_id": 123,
  "item_id": 123,
  "item_owner_id": 123,
  "swap_type": "string",
  "status": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value",
  "owner_response": "example_value",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "expires_at": "example_value",
  "responded_at": "example_value",
  "completed_at": "example_value",
  "requester": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item_owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item": {
    "id": "...",
    "title": "...",
    "brand": "...",
    "size": "...",
    "condition": "...",
    "points_value": "...",
    "primary_image_url": "...",
    "created_at": "..."
  },
  "offered_item": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/swaps/123/complete" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### GET /api/v1/swaps/{swap_id}

**Get Swap**

Get swap details (only if user is involved)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
{
  "requester_message": "example_value",
  "id": 123,
  "requester_id": 123,
  "item_id": 123,
  "item_owner_id": 123,
  "swap_type": "string",
  "status": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value",
  "owner_response": "example_value",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "expires_at": "example_value",
  "responded_at": "example_value",
  "completed_at": "example_value",
  "requester": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item_owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item": {
    "id": "...",
    "title": "...",
    "brand": "...",
    "size": "...",
    "condition": "...",
    "points_value": "...",
    "primary_image_url": "...",
    "created_at": "..."
  },
  "offered_item": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/swaps/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### PUT /api/v1/swaps/{swap_id}/cancel

**Cancel Swap**

Cancel a swap request (only by requester, only if pending)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `swap_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
{
  "requester_message": "example_value",
  "id": 123,
  "requester_id": 123,
  "item_id": 123,
  "item_owner_id": 123,
  "swap_type": "string",
  "status": "string",
  "offered_item_id": "example_value",
  "points_offered": "example_value",
  "owner_response": "example_value",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "expires_at": "example_value",
  "responded_at": "example_value",
  "completed_at": "example_value",
  "requester": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item_owner": {
    "id": "...",
    "username": "...",
    "first_name": "...",
    "last_name": "...",
    "profile_image_url": "...",
    "city": "...",
    "state": "...",
    "country": "...",
    "created_at": "..."
  },
  "item": {
    "id": "...",
    "title": "...",
    "brand": "...",
    "size": "...",
    "condition": "...",
    "points_value": "...",
    "primary_image_url": "...",
    "created_at": "..."
  },
  "offered_item": "example_value"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/swaps/123/cancel" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### GET /api/v1/swaps/stats/summary

**Get Swap Stats**

Get swap statistics for the current user

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/swaps/stats/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

## Admin

### GET /api/v1/admin/dashboard

**Get Admin Dashboard**

Get admin dashboard with platform statistics

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/admin/dashboard" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/admin/users

**List All Users**

List all users (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `is_active` | string | query | ❌ | Filter by active status |
| `is_admin` | string | query | ❌ | Filter by admin status |
| `search` | string | query | ❌ | Search in username or email |
| `limit` | integer | query | ❌ |  |
| `offset` | integer | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
[
  {
    "email": "user@example.com",
    "username": "string",
    "first_name": "example_value",
    "last_name": "example_value",
    "bio": "example_value",
    "city": "example_value",
    "state": "example_value",
    "country": "example_value",
    "id": 123,
    "points_balance": 123,
    "total_points_earned": 123,
    "total_points_spent": 123,
    "is_active": true,
    "is_verified": true,
    "is_admin": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z",
    "last_login": "example_value",
    "profile_image_url": "example_value"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### PUT /api/v1/admin/users/{user_id}/toggle-active

**Toggle User Active Status**

Toggle user active status (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `user_id` | integer | path | ✅ |  |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/123/toggle-active" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### GET /api/v1/admin/items

**List All Items**

List all items (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `status_filter` | string | query | ❌ | Filter by item status |
| `category_id` | string | query | ❌ | Filter by category |
| `search` | string | query | ❌ | Search in title or description |
| `limit` | integer | query | ❌ |  |
| `offset` | integer | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
[
  {
    "title": "string",
    "description": "string",
    "brand": "example_value",
    "size": "string",
    "condition": "string",
    "color": "example_value",
    "material": "example_value",
    "tags": "example_value",
    "pickup_location": "example_value",
    "shipping_available": true,
    "original_price": "example_value",
    "id": 123,
    "category_id": 123,
    "owner_id": 123,
    "status": "string",
    "points_value": 123,
    "image_urls": "example_value",
    "primary_image_url": "example_value",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z",
    "published_at": "example_value",
    "owner": "...",
    "category": "..."
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/admin/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### PUT /api/v1/admin/items/{item_id}/approve

**Approve Item**

Approve an item listing (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |
| `admin_notes` | string | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/admin/items/123/approve" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### PUT /api/v1/admin/items/{item_id}/reject

**Reject Item**

Reject an item listing (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |
| `rejection_reason` | string | query | ❌ |  |
| `admin_notes` | string | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/admin/items/123/reject" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```
---

### GET /api/v1/admin/swaps

**List All Swaps**

List all swaps (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `status_filter` | string | query | ❌ | Filter by swap status |
| `swap_type` | string | query | ❌ | Filter by swap type |
| `limit` | integer | query | ❌ |  |
| `offset` | integer | query | ❌ |  |

#### Responses

**200** - Successful Response

```json
[
  {
    "requester_message": "example_value",
    "id": 123,
    "requester_id": 123,
    "item_id": 123,
    "item_owner_id": 123,
    "swap_type": "string",
    "status": "string",
    "offered_item_id": "example_value",
    "points_offered": "example_value",
    "owner_response": "example_value",
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z",
    "expires_at": "example_value",
    "responded_at": "example_value",
    "completed_at": "example_value",
    "requester": "...",
    "item_owner": "...",
    "item": "...",
    "offered_item": "example_value"
  }
]
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/admin/swaps" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### POST /api/v1/admin/categories

**Create Category**

Create a new category (admin only)

#### Request Body

**Content-Type:** `application/json`

```json
{
  "name": "string",
  "description": "example_value",
  "icon_name": "example_value",
  "color_code": "example_value"
}
```

#### Responses

**200** - Successful Response

```json
{
  "id": 123,
  "name": "string",
  "slug": "string",
  "description": "example_value",
  "icon_name": "example_value",
  "color_code": "example_value",
  "is_active": true,
  "created_at": "2023-12-01T10:00:00Z"
}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/admin/categories" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### PUT /api/v1/admin/categories/{category_id}

**Update Category**

Update a category (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `category_id` | integer | path | ✅ |  |

#### Request Body

**Content-Type:** `application/json`

```json
{
  "name": "example_value",
  "description": "example_value",
  "icon_name": "example_value",
  "color_code": "example_value",
  "is_active": "example_value"
}
```

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X PUT "http://localhost:8000/api/v1/admin/categories/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### GET /api/v1/admin/analytics

**Get Platform Analytics**

Get detailed platform analytics (admin only)

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/admin/analytics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

## Upload

### POST /api/v1/upload/images

**Upload Image**

Upload a single image

#### Request Body

**Content-Type:** `multipart/form-data`

```json
{
  "file": "string"
}
```

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/upload/images" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### POST /api/v1/upload/images/multiple

**Upload Multiple Images**

Upload multiple images at once (max 5 images)

#### Request Body

**Content-Type:** `multipart/form-data`

```json
{
  "files": [
    "string"
  ]
}
```

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/upload/images/multiple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### POST /api/v1/upload/items/{item_id}/images

**Upload Item Images**

Upload images for a specific item

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |

#### Request Body

**Content-Type:** `multipart/form-data`

```json
{
  "files": [
    "string"
  ],
  "set_primary": 123
}
```

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/upload/items/123/images" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "example": "data"
  }'
```
---

### DELETE /api/v1/upload/items/{item_id}/images

**Remove Item Image**

Remove an image from an item

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `item_id` | integer | path | ✅ |  |

#### Request Body

**Content-Type:** `application/x-www-form-urlencoded`

```json
{
  "image_url": "string"
}
```

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X DELETE "http://localhost:8000/api/v1/upload/items/123/images" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/upload/images/{filename}

**Get Image**

Serve uploaded images

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `filename` | string | path | ✅ |  |

#### Responses

**200** - Successful Response

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/upload/images/123"
```
---

## WebSockets

### GET /api/v1/ws/test-notifications

**Test Notification Page**

Test page for WebSocket notifications (development only)

#### Responses

**200** - Successful Response

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/ws/test-notifications"
```
---

### POST /api/v1/ws/admin/send-test-notification

**Send Test Notification**

Send test notification to specific user (admin only)

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `user_id` | integer | query | ✅ |  |
| `message` | string | query | ✅ |  |
| `notification_type` | string | query | ❌ |  |

#### Responses

**200** - Successful Response

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/ws/admin/send-test-notification" \
  -H "Content-Type: application/json"
```
---

### GET /api/v1/ws/admin/websocket-stats

**Get Websocket Stats**

Get WebSocket connection statistics (admin only)

#### Responses

**200** - Successful Response

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/ws/admin/websocket-stats"
```
---

## Enhanced Search

### GET /api/v1/search/items

**Advanced Search Items**

Advanced search for items with comprehensive filtering and ranking

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `q` | string | query | ❌ | Search query |
| `category_id` | string | query | ❌ | Filter by category |
| `size` | string | query | ❌ | Filter by size |
| `condition` | string | query | ❌ | Filter by condition |
| `min_points` | string | query | ❌ | Minimum points value |
| `max_points` | string | query | ❌ | Maximum points value |
| `brand` | string | query | ❌ | Filter by brand |
| `color` | string | query | ❌ | Filter by color |
| `material` | string | query | ❌ | Filter by material |
| `tags` | string | query | ❌ | Comma-separated tags |
| `location` | string | query | ❌ | Filter by pickup location |
| `limit` | integer | query | ❌ | Number of items to return |
| `offset` | integer | query | ❌ | Number of items to skip |
| `include_shipping` | string | query | ❌ | Include items with shipping |
| `sort_by` | string | query | ❌ | Sort by: relevance, date, points_asc, points_desc |

#### Responses

**200** - Successful Response

```json
{}
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/search/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/search/suggestions

**Get Search Suggestions**

Get search suggestions for autocomplete

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `q` | string | query | ✅ | Partial search query |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/search/suggestions"
```
---

### GET /api/v1/search/popular

**Get Popular Searches**

Get popular search terms and trending items

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `limit` | integer | query | ❌ | Number of popular terms to return |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/search/popular"
```
---

### GET /api/v1/search/recommendations

**Get Personalized Recommendations**

Get personalized item recommendations for the user

#### Parameters

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `limit` | integer | query | ❌ | Number of recommendations |

#### Responses

**200** - Successful Response

```json
"example_value"
```

**422** - Validation Error

```json
{
  "detail": [
    "..."
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/search/recommendations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---

### GET /api/v1/search/filters/options

**Get Filter Options**

Get available filter options for the search interface

#### Responses

**200** - Successful Response

```json
"example_value"
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/search/filters/options"
```
---

## Data Models

### Body_login_user_api_v1_auth_login_post

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `grant_type` | string | ❌ |  |
| `username` | string | ✅ |  |
| `password` | string | ✅ |  |
| `scope` | string | ❌ |  |
| `client_id` | string | ❌ |  |
| `client_secret` | string | ❌ |  |

### Body_remove_item_image_api_v1_upload_items__item_id__images_delete

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_url` | string | ✅ | Image URL to remove |

### Body_upload_image_api_v1_upload_images_post

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string | ✅ |  |

### Body_upload_item_images_api_v1_upload_items__item_id__images_post

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | array | ✅ |  |
| `set_primary` | integer | ❌ | Index of image to set as primary (0-based) |

### Body_upload_multiple_images_api_v1_upload_images_multiple_post

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | array | ✅ |  |

### CategoryCreate

Schema for creating categories

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ |  |
| `description` | string | ❌ |  |
| `icon_name` | string | ❌ |  |
| `color_code` | string | ❌ |  |

### CategoryResponse

Category schema for responses

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `name` | string | ✅ |  |
| `slug` | string | ✅ |  |
| `description` | string | ❌ |  |
| `icon_name` | string | ❌ |  |
| `color_code` | string | ❌ |  |
| `is_active` | boolean | ✅ |  |
| `created_at` | string | ✅ |  |

### CategoryUpdate

Schema for updating categories

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ❌ |  |
| `description` | string | ❌ |  |
| `icon_name` | string | ❌ |  |
| `color_code` | string | ❌ |  |
| `is_active` | string | ❌ |  |

### HTTPValidationError

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `detail` | array | ❌ |  |

### ItemCreate

Schema for creating an item

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ |  |
| `description` | string | ✅ |  |
| `brand` | string | ❌ |  |
| `size` | string | ✅ |  |
| `condition` | string | ✅ |  |
| `color` | string | ❌ |  |
| `material` | string | ❌ |  |
| `tags` | string | ❌ |  |
| `pickup_location` | string | ❌ |  |
| `shipping_available` | boolean | ❌ |  |
| `original_price` | string | ❌ |  |
| `category_id` | integer | ✅ |  |
| `points_value` | string | ❌ |  |

### ItemPublic

Public item information for listings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `title` | string | ✅ |  |
| `description` | string | ✅ |  |
| `brand` | string | ❌ |  |
| `size` | string | ✅ |  |
| `condition` | string | ✅ |  |
| `color` | string | ❌ |  |
| `material` | string | ❌ |  |
| `tags` | string | ❌ |  |
| `points_value` | integer | ✅ |  |
| `primary_image_url` | string | ❌ |  |
| `image_urls` | string | ❌ |  |
| `shipping_available` | boolean | ✅ |  |
| `created_at` | string | ✅ |  |
| `owner` | string | ✅ |  |
| `category` | string | ✅ |  |

### ItemResponse

Schema for item responses

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ |  |
| `description` | string | ✅ |  |
| `brand` | string | ❌ |  |
| `size` | string | ✅ |  |
| `condition` | string | ✅ |  |
| `color` | string | ❌ |  |
| `material` | string | ❌ |  |
| `tags` | string | ❌ |  |
| `pickup_location` | string | ❌ |  |
| `shipping_available` | boolean | ❌ |  |
| `original_price` | string | ❌ |  |
| `id` | integer | ✅ |  |
| `category_id` | integer | ✅ |  |
| `owner_id` | integer | ✅ |  |
| `status` | string | ✅ |  |
| `points_value` | integer | ✅ |  |
| `image_urls` | string | ❌ |  |
| `primary_image_url` | string | ❌ |  |
| `is_active` | boolean | ✅ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |
| `published_at` | string | ❌ |  |
| `owner` | string | ✅ |  |
| `category` | string | ✅ |  |

### ItemUpdate

Schema for updating an item

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ❌ |  |
| `description` | string | ❌ |  |
| `brand` | string | ❌ |  |
| `size` | string | ❌ |  |
| `condition` | string | ❌ |  |
| `color` | string | ❌ |  |
| `material` | string | ❌ |  |
| `tags` | string | ❌ |  |
| `pickup_location` | string | ❌ |  |
| `shipping_available` | string | ❌ |  |
| `original_price` | string | ❌ |  |

### PointTransactionSummary

Brief point transaction summary

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `amount` | integer | ✅ |  |
| `transaction_type` | string | ✅ |  |
| `description` | string | ✅ |  |
| `created_at` | string | ✅ |  |

### SwapCreate

Schema for creating a swap request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requester_message` | string | ❌ |  |
| `item_id` | integer | ✅ |  |
| `swap_type` | string | ✅ |  |
| `offered_item_id` | string | ❌ |  |
| `points_offered` | string | ❌ |  |

### SwapResponse

Schema for swap responses

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requester_message` | string | ❌ |  |
| `id` | integer | ✅ |  |
| `requester_id` | integer | ✅ |  |
| `item_id` | integer | ✅ |  |
| `item_owner_id` | integer | ✅ |  |
| `swap_type` | string | ✅ |  |
| `status` | string | ✅ |  |
| `offered_item_id` | string | ❌ |  |
| `points_offered` | string | ❌ |  |
| `owner_response` | string | ❌ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |
| `expires_at` | string | ❌ |  |
| `responded_at` | string | ❌ |  |
| `completed_at` | string | ❌ |  |
| `requester` | string | ✅ |  |
| `item_owner` | string | ✅ |  |
| `item` | string | ✅ |  |
| `offered_item` | string | ❌ |  |

### SwapSummary

Brief swap summary for lists

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `swap_type` | string | ✅ |  |
| `status` | string | ✅ |  |
| `points_offered` | string | ❌ |  |
| `created_at` | string | ✅ |  |
| `item` | string | ✅ |  |
| `offered_item` | string | ❌ |  |

### Token

Schema for JWT token response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_token` | string | ✅ |  |
| `token_type` | string | ❌ |  |
| `expires_in` | integer | ✅ |  |

### UserCreate

Schema for creating a user

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ |  |
| `username` | string | ✅ |  |
| `first_name` | string | ❌ |  |
| `last_name` | string | ❌ |  |
| `bio` | string | ❌ |  |
| `city` | string | ❌ |  |
| `state` | string | ❌ |  |
| `country` | string | ❌ |  |
| `password` | string | ✅ |  |

### UserLogin

Schema for user login

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ |  |
| `password` | string | ✅ |  |

### UserResponse

Schema for user responses

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ |  |
| `username` | string | ✅ |  |
| `first_name` | string | ❌ |  |
| `last_name` | string | ❌ |  |
| `bio` | string | ❌ |  |
| `city` | string | ❌ |  |
| `state` | string | ❌ |  |
| `country` | string | ❌ |  |
| `id` | integer | ✅ |  |
| `points_balance` | integer | ✅ |  |
| `total_points_earned` | integer | ✅ |  |
| `total_points_spent` | integer | ✅ |  |
| `is_active` | boolean | ✅ |  |
| `is_verified` | boolean | ✅ |  |
| `is_admin` | boolean | ✅ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |
| `last_login` | string | ❌ |  |
| `profile_image_url` | string | ❌ |  |

### UserUpdate

Schema for updating user profile

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | ❌ |  |
| `last_name` | string | ❌ |  |
| `bio` | string | ❌ |  |
| `city` | string | ❌ |  |
| `state` | string | ❌ |  |
| `country` | string | ❌ |  |

### ValidationError

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `loc` | array | ✅ |  |
| `msg` | string | ✅ |  |
| `type` | string | ✅ |  |

### app__schemas__item__ItemSummary

Brief item summary for lists

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `title` | string | ✅ |  |
| `brand` | string | ❌ |  |
| `size` | string | ✅ |  |
| `condition` | string | ✅ |  |
| `points_value` | integer | ✅ |  |
| `primary_image_url` | string | ❌ |  |
| `created_at` | string | ✅ |  |

### app__schemas__item__UserPublic

Public user information (for item listings, etc.)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `username` | string | ✅ |  |
| `first_name` | string | ❌ |  |
| `last_name` | string | ❌ |  |
| `profile_image_url` | string | ❌ |  |
| `city` | string | ❌ |  |
| `state` | string | ❌ |  |
| `country` | string | ❌ |  |
| `created_at` | string | ✅ |  |

### app__schemas__swap__ItemSummary

Brief item summary for swaps

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `title` | string | ✅ |  |
| `brand` | string | ❌ |  |
| `size` | string | ✅ |  |
| `condition` | string | ✅ |  |
| `points_value` | integer | ✅ |  |
| `primary_image_url` | string | ❌ |  |
| `created_at` | string | ✅ |  |

### app__schemas__swap__UserPublic

Public user information (for swaps, etc.)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `username` | string | ✅ |  |
| `first_name` | string | ❌ |  |
| `last_name` | string | ❌ |  |
| `profile_image_url` | string | ❌ |  |
| `city` | string | ❌ |  |
| `state` | string | ❌ |  |
| `country` | string | ❌ |  |
| `created_at` | string | ✅ |  |

### app__schemas__user__UserPublic

Public user information (for item listings, etc.)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ |  |
| `username` | string | ✅ |  |
| `first_name` | string | ❌ |  |
| `last_name` | string | ❌ |  |
| `profile_image_url` | string | ❌ |  |
| `city` | string | ❌ |  |
| `state` | string | ❌ |  |
| `country` | string | ❌ |  |
| `created_at` | string | ✅ |  |

