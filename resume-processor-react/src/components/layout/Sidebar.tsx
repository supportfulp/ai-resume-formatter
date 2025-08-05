import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { useAuthStore } from '../../store/useAuthStore'
import { useProcessingStore } from '../../store/useProcessingStore'
import { maskApiKey, formatElapsedTime } from '../../lib/utils'
import { processingAPI } from '../../services/api'
import { toast } from 'sonner'

const Sidebar: React.FC = () => {
  const { user, apiKey, apiKeySetupTime, demoMode } = useAuthStore()
  const { processingComplete, editedData, currentFilename } = useProcessingStore()

  const handleQuickExportDocx = async () => {
    if (!editedData) return

    try {
      const filename = `resume_${currentFilename.replace('.pdf', '')}.docx`
      const blob = await processingAPI.exportDocx(editedData, filename)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success('DOCX exported successfully!')
    } catch (error) {
      toast.error('Failed to export DOCX')
    }
  }

  const handleQuickExportJson = () => {
    if (!editedData) return

    const filename = `resume_data_${currentFilename.replace('.pdf', '')}.json`
    const blob = new Blob([JSON.stringify(editedData, null, 2)], { 
      type: 'application/json' 
    })
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    toast.success('JSON exported successfully!')
  }

  return (
    <div className="w-80 border-r bg-background p-4 space-y-4">
      {/* User Profile Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">👤 {user?.username}</CardTitle>
          <CardDescription>{user?.email || 'User'}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* API Key Status */}
          {apiKey ? (
            <>
              <Badge variant="default">🔑 API Key: Configured</Badge>
              <p className="text-sm text-gray-600">
                Key: {maskApiKey(apiKey)}
              </p>
              {apiKeySetupTime && (
                <p className="text-sm text-gray-500">
                  ⏱️ Setup: {formatElapsedTime(apiKeySetupTime)}
                </p>
              )}
            </>
          ) : (
            <Badge variant="destructive">⚠️ API Key: Not set</Badge>
          )}

          {/* Demo Mode Indicator */}
          {demoMode && (
            <div className="p-2 bg-blue-50 rounded text-sm text-blue-800">
              🔧 Demo Mode - No persistent storage
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Export Section */}
      {processingComplete && editedData && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">📤 Quick Export</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button 
              onClick={handleQuickExportDocx}
              variant="default" 
              className="w-full"
            >
              📄 Export to DOCX
            </Button>
            <Button 
              onClick={handleQuickExportJson}
              variant="outline" 
              className="w-full"
            >
              📄 Export to JSON
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Sidebar