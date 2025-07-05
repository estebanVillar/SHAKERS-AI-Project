# Evaluation: The Metrics Dashboard

Integrating an intelligent system is just the first step. To truly understand its impact and to continuously improve the user experience, you need to measure its performance. The Shakers Developer Dashboard provides a comprehensive view of how your integration is performing in real-time.

This guide explains the available metrics, what they mean, and how you can use them to analyze the effectiveness of your implementation.

---

### Accessing Your Dashboard

You can access your metrics dashboard by logging into your **Shakers Developer Account** and navigating to the "Analytics" tab. All metrics can be filtered by a specific date range, allowing you to track performance over time.

![Metrics Dashboard Screenshot](https://i.imgur.com/example-dashboard.png) <!-- Fictional placeholder for a dashboard UI -->

---

## 1. RAG Query Service Metrics

This section helps you understand the performance of your question-answering system.

| Metric                 | Description                                                                                                                                                             | How to Use It                                                                                                                                  |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| **Total Queries**      | The total number of queries sent to the `/api/query` endpoint during the selected period.                   | Track user engagement. A sudden spike might indicate a new user trend, while a drop could signal a usability issue.                        |
| **Answer Found Rate (%)** | The percentage of queries that were answered with information from the knowledge base, versus those that resulted in an "I don't have information on this..." response. | A low rate might mean your users are asking questions outside the intended scope. Consider adding documentation to the knowledge base or guiding users on what they can ask. |
| **Avg. Response Time (ms)** | The average time it takes for the API to process a query and return a response. We track p50, p90, and p95 latencies. Our SLA guarantees p95 below 5000ms.                  | Monitor the speed and responsiveness of your chatbot. Spikes in latency could indicate temporary system load on our end.                      |
| **User Helpfulness Score (%)** | The percentage of responses that were marked as "Helpful" by end-users via feedback buttons. **(Requires implementation)**                                              | This is your most direct measure of answer quality. A low score indicates that the generated answers are not meeting user expectations.   |

#### Implementing the User Helpfulness Score

To enable this powerful metric, you must provide feedback buttons ("Helpful" / "Not Helpful") in your UI. When a user clicks one, you should make a call to our feedback logging endpoint.

`POST /events/log_feedback`

**Request Body:**
{
  "query_id": "the_id_returned_in_the_rag_response_header",
  "is_helpful": true // or false
}


Note: The query_id will be returned in the X-Query-ID header of every /rag/query response. Capturing and using this ID is essential for linking feedback to a specific query.

2. Personalized Recommendation Service Metrics

This section provides insight into the effectiveness of your proactive content suggestions.

Metric	Description	How to Use It
Recommendations Served	The total number of individual recommendations delivered to users.	Measures how often you are proactively engaging users. Combine with CTR to understand the overall impact.
Click-Through Rate (CTR) (%)	The percentage of recommended items that were clicked by a user. (Requires implementation)	This is the single most important metric for recommendations. A high CTR means your suggestions are relevant and compelling.
Recommendation Diversity Score	A score from 0.0 to 1.0 that measures how varied the topics of recommendations are for individual users. A higher score indicates a better mix of content.	If this score is consistently low, it may mean your users' query histories are too narrow or the system is repeatedly suggesting similar items.
Implementing Click-Through Rate (CTR) Tracking

To enable CTR tracking, you must log an event with us whenever a user clicks on a recommended item.

POST /events/log_click

Request Body:

```json
{
  "recommendation_id": "the_id_returned_with_each_recommendation_object",
  "user_id": "the_user_id_for_whom_the_recommendation_was_generated"
}
```

Note: Each object in the /recommendations/get response will now include a recommendation_id. You must pass this ID back to us to track clicks accurately.

3. Expense Tracking and Monitoring

This section gives you full visibility into your API usage and costs, helping you optimize performance and manage your budget.

API Call Volume: A detailed breakdown of API calls made to each endpoint (`/api/query`, `/api/recommendations`, etc.).

Error Rate (%): The percentage of your API calls that resulted in a 4xx or 5xx error.

Latency Monitoring: Detailed graphs showing p50, p90, and p95 latency for each endpoint over time.

Next Steps

Now that you know how to measure performance, it's time to learn how to test your integration effectively.

Proceed to our guide on Testing Best Practices.
