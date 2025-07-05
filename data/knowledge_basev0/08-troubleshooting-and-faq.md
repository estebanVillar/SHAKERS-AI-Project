# Troubleshooting and FAQ

This section provides answers to common questions and solutions to potential issues you might encounter while integrating with the Shakers Intelligent Support System.

---

## Frequently Asked Questions (FAQ)

### Q: How do I get an API key?

A: This system uses the `GOOGLE_API_KEY` for authentication. You should obtain a Google API key and set it as an environment variable in a `.env` file in your project's root directory.

### Q: What happens if my query is out of scope?

A: If your query cannot be answered by our knowledge base, the RAG service will return a predefined message indicating that it doesn't have information on that topic. The `sources` array in the response will be empty.

### Q: Is there a rate limit for API calls?

A: Yes, our API endpoints are rate-limited to ensure fair usage. You can find the current rate limits and track your usage using the `X-RateLimit-*` headers in our API responses. Refer to the [API Reference: Overview](./04-api-reference/01-overview.md) for more details.

---

## Troubleshooting Common Issues

### Issue: Missing `GOOGLE_API_KEY`

**Problem:** The application fails to start or process requests, indicating a missing `GOOGLE_API_KEY`.

**Solution:** Ensure that you have a valid Google API key and that it is correctly set as an environment variable named `GOOGLE_API_KEY` in a `.env` file in your project's root directory.

### Issue: 429 Too Many Requests Error

**Problem:** You are receiving a `429 Too Many Requests` HTTP status code.

**Solution:** You have exceeded the allowed rate limit for API calls. You should implement a retry mechanism with exponential backoff in your application. Check the `X-RateLimit-Reset` header to know when you can safely retry your request.

### Issue: Inaccurate or Irrelevant Answers from RAG Service

**Problem:** The RAG service is providing answers that seem incorrect or not relevant to the Shakers platform.

**Solution:** This can happen if the query is ambiguous or if the knowledge base does not contain sufficient information on the topic. Consider:

*   **Refining your query:** Try to be more specific in your questions.
*   **Checking the `sources`:** Always examine the `sources` array in the response. If it's empty or points to irrelevant documents, it indicates a gap in the knowledge base or an issue with query understanding.
*   **Contacting Support:** If you believe there's a significant gap in our knowledge base or a persistent issue with answer quality, please contact our support team with examples of your queries.

---

If you encounter an issue not covered here, please refer to the [API Reference](./04-api-reference/01-overview.md) for detailed error codes or reach out to our support team.