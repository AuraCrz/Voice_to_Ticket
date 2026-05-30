<script setup>
import { ref } from "vue"
import Login from "./components/Login.vue"
import Dashboard from "./pages/Dashboard.vue"

const isAuthenticated = ref(false)

function handleLogin() {
  isAuthenticated.value = true
}

function handleLogout() {
  isAuthenticated.value = false
}
</script>

<template>
  <Dashboard
    v-if="isAuthenticated"
    @logout="handleLogout"
  />
  <Login
    v-else
    @login="handleLogin"
  />
</template>
