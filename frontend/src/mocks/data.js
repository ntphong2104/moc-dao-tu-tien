/**
 * Mock data — Mộc Đạo Tu Tiên API
 * ---------------------------------------------------------------------------
 * Dữ liệu mẫu bám theo openapi.json (FastAPI backend). File này KHÔNG tự gắn
 * vào api.js hay các page — bạn import và ghép thủ công khi cần.
 *
 * Mỗi export tương ứng request/response của một endpoint. Các response dạng
 * "additionalProperties: true" (dashboard, leaderboard, admin...) được thiết kế
 * theo chủ đề tu tiên cho nhất quán; bạn chỉnh field tuỳ ý.
 *
 * Tất cả id dạng UUID, thời gian dạng ISO 8601.
 */

const now = new Date()
const iso = (offsetMs = 0) => new Date(now.getTime() + offsetMs).toISOString()
const HOUR = 3600_000

// ─── Cảnh Giới (rank config) ──────────────────────────────────────────────
// Mốc Tu Vi (total_exp) -> tên Cảnh Giới. Dùng chung cho dashboard & leaderboard.
// GET/PUT /api/admin/rank-config
export const rankConfig = [
  { order: 1, name: 'Phàm Mộc',    min_exp: 0 },
  { order: 2, name: 'Luyện Mộc',   min_exp: 500 },
  { order: 3, name: 'Trúc Cơ',     min_exp: 1500 },
  { order: 4, name: 'Kim Đan',     min_exp: 3000 },
  { order: 5, name: 'Nguyên Anh',  min_exp: 6000 },
  { order: 6, name: 'Hóa Thần',    min_exp: 12000 },
  { order: 7, name: 'Thiên Mộc',   min_exp: 24000 },
]

/** Tiện ích: suy ra Cảnh Giới hiện tại + tiến trình từ total_exp. */
export function resolveRank(totalExp) {
  const sorted = [...rankConfig].sort((a, b) => a.min_exp - b.min_exp)
  let current = sorted[0]
  let next = null
  for (let i = 0; i < sorted.length; i++) {
    if (totalExp >= sorted[i].min_exp) {
      current = sorted[i]
      next = sorted[i + 1] || null
    }
  }
  const span = next ? next.min_exp - current.min_exp : 0
  const gained = totalExp - current.min_exp
  return {
    rank_order: current.order,
    rank_name: current.name,
    next_rank_name: next ? next.name : null,
    exp_to_next: next ? next.min_exp - totalExp : 0,
    progress_percent: next ? Math.round((gained / span) * 100) : 100,
  }
}

// ─── Hồ số Tu Vi (exp config) ─────────────────────────────────────────────
// GET/PUT /api/admin/exp-config — cộng/trừ Tu Vi theo chất lượng chăm sóc.
export const expConfig = [
  { quality_level: 'perfect', exp_delta: 10,  description: 'Mọi chỉ số trong ngưỡng lý tưởng' },
  { quality_level: 'good',    exp_delta: 5,   description: 'Đa số chỉ số tốt' },
  { quality_level: 'neutral', exp_delta: 0,   description: 'Bình thường, không thưởng phạt' },
  { quality_level: 'poor',    exp_delta: -5,  description: 'Một vài chỉ số ngoài ngưỡng' },
  { quality_level: 'critical', exp_delta: -15, description: 'Chỉ số nguy hiểm cho cây' },
]

// ─── Loại cây (plant types) ───────────────────────────────────────────────
// GET /api/admin/plant-types -> PlantTypeResponse[]
export const plantTypes = [
  {
    id: '11111111-1111-4111-8111-111111111111',
    name: 'Trầu Bà',
    description: 'Dễ trồng, ưa bóng râm, chịu được điều kiện thiếu sáng.',
    soil_moisture_min: 40, soil_moisture_max: 70,
    light_min: 800,        light_max: 6000,
    temperature_min: 18,   temperature_max: 30,
    humidity_min: 50,      humidity_max: 80,
    created_at: iso(-90 * 24 * HOUR),
    updated_at: iso(-10 * 24 * HOUR),
  },
  {
    id: '22222222-2222-4222-8222-222222222222',
    name: 'Lưỡi Hổ',
    description: 'Cây phong thủy, chịu hạn tốt, tưới ít nước.',
    soil_moisture_min: 20, soil_moisture_max: 50,
    light_min: 1000,       light_max: 10000,
    temperature_min: 18,   temperature_max: 32,
    humidity_min: 30,      humidity_max: 70,
    created_at: iso(-88 * 24 * HOUR),
    updated_at: iso(-8 * 24 * HOUR),
  },
  {
    id: '33333333-3333-4333-8333-333333333333',
    name: 'Sen Đá',
    description: 'Mọng nước, cần nhiều ánh sáng, đất thoát nước tốt.',
    soil_moisture_min: 15, soil_moisture_max: 40,
    light_min: 4000,       light_max: 15000,
    temperature_min: 15,   temperature_max: 30,
    humidity_min: 30,      humidity_max: 60,
    created_at: iso(-80 * 24 * HOUR),
    updated_at: iso(-5 * 24 * HOUR),
  },
  {
    id: '44444444-4444-4444-8444-444444444444',
    name: 'Kim Tiền',
    description: 'Biểu tượng tài lộc, ưa sáng vừa, ít cần tưới.',
    soil_moisture_min: 35, soil_moisture_max: 65,
    light_min: 1500,       light_max: 8000,
    temperature_min: 20,   temperature_max: 30,
    humidity_min: 40,      humidity_max: 75,
    created_at: iso(-70 * 24 * HOUR),
    updated_at: iso(-3 * 24 * HOUR),
  },
]

// ─── Users ────────────────────────────────────────────────────────────────
// GET /api/auth/me -> UserResponse
export const userMe = {
  id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  email: 'dev@plant.local',
  display_name: 'Nhà Phát Triển',
  avatar_url: null,
  role: 'user',
  has_plant: true,
  created_at: iso(-120 * 24 * HOUR),
}

export const userAdmin = {
  id: '00000000-0000-4000-8000-000000000000',
  email: 'admin@plant.local',
  display_name: 'Quản Trị Viên',
  avatar_url: null,
  role: 'admin',
  has_plant: false,
  created_at: iso(-200 * 24 * HOUR),
}

/** User chưa liên kết cây — dùng để test luồng /pair. */
export const userNoPlant = {
  id: '99999999-9999-4999-8999-999999999999',
  email: 'newbie@plant.local',
  display_name: 'Tân Tu Sĩ',
  avatar_url: null,
  role: 'user',
  has_plant: false,
  created_at: iso(-1 * 24 * HOUR),
}

// ─── Auth tokens ──────────────────────────────────────────────────────────
// POST /api/auth/google, /api/auth/refresh -> TokenResponse
export const tokenResponse = {
  access_token: 'mock.access.jwt-eyJhbGciOiJIUzI1NiJ9',
  refresh_token: 'mock.refresh.jwt-eyJhbGciOiJIUzI1NiJ9',
  token_type: 'bearer',
}

// Request bodies (tham khảo khi gọi thử)
export const googleLoginRequest = { id_token: 'GOOGLE_ID_TOKEN_FROM_FRONTEND' }
export const refreshTokenRequest = { refresh_token: tokenResponse.refresh_token }

// ─── Pair plant ───────────────────────────────────────────────────────────
// POST /api/plants/pair (PlantPairRequest)
export const plantPairRequest = {
  plant_code: 'A3K9P2XR',
  verify_code: '482913',
  name: 'Bé Cây Góc Bàn',
  plant_type_id: plantTypes[0].id,
}

export const plantPairResponse = {
  status: 'ok',
  plant_id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
  message: 'Liên kết chậu cây thành công.',
}

// ─── Dashboard ────────────────────────────────────────────────────────────
// GET /api/plants/me/dashboard (additionalProperties: true)
// total_exp = 2500 -> Cảnh Giới "Trúc Cơ".
const dashboardTotalExp = 2500
export const dashboard = {
  plant: {
    id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
    plant_code: 'A3K9P2XR',
    name: 'Bé Cây Trạng Nguyên',
    plant_type_id: plantTypes[0].id,
    plant_type_name: plantTypes[0].name,
    paired_at: iso(-30 * 24 * HOUR),
  },
  cultivation: {
    total_exp: dashboardTotalExp,
    ...resolveRank(dashboardTotalExp),
  },
  // Chỉ số hiện tại + đánh giá so với ngưỡng lý tưởng của loại cây.
  sensors: {
    soil_moisture: { value: 55, unit: '%',   status: 'good',    ideal_min: 40, ideal_max: 70 },
    light:         { value: 5000, unit: 'lux', status: 'good',    ideal_min: 800, ideal_max: 6000 },
    temperature:   { value: 28, unit: '°C',  status: 'good',    ideal_min: 18, ideal_max: 30 },
    humidity:      { value: 60, unit: '%',   status: 'good',    ideal_min: 50, ideal_max: 80 },
  },
  device: {
    is_active: true,
    last_seen: iso(-2 * 60_000), // 2 phút trước
  },
  updated_at: iso(),
}

// ─── History ──────────────────────────────────────────────────────────────
// GET /api/plants/me/history?sensor_key=&hours= (additionalProperties: true)
// Sinh chuỗi điểm theo giờ cho từng loại cảm biến.
function buildHistory(sensorKey, unit, base, jitter, hours = 24) {
  const points = []
  for (let h = hours; h >= 0; h--) {
    const wobble = Math.round((Math.sin(h / 3) * jitter + (Math.random() - 0.5) * jitter) * 10) / 10
    points.push({ recorded_at: iso(-h * HOUR), value: Math.round((base + wobble) * 10) / 10 })
  }
  return { sensor_key: sensorKey, unit, hours, points }
}

export const history = {
  soil_moisture: buildHistory('soil_moisture', '%', 52, 8),
  light:         buildHistory('light', 'lux', 4800, 1500),
  temperature:   buildHistory('temperature', '°C', 27, 3),
  humidity:      buildHistory('humidity', '%', 62, 10),
}

// ─── Update plant ─────────────────────────────────────────────────────────
// PUT /api/plants/me (PlantUpdateRequest)
export const plantUpdateRequest = {
  name: 'Bé Cây Cửa Sổ',
  plant_type_id: plantTypes[3].id,
}

// ─── Telemetry (device IoT) ───────────────────────────────────────────────
// POST /api/devices/{plant_code}/telemetry (TelemetryPayload -> TelemetryResponse)
export const telemetryPayload = {
  sensors: [
    { key: 'soil_moisture', value: 55 },
    { key: 'light',         value: 5000 },
    { key: 'temperature',   value: 28 },
    { key: 'humidity',      value: 60 },
  ],
}

export const telemetryResponse = {
  status: 'ok',
  exp_awarded: true,
  message: '+10 Tu Vi — chăm sóc hoàn hảo!',
}

// ─── Leaderboard ──────────────────────────────────────────────────────────
// GET /api/leaderboard?limit= (additionalProperties: true) — giảm dần theo total_exp.
const leaderboardRaw = [
  { plant_name: 'Cổ Thụ Ngàn Năm', owner_name: 'Lão Mộc Tiên', plant_type: 'Trầu Bà',  total_exp: 25800 },
  { plant_name: 'Bích Ngọc Diệp',  owner_name: 'Thanh Vân',     plant_type: 'Kim Tiền', total_exp: 13200 },
  { plant_name: 'Linh Lung Thảo',  owner_name: 'Diệp Cô Thành', plant_type: 'Lưỡi Hổ',  total_exp: 7400 },
  { plant_name: 'Bé Cây Trạng Nguyên', owner_name: 'Nhà Phát Triển', plant_type: 'Trầu Bà', total_exp: 2500 },
  { plant_name: 'Mầm Xanh Nhỏ',    owner_name: 'Tân Tu Sĩ',     plant_type: 'Sen Đá',   total_exp: 620 },
]
export const leaderboard = leaderboardRaw
  .sort((a, b) => b.total_exp - a.total_exp)
  .map((p, i) => ({
    rank: i + 1,
    plant_id: `aaaaaaaa-0000-4000-8000-00000000000${i + 1}`,
    plant_name: p.plant_name,
    owner_name: p.owner_name,
    plant_type: p.plant_type,
    total_exp: p.total_exp,
    cultivation_rank: resolveRank(p.total_exp).rank_name,
  }))

// ─── Admin: dashboard ─────────────────────────────────────────────────────
// GET /api/admin/dashboard (additionalProperties: true)
export const adminDashboard = {
  total_users: 128,
  total_plants: 96,
  total_devices: 110,
  active_devices: 87,
  paired_devices: 96,
  unpaired_devices: 14,
  telemetry_last_24h: 12480,
  new_users_last_7d: 11,
  top_plant_type: 'Trầu Bà',
  updated_at: iso(),
}

// ─── Admin: devices ───────────────────────────────────────────────────────
// GET /api/admin/devices (object[])
export const adminDevices = [
  {
    id: 'd1111111-1111-4111-8111-111111111111',
    plant_code: 'A3K9P2XR',
    is_active: true,
    is_paired: true,
    paired_to: 'dev@plant.local',
    last_seen: iso(-2 * 60_000),
    created_at: iso(-30 * 24 * HOUR),
  },
  {
    id: 'd2222222-2222-4222-8222-222222222222',
    plant_code: 'B7M4Q1ZK',
    is_active: true,
    is_paired: false,
    paired_to: null,
    last_seen: null,
    created_at: iso(-3 * 24 * HOUR),
  },
  {
    id: 'd3333333-3333-4333-8333-333333333333',
    plant_code: 'C2H8N5WL',
    is_active: false,
    is_paired: true,
    paired_to: 'thanh.van@plant.local',
    last_seen: iso(-5 * 24 * HOUR),
    created_at: iso(-60 * 24 * HOUR),
  },
]

// POST /api/admin/devices — verify_code chỉ hiện 1 lần.
export const createDeviceResponse = {
  id: 'd4444444-4444-4444-8444-444444444444',
  plant_code: 'D9F1K3PT',
  verify_code: '739204',
  is_active: true,
  created_at: iso(),
}

// PUT /api/admin/devices/{device_id} (DeviceUpdateRequest)
export const deviceUpdateRequest = { is_active: false }

// ─── Admin: create/update plant type request bodies ───────────────────────
// POST /api/admin/plant-types (PlantTypeCreateRequest)
export const plantTypeCreateRequest = {
  name: 'Xương Rồng',
  description: 'Chịu hạn cực tốt, cần rất nhiều nắng.',
  soil_moisture_min: 10, soil_moisture_max: 30,
  light_min: 6000,       light_max: 20000,
  temperature_min: 15,   temperature_max: 40,
  humidity_min: 20,      humidity_max: 50,
}

// PUT /api/admin/plant-types/{type_id} (PlantTypeUpdateRequest)
export const plantTypeUpdateRequest = {
  description: 'Cập nhật mô tả & nới ngưỡng nhiệt độ.',
  temperature_max: 35,
}

// ─── SSE events ───────────────────────────────────────────────────────────
// GET /api/events/{plant_id} — mẫu payload cho từng loại event.
export const sseEvents = {
  sensor_update: {
    event: 'sensor_update',
    data: {
      plant_id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
      sensors: {
        soil_moisture: 54,
        light: 5100,
        temperature: 28.2,
        humidity: 59,
      },
      recorded_at: iso(),
    },
  },
  exp_update: {
    event: 'exp_update',
    data: {
      plant_id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
      exp_delta: 10,
      total_exp: 2510,
      rank_name: 'Trúc Cơ',
      breakthrough: false, // true khi đột phá lên Cảnh Giới mới
    },
  },
  exp_breakthrough: {
    event: 'exp_update',
    data: {
      plant_id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
      exp_delta: 10,
      total_exp: 3000,
      rank_name: 'Kim Đan',
      breakthrough: true,
    },
  },
}

// ─── Health ───────────────────────────────────────────────────────────────
export const health = { status: 'ok', service: 'moc-dao-tu-tien', version: '1.0.0' }

// ─── Gom tất cả ───────────────────────────────────────────────────────────
const mockData = {
  rankConfig,
  expConfig,
  plantTypes,
  userMe,
  userAdmin,
  userNoPlant,
  tokenResponse,
  googleLoginRequest,
  refreshTokenRequest,
  plantPairRequest,
  plantPairResponse,
  dashboard,
  history,
  plantUpdateRequest,
  telemetryPayload,
  telemetryResponse,
  leaderboard,
  adminDashboard,
  adminDevices,
  createDeviceResponse,
  deviceUpdateRequest,
  plantTypeCreateRequest,
  plantTypeUpdateRequest,
  sseEvents,
  health,
}

export default mockData
