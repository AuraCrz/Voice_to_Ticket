const BASE_URL = 'http://localhost:5000/api';

/**
 * Envía la descripción de un incidente en texto al Backend para ser analizado por el LLM.
 */
export const registrarIncidente = async (textoIncidente) => {
  const respuesta = await fetch(`${BASE_URL}/incidentes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ texto: textoIncidente }),
  });

  if (!respuesta.ok) {
    const errorData = await respuesta.json();
    throw new Error(errorData.error || 'Error al procesar el incidente');
  }

  return await respuesta.json(); // Retorna { message, incidente }
};

/**
 * Obtiene el historial completo de incidentes guardados en el archivo JSON.
 */
export const obtenerIncidentes = async () => {
  const respuesta = await fetch(`${BASE_URL}/incidentes`);
  
  if (!respuesta.ok) {
    throw new Error('Error al obtener el historial de incidentes');
  }

  return await respuesta.json(); // Retorna el array de incidentes
};