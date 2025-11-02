import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatWindow = ({ messages }) => {
  return (
    <div className="flex-1 p-4 overflow-y-auto">
      {messages.map((msg, index) => (
        <div key={index} className={`mb-4 ${msg.isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block p-2 rounded-lg ${msg.isUser ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Make all links open in new tab with target="_blank"
                a: ({ node, ...props }) => (
                  <a
                    {...props}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-blue-600"
                    style={{ color: msg.isUser ? '#ADD8E6' : '#0066CC' }}
                  />
                ),
              }}
            >
              {msg.text}
            </ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatWindow;