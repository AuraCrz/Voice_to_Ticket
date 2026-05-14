// pages/Dashboard.jsx
import Sidebar from "../components/Sidebar"
import Header from "../components/Header"
import StatsCard from "../components/StatsCard"

function Dashboard({ onLogout }) {  
  const recentTickets = [
    { id: "#TK-2487", description: "No puedo acceder al servidor principal", language: "Español", category: "Técnico", status: "En Proceso", confidence: "94%", date: "24/04/2026 10:30" },
    { id: "#TK-2486", description: "Unable to connect to the VPN", language: "Inglés", category: "Network", status: "Resuelto", confidence: "98%", date: "24/04/2026 09:15" },
    { id: "#TK-2485", description: "Software installation failed", language: "Inglés", category: "Software", status: "Pendiente", confidence: "91%", date: "24/04/2026 08:45" },
    { id: "#TK-2484", description: "Problema de seguridad en el sistema", language: "Español", category: "Seguridad", status: "En Proceso", confidence: "93%", date: "23/04/2026 16:20" },
    { id: "#TK-2483", description: "Drucker funktioniert nicht", language: "Alemán", category: "Técnico", status: "Resuelto", confidence: "95%", date: "23/04/2026 14:10" },
  ]

  const getStatusColor = (status) => {
    switch(status) {
      case "Resuelto": return "bg-green-100 text-green-700"
      case "En Proceso": return "bg-yellow-100 text-yellow-700"
      case "Pendiente": return "bg-red-100 text-red-700"
      default: return "bg-gray-100 text-gray-700"
    }
  }

  return (
    <div className="flex bg-gray-50 min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8">
        <Header onLogout={onLogout} />  

        <div className="grid grid-cols-2 gap-6 mb-8">
          <StatsCard title="Tickets" value="248" trend="up" trendValue="12% vs semana pasada" />
          <StatsCard title="Resueltos" value="180" trend="up" trendValue="8% vs semana pasada" />
        </div>

      </main>
    </div>
  )
}

export default Dashboard