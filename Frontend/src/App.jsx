import { useState } from "react"
import Login from "./components/Login"
import Dashboard from "./pages/Dashboard"

function App() {

  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // LOGIN
  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  // LOGOUT
  const handleLogout = () => {
    setIsAuthenticated(false)
  }

  return (
    <>
      {isAuthenticated ? (
        <Dashboard onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </>
  )
}

export default App