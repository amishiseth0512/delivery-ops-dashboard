import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import DriverView from './pages/DriverView'
import { getToken, getRole, saveToken, clearToken } from './auth'

export default function App() {
  const [token, setToken] = useState(getToken())
  const role = token ? getRole() : null

  function handleLogin(newToken: string) {
    saveToken(newToken)
    setToken(newToken)
  }

  function handleLogout() {
    clearToken()
    setToken(null)
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            token
              ? <Navigate to={role === 'dispatcher' ? '/dashboard' : '/driver'} />
              : <LoginPage onLogin={handleLogin} />
          }
        />
        <Route
          path="/dashboard"
          element={token && role === 'dispatcher' ? <Dashboard onLogout={handleLogout} /> : <Navigate to="/" />}
        />
        <Route
          path="/driver"
          element={token && role === 'driver' ? <DriverView onLogout={handleLogout} /> : <Navigate to="/" />}
        />
      </Routes>
    </BrowserRouter>
  )
}
