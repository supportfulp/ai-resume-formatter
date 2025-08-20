import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { useAuthStore } from '../../store/useAuthStore'
import { validateApiKey } from '../../lib/utils'
import { toast } from 'sonner'

interface ApiKeyFormData {
  apiKey: string
}

const ApiKeySetup: React.FC = () => {
  const [isValidating, setIsValidating] = useState(false)
  const { setApiKey, logout } = useAuthStore()
  const { register, handleSubmit, formState: { errors } } = useForm<ApiKeyFormData>()

  const onSubmit = async (data: ApiKeyFormData) => {
    setIsValidating(true)
    try {
      if (validateApiKey(data.apiKey)) {
        await setApiKey(data.apiKey, true) // Save to database
        toast.success('API key configured successfully!')
      } else {
        toast.error('Invalid API key format. Please check and try again.')
      }
    } catch (error) {
      toast.error('Failed to save API key.')
    } finally {
      setIsValidating(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">
            🔑 API Key Setup
          </h1>
          <p className="text-gray-600">
            Configure your Google API key to get started
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Google API Key Required</CardTitle>
            <CardDescription>
              Enter your Google API key to enable AI processing features
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <Input
                  type="password"
                  placeholder="Enter your Google API key"
                  {...register('apiKey', {
                    required: 'API key is required',
                    validate: (value) => validateApiKey(value) || 'Invalid API key format'
                  })}
                />
                {errors.apiKey && (
                  <p className="text-sm text-red-500 mt-1">{errors.apiKey.message}</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  Google API Key (starts with 'AI' and at least 30 characters)
                </p>
              </div>

              <div className="space-y-2">
                <Button type="submit" disabled={isValidating} className="w-full">
                  {isValidating ? 'Validating...' : '🔑 Set API Key'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={logout}
                  className="w-full"
                >
                  🚪 Logout
                </Button>
              </div>
            </form>

            <div className="mt-6 p-4 bg-blue-50 rounded-md">
              <h4 className="font-semibold text-blue-900 mb-2">💡 How to get your API key:</h4>
              <ol className="text-sm text-blue-800 space-y-1">
                <li>1. Go to Google AI Studio</li>
                <li>2. Create a new API key</li>
                <li>3. Copy the key and paste it above</li>
              </ol>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default ApiKeySetup