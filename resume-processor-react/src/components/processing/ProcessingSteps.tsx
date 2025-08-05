import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { useProcessingStore } from '../../store/useProcessingStore'
import { CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react'

const ProcessingSteps: React.FC = () => {
  const { processingSteps, isProcessing } = useProcessingStore()

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'processing':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStepBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default">Completed</Badge>
      case 'processing':
        return <Badge variant="secondary">Processing...</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  const completedSteps = processingSteps.filter(step => step.status === 'completed').length
  const progress = (completedSteps / processingSteps.length) * 100

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 bg-blue-100 rounded-lg">
            🔄
          </div>
          Processing Steps
        </CardTitle>
        {isProcessing && (
          <div className="space-y-3">
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between text-sm text-gray-600">
              <span>Progress: {completedSteps} of {processingSteps.length} completed</span>
              <span>{Math.round(progress)}%</span>
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {processingSteps.map((step, index) => (
            <div 
              key={step.step} 
              className={`p-4 rounded-lg border transition-all duration-200 ${
                step.status === 'completed' 
                  ? 'bg-green-50 border-green-200' 
                  : step.status === 'processing'
                  ? 'bg-blue-50 border-blue-200'
                  : step.status === 'error'
                  ? 'bg-red-50 border-red-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${
                  step.status === 'completed' 
                    ? 'bg-green-100' 
                    : step.status === 'processing'
                    ? 'bg-blue-100'
                    : step.status === 'error'
                    ? 'bg-red-100'
                    : 'bg-gray-100'
                }`}>
                  {getStepIcon(step.status)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">
                      Step {step.step}: {step.name}
                    </h4>
                    {getStepBadge(step.status)}
                  </div>
                  {step.error && (
                    <p className="text-sm text-red-600 mt-1 bg-red-50 p-2 rounded">
                      ⚠️ {step.error}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default ProcessingSteps