# Backend Plan: AI Trip Planner

This document outlines the plan for the backend of the AI Trip Planner application.

## 1. Technology Stack

*   **Framework:** FastAPI (Python)
    *   **Reasoning:** FastAPI is a modern, fast (high-performance) web framework for building APIs with Python. It's easy to learn, has automatic interactive documentation, and is well-suited for integrating with AI/ML libraries.
*   **AI Integration:** We will use a large language model (LLM) to power the conversational AI. This will be done via an API call to the LLM provider.
*   **Dependencies:**
    *   `fastapi`: The web framework.
    *   `uvicorn`: ASGI server to run the application.
    *   `pydantic`: For data validation.
    *   `requests` or `httpx`: For making requests to external APIs (LLM, travel data).
    *   `python-dotenv`: To manage environment variables (like API keys).

## 2. Core Functionality

The backend will provide an API for the frontend to communicate with the trip-planning AI. The core logic will be as follows:

1.  The user sends a message (e.g., "I want to go to Paris for a week in July").
2.  The backend receives the message and sends it to the LLM.
3.  The LLM extracts key information (destination, dates, duration, etc.).
4.  The LLM determines what information is missing and generates a clarifying question to the user (e.g., "What is your budget?").
5.  Once enough information is gathered, the LLM will call functions to search for flights, hotels, etc., using external APIs.
6.  The backend formats the results and sends them back to the frontend.

## 3. API Endpoints

We will start with a simple API structure.

*   **`POST /api/chat`**: The main endpoint for interacting with the AI.
    *   **Request Body:**
        ```json
        {
            "message": "User's message",
            "session_id": "A unique ID for the conversation"
        }
        ```
    *   **Response Body:**
        ```json
        {
            "reply": "AI's response",
            "data": {
                "flights": [],
                "hotels": []
            }
        }
        ```

## 4. Project Structure

```
backend/
├── .env
├── BACKEND_PLAN.md
├── main.py           # Main application file with FastAPI setup and endpoints
├── requirements.txt  # Python dependencies
└── core/
    ├── __init__.py
    ├── ai_service.py   # Logic for interacting with the LLM
    └── travel_service.py # Logic for fetching travel data (flights, hotels)
```

## 5. Next Steps

1.  Validate this plan.
2.  Set up the basic FastAPI application.
3.  Create the `requirements.txt` file.
4.  Implement the `/api/chat` endpoint.
5.  Develop the `ai_service` to connect to the LLM.
