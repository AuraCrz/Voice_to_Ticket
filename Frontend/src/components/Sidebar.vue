<script setup>
import {
  BarChart3,
  LayoutDashboard,
  LogOut,
  Mic,
  Settings,
  Ticket,
} from "@lucide/vue"

const emit = defineEmits(["logout", "new-report"])
</script>

<template>
  <aside class="flex min-h-screen w-72 flex-col bg-slate-900 p-6 text-white">
    <div class="mb-12">
      <h1 class="text-3xl font-bold">
        Voice<span class="text-blue-500">Ticket AI</span>
      </h1>
      <p class="mt-2 text-slate-400">
        Sistema inteligente de tickets
      </p>
    </div>

    <nav class="flex-1 space-y-3">
      <button class="flex w-full items-center gap-3 rounded-2xl bg-blue-600 p-4">
        <LayoutDashboard />
        Dashboard
      </button>

      <button
        class="flex w-full items-center gap-3 rounded-2xl p-4 transition-all duration-300 hover:bg-slate-800"
        type="button"
        @click="emit('new-report')"
      >
        <Mic />
        Nuevo Reporte
      </button>

      <button class="flex w-full items-center gap-3 rounded-2xl p-4 transition-all duration-300 hover:bg-slate-800">
        <Ticket />
        Tickets
      </button>

      <button class="flex w-full items-center gap-3 rounded-2xl p-4 transition-all duration-300 hover:bg-slate-800">
        <BarChart3 />
        Analytics
      </button>

      <button class="flex w-full items-center gap-3 rounded-2xl p-4 transition-all duration-300 hover:bg-slate-800">
        <Settings />
        Configuracion
      </button>
    </nav>

    <button
      class="mt-4 flex w-full items-center gap-3 border-t border-slate-800 p-4 pt-4 text-red-400 transition-all duration-300 hover:bg-red-500/20 hover:text-red-300"
      type="button"
      @click="emit('logout')"
    >
      <LogOut />
      Cerrar sesion
    </button>
  </aside>
</template>
