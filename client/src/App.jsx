import React from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import Dashboard from './pages/Dashboard';
import './styles/dashboard.css';

/**
 * App Root Component
 * Wraps application with error boundary and initializes main dashboard
 */
function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}

export default App;
