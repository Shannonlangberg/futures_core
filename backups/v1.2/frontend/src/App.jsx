import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LogStats from './pages/LogStats';
import Pulse from './pages/Pulse';
import Passport from './pages/Passport';
import Query from './pages/Query';
import Users from './pages/Users';
import Campuses from './pages/Campuses';
import Settings from './pages/Settings';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
            <p className="text-slate-400 mb-4">Please refresh the page</p>
            <button 
              onClick={() => window.location.reload()} 
              className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg"
            >
              Refresh
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/session', {
          credentials: 'include',
        });
        
        if (response.ok) {
          const data = await response.json();
          // Check if user is authenticated (not guest)
          setIsAuthenticated(data.authenticated || data.user !== 'guest');
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check error:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout>
                <LogStats />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <MainLayout>
                <Dashboard />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/heartbeat" element={
            <ProtectedRoute>
              <MainLayout>
                <Pulse />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/journey" element={
            <ProtectedRoute>
              <MainLayout>
                <Passport />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/query" element={
            <ProtectedRoute>
              <MainLayout>
                <Query />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/users" element={
            <ProtectedRoute>
              <MainLayout>
                <Users />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/campuses" element={
            <ProtectedRoute>
              <MainLayout>
                <Campuses />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <MainLayout>
                <Settings />
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/settings/notifications" element={
            <ProtectedRoute>
              <MainLayout>
                <div className="max-w-4xl mx-auto">
                  <h1 className="text-3xl font-bold text-white mb-6">Notifications</h1>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400">Notification settings coming soon...</p>
                  </div>
                </div>
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/settings/profile" element={
            <ProtectedRoute>
              <MainLayout>
                <div className="max-w-4xl mx-auto">
                  <h1 className="text-3xl font-bold text-white mb-6">Profile</h1>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400">Profile settings coming soon...</p>
                  </div>
                </div>
              </MainLayout>
            </ProtectedRoute>
          } />
          <Route path="/settings/security" element={
            <ProtectedRoute>
              <MainLayout>
                <div className="max-w-4xl mx-auto">
                  <h1 className="text-3xl font-bold text-white mb-6">Security</h1>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400">Security settings coming soon...</p>
                  </div>
                </div>
              </MainLayout>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App; 