import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { useProcessingStore } from '../../store/useProcessingStore'
import { useAuthStore } from '../../store/useAuthStore'
import { processingAPI } from '../../services/api'
import { toast } from 'sonner'

const FileUpload: React.FC = () => {
  const { apiKey } = useAuthStore()
  const {
    currentFilename,
    selectedPrompt,
    isProcessing,
    processingComplete,
    setCurrentFilename,
    setProcessing,
    setProcessingComplete,
    setEditedData,
    setOriginalResults,
    updateProcessingStep,
    resetProcessing,
  } = useProcessingStore()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      if (currentFilename !== file.name) {
        setCurrentFilename(file.name)
        resetProcessing()
      }
    }
  }, [currentFilename, setCurrentFilename, resetProcessing])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  })

  const processResume = async () => {
    if (!acceptedFiles[0] || !apiKey) return

    setProcessing(true)
    
    try {
      // Step 1: Extract Data
      updateProcessingStep(0, { status: 'processing' })
      
      // Step 2: Restructure
      updateProcessingStep(1, { status: 'processing' })
      
      // Step 3: Final Format
      updateProcessingStep(2, { status: 'processing' })

      const response = await processingAPI.processResume(
        acceptedFiles[0],
        apiKey,
        selectedPrompt || undefined
      )

      if (response.success && response.data) {
        // Mark all steps as completed
        updateProcessingStep(0, { status: 'completed', result: response.data.step1_extracted_data })
        updateProcessingStep(1, { status: 'completed', result: response.data.step2_restructured_text })
        updateProcessingStep(2, { status: 'completed', result: response.data.step3_final_data })

        setEditedData(response.data.step3_final_data)
        setOriginalResults(response.data)
        setProcessingComplete(true)
        
        toast.success('Processing complete! You can now edit the data below.')
      } else {
        // Mark all steps as error
        updateProcessingStep(0, { status: 'error', error: response.error })
        updateProcessingStep(1, { status: 'error', error: response.error })
        updateProcessingStep(2, { status: 'error', error: response.error })
        
        toast.error(response.error || 'Processing failed')
      }
    } catch (error) {
      // Mark all steps as error
      const errorMessage = error instanceof Error ? error.message : 'Processing failed'
      updateProcessingStep(0, { status: 'error', error: errorMessage })
      updateProcessingStep(1, { status: 'error', error: errorMessage })
      updateProcessingStep(2, { status: 'error', error: errorMessage })
      
      toast.error('Error processing resume: ' + errorMessage)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>📁 Upload Resume</CardTitle>
        <CardDescription>Choose a PDF file to process</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop the PDF file here...</p>
          ) : (
            <div>
              <p className="text-lg mb-2">📁 Drag & drop a PDF file here</p>
              <p className="text-gray-500">or click to select</p>
            </div>
          )}
        </div>

        {acceptedFiles[0] && (
          <div className="mt-4">
            <p className="text-sm font-medium text-green-600">
              ✅ File uploaded: {acceptedFiles[0].name}
            </p>
            
            {!processingComplete && (
              <Button 
                onClick={processResume}
                disabled={isProcessing || !apiKey}
                className="mt-4 w-full"
              >
                {isProcessing ? 'Processing...' : '🚀 Process Resume (3 Steps)'}
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default FileUpload