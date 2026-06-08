import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore.js'
import toast from 'react-hot-toast'

export default function Navbar() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    toast.success('Đã đăng xuất')
    navigate('/login', { replace: true })
  }

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(244,251,242,0.92)',
      backdropFilter: 'blur(8px)',
      borderBottom: '1px solid var(--border)',
      padding: '0 20px',
      height: 56,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    }}>
      {/* Logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}
        onClick={() => navigate('/plants')}
      >
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <path d="M14 3 C14 3 4 9 4 17 C4 21.4 8.6 25 14 25 C19.4 25 24 21.4 24 17 C24 9 14 3 14 3Z"
            fill="var(--green-300)" />
          <line x1="14" y1="25" x2="14" y2="12" stroke="var(--green-700)" strokeWidth="2" strokeLinecap="round" />
          <path d="M14 18 C14 18 9 15 8 10" stroke="var(--green-500)" strokeWidth="1.2" strokeLinecap="round" />
          <path d="M14 15 C14 15 18 12 19 7" stroke="var(--green-500)" strokeWidth="1.2" strokeLinecap="round" />
        </svg>
        <span style={{
          fontFamily: 'var(--font-display)',
          fontSize: 17,
          color: 'var(--text-primary)',
          fontWeight: 400,
        }}>
          Plant Identity
        </span>
      </div>

      {/* User */}
      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div
           onClick={() => navigate('/profile')}
           style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.display_name}
                style={{ width: 28, height: 28, borderRadius: '50%', border: '1.5px solid var(--border)' }}
              />
            ) : (
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: 'var(--green-200)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, fontWeight: 500, color: 'var(--green-800)',
              }}>
                {user.display_name?.charAt(0).toUpperCase()}
              </div>
            )}
            <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user.display_name}
            </span>
          </div>

          <button
            onClick={handleLogout}
            style={{
              padding: '5px 12px',
              border: '1px solid var(--border-strong)',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              color: 'var(--text-muted)',
              fontSize: 12.5,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-soft)'; e.currentTarget.style.color = 'var(--text-primary)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)' }}
          >
            Đăng xuất
          </button>
        </div>
      )}
    </nav>
  )
}
