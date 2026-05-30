<script setup>
import {
  Bell,
  LogOut,
  Search,
  User,
} from "@lucide/vue"

const emit = defineEmits(["logout"])
</script>

<template>
  <header class="mb-8 flex items-center justify-between">
    <div>
      <h2 class="text-3xl font-bold text-slate-900">
        Dashboard
      </h2>
      <p class="mt-1 text-slate-500">
        Resumen general del sistema y actividad reciente
      </p>
    </div>

    <div class="flex items-center gap-4">
      <div class="relative hidden md:block">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          class="rounded-xl border border-slate-200 py-2 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Buscar..."
          type="text"
        >
      </div>

      <button class="rounded-xl border border-slate-200 bg-white p-3 transition hover:bg-slate-50" type="button">
        <Bell class="h-5 w-5 text-slate-600" />
      </button>

      <button class="rounded-xl border border-slate-200 bg-white p-3 transition hover:bg-slate-50" type="button">
        <User class="h-5 w-5 text-slate-600" />
      </button>

      <button
        class="flex items-center gap-2 rounded-xl bg-red-500 px-4 py-3 text-white shadow-sm transition-all duration-300 hover:bg-red-600"
        type="button"
        @click="emit('logout')"
      >
        <LogOut class="h-4 w-4" />
        <span class="hidden md:inline">Cerrar sesion</span>
      </button>
    </div>
  </header>
</template>
