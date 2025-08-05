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
        <Sidebar selectedTab={selectedTab} onTabChange={setSelectedTab} />
        <div className="flex-1 p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default MainApp