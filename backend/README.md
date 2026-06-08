# 📂 Backend - Mộc Đạo Tu Tiên

Thư mục này chứa mã nguồn Backend của hệ thống **Mộc Đạo Tu Tiên**. Một hệ thống quản lý tu luyện tích hợp IoT.

## 🚀 Công nghệ sử dụng

Dự án được xây dựng với các công cụ hiện đại nhằm đảm bảo chất lượng mã nguồn:

- **Ngôn ngữ**: [Python 3.12+](https://www.python.org/)
- **Quản lý package**: [uv](https://github.com/astral-sh/uv) - Trình quản lý package siêu nhanh cho Python.
- **Linter & Formatter**: [Ruff](https://github.com/astral-sh/ruff) - Công cụ kiểm tra và định dạng code nhanh nhất.
- **Type Checker**: [Ty](https://github.com/lucas-m-p/ty) - Trình kiểm tra kiểu mạnh mẽ.
- **Testing**: [Pytest](https://docs.pytest.org/) - Framework kiểm thử chuyên nghiệp.

## 🛠️ Cài đặt & Phát triển

### 1. Cài đặt môi trường
Sử dụng `uv` để đồng bộ môi trường:
```bash
uv sync
```

### 2. Kiểm tra chất lượng (Quality Assurance)
Dự án áp dụng quy trình kiểm tra nghiêm ngặt thông qua các lệnh:

- **Lint code**: `uv run ruff check .`
- **Định dạng code**: `uv run ruff format .`
- **Kiểm tra kiểu dữ liệu**: `uv run ty check .`

### 3. Chạy Tests & SQA Report
Dự án được cấu hình sẵn file kịch bản SQA tự động để đánh giá chất lượng phần mềm (Linting + Testing Coverage).
Để chạy và lấy minh chứng, chạy lệnh sau:
```bash
chmod +x check_sqa.sh
./check_sqa.sh
```

Hoặc chạy các lệnh thủ công:
```bash
uv run pytest --cov=app tests/
```

## 📂 Cấu trúc thư mục

- `main.py`: Điểm khởi đầu của ứng dụng.
- `tests/`: Chứa các bộ kiểm thử tự động.
- `pyproject.toml`: Cấu hình dự án và dependencies.
- `.gitignore`: Cấu hình các file bị loại bỏ khỏi Git.

## 📝 Chức năng chính
- Cung cấp RESTful APIs cho Frontend.
- Quản lý dữ liệu người dùng, thiết bị IoT (Plant Code), cảnh giới, bảng xếp hạng.
- Xử lý Telemetry Data từ thiết bị IoT.
- Tính toán Tu Vi (EXP) theo logic đã được định nghĩa.
- Hệ thống Admin quản trị.

---

## 🔐 Hướng Dẫn Tích Hợp Đăng Nhập Google (Dành Cho Frontend)

Backend của Mộc Đạo Tu Tiên cung cấp luồng đăng nhập qua Google OAuth2. Frontend **không cần** chuyển hướng trang web mà sử dụng trực tiếp Popup của Google Identity SDK.

### 1. Cài đặt & Cấu hình FE
- Cài đặt thư viện: `npm install @react-oauth/google`
- Đặt `GOOGLE_CLIENT_ID` vào `.env` của Frontend (lấy Client ID từ Backend).

### 2. Code Tích Hợp (React)
```javascript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

function App() {
  const handleLoginSuccess = async (credentialResponse) => {
    // Gửi ID Token từ Google xuống API của Backend
    const response = await axios.post('http://localhost:8000/api/auth/google', {
      id_token: credentialResponse.credential
    });
    
    // Lưu Access Token nội bộ
    localStorage.setItem('access_token', response.data.access_token);
  };

  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <GoogleLogin onSuccess={handleLoginSuccess} />
    </GoogleOAuthProvider>
  );
}
```

### 3. Gọi các API khác sau khi đăng nhập
Frontend cần đính kèm JWT Token vào Header của mọi request:
```javascript
axios.get('http://localhost:8000/api/auth/me', {
  headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
});
```

*Lưu ý: Nếu gặp lỗi 400 (redirect_uri_mismatch) khi đang chạy localhost, hãy báo Backend thêm địa chỉ localhost của Frontend vào danh sách "Authorized JavaScript origins" trên Google Cloud Console.*
