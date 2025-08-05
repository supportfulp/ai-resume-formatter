import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { useAuthStore } from './store/useAuthStore'
import LoginForm from './components/auth/LoginForm'
import ApiKeySetup from './components/auth/ApiKeySetup'
import MainApp from './components/MainApp'

function App() {
  const { isAuthenticated, apiKey } = useAuthStore()

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={
              !isAuthenticated ? (
                <LoginForm />
              ) : !apiKey ? (
                <ApiKeySetup />
              ) : (
                <MainApp />
              )
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="top-right" richColors />
      </div>
    </Router>
  )
}

export default App