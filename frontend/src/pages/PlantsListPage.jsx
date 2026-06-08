import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { plantsApi } from '../services/api.js'
import Navbar from '../components/ui/Navbar.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import TuViBadge from '../components/plant/TuViBadge.jsx'
import toast from 'react-hot-toast'

export default function PlantsListPage() {
  const navigate = useNavigate()
  const [plant, setPlant] = useState(null) // backend: 1 user = 1 cây
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPlant = async () => {
      try {
        const { data } = await plantsApi.getDashboard()
        setPlant(data)
      } catch (err) {
        // 404 = chưa liên kết cây → để trống (hiện empty state)
        if (err.response?.status !== 404) toast.error('Không thể tải dữ liệu cây')
      } finally {
        setLoading(false)
      }
    }
    fetchPlant()
  }, [])

  if (loading) return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar />
      <div style={{ paddingTop: 80 }}><Spinner fullscreen /></div>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar />

      <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 20px', animation: 'fadeUp 0.4s ease both' }}>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <h1 style={{ fontSize: 28, color: 'var(--text-primary)', marginBottom: 4 }}>Vườn của tôi</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
              {plant ? 'Bạn đang chăm sóc 1 chậu cây' : 'Bạn chưa liên kết chậu cây nào'}
            </p>
          </div>
          {!plant && (
            <button
              onClick={() => navigate('/claim')}
              style={{
                padding: '10px 16px', background: 'var(--accent)', color: 'white',
                border: 'none', borderRadius: 'var(--radius-md)', fontSize: 14, fontWeight: 500,
                display: 'flex', alignItems: 'center', gap: 8, transition: '0.2s', cursor: 'pointer'
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-hover)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--accent)'}
            >
              <span>+</span> Liên kết cây
            </button>
          )}
        </div>

        {!plant ? (
          <div style={{
            textAlign: 'center', padding: '64px 20px', background: 'var(--bg-surface)',
            border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-lg)'
          }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🪴</div>
            <h3 style={{ fontSize: 18, color: 'var(--text-primary)', marginBottom: 8 }}>Vườn đang trống</h3>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 20 }}>Hãy liên kết chậu cây đầu tiên của bạn nhé!</p>
          </div>
        ) : (
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20
          }}>
            <div
              onClick={() => navigate('/dashboard')}
              style={{
                background: 'var(--bg-surface)', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-lg)', padding: '20px',
                boxShadow: 'var(--shadow-sm)', cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                display: 'flex', flexDirection: 'column', gap: 16
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = 'var(--shadow-md)'
                e.currentTarget.style.borderColor = 'var(--green-300)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'none'
                e.currentTarget.style.boxShadow = 'var(--shadow-sm)'
                e.currentTarget.style.borderColor = 'var(--border)'
              }}
            >
              <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                <div style={{
                  width: 56, height: 56, background: 'var(--green-50)',
                  border: '1.5px solid var(--green-200)', borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 26
                }}>
                  🪴
                </div>
                <div>
                  <h3 style={{ fontSize: 17, color: 'var(--text-primary)', marginBottom: 4 }}>
                    {plant.plant_name || 'Cây chưa đặt tên'}
                  </h3>
                  <span style={{
                    fontSize: 12, color: 'var(--text-muted)', background: 'var(--bg-soft)',
                    padding: '2px 8px', borderRadius: 4
                  }}>
                    {plant.plant_type?.name || 'Không rõ loài'}
                  </span>
                </div>
              </div>

              <TuViBadge value={plant.total_exp || 0} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
