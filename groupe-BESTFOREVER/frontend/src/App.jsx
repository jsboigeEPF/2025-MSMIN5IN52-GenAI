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

const App = () => {
  const [messages, setMessages] = useState([]);
  const [selectedModel, setSelectedModel] = useState('openai');
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setMessages([{ text: initialMessages[selectedLanguage], isUser: false }]);
  }, [selectedLanguage]);

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

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <h1 className="text-2xl font-bold text-center p-4 bg-white border-b">AI Trip Planner</h1>
      <div className="flex justify-between p-2 border-b">
        <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
        <LanguageSelector selectedLanguage={selectedLanguage} onLanguageChange={setSelectedLanguage} />
      </div>
      <ChatWindow messages={messages} />
      {isLoading && <div className="p-4 text-center">AI is thinking...</div>}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default App;
