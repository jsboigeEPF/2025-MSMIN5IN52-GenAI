import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import ModelSelector from './components/ModelSelector';
import LanguageSelector from './components/LanguageSelector';

const initialMessages = {
  'en-US': "Hello! I'm your travel planning assistant. Where would you like to go?",
  'fr-FR': "Bonjour ! Je suis votre assistant de planification de voyage. Où souhaitez-vous aller ?",
};

const STORAGE_KEY = 'ai_trip_planner_chat_history';
const MODEL_KEY = 'ai_trip_planner_model';
const LANGUAGE_KEY = 'ai_trip_planner_language';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [selectedModel, setSelectedModel] = useState('openai');
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [isLoading, setIsLoading] = useState(false);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem(STORAGE_KEY);
    const savedModel = localStorage.getItem(MODEL_KEY);
    const savedLanguage = localStorage.getItem(LANGUAGE_KEY);

    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    } else {
      // Initialize with welcome message if no history
      setMessages([{ text: initialMessages[selectedLanguage], isUser: false }]);
    }

    if (savedModel) {
      setSelectedModel(savedModel);
    }

    if (savedLanguage) {
      setSelectedLanguage(savedLanguage);
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  // Save model selection to localStorage
  useEffect(() => {
    localStorage.setItem(MODEL_KEY, selectedModel);
  }, [selectedModel]);

  // Save language selection to localStorage
  useEffect(() => {
    localStorage.setItem(LANGUAGE_KEY, selectedLanguage);
  }, [selectedLanguage]);

  // Reset chat when language changes (optional behavior)
  const handleLanguageChange = (newLanguage) => {
    setSelectedLanguage(newLanguage);
    // Optionally reset chat with new language greeting
    // setMessages([{ text: initialMessages[newLanguage], isUser: false }]);
  };

  // Configure axios instance
  const api = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000',
  });

  const handleSendMessage = async (message) => {
    const userMessage = { text: message, isUser: true };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await api.post('/api/chat', {
        history: newMessages,
        session_id: 'some-unique-session-id',
        model_name: selectedModel,
        language: selectedLanguage,
      });

      const aiMessage = { text: response.data.reply, isUser: false };
      setMessages((prevMessages) => [...prevMessages, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { text: `Error: ${error.message}`, isUser: false };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear chat history
  const handleClearChat = () => {
    const confirmClear = window.confirm('Are you sure you want to clear the chat history?');
    if (confirmClear) {
      const newMessages = [{ text: initialMessages[selectedLanguage], isUser: false }];
      setMessages(newMessages);
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <h1 className="text-2xl font-bold text-center p-4 bg-white border-b">AI Trip Planner</h1>
      <div className="flex justify-between p-2 border-b">
        <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
        <LanguageSelector selectedLanguage={selectedLanguage} onLanguageChange={handleLanguageChange} />
        <button 
          onClick={handleClearChat}
          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
        >
          Clear Chat
        </button>
      </div>
      <ChatWindow messages={messages} />
      {isLoading && <div className="p-4 text-center">AI is thinking...</div>}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default App;