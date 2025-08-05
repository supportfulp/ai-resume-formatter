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
        <CardTitle>🔄 Processing Steps</CardTitle>
        {isProcessing && (
          <div className="space-y-2">
            <Progress value={progress} />
            <p className="text-sm text-gray-600">
              Step {completedSteps + 1} of {processingSteps.length}
            </p>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {processingSteps.map((step, index) => (
            <div key={step.step} className="flex items-center space-x-3">
              {getStepIcon(step.status)}
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">
                    Step {step.step}: {step.name}
                  </h4>
                  {getStepBadge(step.status)}
                </div>
                {step.error && (
                  <p className="text-sm text-red-500 mt-1">{step.error}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default ProcessingSteps