import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { plantsApi } from '../services/api.js'
import toast from 'react-hot-toast'
import Navbar from '../components/ui/Navbar.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import SensorCard from '../components/dashboard/SensorCard.jsx'
import SensorChart from '../components/dashboard/SensorChart.jsx'
import TuViBadge from '../components/plant/TuViBadge.jsx'

// Backend dùng sensor_key "light"; biểu đồ/Card dùng "light_level" → map qua lại.
const SENSOR_KEYS = ['soil_moisture', 'temperature', 'light', 'humidity']

export default function DashboardPage() {
  const navigate = useNavigate()

  const [dashboard, setDashboard] = useState(null)
  const [sensorLogs, setSensorLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  // Gộp lịch sử 4 cảm biến thành các hàng theo timestamp để vẽ chart
  const buildLogs = (histories) => {
    const byTime = new Map()
    const fieldOf = { soil_moisture: 'soil_moisture', temperature: 'temperature', light: 'light_level', humidity: 'humidity' }
    SENSOR_KEYS.forEach((key, idx) => {
      const res = histories[idx]
      if (res.status !== 'fulfilled') return
      const readings = res.value.data?.readings || []
      readings.forEach((r) => {
        const t = r.created_at
        const row = byTime.get(t) || { recorded_at: t }
        row[fieldOf[key]] = r.value
        byTime.set(t, row)
      })
    })
    return [...byTime.values()].sort(
      (a, b) => new Date(a.recorded_at) - new Date(b.recorded_at)
    )
  }

  const fetchData = async (silent = false) => {
    if (!silent) setLoading(true)
    else setRefreshing(true)

    try {
      const { data } = await plantsApi.getDashboard()
      setDashboard(data)

      const histories = await Promise.allSettled(
        SENSOR_KEYS.map((key) => plantsApi.getHistory(key, 24))
      )
      setSensorLogs(buildLogs(histories).slice(-40))
    } catch (err) {
      const status = err.response?.status
      // 404 = chưa liên kết cây → chuyển sang trang claim
      if (status === 404) {
        navigate('/claim', { replace: true })
        return
      }
      if (!silent) toast.error('Không thể tải dữ liệu')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(() => fetchData(true), 30_000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar />
      <div style={{ paddingTop: 80 }}>
        <Spinner fullscreen />
      </div>
    </div>
  )

  // Map sensors[] → tra cứu nhanh theo sensor_key
  const sensorMap = {}
  ;(dashboard?.sensors || []).forEach((s) => { sensorMap[s.sensor_key] = s })
  const lastUpdated = (dashboard?.sensors || [])
    .map((s) => s.updated_at)
    .filter(Boolean)
    .sort()
    .at(-1)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar />

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px 20px', animation: 'fadeUp 0.4s ease both' }}>

        {/* Plant header card */}
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '28px 28px 24px',
          marginBottom: 24,
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: 20,
          flexWrap: 'wrap',
          boxShadow: 'var(--shadow-sm)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
            <div style={{
              width: 64, height: 64,
              background: 'var(--green-50)',
              border: '1.5px solid var(--green-200)',
              borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 30,
              flexShrink: 0,
            }}>
              🪴
            </div>
            <div>
              <h1 style={{ fontSize: 26, marginBottom: 4, color: 'var(--text-primary)' }}>
                {dashboard?.plant_name || 'Chậu cây của tôi'}
              </h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <span style={{
                  background: 'var(--green-50)',
                  border: '1px solid var(--green-200)',
                  color: 'var(--text-secondary)',
                  borderRadius: 20,
                  padding: '2px 10px',
                  fontSize: 12.5,
                  fontWeight: 500,
                }}>
                  {dashboard?.plant_type?.name || 'Không rõ loài'}
                </span>
                <span style={{
                  fontSize: 12,
                  color: 'var(--text-muted)',
                  background: 'var(--bg-soft)',
                  padding: '2px 8px',
                  borderRadius: 6,
                }}>
                  Cảnh giới: {dashboard?.current_rank?.name || '—'}
                </span>
                <span style={{
                  fontSize: 11.5,
                  color: dashboard?.device_online ? 'var(--green-600)' : 'var(--text-muted)',
                  display: 'flex', alignItems: 'center', gap: 5,
                }}>
                  <span style={{
                    width: 7, height: 7, borderRadius: '50%',
                    background: dashboard?.device_online ? 'var(--green-500)' : '#c0392b',
                    display: 'inline-block',
                  }} />
                  {dashboard?.device_online ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <TuViBadge value={dashboard?.total_exp || 0} />
            <button
              onClick={() => fetchData(true)}
              title="Làm mới dữ liệu"
              style={{
                width: 36, height: 36,
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-surface)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer',
                color: 'var(--text-muted)',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--green-400)'; e.currentTarget.style.color = 'var(--accent)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-muted)' }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }}>
                <path d="M13.6 2.4A7 7 0 1 0 14.5 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                <polyline points="10,0 14.5,2.5 12,7" fill="currentColor" />
              </svg>
            </button>
          </div>
        </div>

        {/* Sensor cards grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 14,
          marginBottom: 24,
        }}>
          <SensorCard
            label="Độ ẩm đất" value={sensorMap.soil_moisture?.value ?? null}
            unit="%" icon="💧" min={0} max={100} warnBelow={20} warnAbove={80}
          />
          <SensorCard
            label="Nhiệt độ" value={sensorMap.temperature?.value ?? null}
            unit="°C" icon="🌡️" min={10} max={45} warnBelow={15} warnAbove={38}
          />
          <SensorCard
            label="Ánh sáng" value={sensorMap.light?.value ?? null}
            unit="lux" icon="☀️" min={0} max={10000}
          />
          <SensorCard
            label="Độ ẩm KK" value={sensorMap.humidity?.value ?? null}
            unit="%" icon="🌫️" min={0} max={100}
          />
        </div>

        {/* Last updated */}
        {lastUpdated && (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 20, textAlign: 'right' }}>
            Cập nhật lần cuối: {new Date(lastUpdated).toLocaleString('vi-VN')}
          </p>
        )}

        {/* Sensor chart */}
        {sensorLogs.length > 0 && <SensorChart logs={sensorLogs} />}

        {(dashboard?.sensors || []).length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '48px 24px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            color: 'var(--text-muted)',
          }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🌱</div>
            <p style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontStyle: 'italic', marginBottom: 6 }}>
              Chưa có dữ liệu cảm biến
            </p>
            <p style={{ fontSize: 13 }}>Thiết bị IoT chưa gửi dữ liệu về máy chủ</p>
          </div>
        )}

        {/* Plant info footer */}
        <div style={{
          marginTop: 24,
          padding: '16px 20px',
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexWrap: 'wrap', gap: 8,
          fontSize: 12.5, color: 'var(--text-muted)',
        }}>
          <span>Tu Vi (EXP): <code style={{ fontSize: 11 }}>{(dashboard?.total_exp ?? 0).toLocaleString('vi-VN')}</code></span>
          <span>
            Thiết bị: {dashboard?.device_last_seen
              ? new Date(dashboard.device_last_seen).toLocaleString('vi-VN')
              : 'chưa kết nối'}
          </span>
        </div>
      </div>
    </div>
  )
}
