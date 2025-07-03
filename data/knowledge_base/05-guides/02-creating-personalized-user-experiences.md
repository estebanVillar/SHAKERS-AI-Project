# Guide: Creating Personalized User Experiences

While a support chatbot is great for answering direct questions, you can create a truly exceptional user experience by proactively guiding users toward helpful content. This is where the **Personalized Recommendation Service** shines.

This guide will show you how to build a system that tracks a user's interests based on their query history and then suggests relevant articles and tutorials. We will extend the Flask application from the previous guide to add a new endpoint for fetching these recommendations.

---

### Prerequisites

*   You have completed the guide on **[Building a Support Chatbot](./05-guides/01-building-a-support-chatbot.md)**.
*   Your Flask application (`main.py`) and `.env` file are set up.
*   You understand the concepts behind the **[Personalized Recommendation Service](./03-core-concepts.md#2-personalized-recommendation-service)**.

---

### The Goal: From Reactive to Proactive

Our goal is to create an endpoint that, for a given `user_id`, can return a list of recommended articles. You could use this to power a "Recommended for You" section in a user's dashboard or to send a helpful follow-up email after a support interaction.

To do this, our application needs to do two things:
1.  **Store** user query history.
2.  **Provide** recommendations based on that history.

---

### Step 1: User History Management

In the Flask application (`app/main.py`), user query history and inferred interests are automatically managed and persisted to `data/evaluation/user_profiles.json`. You do not need to implement an in-memory database as shown in the previous FastAPI example.

The `handle_query` function in `app/main.py` already includes logic to:

*   Load existing user profiles from `user_profiles.json`.
*   Append the current query to the user's `query_history`.
*   Update `inferred_interests` based on the source topics of the RAG response.
*   Save the updated user profiles back to `user_profiles.json`.

This means that every time a user interacts with the `/api/query` endpoint, their history is automatically recorded and updated.

### Step 2: Understanding the Recommendation Endpoint

The Flask application (`app/main.py`) already includes an endpoint for personalized recommendations:

```python
# app/main.py (simplified for this guide)

# ... (imports and initial setup)

@app.route('/api/recommendations', methods=['POST'])
def handle_recommendations():
    data = request.get_json()
    if not data or 'user_id' not in data: return jsonify({"error": "Missing 'user_id' in request body"}), 400
    user_id = data['user_id']
    user_profiles = load_user_profiles()
    user_profile = user_profiles.get(user_id)
    if not user_profile: return jsonify({"recommendations": []})
    consulted_topics = set(user_profile.get("inferred_interests", []))
    all_topics = sorted(list({doc.metadata.get('topic') for doc in documents_with_metadata if 'topic' in doc.metadata}))
    recommendations = []
    unconsulted = [topic for topic in all_topics if topic not in consulted_topics]
    for topic in unconsulted:
        if len(recommendations) < 3:
            recommendations.append({"title": topic, "explanation": f"You haven't explored this topic yet."})
    if len(recommendations) < 3:
        for topic in all_topics:
            if len(recommendations) < 3 and not any(rec['title'] == topic for rec in recommendations):
                 recommendations.append({"title": topic, "explanation": f"Broaden your knowledge with this article."})
    return jsonify({"recommendations": recommendations[:3]})

# ... (rest of the file)
```

This endpoint:

*   Takes a `user_id` as input.
*   Loads the user's profile, including their `inferred_interests` (topics from previously answered RAG queries).
*   Generates recommendations by suggesting topics the user hasn't explored yet, or general topics if all inferred interests have been covered.

### Step 3: Run and Test the Full Flow

Make sure your Flask server is running (from the `app` directory, run `python main.py`). Now let's test the entire user journey.

A. Build up a user history:
Send a few queries to the `/api/query` endpoint for a new user, `test-user-002`. This simulates a user interacting with your chatbot over time. Each query will update the user's inferred interests in `user_profiles.json`.

Query 1 (Finding talent):

```bash
curl -X POST "http://127.0.0.1:5000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test-user-002", "query": "How to find a good React developer?", "chat_history": []}'
```

Query 2 (Payments):

```bash
curl -X POST "http://127.0.0.1:5000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test-user-002", "query": "What are the fees for clients?", "chat_history": []}'
```

B. Get personalized recommendations:
Now that `test-user-002` has a history, call the new recommendations endpoint.

```bash
curl -X POST "http://127.0.0.1:5000/api/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "test-user-002"
         }'
```

Expected Response:

You should get back a curated list of recommendations that are relevant to finding developers and understanding costs, because the system analyzed the history you just created.

```json
{
  "recommendations": [
    {
      "title": "Guide to Vetting and Interviewing Developers",
      "explanation": "You haven't explored this topic yet."
    },
    {
      "title": "Understanding the Shakers Fee Structure",
      "explanation": "You haven't explored this topic yet."
    },
    {
      "title": "Writing an Effective Job Post",
      "explanation": "You haven't explored this topic yet."
    }
  ]
}
```
Conclusion

You have successfully built an intelligent system that not only responds to user needs but actively anticipates them. By recording user interactions and feeding them to the Recommendation Service, you can create a deeply personalized and helpful user journey.

From here, you can:

*   Integrate this into a frontend dashboard.
*   Explore advanced features like Optimizing for Performance by caching recommendation results.