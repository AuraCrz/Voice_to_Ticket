<script setup>
import { ref } from "vue"
import {
  Eye,
  EyeOff,
  Lock,
  LogIn,
  Mail,
  Sparkles,
} from "@lucide/vue"

const emit = defineEmits(["login"])

const showPassword = ref(false)
const email = ref("")
const password = ref("")
const isLoading = ref(false)

function handleSubmit() {
  isLoading.value = true

  const testEmail = "admin@voiceticket.com"
  const testPassword = "123456"

  window.setTimeout(() => {
    if (email.value === testEmail && password.value === testPassword) {
      emit("login")
    } else {
      window.alert("Correo o contrasena incorrectos")
    }

    isLoading.value = false
  }, 800)
}
</script>

<template>
  <div class="flex min-h-screen">
    <div class="flex flex-1 items-center justify-center bg-white p-8">
      <div class="w-full max-w-md">
        <div class="mb-8 text-center">
          <div class="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg">
            <Sparkles class="h-8 w-8 text-white" />
          </div>
          <h1 class="text-3xl font-bold text-gray-800">
            Voice<span class="text-blue-600">Ticket AI</span>
          </h1>
          <p class="mt-2 text-gray-500">
            Sistema inteligente de tickets
          </p>
        </div>

        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-800">
            Bienvenido de nuevo
          </h2>
          <p class="mt-1 text-gray-500">
            Inicia sesion para acceder al dashboard
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="handleSubmit">
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">
              Correo electronico
            </label>
            <div class="relative">
              <Mail class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                v-model="email"
                class="w-full rounded-xl border border-gray-200 py-3 pl-10 pr-4 transition-all duration-300 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="usuario@empresa.com"
                required
                type="email"
              >
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">
              Contrasena
            </label>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                v-model="password"
                class="w-full rounded-xl border border-gray-200 py-3 pl-10 pr-12 transition-all duration-300 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ingresa tu contrasena"
                required
                :type="showPassword ? 'text' : 'password'"
              >
              <button
                class="absolute right-3 top-1/2 -translate-y-1/2"
                type="button"
                @click="showPassword = !showPassword"
              >
                <EyeOff
                  v-if="showPassword"
                  class="h-5 w-5 text-gray-400 hover:text-gray-600"
                />
                <Eye
                  v-else
                  class="h-5 w-5 text-gray-400 hover:text-gray-600"
                />
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <label class="flex items-center">
              <input
                class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                type="checkbox"
              >
              <span class="ml-2 text-sm text-gray-600">Recordarme</span>
            </label>
            <a class="text-sm font-medium text-blue-600 hover:text-blue-700" href="#">
              Olvidaste tu contrasena?
            </a>
          </div>

          <button
            class="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 py-3 font-semibold text-white shadow-lg transition-all duration-300 hover:from-blue-700 hover:to-blue-800 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="isLoading"
            type="submit"
          >
            <span
              v-if="isLoading"
              class="h-5 w-5 rounded-full border-2 border-white border-t-transparent animate-spin"
            />
            <LogIn v-else class="h-5 w-5" />
            {{ isLoading ? "Iniciando sesion..." : "Iniciar sesion" }}
          </button>
        </form>

        <p class="mt-8 text-center text-gray-600">
          No tienes una cuenta?
          <a class="font-semibold text-blue-600 hover:text-blue-700" href="#">
            Registrate aqui
          </a>
        </p>
      </div>
    </div>

    <div class="relative hidden flex-1 overflow-hidden bg-gradient-to-br from-slate-900 to-slate-800 lg:flex">
      <div class="relative z-10 flex flex-col items-center justify-center p-12 text-center text-white">
        <div class="mb-8">
          <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
            <Sparkles class="h-10 w-10 text-blue-400" />
          </div>
          <h3 class="mb-4 text-3xl font-bold">
            Gestion inteligente de tickets
          </h3>
          <p class="max-w-md text-lg text-slate-300">
            Automatiza, clasifica y resuelve tickets de soporte con inteligencia artificial avanzada
          </p>
        </div>

        <div class="w-full max-w-sm space-y-4">
          <div class="flex items-center gap-3 rounded-lg bg-white/5 p-3 backdrop-blur-sm">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/20">
              <Sparkles class="h-4 w-4 text-blue-400" />
            </div>
            <span class="text-sm">Clasificacion automatica por categoria</span>
          </div>
          <div class="flex items-center gap-3 rounded-lg bg-white/5 p-3 backdrop-blur-sm">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/20">
              <Sparkles class="h-4 w-4 text-blue-400" />
            </div>
            <span class="text-sm">Deteccion de idioma en tiempo real</span>
          </div>
          <div class="flex items-center gap-3 rounded-lg bg-white/5 p-3 backdrop-blur-sm">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/20">
              <Sparkles class="h-4 w-4 text-blue-400" />
            </div>
            <span class="text-sm">Precision del 96% en clasificacion</span>
          </div>
        </div>

        <div class="mt-12 flex gap-8">
          <div class="text-center">
            <p class="text-2xl font-bold">1,248+</p>
            <p class="text-sm text-slate-400">Tickets gestionados</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold">7</p>
            <p class="text-sm text-slate-400">Idiomas soportados</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold">2.4s</p>
            <p class="text-sm text-slate-400">Tiempo promedio</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
