import { useAuthStore } from '../store/authStore.js'
import Navbar from '../components/ui/Navbar.jsx'
import TuViBadge from '../components/plant/TuViBadge.jsx'

export default function ProfilePage() {
  const { user } = useAuthStore()

  if (!user) return null

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar />
      
      <div style={{ maxWidth: 500, margin: '0 auto', padding: '48px 20px', animation: 'fadeUp 0.4s ease both' }}>
        <div style={{
          background: 'var(--bg-surface)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)', padding: '40px 32px',
          boxShadow: 'var(--shadow-md)', textAlign: 'center'
        }}>
          
          {/* Avatar & Name */}
          <div style={{ marginBottom: 24 }}>
            <div style={{
              width: 100, height: 100, borderRadius: '50%',
              background: 'var(--green-100)', border: '3px solid var(--green-200)',
              margin: '0 auto 16px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 40, color: 'var(--green-700)', overflow: 'hidden'
            }}>
              {user.avatar_url ? (
                <img src={user.avatar_url} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                user.display_name?.charAt(0).toUpperCase()
              )}
            </div>
            <h1 style={{ fontSize: 24, color: 'var(--text-primary)', marginBottom: 4 }}>{user.display_name}</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>{user.email}</p>
          </div>

          <div style={{ height: 1, background: 'var(--border)', margin: '24px 0' }} />

          {/* User Stats */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
                Cấp độ Tu Vi cá nhân
              </p>
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <TuViBadge value={parseInt(user.tu_vi) || 0} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: 'var(--bg-soft)', borderRadius: 'var(--radius-md)', fontSize: 14 }}>
              <span style={{ color: 'var(--text-muted)' }}>ID Tài khoản:</span>
              <code style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{user.id?.slice(0, 8)}...</code>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: 'var(--bg-soft)', borderRadius: 'var(--radius-md)', fontSize: 14 }}>
              <span style={{ color: 'var(--text-muted)' }}>Ngày gia nhập:</span>
              <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                {new Date(user.created_at).toLocaleDateString('vi-VN')}
              </span>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}