import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 6,
    maximumFractionDigits: 6,
  }).format(amount)
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num)
}

export function formatCompactNumber(num: number): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(num)
}

export function validateApiKey(apiKey: string): boolean {
  if (!apiKey) return false
  return apiKey.length >= 30 && (apiKey.startsWith('AI') || apiKey.toLowerCase().includes('google'))
}

export function maskApiKey(apiKey: string): string {
  if (apiKey.length <= 12) return '***'
  return `${apiKey.slice(0, 8)}...${apiKey.slice(-4)}`
}

export function formatElapsedTime(timestamp: number): string {
  const elapsed = Date.now() - timestamp
  const hours = Math.floor(elapsed / (1000 * 60 * 60))
  const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60))
  return `${hours}h ${minutes}m ago`
}

