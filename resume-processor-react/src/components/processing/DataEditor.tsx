import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Textarea } from '../ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { useProcessingStore } from '../../store/useProcessingStore'
import { toast } from 'sonner'

const DataEditor: React.FC = () => {
  const { editedData, originalResults, setEditedData } = useProcessingStore()
  const [jsonString, setJsonString] = useState('')
  const [isValidJson, setIsValidJson] = useState(true)

  useEffect(() => {
    if (editedData) {
      setJsonString(JSON.stringify(editedData, null, 2))
    }
  }, [editedData])

  const handleJsonChange = (value: string) => {
    setJsonString(value)
    try {
      JSON.parse(value)
      setIsValidJson(true)
    } catch {
      setIsValidJson(false)
    }
  }

  const saveJsonChanges = () => {
    try {
      const parsedData = JSON.parse(jsonString)
      setEditedData(parsedData)
      toast.success('Data saved successfully!')
    } catch {
      toast.error('Invalid JSON format. Please check your syntax.')
    }
  }

  const exportJson = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { 
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
  }

  const exportText = (text: string, filename: string) => {
    const blob = new Blob([text], { type: 'text/plain' })
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
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
                    'step1_extracted_data.json'
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
                    'step2_restructured.txt'
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
              <CardTitle>✨ Step 3: Final Data (Editable)</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={jsonString}
                onChange={(e) => handleJsonChange(e.target.value)}
                className={`min-h-[400px] font-mono text-sm ${
                  !isValidJson ? 'border-red-500' : ''
                }`}
                placeholder="Edit your resume data here..."
              />
              {!isValidJson && (
                <p className="text-red-500 text-sm mt-2">
                  ⚠️ Invalid JSON format. Please check your syntax.
                </p>
              )}
              <div className="mt-4 flex gap-2">
                <Button
                  onClick={saveJsonChanges}
                  disabled={!isValidJson}
                  variant="default"
                >
                  💾 Save Changes
                </Button>
                <Button
                  onClick={() => exportJson(editedData, 'step3_final_data.json')}
                  variant="outline"
                >
                  📥 Export Step 3 Data (JSON)
                </Button>
              </div>
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
                    'formatted_resume.txt'
                  )}
                  variant="outline"
                >
                  📥 Export Formatted Resume (TXT)
                </Button>
                <Button
                  onClick={() => exportJson(
                    originalResults, 
                    'all_results.json'
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