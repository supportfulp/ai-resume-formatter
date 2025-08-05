import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '../types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  apiKey: string
  apiKeySetupTime: number | null
  demoMode: boolean
  login: (user: User) => void
  logout: () => void
  setApiKey: (apiKey: string) => void
  setDemoMode: (demo: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      apiKey: '',
      apiKeySetupTime: null,
      demoMode: false,
      login: (user) =>
        set({
          user,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          user: null,
          isAuthenticated: false,
          apiKey: '',
          apiKeySetupTime: null,
        }),
      setApiKey: (apiKey) =>
        set({
          apiKey,
          apiKeySetupTime: Date.now(),
        }),
      setDemoMode: (demo) =>
        set({
          demoMode: demo,
        }),
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        demoMode: state.demoMode,
      }),
    }
  )
)