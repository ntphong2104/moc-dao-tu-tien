import { useState } from 'react'

const METRICS = [
  { key: 'soil_moisture', label: 'Độ ẩm đất',  unit: '%',   color: '#3fa03f' },
  { key: 'temperature',   label: 'Nhiệt độ',    unit: '°C',  color: '#e67e22' },
  { key: 'light_level',   label: 'Ánh sáng',    unit: 'lux', color: '#f1c40f' },
  { key: 'humidity',      label: 'Độ ẩm KK',    unit: '%',   color: '#3498db' },
]

export default function SensorChart({ logs }) {
  const [active, setActive] = useState('soil_moisture')

  const metric = METRICS.find(m => m.key === active)
  const values = logs.map(l => l[active]).filter(v => v != null)

  if (values.length === 0) return null

  const W = 640, H = 180
  const PAD = { top: 16, right: 16, bottom: 28, left: 40 }
  const innerW = W - PAD.left - PAD.right
  const innerH = H - PAD.top - PAD.bottom

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const pts = values.map((v, i) => ({
    x: PAD.left + (i / (values.length - 1 || 1)) * innerW,
    y: PAD.top + (1 - (v - min) / range) * innerH,
    v,
  }))

  const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
  const areaD = `${pathD} L ${pts[pts.length-1].x.toFixed(1)} ${(PAD.top + innerH).toFixed(1)} L ${pts[0].x.toFixed(1)} ${(PAD.top + innerH).toFixed(1)} Z`

  // Y axis labels
  const yLabels = [min, min + range * 0.5, max].map(v => ({
    y: PAD.top + (1 - (v - min) / range) * innerH,
    label: v.toFixed(0),
  }))

  // X axis labels (show first, mid, last timestamps)
  const xSamples = [0, Math.floor(logs.length / 2), logs.length - 1]
    .filter((i, _, arr) => arr.indexOf(i) === arr.lastIndexOf(i) || i < logs.length)
    .map(i => ({
      x: PAD.left + (i / (logs.length - 1 || 1)) * innerW,
      label: logs[i]?.recorded_at
        ? new Date(logs[i].recorded_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
        : '',
    }))

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      padding: '20px',
      boxShadow: 'var(--shadow-sm)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
        <h3 style={{ fontSize: 15, fontWeight: 500, color: 'var(--text-primary)' }}>
          Lịch sử cảm biến
        </h3>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {METRICS.map(m => (
            <button
              key={m.key}
              onClick={() => setActive(m.key)}
              style={{
                padding: '4px 12px',
                fontSize: 12.5,
                border: '1px solid',
                borderColor: active === m.key ? m.color : 'var(--border)',
                borderRadius: 20,
                background: active === m.key ? `${m.color}18` : 'transparent',
                color: active === m.key ? m.color : 'var(--text-muted)',
                cursor: 'pointer',
                fontWeight: active === m.key ? 500 : 400,
                transition: 'all 0.15s',
              }}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Chart */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}
      >
        <defs>
          <linearGradient id={`grad-${active}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={metric.color} stopOpacity="0.18" />
            <stop offset="100%" stopColor={metric.color} stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {yLabels.map((yl, i) => (
          <g key={i}>
            <line
              x1={PAD.left} y1={yl.y} x2={PAD.left + innerW} y2={yl.y}
              stroke="var(--border)" strokeWidth="1" strokeDasharray="4 4"
            />
            <text x={PAD.left - 6} y={yl.y + 4} textAnchor="end" fontSize="11" fill="var(--text-muted)">
              {yl.label}
            </text>
          </g>
        ))}

        {/* X axis labels */}
        {xSamples.map((xs, i) => (
          <text key={i} x={xs.x} y={PAD.top + innerH + 18} textAnchor="middle" fontSize="11" fill="var(--text-muted)">
            {xs.label}
          </text>
        ))}

        {/* Unit label */}
        <text x={PAD.left - 6} y={PAD.top - 4} textAnchor="end" fontSize="11" fill={metric.color} fontWeight="500">
          {metric.unit}
        </text>

        {/* Area fill */}
        {pts.length > 1 && (
          <path d={areaD} fill={`url(#grad-${active})`} />
        )}

        {/* Line */}
        {pts.length > 1 && (
          <path d={pathD} fill="none" stroke={metric.color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        )}

        {/* Data points */}
        {pts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" fill={metric.color} stroke="white" strokeWidth="1.5">
            <title>{p.v.toFixed(1)} {metric.unit}</title>
          </circle>
        ))}
      </svg>
    </div>
  )
}
