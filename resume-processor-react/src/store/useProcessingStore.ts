import { create } from 'zustand'
import { ProcessingResult, ProcessingStep } from '../types'

interface ProcessingState {
  isProcessing: boolean
  currentFilename: string
  processingSteps: ProcessingStep[]
  processingComplete: boolean
  editedData: any
  originalResults: ProcessingResult | null
  selectedPrompt: string
  selectedPromptName: string
  setProcessing: (processing: boolean) => void
  setCurrentFilename: (filename: string) => void
  setProcessingSteps: (steps: ProcessingStep[]) => void
  updateProcessingStep: (stepIndex: number, update: Partial<ProcessingStep>) => void
  setProcessingComplete: (complete: boolean) => void
  setEditedData: (data: any) => void
  setOriginalResults: (results: ProcessingResult | null) => void
  setSelectedPrompt: (prompt: string, name: string) => void
  resetProcessing: () => void
}

export const useProcessingStore = create<ProcessingState>((set) => ({
  isProcessing: false,
  currentFilename: '',
  processingSteps: [
    { step: 1, name: 'Extract Data', status: 'pending' },
    { step: 2, name: 'Restructure', status: 'pending' },
    { step: 3, name: 'Final Format', status: 'pending' },
  ],
  processingComplete: false,
  editedData: null,
  originalResults: null,
  selectedPrompt: '',
  selectedPromptName: 'Default',
  setProcessing: (processing) => set({ isProcessing: processing }),
  setCurrentFilename: (filename) => set({ currentFilename: filename }),
  setProcessingSteps: (steps) => set({ processingSteps: steps }),
  updateProcessingStep: (stepIndex, update) =>
    set((state) => ({
      processingSteps: state.processingSteps.map((step, index) =>
        index === stepIndex ? { ...step, ...update } : step
      ),
    })),
  setProcessingComplete: (complete) => set({ processingComplete: complete }),
  setEditedData: (data) => set({ editedData: data }),
  setOriginalResults: (results) => set({ originalResults: results }),
  setSelectedPrompt: (prompt, name) =>
    set({ selectedPrompt: prompt, selectedPromptName: name }),
  resetProcessing: () =>
    set({
      isProcessing: false,
      currentFilename: '',
      processingSteps: [
        { step: 1, name: 'Extract Data', status: 'pending' },
        { step: 2, name: 'Restructure', status: 'pending' },
        { step: 3, name: 'Final Format', status: 'pending' },
      ],
      processingComplete: false,
      editedData: null,
      originalResults: null,
    }),
}))