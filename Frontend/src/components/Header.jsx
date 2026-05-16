import {
  ArrowLeft,
  Bell,
  User,
  Search,
  LogOut,
} from "lucide-react"

function Header({ onLogout }) {

  return (
    <header className="flex justify-between items-center mb-8">

      {/* Left */}
      <div>

        <h2 className="text-3xl font-bold text-slate-900">
          Dashboard
        </h2>

        <p className="text-slate-500 mt-1">
          Resumen general del sistema y actividad reciente
        </p>

      </div>

      {/* Right */}
      <div className="flex items-center gap-4">

        {/* Search */}
        <div className="relative hidden md:block">

          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />

          <input
            type="text"
            placeholder="Buscar..."
            className="pl-10 pr-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

        </div>

        {/* Notifications */}
        <button className="p-3 bg-white rounded-xl border border-slate-200 hover:bg-slate-50 transition">

          <Bell className="w-5 h-5 text-slate-600" />

        </button>

        {/* User */}
        <button className="p-3 bg-white rounded-xl border border-slate-200 hover:bg-slate-50 transition">

          <User className="w-5 h-5 text-slate-600" />

        </button>

        {/* Logout */}
        <button
          onClick={onLogout}
          className="flex items-center gap-2 px-4 py-3 bg-red-500 hover:bg-red-600 text-white rounded-xl transition-all duration-300 shadow-sm"
        >

          <LogOut className="w-4 h-4" />

          <span className="hidden md:inline">
            Cerrar sesión
          </span>

        </button>

      </div>

    </header>
  )
}

export default Header