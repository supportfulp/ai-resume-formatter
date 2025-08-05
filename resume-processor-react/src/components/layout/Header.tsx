import React from 'react'
import { Button } from '../ui/button'
import { useAuthStore } from '../../store/useAuthStore'

const Header: React.FC = () => {
  const { logout } = useAuthStore()

  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold gradient-text">
            📄 Resume Processing Tool
          </h1>
          <p className="text-gray-600 text-sm">
            Upload a PDF resume and process it through our 3-step AI pipeline
          </p>
        </div>
        <Button onClick={logout} variant="outline">
          🚪 Logout
        </Button>
      </div>
    </header>
  )
}

export default Header