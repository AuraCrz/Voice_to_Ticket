<script setup>
import axios from "axios"
import { computed, onBeforeUnmount, ref } from "vue"
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
} from "@lucide/vue"

defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(["close"])

const reportText = ref("")
const isListening = ref(false)
const isRecording = ref(false)
const interimText = ref("")
const audioUrl = ref("")
const error = ref("")
const isSaving = ref(false)
const savedIncident = ref(null)

const recognitionRef = ref(null)
const mediaRecorderRef = ref(null)
const streamRef = ref(null)
const audioChunksRef = ref([])

const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition

const canUseSpeechRecognition = computed(
  () => Boolean(SpeechRecognition)
)

const canRecordAudio = computed(
  () => Boolean(
    navigator.mediaDevices?.getUserMedia
  )
)

onBeforeUnmount(() => {
  stopListening()
  stopRecording()

  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
})

function appendTranscript(text) {

  if (!text.trim()) {
    return
  }

  const separator =
    reportText.value.trim()
      ? " "
      : ""

  reportText.value =
    `${reportText.value}${separator}${text.trim()}`
}

function startListening() {

  if (!canUseSpeechRecognition.value) {

    error.value =
      "Tu navegador no soporta dictado por voz."

    return
  }

  error.value = ""
  interimText.value = ""

  const recognition =
    new SpeechRecognition()

  recognition.lang = "es-MX"
  recognition.continuous = true
  recognition.interimResults = true

  recognition.onresult = (event) => {

    let finalTranscript = ""
    let currentInterim = ""

    for (
      let index = event.resultIndex;
      index < event.results.length;
      index += 1
    ) {

      const transcript =
        event.results[index][0].transcript

      if (event.results[index].isFinal) {
        finalTranscript += transcript
      }
      else {
        currentInterim += transcript
      }
    }

    appendTranscript(finalTranscript)
    interimText.value = currentInterim
  }

  recognition.onerror = () => {

    error.value =
      "No se pudo usar el microfono."

    isListening.value = false
  }

  recognition.onend = () => {

    isListening.value = false
    interimText.value = ""
  }

  recognitionRef.value = recognition
  recognition.start()
  isListening.value = true
}

function stopListening() {

  if (recognitionRef.value) {

    recognitionRef.value.stop()
    recognitionRef.value = null
  }

  isListening.value = false
  interimText.value = ""
}

async function startRecording() {

  if (!canRecordAudio.value) {

    error.value =
      "Tu navegador no soporta grabacion."

    return
  }

  try {

    error.value = ""
    audioChunksRef.value = []

    const stream =
      await navigator.mediaDevices.getUserMedia({
        audio: true,
      })

    const mediaRecorder =
      new MediaRecorder(stream)

    streamRef.value = stream
    mediaRecorderRef.value = mediaRecorder

    mediaRecorder.ondataavailable =
      (event) => {

        if (event.data.size > 0) {
          audioChunksRef.value.push(
            event.data
          )
        }
      }

    mediaRecorder.onstop = () => {

      const audioBlob = new Blob(
        audioChunksRef.value,
        {
          type: "audio/webm",
        }
      )

      if (audioUrl.value) {
        URL.revokeObjectURL(
          audioUrl.value
        )
      }

      audioUrl.value =
        URL.createObjectURL(audioBlob)

      stream
        .getTracks()
        .forEach(track =>
          track.stop()
        )

      streamRef.value = null
    }

    mediaRecorder.start()
    isRecording.value = true

  } catch {

    error.value =
      "No se pudo iniciar grabacion."

    isRecording.value = false
  }
}

function stopRecording() {

  if (
    mediaRecorderRef.value?.state ===
    "recording"
  ) {
    mediaRecorderRef.value.stop()
  }

  streamRef.value
    ?.getTracks()
    .forEach(track => track.stop())

  mediaRecorderRef.value = null
  streamRef.value = null
  isRecording.value = false
}

function resetReport() {

  stopListening()
  stopRecording()

  reportText.value = ""
  interimText.value = ""
  error.value = ""

  if (audioUrl.value) {

    URL.revokeObjectURL(
      audioUrl.value
    )

    audioUrl.value = ""
  }
}

function closeModal() {

  stopListening()
  stopRecording()

  error.value = ""
  interimText.value = ""

  emit("close")
}

async function saveReport() {

  if (!reportText.value.trim()) {

    alert(
      "Describe el incidente"
    )

    return
  }

  try {

    isSaving.value = true

    const response =
      await axios.post(
        "http://localhost:8000/incidents",
        {
          texto:
            reportText.value,
        }
      )

    savedIncident.value =
      response.data

    alert(
`Reporte guardado

Categoria:
${response.data.categoria}

Severidad:
${response.data.severidad}`
    )

    resetReport()
    closeModal()

  }
  catch (err) {

    console.error(err)

    if (err.response) {

      alert(
        `Backend error:
${err.response.data.detail}`
      )
    }
    else if (err.request) {

      alert(
        "No se pudo conectar al backend."
      )
    }
    else {

      alert(
        "Error inesperado."
      )
    }
  }
  finally {

    isSaving.value = false
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4"
  >
    <section class="w-full max-w-3xl rounded-2xl bg-white shadow-2xl">

      <header class="flex items-center justify-between border-b border-slate-100 px-6 py-5">

        <div>
          <h2 class="text-2xl font-bold text-slate-900">
            Nuevo Reporte
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Captura informacion y guarda el incidente en el sistema.
          </p>
        </div>

        <button
          class="rounded-xl border border-slate-200 p-2"
          type="button"
          @click="closeModal"
        >
          <X class="h-5 w-5" />
        </button>

      </header>

      <div class="space-y-5 px-6 py-6">

        <div
          v-if="error"
          class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"
        >
          <div class="flex gap-2">
            <AlertCircle class="h-5 w-5" />
            {{ error }}
          </div>
        </div>

        <div>

          <label class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
            <FileText class="h-4 w-4" />
            Descripcion del incidente
          </label>

          <textarea
            v-model="reportText"
            class="min-h-44 w-full resize-none rounded-xl border border-slate-200 p-4"
            placeholder="Describe el incidente..."
          />

          <p
            v-if="interimText"
            class="mt-2 rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700"
          >
            Escuchando:
            {{ interimText }}
          </p>

        </div>

        <div class="grid gap-4 md:grid-cols-2">

          <button
            class="rounded-xl bg-blue-600 px-4 py-3 text-white"
            type="button"
            @click="isListening ? stopListening() : startListening()"
          >
            <Pause
              v-if="isListening"
              class="inline h-4 w-4"
            />
            <Play
              v-else
              class="inline h-4 w-4"
            />

            {{ isListening ? "Pausar dictado" : "Iniciar dictado" }}
          </button>

          <button
            class="rounded-xl bg-slate-900 px-4 py-3 text-white"
            type="button"
            @click="isRecording ? stopRecording() : startRecording()"
          >
            <Square
              v-if="isRecording"
              class="inline h-4 w-4"
            />
            <Mic
              v-else
              class="inline h-4 w-4"
            />

            {{ isRecording ? "Detener audio" : "Grabar audio" }}
          </button>

        </div>

        <audio
          v-if="audioUrl"
          class="w-full"
          controls
          :src="audioUrl"
        />

      </div>

      <footer class="flex justify-between border-t border-slate-100 px-6 py-5">

        <button
          class="rounded-xl border border-slate-200 px-4 py-3"
          type="button"
          @click="resetReport"
        >
          <RotateCcw class="inline h-4 w-4" />
          Limpiar
        </button>

        <button
          class="rounded-xl bg-blue-600 px-4 py-3 text-white"
          :disabled="isSaving"
          type="button"
          @click="saveReport"
        >
          <Send class="inline h-4 w-4" />

          {{ isSaving ? "Guardando..." : "Guardar reporte" }}
        </button>

      </footer>

    </section>
  </div>
</template>