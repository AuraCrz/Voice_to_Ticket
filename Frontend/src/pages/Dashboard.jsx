import { useState } from "react"
import Sidebar from "../components/Sidebar"
import Header from "../components/Header"
import StatsCard from "../components/StatsCard"
import NewReportModal from "../components/NewReportModal"

function Dashboard({ onLogout }) {
  const [isNewReportOpen, setIsNewReportOpen] = useState(false)

  return (
    <div className="flex bg-gray-50 min-h-screen">
      <Sidebar
        onLogout={onLogout}
        onNewReport={() => setIsNewReportOpen(true)}
      />

      <main className="flex-1 p-8">
        <Header onLogout={onLogout} />

        <div className="grid grid-cols-2 gap-6 mb-8">
          <StatsCard title="Tickets" value="248" trend="up" trendValue="12% vs semana pasada" />
          <StatsCard title="Resueltos" value="180" trend="up" trendValue="8% vs semana pasada" />
        </div>
      </main>

      <NewReportModal
        isOpen={isNewReportOpen}
        onClose={() => setIsNewReportOpen(false)}
      />
    </div>
  )
}

export default Dashboard
