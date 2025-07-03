# Getting Started: Setting Up and Running the Shakers Intelligent Support System

This guide provides a detailed, step-by-step walkthrough for setting up your development environment and launching the Shakers Intelligent Support System, a Python Flask application. We will cover dependency installation, environment configuration, and the execution of the Flask server, enabling you to interact with its RAG and Recommendation API endpoints.

---

### Prerequisites

Before proceeding, ensure your system meets the following technical requirements:

*   **Python 3.8+:** The application is developed and tested with Python 3.8 and newer versions. Verify your Python installation by running `python --version` or `python3 --version` in your terminal.
*   **Git:** Required for cloning the project repository. Install Git from [git-scm.com](https://git-scm.com/).
*   **Google API Key:** An API key for accessing Google's Generative AI services (specifically for `models/embedding-001` and `gemini-1.5-flash-latest`). Obtain your key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

---

### Step 1: Project Setup and Dependency Installation

This step involves cloning the repository, establishing a dedicated Python virtual environment, and installing all required libraries. Utilizing a virtual environment is a best practice that isolates project dependencies, preventing conflicts with other Python projects on your system.

1.  **Clone the Repository:**
    Begin by cloning the project repository from its source. Replace `[repository_url]` with the actual URL of your Git repository.
    ```bash
    git clone [repository_url]
    cd shakers-integration-project # Navigate into the cloned directory
    ```

2.  **Create a Python Virtual Environment:**
    Execute the following command within the project's root directory to create a virtual environment named `venv`.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    Activate the newly created virtual environment. This ensures that any packages you install are confined to this environment.
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```

4.  **Install Project Dependencies:**
    With the virtual environment active, install all necessary Python packages. These include Flask for the web framework, `python-dotenv` for environment variable management, and `langchain-google-genai`, `langchain-community`, and `faiss-cpu` for the RAG and embedding functionalities.
    ```bash
    pip install Flask python-dotenv langchain-google-genai langchain-community faiss-cpu
    ```

---

### Step 2: Google API Key Configuration

Authentication with Google's Generative AI services is managed via an API key. For security and portability, this key should be stored as an environment variable, not hardcoded within the application's source code.

1.  **Create a `.env` file:**
    In the root directory of your `shakers-integration-project`, create a new file named `.env`.

2.  **Add Your Google API Key:**
    Open the `.env` file and add your obtained Google API Key in the following format:
    ```.env
    GOOGLE_API_KEY="your_google_api_key_here"
    ```
    Replace `your_google_api_key_here` with the actual API key you obtained from Google AI Studio.

    **Security Note:** It is crucial to add `.env` to your project's `.gitignore` file. This prevents accidental exposure of your sensitive API key if you commit your code to a version control system like Git.

---

### Step 3: Running the Flask Application

With all dependencies installed and the `GOOGLE_API_KEY` configured, you can now launch the Flask application. The `main.py` file, located in the `app/` subdirectory, serves as the entry point for the server.

1.  **Navigate to the `app` Directory:**
    ```bash
    cd app
    ```

2.  **Execute the Flask Application:**
    Run the `main.py` script. This will initialize the RAG pipeline (loading or building the FAISS index) and start the Flask development server.
    ```bash
    python main.py
    ```

    Upon successful execution, you should observe output similar to the following, indicating that the Flask server is listening for requests, typically on port `5000`:
    ```
     * Serving Flask app 'main'
     * Debug mode: off
    WARNING: This is a development server. Do not use it in a production deployment.
    Use a production WSGI server instead.
     * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    ```

---

### Step 4: Making Your First Query (RAG Service)

Once the Flask server is operational, you can interact with the RAG Query Service via its `/api/query` endpoint. This endpoint processes natural language questions and returns contextual answers derived from the knowledge base.

Use `curl` from a new terminal window (ensure your Flask server is still running in the first terminal) to send a POST request:

```bash
curl -X POST "http://127.0.0.1:5000/api/query" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "How do payments work on the platform?",
           "user_id": "test-user-123",
           "chat_history": []
         }'
```

**Expected Response:**

A successful response will return a JSON object containing the generated answer and the source topics from which the information was retrieved. This demonstrates the RAG service's ability to provide grounded responses.

```json
{
  "answer": "Payments on the Shakers platform are processed at the end of a project milestone. Once a client approves the delivered work, funds are released from escrow and transferred to the freelancer's account within 3-5 business days.",
  "sources": [
    "payments",
    "getting-paid"
  ]
}
```

---

### Step 5: Retrieving Your First Recommendations

Beyond direct query answering, the system offers personalized recommendations. The `/api/recommendations` endpoint leverages inferred user interests to suggest relevant content. Note that for meaningful recommendations, the `user_id` provided should have some query history with the RAG service, as this history informs the recommendation logic.

Use `curl` to send a POST request to the recommendation endpoint:

```bash
curl -X POST "http://127.0.0.1:5000/api/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "test-user-123"
         }'
```

**Expected Response:**

The response will be a JSON object containing a list of recommended resources, each with a title and an explanation of its relevance. The recommendations will be tailored based on the `test-user-123`'s previous interactions with the RAG service.

```json
{
  "recommendations": [
    {
      "title": "Advanced Guide to Vetting Technical Talent",
      "explanation": "You haven't explored this topic yet."
    },
    {
      "title": "Understanding Project Contracts and Agreements",
      "explanation": "You haven't explored this topic yet."
    }
  ]
}
```

---

This concludes the initial setup and basic interaction guide. You now have a running instance of the Shakers Intelligent Support System and have successfully interacted with its core functionalities. Proceed to the next sections for a deeper understanding of the system's concepts, API details, and advanced features.