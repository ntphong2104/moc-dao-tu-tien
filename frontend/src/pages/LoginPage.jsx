import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'
import { authApi } from '../services/api.js'
import toast from 'react-hot-toast'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

const styles = {
  root: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'var(--bg-base)',
    position: 'relative',
    overflow: 'hidden',
    padding: '24px',
  },
  card: {
    background: 'var(--bg-surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '48px 40px 40px',
    width: '100%',
    maxWidth: 380,
    boxShadow: 'var(--shadow-md)',
    position: 'relative',
    zIndex: 1,
    animation: 'fadeUp 0.5s ease both',
  },
  logoWrap: { display: 'flex', justifyContent: 'center', marginBottom: 24 },
  title: { textAlign: 'center', fontSize: 32, color: 'var(--text-primary)', marginBottom: 8 },
  subtitle: {
    textAlign: 'center',
    fontSize: 15,
    color: 'var(--text-muted)',
    lineHeight: 1.6,
    marginBottom: 32,
  },
  divider: { height: 1, background: 'var(--border)', marginBottom: 28 },
  btnWrap: { display: 'flex', justifyContent: 'center', minHeight: 44 },
  hint: {
    marginTop: 20,
    textAlign: 'center',
    fontSize: 12.5,
    color: 'var(--text-muted)',
    lineHeight: 1.7,
  },
  footer: { position: 'absolute', bottom: 20, fontSize: 12, color: 'var(--text-muted)', opacity: 0.6 },
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { isAuthenticated, setTokens, fetchMe } = useAuthStore()
  const btnRef = useRef(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard', { replace: true })
  }, [isAuthenticated])

  // Đăng nhập: nhận Google ID token → gửi backend → lưu JWT → điều hướng
  const handleCredential = async (response) => {
    try {
      const idToken = response?.credential
      if (!idToken) {
        toast.error('Không nhận được thông tin từ Google.')
        return
      }
      const { data } = await authApi.loginWithGoogle(idToken)
      setTokens(data.access_token, data.refresh_token)

      const me = await fetchMe()
      if (!me) {
        toast.error('Không thể lấy thông tin tài khoản.')
        return
      }
      toast.success(`Xin chào ${me.display_name}!`)
      navigate(me.has_plant ? '/dashboard' : '/claim', { replace: true })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.'
      toast.error(msg)
    }
  }

  // Nạp Google Identity Services rồi render nút đăng nhập chính chủ của Google
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return

    const init = () => {
      if (!window.google?.accounts?.id) return
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredential,
      })
      if (btnRef.current) {
        window.google.accounts.id.renderButton(btnRef.current, {
          theme: 'outline',
          size: 'large',
          width: 300,
          text: 'continue_with',
          shape: 'rectangular',
        })
      }
      setReady(true)
    }

    if (window.google?.accounts?.id) {
      init()
      return
    }
    const existing = document.getElementById('gsi-script')
    if (existing) {
      existing.addEventListener('load', init)
      return () => existing.removeEventListener('load', init)
    }
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.id = 'gsi-script'
    script.onload = init
    document.body.appendChild(script)
  }, [])

  return (
    <div style={styles.root}>
      <LeafBackground />

      <div style={styles.card}>
        <div style={styles.logoWrap}>
          <PlantLogo />
        </div>

        <h1 style={styles.title}>Plant Identity</h1>
        <p style={styles.subtitle}>
          Hệ thống định danh &amp; xác thực<br />
          <em style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
            chậu cây thông minh
          </em>
        </p>

        <div style={styles.divider} />

        <div ref={btnRef} style={styles.btnWrap} />

        {!GOOGLE_CLIENT_ID && (
          <p style={{ ...styles.hint, color: '#c0392b' }}>
            Thiếu cấu hình <strong>VITE_GOOGLE_CLIENT_ID</strong> trong file .env
          </p>
        )}
        {GOOGLE_CLIENT_ID && !ready && (
          <p style={styles.hint}>Đang tải đăng nhập Google…</p>
        )}

        <p style={styles.hint}>
          Sau khi đăng nhập, bạn sẽ nhập <strong>Plant Code</strong> in trên<br />
          thiết bị để liên kết chậu cây vào tài khoản.
        </p>
      </div>

      <footer style={styles.footer}>Plant Identity MVP · 2025</footer>
    </div>
  )
}

function PlantLogo() {
  return (
    <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
      <circle cx="36" cy="36" r="34" fill="var(--green-50)" stroke="var(--green-200)" strokeWidth="1" />
      <line x1="36" y1="58" x2="36" y2="28" stroke="var(--green-600)" strokeWidth="2.5" strokeLinecap="round"
        style={{ animation: 'growStem 1.2s ease both', strokeDasharray: 200 }} />
      <path d="M36 42 C36 42 22 34 20 18 C20 18 34 20 36 36"
        fill="var(--green-300)" opacity="0.85"
        style={{ animation: 'leafPop 0.6s ease 0.5s both' }} />
      <path d="M36 34 C36 34 50 26 52 10 C52 10 38 14 36 28"
        fill="var(--green-500)" opacity="0.9"
        style={{ animation: 'leafPop 0.6s ease 0.8s both' }} />
      <ellipse cx="36" cy="59" rx="10" ry="3" fill="var(--earth-200)" opacity="0.5" />
    </svg>
  )
}

function LeafBackground() {
  const leaves = [
    { top: '6%',  left: '4%',   size: 90,  rotate: -25, opacity: 0.10 },
    { top: '12%', right: '6%',  size: 65,  rotate: 35,  opacity: 0.08 },
    { top: '45%', left: '2%',   size: 110, rotate: -50, opacity: 0.06 },
    { bottom: '18%', right: '4%', size: 95, rotate: 18, opacity: 0.09 },
    { bottom: '6%', left: '12%', size: 60, rotate: -8,  opacity: 0.07 },
    { top: '30%', right: '2%',  size: 75,  rotate: 55,  opacity: 0.06 },
  ]
  return (
    <>
      {leaves.map((l, i) => (
        <div key={i} style={{
          position: 'absolute',
          top: l.top, left: l.left, right: l.right, bottom: l.bottom,
          width: l.size, height: l.size,
          opacity: l.opacity,
          transform: `rotate(${l.rotate}deg)`,
          pointerEvents: 'none',
        }}>
          <svg viewBox="0 0 100 120" fill="var(--green-600)">
            <path d="M50 5 C50 5 8 30 8 65 C8 88 26 108 50 108 C74 108 92 88 92 65 C92 30 50 5 50 5Z" />
            <line x1="50" y1="108" x2="50" y2="55" stroke="var(--green-800)" strokeWidth="2.5" />
            <line x1="50" y1="80" x2="30" y2="60" stroke="var(--green-800)" strokeWidth="1.5" />
            <line x1="50" y1="65" x2="68" y2="48" stroke="var(--green-800)" strokeWidth="1.5" />
          </svg>
        </div>
      ))}
    </>
  )
}
