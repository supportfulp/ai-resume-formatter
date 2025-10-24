import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { useProcessingStore } from '../../store/useProcessingStore'
import { CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react'

const ProcessingSteps: React.FC = () => {
  const { processingSteps } = useProcessingStore()

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
          <div className="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">🔄</div>
          Processing Steps
        </CardTitle>
        <div className="space-y-3">
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>
              {completedSteps} of {processingSteps.length} completed
            </span>
            <span>{Math.round(progress)}%</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ol className="relative border-l border-gray-200 dark:border-gray-700 pl-6 space-y-6">
          {processingSteps.map((step) => (
            <li key={step.step} className="ml-4">
              <span
                className={`absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full border-2 bg-background text-xs ${
                  step.status === 'completed'
                    ? 'border-green-500 text-green-600'
                    : step.status === 'processing'
                    ? 'border-blue-500 text-blue-600'
                    : step.status === 'error'
                    ? 'border-red-500 text-red-600'
                    : 'border-gray-300 text-gray-500'
                }`}
              >
                {getStepIcon(step.status)}
              </span>
              <div
                className={`rounded-lg border p-4 transition-colors ${
                  step.status === 'completed'
                    ? 'border-green-200/60 bg-green-50 dark:border-green-900/40 dark:bg-green-950/20'
                    : step.status === 'processing'
                    ? 'border-blue-200/60 bg-blue-50 dark:border-blue-900/40 dark:bg-blue-950/20'
                    : step.status === 'error'
                    ? 'border-red-200/60 bg-red-50 dark:border-red-900/40 dark:bg-red-950/20'
                    : 'border-gray-200/60 bg-gray-50 dark:border-gray-800 dark:bg-gray-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Step {step.step}: {step.name}</h4>
                  {getStepBadge(step.status)}
                </div>
                {step.error && (
                  <p className="mt-2 rounded bg-red-100 p-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
                    ⚠️ {step.error}
                  </p>
                )}
              </div>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  )
}

export default ProcessingSteps