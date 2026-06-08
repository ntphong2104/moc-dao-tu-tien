import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore.js'
import LoginPage      from './pages/LoginPage.jsx'
import CallbackPage   from './pages/CallbackPage.jsx'
import ClaimPage      from './pages/ClaimPage.jsx'
import DashboardPage  from './pages/DashboardPage.jsx'
import ProtectedRoute from './components/auth/ProtectedRoute.jsx'
import PlantsListPage from './pages/PlantsListPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'

export default function App() {
  const { fetchMe, accessToken } = useAuthStore()

  useEffect(() => {
    if (accessToken) fetchMe()
  }, [])

  return (
    <BrowserRouter>
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '14px',
            background: '#f0faf0',
            color: '#0f2e0f',
            border: '1px solid #a8dfa8',
            borderRadius: '10px',
            padding: '10px 16px',
          },
          success: { iconTheme: { primary: '#2d7a2d', secondary: '#f0faf0' } },
          error:   { iconTheme: { primary: '#c0392b', secondary: '#fff' } },
        }}
      />
      <Routes>
        <Route path="/login"          element={<LoginPage />} />
        <Route path="/profile"          element={<ProfilePage />} />
        <Route path="/auth/callback"  element={<CallbackPage />} />
        <Route element={<ProtectedRoute />}>
        <Route path="/plants"           element={<PlantsListPage />} />
          <Route path="/claim"            element={<ClaimPage />} />
          <Route path="/dashboard"        element={<DashboardPage />} />
          <Route path="/dashboard/:plantId" element={<DashboardPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
