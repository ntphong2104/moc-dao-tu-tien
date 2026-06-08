import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

// Luồng đăng nhập hiện dùng Google Identity Services (hoàn tất ngay tại LoginPage),
// không còn redirect qua trang callback nữa. Giữ route này để tương thích: chỉ điều hướng về /login.
export default function CallbackPage() {
  const navigate = useNavigate()
  useEffect(() => {
    navigate('/login', { replace: true })
  }, [])
  return null
}
