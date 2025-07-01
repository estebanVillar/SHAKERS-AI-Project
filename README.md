# Intelligent Technical Support System for Shakers

This project is a case study submission for the AI Specialist role. It implements an intelligent support system with a RAG (Retrieval-Augmented Generation) query service and a personalized recommendation engine for a fictional platform called "Shakers".

## Features

- **RAG Query Service**: Answers user questions based on a provided knowledge base of markdown files. It cites its sources and handles out-of-scope questions gracefully.
- **Personalized Recommendations**: Proactively suggests relevant articles from the knowledge base that the user hasn't consulted yet, based on their query history.
- **Interactive UI**: A multi-page Streamlit application with a chat interface and a metrics dashboard.
- **Metrics Dashboard**: Displays real-time performance metrics such as total queries and average response latency.

## System Architecture

The system consists of two main components:

1.  **Flask Backend (`app/main.py`)**: A Python server that exposes two API endpoints:
    -   `/api/query`: Handles the RAG pipeline. It takes a user query, retrieves relevant documents from a FAISS vector store, and uses Google's Gemini-1.5-Flash model to generate a contextualized answer.
    -   `/api/recommendations`: Takes a user's query history and recommends diverse, unconsulted articles.
2.  **Streamlit Frontend (`app/`)**: A multi-page web application for user interaction.
    -   `1_Chat.py`: The main chat interface.
    -   `pages/2_Metrics_Dashboard.py`: A dashboard to visualize system performance by reading from a log file.

## Tech Stack

- **Backend**: Flask, LangChain, Google Gemini (LLM & Embeddings), FAISS (Vector Store)
- **Frontend**: Streamlit
- **Language**: Python 3.10+

## Setup and Running the Project

**1. Clone the Repository**

git clone https://github.com/YOUR_USERNAME/shakers-ai-specialist-casestudy.git
cd shakers-ai-specialist-casestudy
Use code with caution.
Markdown
2. Create a Virtual Environment
Generated bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Use code with caution.
Bash
3. Install Dependencies
Generated bash
pip install -r requirements.txt
Use code with caution.
Bash
4. Set Up Environment Variables
Get a Google API key from Google AI Studio.
Create a file named .env in the project root.
Add your key to the file:
Generated code
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
Use code with caution.
5. Run the Application
You will need two separate terminals.
Terminal 1: Start the Flask Backend
Generated bash
python app/main.py
Use code with caution.
Bash
Terminal 2: Start the Streamlit Frontend
Generated bash
streamlit run app/1_Chat.py
Use code with caution.
Bash
The application will open in your browser at http://localhost:8501.
Generated code
**6. Commit Your Final Work**

This is your final commit before submission.

git add .
git commit -m "feat: Add metrics dashboard and finalize project documentation"
git push