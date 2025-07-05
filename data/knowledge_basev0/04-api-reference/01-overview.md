# API Reference: Overview

Welcome to the Shakers API reference! This section provides comprehensive, technical details about our API endpoints. Whether you're querying for answers or fetching recommendations, this is your source for request schemas, response formats, and status codes.

Our API is built on REST principles, with predictable, resource-oriented URLs and uses standard HTTP verbs and response codes. All API requests and responses, including errors, are in JSON format.

---

### Base URL

All API endpoints are accessible via the following base URL. We encourage you to store this in a configuration file rather than hardcoding it.

`http://127.0.0.1:5000`

All endpoints are served over HTTPS to ensure data privacy and security.

---

### Authentication

This system uses the `GOOGLE_API_KEY` for authentication, which should be set as an environment variable. The Flask application handles this internally, so you do not need to include an `Authorization` header in your API requests.

**Example Request (using cURL):**

```bash
curl -X POST "http://127.0.0.1:5000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is a freelancer?", "user_id": "test-user-123", "chat_history": []}'
```


Error Handling

Our API uses standard HTTP status codes to indicate the success or failure of a request. In general:

Codes in the 2xx range indicate success.

Codes in the 4xx range indicate a client-side error (e.g., a malformed request or invalid authentication).

Codes in the 5xx range indicate a server-side error.

When an error occurs, the response body will contain a JSON object with a detail key that provides a human-readable explanation of the error.

Example Error Response (400 Bad Request):

{
  "detail": "Field 'query' is required in the request body."
}

**Common HTTP Status Codes:**

| Code                | Meaning                                                                    |
| ------------------- | -------------------------------------------------------------------------- |
| `200 OK`            | The request was successful.                                                |
| `400 Bad Request`   | The server could not process the request due to a client error (e.g., missing required parameters, invalid JSON). |
| `401 Unauthorized`  | Authentication failed. The API key is missing, invalid, or expired.        |
| `403 Forbidden`     | The API key is valid, but you do not have permission to access this resource. |
| `404 Not Found`     | The requested resource or endpoint does not exist.                         |
| `429 Too Many Requests` | You have exceeded the allowed rate limit. Check the response headers for details. |
| `500 Internal Server Error` | Something went wrong on our end. Please try again later or contact support if the issue persists. |

---

### Rate Limiting

To ensure high availability and fair usage for all users, our API endpoints are rate-limited. The current rate limit for standard plans is **60 requests per minute**.

The following headers are included in every API response to help you track your usage:

| Header                 | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `X-RateLimit-Limit`    | The maximum number of requests allowed in the current window.  |
| `X-RateLimit-Remaining`| The number of requests remaining in the current window.        |
| `X-RateLimit-Reset`    | The time at which the current rate limit window resets, in UTC epoch seconds. |

If you exceed the rate limit, you will receive a `429 Too Many Requests` error response.

---

### Versioning

Our API is versioned to ensure that we can make future improvements without breaking your existing integrations. The API version is specified in the URL path.

**Current Version:** `/v1`

When we release a new version with breaking changes, we will introduce a new version prefix (e.g., `/v2`). We are committed to providing a stable `v1` and will notify you well in advance of any deprecation plans.

### Next Steps

Now that you understand the basics of interacting with our API, you're ready to explore the specific endpoints:

*   **[RAG Query Service](./02-rag-query-service.md):** For answering technical user questions.
*   **[Recommendation Service](./03-recommendation-service.md):** For proactively recommending resources.
