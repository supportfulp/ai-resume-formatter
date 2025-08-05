import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { useProcessingStore } from '../../store/useProcessingStore'
import { formatNumber, formatCurrency } from '../../lib/utils'

const TokenUsageCard: React.FC = () => {
  const { originalResults } = useProcessingStore()

  if (!originalResults?.token_usage) return null

  const { total_tokens, cost_estimation } = originalResults.token_usage

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 bg-green-100 rounded-lg">
            💰
          </div>
          Token Usage & Cost
        </CardTitle>
        <CardDescription>Processing statistics for this session</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="p-2 bg-blue-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-blue-600 font-bold">📥</span>
            </div>
            <p className="text-2xl font-bold text-blue-600">
              {formatNumber(total_tokens.input_tokens)}
            </p>
            <p className="text-sm text-gray-600">Input Tokens</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="p-2 bg-green-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-green-600 font-bold">📤</span>
            </div>
            <p className="text-2xl font-bold text-green-600">
              {formatNumber(total_tokens.output_tokens)}
            </p>
            <p className="text-sm text-gray-600">Output Tokens</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div className="p-2 bg-purple-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-purple-600 font-bold">📊</span>
            </div>
            <p className="text-2xl font-bold text-purple-600">
              {formatNumber(total_tokens.total_tokens)}
            </p>
            <p className="text-sm text-gray-600">Total Tokens</p>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
            <div className="p-2 bg-orange-100 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
              <span className="text-orange-600 font-bold">💵</span>
            </div>
            <p className="text-2xl font-bold text-orange-600">
              {formatCurrency(cost_estimation.total_cost_usd)}
            </p>
            <p className="text-sm text-gray-600">Estimated Cost</p>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="font-semibold mb-2">📊 Detailed Cost Breakdown</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
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