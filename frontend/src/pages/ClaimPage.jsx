import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { plantsApi } from '../services/api.js'
import { useAuthStore } from '../store/authStore.js'
import toast from 'react-hot-toast'
import Navbar from '../components/ui/Navbar.jsx'

export default function ClaimPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const [code, setCode] = useState(Array(8).fill(''))
  const [verifyCode, setVerifyCode] = useState('')
  const [plantName, setPlantName] = useState('')
  const [plantTypeId, setPlantTypeId] = useState('')
  const [plantTypes, setPlantTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const inputRefs = useRef([])

  useEffect(() => {
    inputRefs.current[0]?.focus()
    // Nạp danh sách loại cây cho dropdown
    plantsApi
      .getPlantTypes()
      .then(({ data }) => setPlantTypes(Array.isArray(data) ? data : []))
      .catch(() => {})
  }, [])

  const handleCodeChange = (index, value) => {
    const char = value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(-1)
    const next = [...code]
    next[index] = char
    setCode(next)
    if (char && index < 7) inputRefs.current[index + 1]?.focus()
  }

  const handleCodeKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) inputRefs.current[index - 1]?.focus()
    if (e.key === 'ArrowLeft' && index > 0) inputRefs.current[index - 1]?.focus()
    if (e.key === 'ArrowRight' && index < 7) inputRefs.current[index + 1]?.focus()
  }

  const handleCodePaste = (e) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 8)
    const next = Array(8).fill('')
    for (let i = 0; i < pasted.length; i++) next[i] = pasted[i]
    setCode(next)
    inputRefs.current[Math.min(pasted.length, 7)]?.focus()
  }

  const validate = () => {
    const errs = {}
    if (code.join('').length < 8) errs.code = 'Vui lòng nhập đủ 8 ký tự Plant Code'
    if (!verifyCode.trim()) errs.verifyCode = 'Vui lòng nhập Verify Code in trên thiết bị'
    if (!plantName.trim()) errs.plantName = 'Vui lòng đặt tên cho cây của bạn'
    if (!plantTypeId.trim()) errs.plantTypeId = 'Vui lòng nhập Plant Type ID (loại cây)'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      await plantsApi.pairPlant({
        plant_code: code.join(''),
        verify_code: verifyCode.trim(),
        name: plantName.trim(),
        plant_type_id: plantTypeId.trim(),
      })
      toast.success('🌱 Đã liên kết chậu cây thành công!')
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail || ''

      if (status === 400 && detail) {
        toast.error(detail) // backend trả lý do cụ thể (sai verify code, loại cây không tồn tại, ...)
        if (detail.includes('Verify')) setErrors({ verifyCode: 'Verify Code không chính xác' })
        else if (detail.includes('Plant Code')) setErrors({ code: 'Plant Code không hợp lệ' })
        else if (detail.includes('Loại cây')) setErrors({ plantTypeId: 'Loại cây không tồn tại' })
        else if (detail.includes('đã liên kết')) navigate('/dashboard', { replace: true })
      } else if (status === 401) {
        toast.error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.')
      } else {
        toast.error('Có lỗi xảy ra. Vui lòng thử lại.')
      }
    } finally {
      setLoading(false)
    }
  }

  const codeComplete = code.every(c => c !== '')

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar />
      <div style={{ maxWidth: 480, margin: '0 auto', padding: '48px 24px', animation: 'fadeUp 0.4s ease both' }}>
        {/* Header */}
        <div style={{ marginBottom: 36 }}>
          <div style={{
            width: 56, height: 56, background: 'var(--green-50)', border: '1px solid var(--border)',
            borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
          }}>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <path d="M14 3 C14 3 4 9 4 17 C4 21.4 8.6 25 14 25 C19.4 25 24 21.4 24 17 C24 9 14 3 14 3Z" fill="var(--green-300)" />
              <line x1="14" y1="25" x2="14" y2="13" stroke="var(--green-700)" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </div>
          <h1 style={{ fontSize: 28, marginBottom: 6, color: 'var(--text-primary)' }}>Liên kết chậu cây</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.6 }}>
            Nhập <strong style={{ color: 'var(--text-secondary)' }}>Plant Code</strong> &amp;{' '}
            <strong style={{ color: 'var(--text-secondary)' }}>Verify Code</strong> in trên thiết bị IoT
            để liên kết vào tài khoản <em>{user?.email}</em>
          </p>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {/* Plant Code */}
          <div style={{ marginBottom: 24 }}>
            <label style={labelStyle}>
              Plant Code
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 400, marginLeft: 8 }}>
                8 ký tự in trên thiết bị
              </span>
            </label>
            <div style={{ display: 'flex', gap: 7, justifyContent: 'center' }} onPaste={handleCodePaste}>
              {code.map((char, i) => (
                <input
                  key={i}
                  ref={el => inputRefs.current[i] = el}
                  value={char}
                  onChange={e => handleCodeChange(i, e.target.value)}
                  onKeyDown={e => handleCodeKeyDown(i, e)}
                  maxLength={1}
                  disabled={loading}
                  style={{
                    width: 46, height: 52, textAlign: 'center', fontSize: 20, fontWeight: 500,
                    fontFamily: "'Courier New', monospace", letterSpacing: 1,
                    background: char ? 'var(--green-50)' : 'var(--bg-surface)',
                    border: `1.5px solid ${errors.code ? '#e74c3c' : char ? 'var(--green-400)' : 'var(--border-strong)'}`,
                    borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', outline: 'none',
                    transition: 'border-color 0.15s, background 0.15s', textTransform: 'uppercase',
                  }}
                />
              ))}
            </div>
            {errors.code && <p style={errorStyle}>{errors.code}</p>}
          </div>

          {/* Verify Code */}
          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>Verify Code</label>
            <input
              type="text"
              value={verifyCode}
              onChange={e => setVerifyCode(e.target.value)}
              placeholder="Mã xác minh in kèm trên thiết bị"
              disabled={loading}
              style={{ ...inputStyle, borderColor: errors.verifyCode ? '#e74c3c' : 'var(--border-strong)' }}
            />
            {errors.verifyCode && <p style={errorStyle}>{errors.verifyCode}</p>}
          </div>

          {/* Plant Name */}
          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>Tên cây</label>
            <input
              type="text"
              value={plantName}
              onChange={e => setPlantName(e.target.value)}
              placeholder="Ví dụ: Bé Cây Góc Bàn"
              disabled={loading}
              maxLength={50}
              style={{ ...inputStyle, borderColor: errors.plantName ? '#e74c3c' : 'var(--border-strong)' }}
            />
            {errors.plantName && <p style={errorStyle}>{errors.plantName}</p>}
          </div>

          {/* Loại cây */}
          <div style={{ marginBottom: 32 }}>
            <label style={labelStyle}>Loại cây</label>
            <select
              value={plantTypeId}
              onChange={e => setPlantTypeId(e.target.value)}
              disabled={loading}
              style={{
                ...inputStyle,
                cursor: 'pointer',
                color: plantTypeId ? 'var(--text-primary)' : 'var(--text-muted)',
                borderColor: errors.plantTypeId ? '#e74c3c' : 'var(--border-strong)',
              }}
            >
              <option value="">— Chọn loại cây —</option>
              {plantTypes.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
            {errors.plantTypeId && <p style={errorStyle}>{errors.plantTypeId}</p>}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !codeComplete}
            style={{
              width: '100%', padding: '14px',
              background: (loading || !codeComplete) ? 'var(--green-200)' : 'var(--accent)',
              color: (loading || !codeComplete) ? 'var(--green-600)' : 'white',
              border: 'none', borderRadius: 'var(--radius-md)', fontSize: 15, fontWeight: 500,
              cursor: (loading || !codeComplete) ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}
          >
            {loading ? 'Đang xác minh…' : 'Liên kết chậu cây'}
          </button>
        </form>

        <div style={{
          marginTop: 24, padding: '14px 16px', background: 'var(--green-50)',
          border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)',
          fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.7,
        }}>
          <strong style={{ color: 'var(--text-secondary)' }}>Lưu ý:</strong> Mỗi tài khoản chỉ liên kết 1 chậu cây.
          Plant Code &amp; Verify Code do hệ thống sinh ra khi Admin tạo thiết bị (provisioning).
        </div>
      </div>
    </div>
  )
}

const labelStyle = {
  display: 'block', fontSize: 13.5, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 8,
}

const inputStyle = {
  width: '100%', padding: '11px 14px', fontSize: 15,
  background: 'var(--bg-surface)', border: '1.5px solid var(--border-strong)',
  borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', outline: 'none',
  transition: 'border-color 0.15s, box-shadow 0.15s',
}

const errorStyle = { marginTop: 5, fontSize: 12, color: '#e74c3c' }
