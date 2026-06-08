import axios from 'axios'

// Prefix /api được Vite proxy forward sang backend FastAPI (giữ nguyên /api).
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const ACCESS_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

export const tokenStore = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  set: (access, refresh) => {
    if (access) localStorage.setItem(ACCESS_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

export const api = axios.create({
  baseURL: BASE_URL,
})

// Gắn access token vào mọi request
api.interceptors.request.use((config) => {
  const token = tokenStore.getAccess()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Tự refresh khi gặp 401 (một lần), rồi retry request gốc
let refreshing = null
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    const status = error.response?.status

    // Không xử lý nếu không phải 401, đã retry, hoặc chính request refresh bị 401
    if (
      status !== 401 ||
      original?._retry ||
      original?.url?.includes('/auth/refresh')
    ) {
      return Promise.reject(error)
    }

    const refreshToken = tokenStore.getRefresh()
    if (!refreshToken) {
      tokenStore.clear()
      return Promise.reject(error)
    }

    original._retry = true
    try {
      // Gộp nhiều request 401 cùng lúc vào 1 lần refresh
      refreshing =
        refreshing ||
        axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
      const { data } = await refreshing
      refreshing = null

      tokenStore.set(data.access_token, data.refresh_token)
      original.headers.Authorization = `Bearer ${data.access_token}`
      return api(original)
    } catch (e) {
      refreshing = null
      tokenStore.clear()
      if (typeof window !== 'undefined') window.location.href = '/login'
      return Promise.reject(e)
    }
  }
)

// ─── Auth ────────────────────────────────────────────────────────────────────
// Backend: POST /api/auth/google { id_token } → { access_token, refresh_token }
export const authApi = {
  loginWithGoogle: (idToken) => api.post('/auth/google', { id_token: idToken }),
  getMe: () => api.get('/auth/me'),
  refresh: (refreshToken) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
}

// ─── Plants (mô hình 1 user = 1 cây) ──────────────────────────────────────────
export const plantsApi = {
  // GET /api/plants/types → danh sách loại cây để chọn khi liên kết
  getPlantTypes: () => api.get('/plants/types'),

  // GET /api/plants/me/dashboard → chỉ số, Tu Vi, Cảnh Giới, sensors hiện tại
  getDashboard: () => api.get('/plants/me/dashboard'),

  // GET /api/plants/me/history?sensor_key=&hours= → time series 1 loại cảm biến
  getHistory: (sensorKey, hours = 24) =>
    api.get('/plants/me/history', { params: { sensor_key: sensorKey, hours } }),

  // POST /api/plants/pair { plant_code, verify_code, name, plant_type_id }
  pairPlant: ({ plant_code, verify_code, name, plant_type_id }) =>
    api.post('/plants/pair', { plant_code, verify_code, name, plant_type_id }),

  // PUT /api/plants/me { name?, plant_type_id? }
  updatePlant: (payload) => api.put('/plants/me', payload),
}

// ─── Leaderboard ──────────────────────────────────────────────────────────────
export const leaderboardApi = {
  getLeaderboard: (limit = 20) => api.get('/leaderboard', { params: { limit } }),
}
