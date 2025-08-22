import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App'

// Pre-apply persisted theme to avoid FOUC
try {
  const raw = localStorage.getItem('theme-store')
  if (raw) {
    const parsed = JSON.parse(raw)
    const theme = parsed?.state?.theme
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (theme === 'light') {
      document.documentElement.classList.remove('dark')
    } else {
      // system
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) document.documentElement.classList.add('dark')
    }
  }
} catch {}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)