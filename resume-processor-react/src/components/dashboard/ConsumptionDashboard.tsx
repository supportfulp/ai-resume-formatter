import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { tokenAPI } from '../../services/api'
import { useAuthStore } from '../../store/useAuthStore'
import { TokenUsage } from '../../types'
import { formatNumber, formatCurrency } from '../../lib/utils'

const ConsumptionDashboard: React.FC = () => {
  const { user, demoMode } = useAuthStore()
  const [tokenUsage, setTokenUsage] = useState<TokenUsage[]>([])
  const [stats, setStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  const loadTokenData = useCallback(async () => {
    if (!user) return

    setIsLoading(true)
    try {
      const [usageResponse, statsResponse] = await Promise.all([
        tokenAPI.getTokenUsage(user.id),
        tokenAPI.getTokenStats(user.id)
      ])

      if (usageResponse.success && usageResponse.data) {
        setTokenUsage(usageResponse.data)
      }

      if (statsResponse.success && statsResponse.data) {
        setStats(statsResponse.data)
      }
    } catch (error) {
      console.error('Failed to load token data:', error)
    } finally {
      setIsLoading(false)
    }
  }, [user])

  useEffect(() => {
    if (user && !demoMode) {
      loadTokenData()
    }
  }, [user, demoMode, loadTokenData])

  if (demoMode) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>💰 Consumption Dashboard</CardTitle>
          <CardDescription>Track your API usage and costs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500">
              🔧 Demo Mode - No consumption tracking available
            </p>
            <p className="text-sm text-gray-400 mt-2">
              Usage statistics are not tracked in demo mode
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_sessions || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {formatNumber(stats.total_tokens || 0)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(stats.total_cost || 0)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Cost/Session</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {formatCurrency(stats.average_cost_per_session || 0)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Usage */}
      <Card>
        <CardHeader>
          <CardTitle>📊 Recent Token Usage</CardTitle>
          <CardDescription>Your recent API consumption breakdown</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Loading usage data...</p>
            </div>
          ) : tokenUsage.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No usage data found</p>
              <p className="text-sm text-gray-400 mt-2">
                Process some resumes to see usage statistics here
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {tokenUsage.slice(0, 10).map((usage) => (
                <div key={usage.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-gray-500">
                        {new Date(usage.created_at).toLocaleString()}
                      </p>
                      <div className="grid grid-cols-3 gap-4 mt-2">
                        <div>
                          <p className="text-sm font-medium">Input Tokens</p>
                          <p className="text-lg font-bold text-blue-600">
                            {formatNumber(usage.input_tokens)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Output Tokens</p>
                          <p className="text-lg font-bold text-green-600">
                            {formatNumber(usage.output_tokens)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Total Cost</p>
                          <p className="text-lg font-bold text-purple-600">
                            {formatCurrency(usage.total_cost_usd)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pricing Information */}
      <Card>
        <CardHeader>
          <CardTitle>💰 Pricing Information</CardTitle>
          <CardDescription>Current API pricing structure</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Gemini 2.5 Flash Pricing (as of 2024):</h4>
              <ul className="space-y-1 text-sm">
                <li>• <strong>Input Tokens:</strong> $0.000125 per 1K tokens</li>
                <li>• <strong>Output Tokens:</strong> $0.000375 per 1K tokens</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2">Cost Calculation:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Input Cost = (Input Tokens ÷ 1000) × $0.000125</li>
                <li>• Output Cost = (Output Tokens ÷ 1000) × $0.000375</li>
                <li>• Total Cost = Input Cost + Output Cost</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ConsumptionDashboard