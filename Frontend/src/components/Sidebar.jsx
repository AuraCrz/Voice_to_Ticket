
import { 
  LayoutDashboard, 
  Ticket, 
  Settings, 
  BarChart3, 
  Mic,
  LogOut  
} from "lucide-react"

function Sidebar({ onLogout, onNewReport }) { 
  return (
    <aside className="w-72 bg-slate-900 min-h-screen text-white p-6 flex flex-col">
      <div className="mb-12">
        <h1 className="text-3xl font-bold">
          Voice<span className="text-blue-500">Ticket AI</span>
        </h1>
        <p className="text-slate-400 mt-2">
          Sistema inteligente de tickets
        </p>
      </div>

      <nav className="space-y-3 flex-1">
        {/* Menú principal */}
        <button className="flex items-center gap-3 bg-blue-600 w-full p-4 rounded-2xl">
          <LayoutDashboard />
          Dashboard
        </button>

        <button
          onClick={onNewReport}
          className="flex items-center gap-3 hover:bg-slate-800 transition-all duration-300 w-full p-4 rounded-2xl"
        >
          <Mic />
          Nuevo Reporte
        </button>

        <button className="flex items-center gap-3 hover:bg-slate-800 transition-all duration-300 w-full p-4 rounded-2xl">
          <Ticket />
          Tickets
        </button>

        <button className="flex items-center gap-3 hover:bg-slate-800 transition-all duration-300 w-full p-4 rounded-2xl">
          <BarChart3 />
          Analytics
        </button>

        <button className="flex items-center gap-3 hover:bg-slate-800 transition-all duration-300 w-full p-4 rounded-2xl">
          <Settings />
          Configuración
        </button>
      </nav>

      {/* Botón de cerrar sesión al final */}
      <button
        onClick={onLogout}
        className="flex items-center gap-3 hover:bg-red-500/20 transition-all duration-300 w-full p-4 rounded-2xl text-red-400 hover:text-red-300 mt-4 border-t border-slate-800 pt-4"
      >
        <LogOut />
        Cerrar sesión
      </button>
    </aside>
  )
}

export default Sidebar
