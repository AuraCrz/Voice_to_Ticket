<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: String,
    required: true,
  },
  percentage: {
    type: String,
    default: "0",
  },
})
</script>

<template>
  <div class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
    <p class="text-slate-500">{{ title }}</p>

    <h2 class="mt-3 text-4xl font-bold text-slate-900">
      {{ value }}
    </h2>

    <p class="mt-2 text-sm text-green-500">
      +{{ percentage }}% esta semana
    </p>
  </div>
</template>
