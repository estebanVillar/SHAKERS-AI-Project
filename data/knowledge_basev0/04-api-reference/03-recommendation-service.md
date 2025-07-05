# API Reference: Personalized Recommendation Service

The Personalized Recommendation Service provides proactive assistance by suggesting relevant articles, tutorials, and guides to users based on their demonstrated interests. This endpoint is designed to enhance user engagement and facilitate platform mastery by surfacing helpful, undiscovered content.

---

## Endpoint: Get Personalized Recommendations

This endpoint analyzes a user's activity to generate a list of 2-3 diverse and relevant resources.

`POST /api/recommendations`

### Request Body

The request body must be a JSON object containing information about the user's context and history.

| Key             | Type             | Required | Description                                                                                                   |
| :-------------- | :--------------- | :------- | :------------------------------------------------------------------------------------------------------------ |
| `user_id`       | string           | **Yes**  | A unique and persistent identifier for the end-user. |

#### Example Request

```json
{
  "user_id": "user_12345"
}
```

Example cURL Command
```bash
curl -X POST "http://127.0.0.1:5000/api/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "user_12345"
         }'
```
Response (200 OK)

A successful request will return a 200 OK status with a JSON object containing a list of recommendations.

Key	Type	Description
recommendations	array of objects	An array of recommendation objects. This will typically contain 2-3 diverse suggestions.
recommendations Object Structure

Each object within the recommendations array represents a suggested resource.

Key	Type	Description
title	string	The title of the recommended article or guide.
explanation	string	A brief, human-readable explanation of why this specific resource is relevant to the user's journey.
Example Success Response
```json
{
  "recommendations": [
    {
      "title": "Mastering the Art of the Project Proposal",
      "explanation": "You haven't explored this topic yet."
    },
    {
      "title": "A Freelancer's Guide to Pricing Strategies",
      "explanation": "You haven't explored this topic yet."
    },
    {
      "title": "Understanding Client Contracts and Agreements",
      "explanation": "You haven't explored this topic yet."
    }
  ]
}
```
Special Case: New Users

If you provide a `user_id` that has no history, the system will return a generic set of high-value recommendations suitable for new users.

Example Request (New User):

```json
{
  "user_id": "new-user-abcde"
}
```

The response will still be a 200 OK with a list of recommendations, but they will be geared towards getting started on the platform.

Next Steps

Discover how to integrate these services into a functional application in our Guides section.
