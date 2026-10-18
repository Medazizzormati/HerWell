import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '3rem', 
          textAlign: 'center',
          background: '#FEF2F2',
          margin: '2rem auto',
          maxWidth: '600px',
          borderRadius: '12px',
          border: '1px solid #FECACA'
        }}>
          <h2 style={{ color: '#DC2626', marginBottom: '1rem' }}>
            Something went wrong
          </h2>
          <p style={{ color: '#7A6455', marginBottom: '1rem' }}>
            An error occurred while loading this page. Please try refreshing.
          </p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#652D90',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
