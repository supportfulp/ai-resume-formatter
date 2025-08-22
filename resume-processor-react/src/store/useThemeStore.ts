import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ThemeMode = 'light' | 'dark' | 'system'

interface ThemeState {
  theme: ThemeMode
  setTheme: (mode: ThemeMode) => void
  toggleTheme: () => void
}

function isSystemDark(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      setTheme: (mode) => set({ theme: mode }),
      toggleTheme: () => {
        const current = get().theme
        const next: ThemeMode = current === 'dark' ? 'light' : 'dark'
        set({ theme: next })
      },
    }),
    {
      name: 'theme-store',
    }
  )
)

export function applyThemeClass(theme: ThemeMode) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  const enableDark = theme === 'dark' || (theme === 'system' && isSystemDark())
  if (enableDark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}


