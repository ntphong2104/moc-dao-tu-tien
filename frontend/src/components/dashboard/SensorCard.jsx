export default function SensorCard({ label, value, unit, icon, min = 0, max = 100, warnBelow, warnAbove }) {
  const hasData = value !== null && value !== undefined

  const getStatus = () => {
    if (!hasData) return 'none'
    if (warnBelow !== undefined && value < warnBelow) return 'low'
    if (warnAbove !== undefined && value > warnAbove) return 'high'
    return 'ok'
  }

  const status = getStatus()

  const statusColors = {
    none: { bar: 'var(--green-100)', text: 'var(--text-muted)' },
    ok:   { bar: 'var(--green-400)', text: 'var(--text-secondary)' },
    low:  { bar: '#e67e22',          text: '#e67e22' },
    high: { bar: '#e74c3c',          text: '#e74c3c' },
  }

  const pct = hasData ? Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100)) : 0
  const col = statusColors[status]

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-md)',
      padding: '18px 16px',
      boxShadow: 'var(--shadow-sm)',
      transition: 'box-shadow 0.2s',
    }}
    onMouseEnter={e => e.currentTarget.style.boxShadow = 'var(--shadow-md)'}
    onMouseLeave={e => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{label}</span>
        <span style={{ fontSize: 18 }}>{icon}</span>
      </div>

      <div style={{ marginBottom: 10 }}>
        {hasData ? (
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 3 }}>
            <span style={{ fontSize: 26, fontWeight: 500, color: col.text, fontFamily: 'var(--font-display)' }}>
              {typeof value === 'number' ? value.toFixed(1) : value}
            </span>
            <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{unit}</span>
          </div>
        ) : (
          <span style={{ fontSize: 22, color: 'var(--text-muted)', fontStyle: 'italic', fontFamily: 'var(--font-display)' }}>—</span>
        )}
      </div>

      {/* Progress bar */}
      <div style={{
        height: 4, borderRadius: 2,
        background: 'var(--green-50)',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          width: `${pct}%`,
          background: col.bar,
          borderRadius: 2,
          transition: 'width 0.6s ease',
        }} />
      </div>

      {status === 'low' && (
        <p style={{ fontSize: 11, color: '#e67e22', marginTop: 6 }}>⚠ Thấp hơn mức bình thường</p>
      )}
      {status === 'high' && (
        <p style={{ fontSize: 11, color: '#e74c3c', marginTop: 6 }}>⚠ Cao hơn mức bình thường</p>
      )}
    </div>
  )
}
