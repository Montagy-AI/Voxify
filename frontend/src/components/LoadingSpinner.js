import React from 'react';

const LoadingSpinner = ({ message = "Generating... This might take a while" }) => {
  return (
    <div className="mt-6 flex flex-col items-center space-y-4">
      {/* Spinning circle */}
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      
      {/* Loading message */}
      <div className="text-center">
        <p className="text-gray-300">{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;