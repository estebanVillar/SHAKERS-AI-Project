Of course. Let's create the guide for testing best practices. This document is crucial as it directly addresses several evaluation criteria mentioned in the case study.

06-evaluation-and-testing/02-testing-best-practices.md
Generated markdown
# Guide: Testing Best Practices

For any application, testing is key to ensuring reliability. For applications built on AI services, a comprehensive testing strategy is even more critical. It not only validates that your code works but also that the AI's performance meets your quality standards.

This guide provides best practices for testing your Shakers platform integration, covering everything from isolating your code with unit tests to measuring the quality of AI responses with automated evaluation.

---

## 1. Unit Testing: Isolating Your Business Logic

Unit tests are fast, reliable, and free. Their goal is to test your application's logic in isolation, without making any real calls to the Shakers API. This is achieved by "mocking" the API client.

We recommend using Python's built-in `unittest.mock` library, which integrates seamlessly with frameworks like `pytest`.

### Example: Testing the `/chat` Endpoint

Let's write a unit test for the `/chat` endpoint we built in the FastAPI guide. We want to verify two scenarios:
1.  Our endpoint correctly processes a successful response from the Shakers API.
2.  Our endpoint gracefully handles an error from the Shakers API.

**First, install `pytest` and `requests` (for the test client):*

pip install pytest requests


Next, create a test file, e.g., test_main.py:

test_main.py

Generated python
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
from shakers.sdk import ShakersApiError

# Create a test client for your app
client = TestClient(app)

@patch('main.shakers_client') # Target the client instance in your main app file
def test_chat_endpoint_success(mock_shakers_client):
    """
    Tests the /chat endpoint's success path by mocking the Shakers client.
    """
    # 1. Configure the mock to return a successful response
    mock_response = MagicMock()
    mock_response.answer = "This is a test answer."
    mock_response.sources = [
        MagicMock(title="Test Source", url="/kb/test-source", dict=lambda: {"title": "Test Source", "url": "/kb/test-source"})
    ]
    mock_shakers_client.rag.query.return_value = mock_response

    # 2. Make a request to your endpoint
    response = client.post("/chat", json={"user_id": "unit-test-1", "message": "Test query"})

    # 3. Assert the results
    assert response.status_code == 200
    data = response.json()
    assert data['reply'] == "This is a test answer."
    assert len(data['sources']) == 1
    assert data['sources']['title'] == "Test Source"
    
    # Assert that the mock was called correctly
    mock_shakers_client.rag.query.assert_called_with(query="Test query", user_id="unit-test-1")


@patch('main.shakers_client')
def test_chat_endpoint_api_error(mock_shakers_client):
    """
    Tests that the endpoint handles a 401 error from the Shakers API.
    """
    # 1. Configure the mock to raise a specific error
    mock_shakers_client.rag.query.side_effect = ShakersApiError(
        status_code=401, message="Invalid API Key"
    )

    # 2. Make the request
    response = client.post("/chat", json={"user_id": "unit-test-2", "message": "Another query"})

    # 3. Assert the HTTP exception was raised correctly
    assert response.status_code == 401
    assert response.json() == {"detail": "An error occurred with the Shakers API: Invalid API Key"}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

To run these tests, simply execute pytest in your terminal.

2. Integration Testing: Verifying the Connection

Integration tests make real calls to the live Shakers API. Their purpose is not to test the quality of the AI response but to verify that:

Your API key is valid.

Your request and response models match the live API.

The connection between your application and our servers is healthy.

Best Practice: Use a separate, dedicated "Test" API key for these tests. Mark these tests so you can run them separately from your fast unit tests (e.g., using pytest.mark).

Example: A Simple Integration Test

Generated python
import pytest

# This test makes a real API call and should be run sparingly.
@pytest.mark.integration
def test_rag_service_integration():
    """
    Makes a real call to the Shakers API to check for a valid connection.
    Assumes SHAKERS_API_KEY is configured in the environment.
    """
    # Using the real client, not a mock
    from shakers.sdk import ShakersClient
    real_client = ShakersClient()

    try:
        # Use a simple, predictable query
        response = real_client.rag.query(query="What is a freelancer?")
        assert isinstance(response.answer, str)
        assert len(response.answer) > 0
        assert isinstance(response.sources, list)
    except ShakersApiError as e:
        pytest.fail(f"Integration test failed with an API error: {e}")
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

You can run only your integration tests using: pytest -m integration

3. Automated Evaluation: Measuring AI Quality

This is the most advanced and valuable form of testing for AI systems. The goal is to automatically measure the quality of the AI responses against a pre-defined "ground truth" dataset.

Evaluating the RAG Service

Create a Ground Truth Dataset:
Create a CSV or JSON file with test questions and key pieces of information you expect in the answer.

rag_evaluation_set.json

Generated json
[
  {
    "query": "How do payments work?",
    "expected_keywords": ["milestone", "escrow", "approve", "release"]
  },
  {
    "query": "What is Shakers' fee?",
    "expected_keywords": ["service fee", "percentage", "client", "freelancer"]
  },
  {
    "query": "Can I hire for a full-time position?",
    "expected_keywords": ["freelancers", "independent contractor", "not employees"]
  }
]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

Write an Evaluation Script:
This script will loop through your dataset, call your API, and score the results.

evaluate_rag.py

Generated python
import json
import requests

def evaluate_rag_accuracy():
    with open('rag_evaluation_set.json', 'r') as f:
        evaluation_set = json.load(f)

    score = 0
    total = len(evaluation_set)

    for item in evaluation_set:
        response = requests.post(
            "http://127.0.0.1:8000/chat", # Your local endpoint
            json={"user_id": "eval-script", "message": item['query']}
        )
        
        if response.status_code == 200:
            answer = response.json()['reply'].lower()
            # Check if all expected keywords are in the answer
            if all(keyword in answer for keyword in item['expected_keywords']):
                score += 1
        
    accuracy = (score / total) * 100
    print(f"RAG Evaluation Complete. Accuracy: {accuracy:.2f}% ({score}/{total})")

if __name__ == "__main__":
    evaluate_rag_accuracy()

Running this script (python evaluate_rag.py) gives you a quantitative measure of your chatbot's factual accuracy.

Next Steps

By implementing this multi-layered testing strategy, you can build a high-quality, reliable, and predictable AI-powered application.

CI/CD Integration: Automate the execution of your unit and integration tests in a CI/CD pipeline (e.g., GitHub Actions) to catch regressions before they reach production.

Performance Optimization: Now that your system is robustly tested, explore advanced features to make it faster and more cost-effective. Check out our guide on Optimizing for Performance.