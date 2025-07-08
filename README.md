# Project: The Self-Documenting AI Assistant

## 1. Overview
This project is an intelligent technical support system built for a unique purpose: to answer questions about its own architecture, design, and functionality. It's a "meta" chatbot that uses a built-in knowledge base (the project's own documentation) to provide detailed, cited answers about how it works.

The system meets two primary objectives:
1.  **Technical Q&A:** Accurately answers user questions using a Retrieval-Augmented Generation (RAG) pipeline.
2.  **Personalized Recommendations:** Proactively suggests relevant documentation to the user based on their inferred interests.

The entire system is designed to be explored interactively, providing a rich and in-depth evaluation experience.

## 2. Architecture
The system uses a modern, scalable architecture with a strict separation of concerns between the frontend and backend.

-   **Backend:** A **Flask** API server that houses all AI logic, including the LangChain-orchestrated RAG pipeline, user profile management, recommendation engine, and performance logging.
-   **Frontend:** A **Streamlit** user interface that is a pure "view" layer. It handles rendering the chat, managing sessions, and displaying a real-time metrics dashboard. It communicates with the backend via REST API calls.

  <!-- You can create a simple diagram and upload it -->

## 3. Setup and Installation

**Prerequisites:**
- Python 3.9+
- A Google API Key with the "Gemini API" enabled.

**Instructions:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/estebanVillar/SHAKERS-AI-Project.git
    cd shakers-ai-project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    -   Copy the example file: `cp .env.example .env` (or `copy .env.example .env` on Windows).
    -   Open the `.env` file and add your Google API key:
        ```env
        GOOGLE_API_KEY="your-google-api-key-here"
        ```

## 4. How to Run the Application

The application requires two separate terminal processes to run the backend and frontend concurrently.

1.  **Start the Backend (Flask API Server):**
    Open a terminal, activate the virtual environment, and run:
    ```bash
    python -m flask --app app/main run
    ```
    You should see output indicating the server is running on `http://127.0.0.1:5000`.

2.  **Start the Frontend (Streamlit UI):**
    Open a **second** terminal, activate the virtual environment, and run:
    ```bash
    python -m streamlit run app/Chat_app.py
    ```
    Your web browser should automatically open to the chat application.

## 5. How to Run the Evaluation

To run the full, objective quality assessment of the RAG and recommendation systems, there are two options:
1. Run the evaluation in the terminal 
    1.1  Ensure the backend server is running (see step 4.1).
    1.2  Open a **third** terminal, activate the virtual environment, and run the evaluation script:
        ```bash
         python evaluation.py
        ```
        The results will be printed to the console and saved in `evaluation_results.json`. You can also view a summary of the latest evaluation run on the "Metrics" page of the Streamlit app.
2. Run the evaluation within the **metrics** page
    Hit the button "Run full system evaluation" and wait for the process to finish.