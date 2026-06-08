import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore.js'
import Spinner from '../ui/Spinner.jsx'

export default function ProtectedRoute() {
  const { isAuthenticated, accessToken, isLoading } = useAuthStore()

  if (isLoading) return <Spinner fullscreen />

  if (!isAuthenticated && !accessToken) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
