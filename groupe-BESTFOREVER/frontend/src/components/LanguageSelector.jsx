import React from 'react';

const LanguageSelector = ({ selectedLanguage, onLanguageChange }) => {
  return (
    <div className="p-2 border-b">
      <label htmlFor="language-select" className="mr-2">Language:</label>
      <select
        id="language-select"
        value={selectedLanguage}
        onChange={(e) => onLanguageChange(e.target.value)}
        className="p-1 border rounded"
      >
        <option value="en-US">English (US)</option>
        <option value="fr-FR">Français (France)</option>
      </select>
    </div>
  );
};

export default LanguageSelector;
