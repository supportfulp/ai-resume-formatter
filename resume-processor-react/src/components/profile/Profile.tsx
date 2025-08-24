import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { useAuthStore } from '../../store/useAuthStore'
import { maskApiKey, formatElapsedTime, validateApiKey } from '../../lib/utils'
import { toast } from 'sonner'

const Profile: React.FC = () => {
  const { user, apiKey, apiKeySetupTime, demoMode, logout, setApiKey, hasApiKey } = useAuthStore()
  const [newKey, setNewKey] = useState('')
  const [saving, setSaving] = useState(false)

  const onSave = async () => {
    if (!newKey) return
    if (!validateApiKey(newKey)) {
      toast.error('Invalid API key format')
      return
    }
    setSaving(true)
    try {
      await setApiKey(newKey, true)
      setNewKey('')
      toast.success('API key updated')
    } catch (e) {
      toast.error('Failed to update API key')
    } finally {
      setSaving(false)
    }
  }

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
            {apiKey || hasApiKey ? (
              <div className="space-y-1">
                <Badge>🔑 API Key: Configured</Badge>
                {apiKey && (
                  <p className="text-sm text-muted-foreground">Key: {maskApiKey(apiKey)}</p>
                )}
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

          <div className="h-px bg-border" />

          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Update API Key</p>
            <div className="flex gap-2">
              <Input
                type="password"
                placeholder="Enter new API key"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
              />
              <Button onClick={onSave} disabled={saving || !newKey}>
                {saving ? 'Saving...' : 'Save'}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">Stored securely on server; used by default.</p>
          </div>

          <div className="pt-2">
            <Button onClick={logout} variant="outline">🚪 Logout</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Profile


