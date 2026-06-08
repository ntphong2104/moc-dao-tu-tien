export default function TuViBadge({ value = 0 }) {
  const level = value < 100 ? 1 : value < 500 ? 2 : value < 2000 ? 3 : value < 5000 ? 4 : 5
  const label = ['Mầm', 'Cây Non', 'Trưởng Thành', 'Linh Thảo', 'Thiên Mộc'][level - 1]
  const stars = '★'.repeat(level) + '☆'.repeat(5 - level)

  return (
    <div style={{
      background: 'var(--green-50)',
      border: '1px solid var(--green-200)',
      borderRadius: 'var(--radius-md)',
      padding: '10px 14px',
      textAlign: 'center',
      minWidth: 110,
    }}>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 3 }}>
        Tu Vi
      </div>
      <div style={{
        fontSize: 22,
        fontFamily: 'var(--font-display)',
        fontWeight: 400,
        color: 'var(--text-secondary)',
        lineHeight: 1.1,
        marginBottom: 2,
      }}>
        {value.toLocaleString('vi-VN')}
      </div>
      <div style={{ fontSize: 11, color: 'var(--green-500)', letterSpacing: 1 }}>{stars}</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
    </div>
  )
}
