import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { logger } from './utils/logger';

// Log app startup
logger.info('Robot Arm Control App Starting', {
  env: import.meta.env.MODE,
  version: '1.0.0',
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
