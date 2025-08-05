import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { historyAPI } from '../../services/api'
import { useAuthStore } from '../../store/useAuthStore'
import { useProcessingStore } from '../../store/useProcessingStore'
import { ProcessingHistory } from '../../types'
import { toast } from 'sonner'

const ProcessingHistoryComponent: React.FC = () => {
  const { user, demoMode } = useAuthStore()
  const { setEditedData, setProcessingComplete } = useProcessingStore()
  const [history, setHistory] = useState<ProcessingHistory[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (user && !demoMode) {
      loadHistory()
    }
  }, [user, demoMode])

  const loadHistory = async () => {
    if (!user) return

    setIsLoading(true)
    try {
      const response = await historyAPI.getProcessingHistory(user.id, 10)
      if (response.success && response.data) {
        setHistory(response.data)
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadResult = async (historyId: number) => {
    try {
      const response = await historyAPI.getProcessingResult(historyId)
      if (response.success && response.data) {
        setEditedData(response.data)
        setProcessingComplete(true)
        toast.success('Result loaded successfully!')
      } else {
        toast.error('No result data found for this record')
      }
    } catch (error) {
      toast.error('Failed to load result')
    }
  }

  const deleteRecord = async (historyId: number) => {
    if (!user) return

    try {
      const response = await historyAPI.deleteHistory(historyId, user.id)
      if (response.success) {
        toast.success('Record deleted successfully!')
        loadHistory()
      } else {
        toast.error('Failed to delete record')
      }
    } catch (error) {
      toast.error('Failed to delete record')
    }
  }

  if (demoMode) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>📊 Processing History</CardTitle>
          <CardDescription>View your past processing results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500">
              🔧 Demo Mode - No persistent storage available
            </p>
            <p className="text-sm text-gray-400 mt-2">
              History is not saved in demo mode
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>📊 Processing History</CardTitle>
        <CardDescription>View and manage your past processing results</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading history...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No processing history found</p>
            <p className="text-sm text-gray-400 mt-2">
              Process some resumes to see them appear here
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((record) => (
              <div key={record.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium">📄 {record.filename}</h4>
                    <p className="text-sm text-gray-500">
                      🕒 {new Date(record.processing_date).toLocaleString()}
                    </p>
                    {record.metadata && (
                      <div className="mt-1">
                        <Badge variant="secondary">
                          {record.status}
                        </Badge>
                        {record.metadata.prompt_used && (
                          <Badge variant="outline" className="ml-2">
                            Prompt: {record.metadata.prompt_used}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => loadResult(record.id)}
                      variant="default"
                      size="sm"
                    >
                      🔄 Load Result
                    </Button>
                    <Button
                      onClick={() => deleteRecord(record.id)}
                      variant="destructive"
                      size="sm"
                    >
                      🗑️ Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default ProcessingHistoryComponent