import React from 'react';

const ModelSelector = ({ selectedModel, onModelChange }) => {
  return (
    <div className="p-2 border-b">
      <label htmlFor="model-select" className="mr-2">Select AI Model:</label>
      <select
        id="model-select"
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value)}
        className="p-1 border rounded"
      >
        <option value="openai">OpenAI</option>
        <option value="gemini">Gemini</option>
      </select>
    </div>
  );
};

export default ModelSelector;
