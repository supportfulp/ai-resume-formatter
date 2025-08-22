import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { useAuthStore } from '../../store/useAuthStore'
import { maskApiKey, formatElapsedTime } from '../../lib/utils'

const Profile: React.FC = () => {
  const { user, apiKey, apiKeySetupTime, demoMode, logout } = useAuthStore()

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>👤 Profile</CardTitle>
          <CardDescription>Your account and API configuration</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-muted-foreground">Username</p>
            <p className="text-lg font-medium">{user?.username || '—'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Email</p>
            <p className="text-lg font-medium">{user?.email || '—'}</p>
          </div>

          <div className="h-px bg-border" />

          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">API Key Status</p>
            {apiKey ? (
              <div className="space-y-1">
                <Badge>🔑 API Key: Configured</Badge>
                <p className="text-sm text-muted-foreground">Key: {maskApiKey(apiKey)}</p>
                {apiKeySetupTime && (
                  <p className="text-xs text-muted-foreground">⏱️ Setup: {formatElapsedTime(apiKeySetupTime)}</p>
                )}
              </div>
            ) : (
              <Badge variant="destructive">⚠️ API Key: Not set</Badge>
            )}
          </div>

          {demoMode && (
            <div className="p-2 rounded border bg-blue-50 dark:bg-blue-950/20 dark:border-blue-900/40 text-sm">
              🔧 Demo Mode - No persistent storage
            </div>
          )}

          <div className="pt-2">
            <Button onClick={logout} variant="outline">🚪 Logout</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Profile


