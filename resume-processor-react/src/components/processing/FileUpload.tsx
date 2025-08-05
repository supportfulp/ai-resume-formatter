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
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 bg-blue-100 rounded-lg">
            📁
          </div>
          Upload Resume
        </CardTitle>
        <CardDescription>Choose a PDF file to process through our AI pipeline</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragActive 
              ? 'border-blue-500 bg-blue-50 scale-105' 
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <div className="space-y-2">
              <div className="text-4xl mb-4">📄</div>
              <p className="text-lg font-medium text-blue-600">Drop the PDF file here...</p>
              <p className="text-sm text-gray-500">Release to upload</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-6xl mb-4">📁</div>
              <div>
                <p className="text-xl font-medium text-gray-700 mb-2">
                  Drag & drop a PDF file here
                </p>
                <p className="text-gray-500 mb-4">or click to browse files</p>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-600">
                  <span>📄</span>
                  <span>PDF files only</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {acceptedFiles[0] && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-full">
                <span className="text-green-600">✅</span>
              </div>
              <div className="flex-1">
                <p className="font-medium text-green-800">
                  File uploaded successfully
                </p>
                <p className="text-sm text-green-600">
                  {acceptedFiles[0].name} ({(acceptedFiles[0].size / 1024 / 1024).toFixed(2)} MB)
                </p>
              </div>
            </div>
            
            {!processingComplete && (
              <Button 
                onClick={processResume}
                disabled={isProcessing || !apiKey}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700"
                size="lg"
              >
                {isProcessing ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Processing...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    🚀 Process Resume (3 Steps)
                  </div>
                )}
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default FileUpload