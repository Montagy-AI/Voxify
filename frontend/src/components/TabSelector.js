import React from 'react';

const TabSelector = ({ activeTab, onTabChange, tabs }) => {
  return (
    <div className="flex border-b border-zinc-800 mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => !tab.disabled && onTabChange(tab.id)}
          disabled={tab.disabled}
          className={`px-6 py-3 font-medium transition-all duration-200 border-b-2 ${
            tab.disabled
              ? 'text-gray-600 border-transparent cursor-not-allowed opacity-50'
              : activeTab === tab.id
              ? 'text-white border-white bg-zinc-800'
              : 'text-gray-400 border-transparent hover:text-gray-300 hover:border-gray-600'
          }`}
          title={tab.disabled ? 'This feature is not available for the selected language' : ''}
        >
          {tab.label}
          {tab.disabled && (
            <span className="ml-2 text-xs">(ZH/EN only)</span>
          )}
        </button>
      ))}
    </div>
  );
};

export default TabSelector;