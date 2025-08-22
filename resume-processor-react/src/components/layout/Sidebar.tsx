import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { useProcessingStore } from '../../store/useProcessingStore'
import { processingAPI } from '../../services/api'
import { toast } from 'sonner'

interface SidebarProps {
  selectedTab: string
  onTabChange: (tab: string) => void
}

const Sidebar: React.FC<SidebarProps> = ({ selectedTab, onTabChange }) => {
  const { processingComplete, editedData, currentFilename } = useProcessingStore()

  const handleQuickExportDocx = async () => {
    if (!editedData) return

    try {
      // Create a better filename using the person's name if available
      let filename = `resume_${currentFilename.replace('.pdf', '')}.docx`
      
      // If we have the person's name, use it in the filename
      if (editedData.name && editedData.name !== 'Unknown' && editedData.name !== 'Resume Candidate') {
        const cleanName = editedData.name.replace(/[^a-zA-Z\s]/g, '').trim().replace(/\s+/g, ' ')
        filename = `${cleanName}.docx`
      }
      
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

    // Create a better filename using the person's name if available
    let filename = `resume_data_${currentFilename.replace('.pdf', '')}.json`
    
    // If we have the person's name, use it in the filename
    if (editedData.name && editedData.name !== 'Unknown' && editedData.name !== 'Resume Candidate') {
      const cleanName = editedData.name.replace(/[^a-zA-Z\s]/g, '').trim().replace(/\s+/g, '_')
      filename = `${cleanName}_Resume_Data.json`
    }
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
    <div className="w-80 border-r bg-background p-4 space-y-4 sticky top-[64px] h-[calc(100vh-64px)] overflow-y-auto">
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">⚡ Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Button 
              onClick={handleQuickExportDocx}
              variant="default" 
              className="w-full"
              disabled={!processingComplete || !editedData}
            >
              📄 Export to DOCX
            </Button>
            <Button 
              onClick={handleQuickExportJson}
              variant="outline" 
              className="w-full"
              disabled={!processingComplete || !editedData}
            >
              📄 Export to JSON
            </Button>
          </div>
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