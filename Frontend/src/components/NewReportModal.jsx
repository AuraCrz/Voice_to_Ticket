import { useEffect, useRef, useState } from "react"
import {
  AlertCircle,
  FileText,
  Mic,
  Pause,
  Play,
  RotateCcw,
  Send,
  Square,
  X,
} from "lucide-react"

function NewReportModal({ isOpen, onClose }) {
  const [reportText, setReportText] = useState("")
  const [isListening, setIsListening] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [interimText, setInterimText] = useState("")
  const [audioUrl, setAudioUrl] = useState("")
  const [error, setError] = useState("")

  const recognitionRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const streamRef = useRef(null)
  const audioChunksRef = useRef([])

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition

  const canUseSpeechRecognition = Boolean(SpeechRecognition)
  const canRecordAudio = Boolean(navigator.mediaDevices?.getUserMedia)

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
    }
  }, [audioUrl])

  if (!isOpen) {
    return null
  }

  function appendTranscript(text) {
    if (!text.trim()) {
      return
    }

    setReportText((current) => {
      const separator = current.trim() ? " " : ""
      return `${current}${separator}${text.trim()}`
    })
  }

  function startListening() {
    if (!canUseSpeechRecognition) {
      setError("Tu navegador no soporta dictado por voz. Puedes escribir el reporte manualmente.")
      return
    }

    setError("")
    setInterimText("")

    const recognition = new SpeechRecognition()
    recognition.lang = "es-MX"
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event) => {
      let finalTranscript = ""
      let currentInterim = ""

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const transcript = event.results[index][0].transcript

        if (event.results[index].isFinal) {
          finalTranscript += transcript
        } else {
          currentInterim += transcript
        }
      }

      appendTranscript(finalTranscript)
      setInterimText(currentInterim)
    }

    recognition.onerror = () => {
      setError("No se pudo usar el microfono para dictado. Revisa los permisos del navegador.")
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
      setInterimText("")
    }

    recognitionRef.current = recognition
    recognition.start()
    setIsListening(true)
  }

  function stopListening() {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }

    setIsListening(false)
    setInterimText("")
  }

  async function startRecording() {
    if (!canRecordAudio) {
      setError("Tu navegador no soporta grabacion de audio.")
      return
    }

    try {
      setError("")
      audioChunksRef.current = []

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)

      streamRef.current = stream
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" })

        if (audioUrl) {
          URL.revokeObjectURL(audioUrl)
        }

        setAudioUrl(URL.createObjectURL(audioBlob))
        stream.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch {
      setError("No se pudo iniciar la grabacion. Revisa el permiso del microfono.")
      setIsRecording(false)
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop()
    }

    streamRef.current?.getTracks().forEach((track) => track.stop())
    mediaRecorderRef.current = null
    streamRef.current = null
    setIsRecording(false)
  }

  function resetReport() {
    stopListening()
    stopRecording()
    setReportText("")
    setInterimText("")
    setError("")

    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl("")
    }
  }

  function closeModal() {
    stopListening()
    stopRecording()
    setError("")
    setInterimText("")
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
      <section className="w-full max-w-3xl rounded-2xl bg-white shadow-2xl">
        <header className="flex items-center justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Nuevo Reporte</h2>
            <p className="mt-1 text-sm text-slate-500">
              Captura informacion por texto, dictado o audio. Aun no se guardara.
            </p>
          </div>

          <button
            type="button"
            onClick={closeModal}
            className="rounded-xl border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-50 hover:text-slate-900"
            aria-label="Cerrar nuevo reporte"
          >
            <X className="h-5 w-5" />
          </button>
        </header>

        <div className="space-y-5 px-6 py-6">
          {error && (
            <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <div>
            <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
              <FileText className="h-4 w-4" />
              Descripcion del incidente
            </label>

            <textarea
              value={reportText}
              onChange={(event) => setReportText(event.target.value)}
              placeholder="Describe que ocurrio, a quien afecta, desde cuando pasa y cualquier detalle util..."
              className="min-h-44 w-full resize-none rounded-xl border border-slate-200 p-4 text-slate-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />

            {interimText && (
              <p className="mt-2 rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700">
                Escuchando: {interimText}
              </p>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-200 p-4">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">Dictado a texto</h3>
                  <p className="text-sm text-slate-500">Convierte tu voz en texto editable.</p>
                </div>
                <Mic className={isListening ? "h-5 w-5 text-blue-600" : "h-5 w-5 text-slate-400"} />
              </div>

              <button
                type="button"
                onClick={isListening ? stopListening : startListening}
                className={`flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-semibold text-white transition ${
                  isListening ? "bg-slate-700 hover:bg-slate-800" : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {isListening ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                {isListening ? "Pausar dictado" : "Iniciar dictado"}
              </button>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">Audio original</h3>
                  <p className="text-sm text-slate-500">Graba una nota temporal del reporte.</p>
                </div>
                <span className={isRecording ? "h-3 w-3 rounded-full bg-red-500" : "h-3 w-3 rounded-full bg-slate-300"} />
              </div>

              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                className={`flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-semibold text-white transition ${
                  isRecording ? "bg-red-600 hover:bg-red-700" : "bg-slate-900 hover:bg-slate-800"
                }`}
              >
                {isRecording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                {isRecording ? "Detener audio" : "Grabar audio"}
              </button>

              {audioUrl && (
                <audio controls src={audioUrl} className="mt-4 w-full">
                  Tu navegador no soporta audio.
                </audio>
              )}
            </div>
          </div>
        </div>

        <footer className="flex flex-col gap-3 border-t border-slate-100 px-6 py-5 sm:flex-row sm:justify-between">
          <button
            type="button"
            onClick={resetReport}
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            <RotateCcw className="h-4 w-4" />
            Limpiar
          </button>

          <button
            type="button"
            disabled
            className="flex items-center justify-center gap-2 rounded-xl bg-slate-200 px-4 py-3 font-semibold text-slate-500"
            title="El guardado se conectara en una siguiente etapa"
          >
            <Send className="h-4 w-4" />
            Guardar reporte proximamente
          </button>
        </footer>
      </section>
    </div>
  )
}

export default NewReportModal
