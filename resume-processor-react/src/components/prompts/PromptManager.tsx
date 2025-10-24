import React, { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Textarea } from '../ui/textarea'
import { Badge } from '../ui/badge'
import { promptsAPI } from '../../services/api'
import { useAuthStore } from '../../store/useAuthStore'
import { useProcessingStore } from '../../store/useProcessingStore'
import { CustomPrompt } from '../../types'
import { toast } from 'sonner'

const DEFAULT_PROMPT = `You are a professional resume restructuring expert. Your task is to transform the provided resume data into a specific format while preserving all important information.

Please restructure the following resume data: {resume_data}

Use reference number: {reference_number}

Ensure the output follows a professional format and maintains all key information about the candidate's experience, skills, and qualifications.`

interface PromptFormData {
  name: string
  prompt_text: string
}

const PromptManager: React.FC = () => {
  const { user, demoMode } = useAuthStore()
  const { selectedPrompt, selectedPromptName, setSelectedPrompt } = useProcessingStore()
  const [customPrompts, setCustomPrompts] = useState<CustomPrompt[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [expandedPrompt, setExpandedPrompt] = useState<number | null>(null)

  const { register, handleSubmit, reset, formState: { errors } } = useForm<PromptFormData>({
    defaultValues: {
      prompt_text: DEFAULT_PROMPT
    }
  })

  const loadCustomPrompts = useCallback(async () => {
    if (!user) return
    
    try {
      const response = await promptsAPI.getCustomPrompts(user.id)
      if (response.success && response.data) {
        setCustomPrompts(response.data)
      }
    } catch (error) {
      console.error('Failed to load custom prompts:', error)
    }
  }, [user])

  useEffect(() => {
    if (user && !demoMode) {
      loadCustomPrompts()
    }
  }, [user, demoMode, loadCustomPrompts])

  const onCreatePrompt = async (data: PromptFormData) => {
    if (!user) return

    if (demoMode) {
      toast.error('Cannot save prompts in demo mode')
      return
    }

    setIsLoading(true)
    try {
      const response = await promptsAPI.saveCustomPrompt(user.id, data.name, data.prompt_text)
      if (response.success) {
        toast.success('Custom prompt saved successfully!')
        reset()
        loadCustomPrompts()
      } else {
        toast.error(response.error || 'Failed to save prompt')
      }
    } catch (error) {
      toast.error('Failed to save custom prompt')
    } finally {
      setIsLoading(false)
    }
  }

  const deletePrompt = async (promptId: number) => {
    if (!user || demoMode) return

    try {
      const response = await promptsAPI.deleteCustomPrompt(promptId, user.id)
      if (response.success) {
        toast.success('Prompt deleted successfully!')
        loadCustomPrompts()
      } else {
        toast.error('Failed to delete prompt')
      }
    } catch (error) {
      toast.error('Failed to delete prompt')
    }
  }

  const selectPrompt = (prompt: string, name: string) => {
    setSelectedPrompt(prompt, name)
    toast.success(`Now using prompt: ${name}`)
  }

  const previewPrompt = selectedPrompt || DEFAULT_PROMPT
  const previewText = previewPrompt.length > 500 
    ? previewPrompt.substring(0, 500) + '...' 
    : previewPrompt

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>🎯 Current Prompt Selection</CardTitle>
          <CardDescription>Choose which prompt to use for processing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Selected Prompt: {selectedPromptName}</p>
                <Badge variant="default" className="mt-1">Active</Badge>
              </div>
              <Button
                onClick={() => selectPrompt(DEFAULT_PROMPT, 'Default')}
                variant="outline"
                size="sm"
              >
                Use Default
              </Button>
            </div>
            
            <div className="border rounded-md p-3 bg-gray-50 dark:bg-gray-800/60 dark:border-gray-700">
              <p className="text-sm font-medium mb-2">👀 Current Prompt Preview:</p>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{previewText}</p>
              {previewPrompt.length > 500 && (
                <p className="text-xs text-gray-500 mt-1">(Showing first 500 characters)</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>📝 Create New Custom Prompt</CardTitle>
          <CardDescription>Design your own prompt template</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onCreatePrompt)} className="space-y-4">
            <div>
              <Input
                placeholder="Enter prompt name"
                {...register('name', { required: 'Prompt name is required' })}
              />
              {errors.name && (
                <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>
              )}
              <p className="text-sm text-gray-500 mt-1">Prompt Name</p>
            </div>

            <div>
              <Textarea
                placeholder="Enter your custom prompt template"
                className="min-h-[200px]"
                {...register('prompt_text', { required: 'Prompt text is required' })}
              />
              {errors.prompt_text && (
                <p className="text-sm text-red-500 mt-1">{errors.prompt_text.message}</p>
              )}
              <p className="text-sm text-gray-500 mt-1">Prompt Template</p>
            </div>

            <Button 
              type="submit" 
              disabled={isLoading || demoMode}
              className="w-full"
            >
              {isLoading ? 'Saving...' : '💾 Save New Prompt'}
            </Button>

            {demoMode && (
              <p className="text-sm text-amber-600">
                ⚠️ Prompt saving is disabled in demo mode
              </p>
            )}
          </form>

          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-md dark:border-blue-900/40">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Available Placeholders</h4>
            <div className="text-sm text-blue-800 space-y-1">
              <p><code className="bg-blue-100 px-1 rounded">{'{resume_data}'}</code> - The structured resume data to process</p>
              <p><code className="bg-blue-100 px-1 rounded">{'{reference_number}'}</code> - The reference number for the resume</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {customPrompts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>📋 Manage Custom Prompts</CardTitle>
            <CardDescription>View and manage your saved prompts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {customPrompts.map((prompt) => (
                <div key={prompt.id} className="border rounded-md p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h4 className="font-medium">{prompt.name}</h4>
                      <p className="text-sm text-gray-500">
                        Created: {new Date(prompt.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={() => selectPrompt(prompt.prompt_text, prompt.name)}
                        variant="default"
                        size="sm"
                      >
                        📋 Use This Prompt
                      </Button>
                      <Button
                        onClick={() => setExpandedPrompt(
                          expandedPrompt === prompt.id ? null : prompt.id
                        )}
                        variant="outline"
                        size="sm"
                      >
                        {expandedPrompt === prompt.id ? 'Hide' : 'View'}
                      </Button>
                      <Button
                        onClick={() => deletePrompt(prompt.id)}
                        variant="destructive"
                        size="sm"
                      >
                        🗑️ Delete
                      </Button>
                    </div>
                  </div>
                  
                  {expandedPrompt === prompt.id && (
                    <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800/60 rounded border dark:border-gray-700">
                      <p className="text-sm whitespace-pre-wrap">{prompt.prompt_text}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default PromptManager