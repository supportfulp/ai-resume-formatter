import React, { useEffect } from 'react'
import { Button } from '../ui/button'
import { useAuthStore } from '../../store/useAuthStore'
import { useThemeStore, applyThemeClass } from '../../store/useThemeStore'

interface HeaderProps {
  selectedTab: string
  onTabChange: (tab: string) => void
}

const Header: React.FC<HeaderProps> = ({ selectedTab, onTabChange }) => {
  const { logout } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()

  useEffect(() => {
    applyThemeClass(theme)
  }, [theme])

  const tabs = [
    { id: 'processing', label: 'Processing', icon: '📁' },
    { id: 'prompts', label: 'Prompts', icon: '🔧' },
    { id: 'history', label: 'History', icon: '📊' },
    { id: 'dashboard', label: 'Dashboard', icon: '💰' },
    { id: 'profile', label: 'Profile', icon: '👤' },
  ]

  return (
    <header className="sticky top-0 z-40 border-b backdrop-blur supports-[backdrop-filter]:bg-background/80 bg-background">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between gap-4">
        <nav className="flex items-center gap-1">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => onTabChange(t.id)}
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                selectedTab === t.id
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              }`}
            >
              <span className="mr-1">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>

        <div className="text-center hidden md:block">
          <h1 className="text-2xl font-bold gradient-text">📄 Resume Processing Tool</h1>
          <p className="text-gray-600 dark:text-gray-300 text-xs">
            Upload a PDF resume and process it through our 3-step AI pipeline
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button onClick={toggleTheme} variant="ghost" aria-label="Toggle theme">
            {theme === 'dark' ? '🌙' : '🌞'}
          </Button>
          <Button onClick={logout} variant="outline">
            🚪 Logout
          </Button>
        </div>
      </div>
    </header>
  )
}

export default Header