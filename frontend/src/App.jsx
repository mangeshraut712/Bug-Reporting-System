import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import IssueListPage from './pages/IssueListPage';
import IssueDetailPage from './pages/IssueDetailPage';

const routerBasename = import.meta.env.BASE_URL.replace(/\/$/, '');

function App() {
  return (
    <Router basename={routerBasename || undefined}>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <a
            href="#main"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-blue-700 focus:shadow"
          >
            Skip to content
          </a>
          <Navbar />
          <main id="main">
            <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <DashboardPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/projects/:projectId/issues"
              element={
                <PrivateRoute>
                  <IssueListPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/issues/:issueId"
              element={
                <PrivateRoute>
                  <IssueDetailPage />
                </PrivateRoute>
              }
            />
              <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
          </main>
          <ToastContainer
            position="bottom-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
