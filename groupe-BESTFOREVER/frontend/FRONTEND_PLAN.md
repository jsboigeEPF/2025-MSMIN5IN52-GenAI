# Frontend Plan: AI Trip Planner

This document outlines the plan for the frontend of the AI Trip Planner application.

## 1. Technology Stack

*   **Framework:** React (with Vite for a fast development experience)
    *   **Reasoning:** React is a popular and efficient library for building user interfaces. Vite provides a very fast development server and build process.
*   **Language:** JavaScript (JSX)
*   **Styling:** Tailwind CSS
    *   **Reasoning:** Tailwind CSS is a utility-first CSS framework that allows for rapid UI development and easy customization without writing custom CSS.
*   **HTTP Client:** Axios
    *   **Reasoning:** Axios is a promise-based HTTP client for the browser and node.js, making API requests straightforward.

## 2. Core Components

*   **`App.jsx`:** The main application component that orchestrates other components.
*   **`ChatWindow.jsx`:** Displays the conversation history between the user and the AI.
*   **`MessageInput.jsx`:** Provides an input field for the user to type messages and a send button.
*   **`ModelSelector.jsx`:** A component (e.g., dropdown or radio buttons) to allow the user to select between OpenAI and Gemini models.

## 3. Functionality

*   **Display Messages:** Render a list of messages, distinguishing between user and AI messages.
*   **Send Messages:** Capture user input and send it to the backend's `/api/chat` endpoint.
*   **Select AI Model:** Allow users to choose their preferred AI model (OpenAI or Gemini) before sending a message.
*   **Loading Indicator:** Show a visual indicator while waiting for a response from the AI.
*   **Error Handling:** Display user-friendly error messages if there are issues with API calls or AI responses.
*   **Session Management:** Maintain a `session_id` to ensure conversation continuity with the backend.

## 4. Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/             # For images, icons, etc.
│   ├── components/         # Reusable UI components
│   │   ├── ChatWindow.jsx
│   │   ├── MessageInput.jsx
│   │   └── ModelSelector.jsx
│   ├── App.jsx             # Main application component
│   ├── main.jsx            # Entry point for React application
│   └── index.css           # Global styles, including Tailwind CSS imports
├── .env                    # Frontend environment variables (e.g., VITE_BACKEND_URL)
├── package.json            # Project dependencies and scripts
└── vite.config.js          # Vite configuration
```

## 5. Next Steps (after plan approval)

1.  Scaffold a new React project using Vite within the `frontend/` directory.
2.  Install necessary dependencies (`tailwindcss`, `axios`).
3.  Configure Tailwind CSS.
4.  Create the basic `App.jsx`, `ChatWindow.jsx`, `MessageInput.jsx`, and `ModelSelector.jsx` components.
5.  Implement basic chat functionality and model selection, connecting to the backend API.
