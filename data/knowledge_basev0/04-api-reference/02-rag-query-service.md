# API Reference: RAG Query Service

The RAG Query Service endpoint allows you to ask a question in natural language and receive a contextual, fact-based answer generated from the Shakers platform knowledge base. This service is ideal for building support chatbots, interactive FAQs, and in-app help systems.

---

## Endpoint: Get a Contextual Answer

This endpoint takes a user's query, retrieves relevant information, and generates a clear, concise answer.

`POST /api/query`

### Request Body

The request body must be a JSON object containing the user's query.

| Key       | Type   | Required | Description                                                                                                      |
| :-------- | :----- | :------- | :--------------------------------------------------------------------------------------------------------------- |
| `query`   | string | **Yes**  | The natural language question you want to ask the system. E.g., "How do payments work?".                         |
| `user_id` | string | **Yes**  | A unique identifier for the end-user. |
| `chat_history` | array of objects | No       | An optional array of previous messages in the conversation, each with `role` (user/assistant) and `content`. |

#### Example Request

```json
{
  "query": "What are the key differences between a freelancer and an employee on Shakers?",
  "user_id": "user-session-f8a9b2c1",
  "chat_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there! How can I help you?"}
  ]
}
```

Example cURL Command
```bash
curl -X POST "http://127.0.0.1:5000/api/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "What are the key differences between a freelancer and an employee on Shakers?",
           "user_id": "user-session-f8a9b2c1",
           "chat_history": []
         }'
```

Response (200 OK)

If the request is successful and an answer is found, the API will return a 200 OK status with a JSON object containing the generated answer and its sources.

Key	Type	Description
answer	string	The generated, human-readable answer to the user's query.
sources	array of strings	An array of source topics (e.g., "payments", "freelancer-types") used to generate the answer.
Example Success Response
```json
{
  "answer": "On the Shakers platform, a freelancer is an independent contractor who operates their own business and is hired on a per-project basis. An employee, on the other hand, would be a direct hire for a company. Shakers is primarily a platform for connecting with freelancers, who manage their own taxes and benefits.",
  "sources": [
    "what-is-a-freelancer",
    "legal-classifications"
  ]
}
```
Special Case: Out-of-Scope Queries

A core feature of the system is its ability to recognize when a query cannot be answered by our knowledge base. This prevents the LLM from providing inaccurate or irrelevant information.

If a query is determined to be out of scope (e.g., asking "What is the weather in New York?"), the API will still return a 200 OK status, but the answer field will contain a specific, pre-defined message and the sources array will be empty.

Example Response for Out-of-Scope Query

Request:

```json
{
  "query": "Can you recommend a good local restaurant?",
  "user_id": "user-session-x7y8z9a0",
  "chat_history": []
}
```

**Response:**

```json
{
  "answer": "I'm sorry, I don't have enough information to answer that question based on the provided documents.",
  "sources": []
}
```
