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
import Profile from './profile/Profile'
import { useProcessingStore } from '../store/useProcessingStore'

const MainApp: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState('processing')
  const { processingComplete } = useProcessingStore()

  const contentClass =
    selectedTab === 'processing'
      ? 'flex-1 p-6 max-w-7xl mx-auto w-full'
      : 'flex-1 p-6 max-w-5xl mx-auto w-full'

  const renderTabContent = () => {
    switch (selectedTab) {
      case 'processing':
        return (
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 space-y-6">
              <FileUpload />
              <ProcessingSteps />
              {processingComplete && <DataEditor />}
            </div>
            <div className="lg:col-span-1 lg:sticky lg:top-[64px] space-y-6 h-fit">
              {processingComplete && <TokenUsageCard />}
            </div>
          </div>
        )
      case 'prompts':
        return <PromptManager />
      case 'history':
        return <ProcessingHistory />
      case 'dashboard':
        return <ConsumptionDashboard />
      case 'profile':
        return <Profile />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Header selectedTab={selectedTab} onTabChange={setSelectedTab} />
      <div className="flex">
        {/* Sidebar kept for future context panels; navigation moved to header */}
        <Sidebar selectedTab={selectedTab} onTabChange={setSelectedTab} />
        <div className={contentClass}>
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default MainApp