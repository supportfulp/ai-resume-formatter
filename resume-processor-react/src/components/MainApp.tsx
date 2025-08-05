import React, { useState } from 'react'
import Header from './layout/Header'
import Sidebar from './layout/Sidebar'
import FileUpload from './processing/FileUpload'
import ProcessingSteps from './processing/ProcessingSteps'
import TokenUsageCard from './processing/TokenUsageCard'
import DataEditor from './processing/DataEditor'
import PromptManager from './prompts/PromptManager'
import ProcessingHistory from './history/ProcessingHistory'
import ConsumptionDashboard from './dashboard/ConsumptionDashboard'
import { useProcessingStore } from '../store/useProcessingStore'

const MainApp: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState('processing')
  const { processingComplete } = useProcessingStore()

  const renderTabContent = () => {
    switch (selectedTab) {
      case 'processing':
        return (
          <div className="space-y-6">
            <FileUpload />
            <ProcessingSteps />
            {processingComplete && (
              <>
                <TokenUsageCard />
                <DataEditor />
              </>
            )}
          </div>
        )
      case 'prompts':
        return <PromptManager />
      case 'history':
        return <ProcessingHistory />
      case 'dashboard':
        return <ConsumptionDashboard />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 flex">
          {/* Navigation Sidebar */}
          <div className="w-64 border-r bg-background p-4">
            <nav className="space-y-2">
              <button
                onClick={() => setSelectedTab('processing')}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  selectedTab === 'processing'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                📁 Resume Processing
              </button>
              <button
                onClick={() => setSelectedTab('prompts')}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  selectedTab === 'prompts'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                🔧 Prompt Management
              </button>
              <button
                onClick={() => setSelectedTab('history')}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  selectedTab === 'history'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                📊 Processing History
              </button>
              <button
                onClick={() => setSelectedTab('dashboard')}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  selectedTab === 'dashboard'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                💰 Consumption Dashboard
              </button>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MainApp