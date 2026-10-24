import React from 'react';

const LoadingSpinner = () => {
  return (
    <div role="status" className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" aria-hidden="true"></div>
      <span className="sr-only">Loading</span>
    </div>
  );
};

export default LoadingSpinner;
