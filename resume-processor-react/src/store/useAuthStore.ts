import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '../types'
import { authAPI } from '../services/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  apiKey: string
  apiKeySetupTime: number | null
  hasApiKey: boolean | null
  demoMode: boolean
  sessionToken: string | null
  login: (user: User) => void
  logout: () => void
  setApiKey: (apiKey: string, persist?: boolean) => Promise<void>
  setDemoMode: (demo: boolean) => void
  setSessionToken: (token: string | null) => void
  loadApiKey: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      apiKey: '',
      apiKeySetupTime: null,
      hasApiKey: null,
      demoMode: false,
      sessionToken: null,
      login: (user) =>
        set({
          user,
          isAuthenticated: true,
        }),
      logout: async () => {
        const { sessionToken } = get()
        if (sessionToken) {
          try {
            await authAPI.logout(sessionToken)
          } catch (error) {
            console.error('Logout error:', error)
          }
        }
        set({
          user: null,
          isAuthenticated: false,
          apiKey: '',
          apiKeySetupTime: null,
          hasApiKey: null,
          sessionToken: null,
        })
      },
      setApiKey: async (apiKey, persist = true) => {
        const { user, demoMode } = get()
        
        set({
          apiKey,
          apiKeySetupTime: Date.now(),
          hasApiKey: true,
        })

        // Save to database if not in demo mode and user is logged in
        if (persist && !demoMode && user?.id) {
          try {
            await authAPI.saveApiKey(user.id, apiKey)
          } catch (error) {
            console.error('Failed to save API key:', error)
          }
        }
      },
      setDemoMode: (demo) =>
        set({
          demoMode: demo,
        }),
      setSessionToken: (token) =>
        set({
          sessionToken: token,
        }),
      loadApiKey: async () => {
        const { user, demoMode } = get()
        if (!demoMode && user?.id) {
          try {
            const response = await authAPI.getApiKey(user.id)
            if (response.success && response.data?.has_api_key) {
              // Don't set the actual key, just mark as configured
              set({
                apiKeySetupTime: Date.now(),
                hasApiKey: true,
              })
            } else {
              set({ hasApiKey: false })
            }
          } catch (error) {
            console.error('Failed to load API key status:', error)
            set({ hasApiKey: false })
          }
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        demoMode: state.demoMode,
        sessionToken: state.sessionToken,
        apiKeySetupTime: state.apiKeySetupTime,
      }),
    }
  )
)