import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Textarea } from '../ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { useProcessingStore } from '../../store/useProcessingStore'
import { toast } from 'sonner'
import ResumeFormEditor from './ResumeFormEditor'

const DataEditor: React.FC = () => {
  const { editedData, originalResults } = useProcessingStore()

  const saveJsonChanges = () => {
    // This function is now handled by the ResumeFormEditor component
    toast.success('Data saved successfully!')
  }

  // Helper function to create better filenames using person's name
  const createFilename = (baseFilename: string, data?: any) => {
    if (data?.name && data.name !== 'Unknown' && data.name !== 'Resume Candidate') {
      const cleanName = data.name.replace(/[^a-zA-Z\s]/g, '').trim().replace(/\s+/g, '_')
      const extension = baseFilename.split('.').pop()
      const baseName = baseFilename.split('.')[0]
      return `${cleanName}_${baseName}.${extension}`
    }
    return baseFilename
  }

  const exportJson = (data: any, filename: string) => {
    const finalFilename = createFilename(filename, data)
    const blob = new Blob([JSON.stringify(data, null, 2)], { 
      type: 'application/json' 
    })
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = finalFilename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const exportText = (text: string, filename: string, data?: any) => {
    const finalFilename = createFilename(filename, data)
    const blob = new Blob([text], { type: 'text/plain' })
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = finalFilename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  if (!originalResults) return null

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800">
          💡 <strong>Export Options:</strong> You can export your resume as JSON, TXT, or DOCX format. 
          Use the buttons below or the Quick Export section in the sidebar.
        </p>
      </div>

      <Tabs defaultValue="step3" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="step1">📊 Step 1: Extracted</TabsTrigger>
          <TabsTrigger value="step2">🔄 Step 2: Restructured</TabsTrigger>
          <TabsTrigger value="step3">✨ Step 3: Final Data</TabsTrigger>
          <TabsTrigger value="formatted">📄 Final Formatted</TabsTrigger>
        </TabsList>

        <TabsContent value="step1">
          <Card>
            <CardHeader>
              <CardTitle>📊 Step 1: Extracted Data</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={JSON.stringify(originalResults.step1_extracted_data, null, 2)}
                readOnly
                className="min-h-[400px] font-mono text-sm"
              />
              <div className="mt-4 flex gap-2">
                <Button
                  onClick={() => exportJson(
                    originalResults.step1_extracted_data, 
                    'extracted_data.json'
                  )}
                  variant="outline"
                >
                  📥 Export Step 1 Data (JSON)
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="step2">
          <Card>
            <CardHeader>
              <CardTitle>🔄 Step 2: Restructured Text</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={originalResults.step2_restructured_text}
                readOnly
                className="min-h-[400px]"
              />
              <div className="mt-4 flex gap-2">
                <Button
                  onClick={() => exportText(
                    originalResults.step2_restructured_text, 
                    'restructured_resume.txt',
                    originalResults.step1_extracted_data
                  )}
                  variant="outline"
                >
                  📥 Export Step 2 Text (TXT)
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="step3">
          <Card>
            <CardHeader>
              <CardTitle>✨ Step 3: Final Data (User-Friendly Editor)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResumeFormEditor 
                data={editedData} 
                onSave={saveJsonChanges}
                onExport={() => exportJson(editedData, 'final_resume_data.json')}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="formatted">
          <Card>
            <CardHeader>
              <CardTitle>📄 Final Formatted Resume</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={originalResults.step3_final_formatted}
                readOnly
                className="min-h-[400px]"
              />
              <div className="mt-4 flex gap-2">
                <Button
                  onClick={() => exportText(
                    originalResults.step3_final_formatted, 
                    'formatted_resume.txt',
                    editedData
                  )}
                  variant="outline"
                >
                  📥 Export Formatted Resume (TXT)
                </Button>
                <Button
                  onClick={() => exportJson(
                    originalResults, 
                    'all_processing_results.json'
                  )}
                  variant="outline"
                >
                  📥 Export All Results (JSON)
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default DataEditor