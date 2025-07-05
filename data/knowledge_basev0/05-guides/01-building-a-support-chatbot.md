# Guide: Building a Support Chatbot with Flask

This guide will walk you through the process of building a simple but powerful technical support chatbot. We will use **Flask**, a Python web framework, to create a web server that integrates with the Shakers **RAG Query Service**.

By the end of this tutorial, you will have a functional API endpoint that can receive a user's question and respond with an intelligent, fact-checked answer.

---

### Prerequisites

*   You have completed the **[Getting Started](./02-getting-started.md)** guide.
*   You have Python 3.8+, a virtual environment, and your Shakers API key ready.
*   Basic understanding of how web APIs work.

---

### Step 1: Project Setup

If you're continuing from the "Getting Started" guide, you can use the same project. If not, create a new one. Let's install the necessary libraries for our Flask application.

```bash
# Make sure your virtual environment is activated
# source venv/bin/activate

# Install required libraries
pip install Flask python-dotenv langchain-google-genai langchain-community faiss-cpu
```

Your project directory should look like this:

```
shakers-integration-project/
├── venv/
├── .env
├── app/
│   └── main.py
└── ...
```

Ensure your `.env` file contains your Google API key:

```.env
GOOGLE_API_KEY="your_google_api_key_here"
```
Step 2: Understand the Flask Application

Instead of creating a new file, we will be referencing the existing `main.py` file located in the `app/` directory of your project. This file already contains the Flask application setup and the RAG pipeline integration.

Here's a simplified look at the relevant parts of `app/main.py`:

```python
# app/main.py (simplified for this guide)

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# --- LangChain & GenAI Imports ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# ... (other imports and initial setup)

app = Flask(__name__)

@app.route('/api/query', methods=['POST'])
def handle_query():
    start_time = time.time()
    data = request.get_json()
    if not data or 'query' not in data or 'user_id' not in data:
        return jsonify({"error": "Request must include 'query', 'user_id', and 'chat_history'"}), 400
    
    user_query = data['query']
    user_id = data['user_id']
    chat_history_json = data.get('chat_history', [])
    
    chat_history_messages = []
    for msg in chat_history_json:
        if msg['role'] == 'user': chat_history_messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant': chat_history_messages.append(AIMessage(content=msg['content']))

    try:
        result = retrieval_chain.invoke({
            "input": user_query,
            "chat_history": chat_history_messages
        })
        
        generated_answer = result.get('answer', "I couldn't generate a response.")
        source_docs = result.get('context', [])
        source_topics = sorted(list(set(doc.metadata.get('topic', 'Unknown Source') for doc in source_docs)))
        final_answer = generated_answer

        # ... (user profile and logging logic)
        
        return jsonify({"answer": final_answer, "sources": source_topics})

    except Exception as e:
        # ... (error handling)
        return jsonify({"error": "An internal error occurred."}), 500

# ... (recommendation endpoint and main run block)
```

This Flask application sets up an endpoint `/api/query` that receives user questions, processes them using the RAG pipeline, and returns a fact-based answer along with source topics.

Step 3: Run and Test Your Chatbot

Your chatbot server is now ready to run! From your terminal, navigate to the `app` directory and execute `main.py`:

```bash
cd app
python main.py
```

You should see output indicating the server is running, usually on `http://127.0.0.1:5000`.

Now, let's test it. Open a new terminal and use `curl` to send a question to the `/api/query` endpoint:

```bash
curl -X POST "http://127.0.0.1:5000/api/query" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "test-user-001",
           "query": "How do I pay a freelancer?",
           "chat_history": []
         }'
```

Expected Response:

You should get back a JSON response from your own server, powered by the RAG pipeline:

```json
{
  "answer": "You can pay a freelancer by funding project milestones. When a milestone is submitted and you approve the work, the funds are released from escrow to the freelancer. This ensures payment is made only for completed work.",
  "sources": [
    "making-payments",
    "milestone-payments"
  ]
}
```

Congratulations! You have a working, intelligent chatbot backend. Here are some ideas for taking this project further:

*   **Build a Frontend:** Use a framework like Streamlit, React, or Vue.js to build a user interface that interacts with your new API endpoint.
*   **Add Conversation History:** The current `main.py` already supports `chat_history` in the `/api/query` endpoint. You can extend your frontend to send the full conversation history.
*   **Integrate Recommendations:** After a user receives an answer, you can make a call to the `/api/recommendations` endpoint using the user's ID to suggest relevant articles.

Explore Further: Now that you know how to build a basic integration, check out our guide on [Creating Personalized User Experiences](./02-creating-personalized-user-experiences.md).
