import React, { useState } from 'react';
import axios from 'axios';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import ModelSelector from './components/ModelSelector';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [selectedModel, setSelectedModel] = useState('openai');
  const [isLoading, setIsLoading] = useState(false);

  // Configure axios instance
  const api = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000',
  });

  const handleSendMessage = async (message) => {
    // Add user message to the chat
    const userMessage = { text: message, isUser: true };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.post('/api/chat', {
        message: message,
        session_id: 'some-unique-session-id', // You can generate a real unique ID here
        model_name: selectedModel,
      });

      // Add AI response to the chat
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

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <h1 className="text-2xl font-bold text-center p-4 bg-white border-b">AI Trip Planner</h1>
      <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
      <ChatWindow messages={messages} />
      {isLoading && <div className="p-4 text-center">AI is thinking...</div>}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default App;
