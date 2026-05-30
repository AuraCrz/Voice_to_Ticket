<script setup>
import { ref } from "vue"
import Header from "../components/Header.vue"
import NewReportModal from "../components/NewReportModal.vue"
import Sidebar from "../components/Sidebar.vue"
import StatsCard from "../components/StatsCard.vue"

const emit = defineEmits(["logout"])
const isNewReportOpen = ref(false)
</script>

<template>
  <div class="flex min-h-screen bg-gray-50">
    <Sidebar
      @logout="emit('logout')"
      @new-report="isNewReportOpen = true"
    />

    <main class="flex-1 p-8">
      <Header @logout="emit('logout')" />

      <div class="mb-8 grid grid-cols-2 gap-6">
        <StatsCard title="Tickets" value="248" percentage="12" />
        <StatsCard title="Resueltos" value="180" percentage="8" />
      </div>
    </main>

    <NewReportModal
      :is-open="isNewReportOpen"
      @close="isNewReportOpen = false"
    />
  </div>
</template>
