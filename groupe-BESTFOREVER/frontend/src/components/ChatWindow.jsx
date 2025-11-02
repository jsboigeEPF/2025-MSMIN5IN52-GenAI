import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatWindow = ({ messages }) => {
  return (
    <div className="flex-1 p-4 overflow-y-auto">
      {messages.map((msg, index) => (
        <div key={index} className={`mb-4 ${msg.isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block p-2 rounded-lg ${msg.isUser ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'}`}>
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatWindow;
