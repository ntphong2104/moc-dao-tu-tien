export default function Spinner({ fullscreen = false, size = 44 }) {
  const inner = (
    <div style={{ textAlign: 'center' }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 44 44"
        fill="none"
        style={{ animation: 'spin 1.4s linear infinite', display: 'block', margin: '0 auto 10px' }}
      >
        <circle
          cx="22" cy="22" r="18"
          stroke="var(--green-100)"
          strokeWidth="3"
        />
        <path
          d="M22 4 A18 18 0 0 1 40 22"
          stroke="var(--green-500)"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Đang tải…</p>
    </div>
  )

  if (fullscreen) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-base)',
      }}>
        {inner}
      </div>
    )
  }

  return inner
}
