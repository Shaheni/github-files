/**
 * Error Boundary - catches React component errors
 * Production-grade error handling at application level
 */

import React from 'react';
import { logger } from '../utils/logger';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    logger.error('React component error caught', {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#fee', border: '1px solid #c00' }}>
          <h2>Application Error</h2>
          <p>An unexpected error occurred. Please try refreshing the page.</p>
          {import.meta.env.DEV && (
            <details style={{ marginTop: '10px', padding: '10px', background: '#fff' }}>
              <summary>Error Details (Development Only)</summary>
              <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                {this.state.error?.toString()}
              </pre>
            </details>
          )}
          <button onClick={this.handleReset} style={{ marginTop: '10px' }}>
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
