import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { useProcessingStore } from '../../store/useProcessingStore'
import { formatNumber, formatCurrency, formatCompactNumber } from '../../lib/utils'

const TokenUsageCard: React.FC = () => {
  const { originalResults } = useProcessingStore()

  if (!originalResults?.token_usage) return null

  const { total_tokens, cost_estimation } = originalResults.token_usage

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">💰</div>
          Token Usage & Cost
        </CardTitle>
        <CardDescription>Processing statistics for this session</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Compact list for narrow columns */}
        <div className="block xl:hidden space-y-3 mb-6">
          <div className="flex items-center justify-between p-3 rounded-md border border-blue-200 bg-blue-50 dark:border-blue-900/40 dark:bg-blue-950/20">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 bg-blue-100 rounded-full w-8 h-8 flex items-center justify-center">
                <span className="text-blue-600 font-bold">📥</span>
              </div>
              <span className="text-sm font-medium text-blue-900 dark:text-blue-200">Input Tokens</span>
            </div>
            <span className="text-base font-semibold text-blue-600 tabular-nums break-all max-w-[45%] text-right truncate">
              {formatCompactNumber(total_tokens.input_tokens)}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-md border border-green-200 bg-green-50 dark:border-green-900/40 dark:bg-green-950/20">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 bg-green-100 rounded-full w-8 h-8 flex items-center justify-center">
                <span className="text-green-600 font-bold">📤</span>
              </div>
              <span className="text-sm font-medium text-green-900 dark:text-green-200">Output Tokens</span>
            </div>
            <span className="text-base font-semibold text-green-600 tabular-nums break-all max-w-[45%] text-right truncate">
              {formatCompactNumber(total_tokens.output_tokens)}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-md border border-purple-200 bg-purple-50 dark:border-purple-900/40 dark:bg-purple-950/20">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 bg-purple-100 rounded-full w-8 h-8 flex items-center justify-center">
                <span className="text-purple-600 font-bold">📊</span>
              </div>
              <span className="text-sm font-medium text-purple-900 dark:text-purple-200">Total Tokens</span>
            </div>
            <span className="text-base font-semibold text-purple-600 tabular-nums break-all max-w-[45%] text-right truncate">
              {formatCompactNumber(total_tokens.total_tokens)}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-md border border-orange-200 bg-orange-50 dark:border-orange-900/40 dark:bg-orange-950/20">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 bg-orange-100 rounded-full w-8 h-8 flex items-center justify-center">
                <span className="text-orange-600 font-bold">💵</span>
              </div>
              <span className="text-sm font-medium text-orange-900 dark:text-orange-200">Estimated Cost</span>
            </div>
            <span className="text-base font-semibold text-orange-600 tabular-nums break-all max-w-[45%] text-right truncate">
              {formatCurrency(cost_estimation.total_cost_usd)}
            </span>
          </div>
        </div>

        {/* Tile grid for wide screens */}
        <div className="hidden xl:grid grid-cols-4 gap-4 mb-6">
          <div className="min-w-0 text-center p-4 rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-900/40 dark:bg-blue-950/20">
            <div className="p-2 bg-blue-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-blue-600 font-bold">📥</span>
            </div>
            <p className="text-2xl md:text-3xl xl:text-4xl font-bold text-blue-600 font-mono">
              {formatNumber(total_tokens.input_tokens)}
            </p>
            <p className="text-sm text-muted-foreground whitespace-nowrap">Input Tokens</p>
          </div>
          <div className="min-w-0 text-center p-4 rounded-lg border border-green-200 bg-green-50 dark:border-green-900/40 dark:bg-green-950/20">
            <div className="p-2 bg-green-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-green-600 font-bold">📤</span>
            </div>
            <p className="text-2xl md:text-3xl xl:text-4xl font-bold text-green-600 font-mono">
              {formatNumber(total_tokens.output_tokens)}
            </p>
            <p className="text-sm text-muted-foreground whitespace-nowrap">Output Tokens</p>
          </div>
          <div className="min-w-0 text-center p-4 rounded-lg border border-purple-200 bg-purple-50 dark:border-purple-900/40 dark:bg-purple-950/20">
            <div className="p-2 bg-purple-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-purple-600 font-bold">📊</span>
            </div>
            <p className="text-2xl md:text-3xl xl:text-4xl font-bold text-purple-600 font-mono">
              {formatNumber(total_tokens.total_tokens)}
            </p>
            <p className="text-sm text-muted-foreground whitespace-nowrap">Total Tokens</p>
          </div>
          <div className="min-w-0 text-center p-4 rounded-lg border border-orange-200 bg-orange-50 dark:border-orange-900/40 dark:bg-orange-950/20">
            <div className="p-2 bg-orange-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-orange-600 font-bold">💵</span>
            </div>
            <p className="text-xl md:text-2xl xl:text-3xl font-bold text-orange-600 font-mono">
              {formatCurrency(cost_estimation.total_cost_usd)}
            </p>
            <p className="text-sm text-muted-foreground whitespace-nowrap">Estimated Cost</p>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="font-semibold mb-2">📊 Detailed Cost Breakdown</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium">Input Cost:</p>
              <p className="text-gray-600">{formatCurrency(cost_estimation.input_cost_usd)}</p>
              <p className="font-medium mt-2">Output Cost:</p>
              <p className="text-gray-600">{formatCurrency(cost_estimation.output_cost_usd)}</p>
            </div>
            <div>
              <p className="font-medium">Model Used:</p>
              <p className="text-gray-600">{cost_estimation.model}</p>
              <p className="font-medium mt-2">Pricing:</p>
              <p className="text-gray-600">Input: $0.000125/1K tokens</p>
              <p className="text-gray-600">Output: $0.000375/1K tokens</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default TokenUsageCard