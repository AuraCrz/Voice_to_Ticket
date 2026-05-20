// pages/Dashboard.jsx
import Sidebar from "../components/Sidebar"
import Header from "../components/Header"
import StatsCard from "../components/StatsCard"
import { useEffect, useState } from 'react';
import { obtenerIncidentes } from '../api'; // Ajusta la ruta de importación

function Dashboard({ onLogout }) { 
  const [tickets, setTickets] = useState([]);
  const [cargando, setCargando] = useState(true) 

  /*const getStatusColor = (status) => {
    switch(status) {
      case "Resuelto": return "bg-green-100 text-green-700"
      case "En Proceso": return "bg-yellow-100 text-yellow-700"
      case "Pendiente": return "bg-red-100 text-red-700"
      default: return "bg-gray-100 text-gray-700"
    }
  }*/

    // Hook para traer la información de incidents.json al cargar el componente
    useEffect(() => {
      const traerDatosReales = async () => {
        try {
          const datosBackend = await obtenerIncidentes();
          // Volteamos la lista para que el reporte más reciente aparezca al principio de la tabla
          setTickets(datosBackend.reverse()); 
        } catch (error) {
          console.error("Error al conectar con el backend de Python:", error);
        } finally {
          setTickets([]); // Por si ocurre un error, asegura que no se quede colgado
          setCargando(false);
        }
      };

      traerDatosReales();
    }, []); 

    // Mapeo de colores dinámicos según la severidad detectada por GPT-4o-mini
    const getSeverityColor = (severity) => {
      switch(severity?.toLowerCase()) {
        case "critica": return "bg-red-100 text-red-700 font-semibold"
        case "alta": return "bg-orange-100 text-orange-700"
        case "media": return "bg-yellow-100 text-yellow-700"
        case "baja": return "bg-green-100 text-green-700"
        default: return "bg-gray-100 text-gray-700"
      }
    }

  return (
    <div className="flex bg-gray-50 min-h-screen">
      {/* Componente de navegación lateral */}
      <Sidebar />

      <main className="flex-1 p-8">
        {/* Barra superior con botón de cerrar sesión */}
        <Header onLogout={onLogout} />  

        {/* Tarjetas de Estadísticas superiores */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <StatsCard 
            title="Total de Tickets IA" 
            value={tickets.length.toString()} 
            trend="up" 
            trendValue="Sincronizado con el backend" 
          />
          <StatsCard 
            title="Resueltos" 
            value="180" 
            trend="up" 
            trendValue="8% vs semana pasada" 
          />
        </div>

        {/* Panel de la Tabla de Incidentes */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">Incidentes Procesados por IA</h2>
            <span className="text-xs text-gray-400 bg-gray-50 px-3 py-1 rounded-full font-medium">
              Actualizado en tiempo real
            </span>
          </div>
          
          {/* Renderizado Condicional: Cargando -> Vacío -> Tabla con datos */}
          {cargando ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500 gap-2">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p>Conectando con el servidor de Python...</p>
            </div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-12 text-gray-400 border border-dashed border-gray-200 rounded-xl">
              <p className="font-medium text-base">No hay incidentes registrados en el sistema</p>
              <p className="text-xs text-gray-400 mt-1">Los reportes que procese la IA aparecerán listados aquí automáticamente.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-gray-100 text-gray-400 text-xs uppercase tracking-wider">
                    <th className="py-3 px-4 font-semibold">ID</th>
                    <th className="py-3 px-4 font-semibold">Descripción Original</th>
                    <th className="py-3 px-4 font-semibold">Idioma</th>
                    <th className="py-3 px-4 font-semibold">Categoría</th>
                    <th className="py-3 px-4 font-semibold">Severidad</th>
                    <th className="py-3 px-4 font-semibold">Resumen de la IA</th>
                  </tr>
                </thead>
                <tbody className="text-gray-600 text-sm divide-y divide-gray-50">
                  {tickets.map((ticket) => (
                    <tr key={ticket.id} className="hover:bg-gray-50/50 transition-colors duration-200">
                      {/* ID único truncado */}
                      <td className="py-4 px-4 font-mono font-bold text-blue-600">
                        #{ticket.id}
                      </td>
                      
                      {/* Texto original ingresado por el usuario */}
                      <td className="py-4 px-4 max-w-xs truncate" title={ticket.texto_original}>
                        {ticket.texto_original}
                      </td>
                      
                      {/* Idioma detectado en la capa gratuita */}
                      <td className="py-4 px-4">
                        <span className="bg-blue-50 text-blue-600 text-xs px-2.5 py-1 rounded-md font-medium">
                          {ticket.idioma_nombre}
                        </span>
                      </td>
                      
                      {/* Categoría asignada por GPT */}
                      <td className="py-4 px-4 font-medium text-gray-700">
                        {ticket.categoria}
                      </td>
                      
                      {/* Severidad del ticket con badge de color */}
                      <td className="py-4 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium tracking-wide ${getSeverityColor(ticket.severidad)}`}>
                          {ticket.severidad ? ticket.severidad.toUpperCase() : "BAJA"}
                        </span>
                      </td>
                      
                      {/* Resumen corto del incidente (máx 30 palabras) */}
                      <td className="py-4 px-4 text-gray-500 italic max-w-xs truncate" title={ticket.resumen}>
                        "{ticket.resumen}"
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </main>
    </div>
  )
}

export default Dashboard