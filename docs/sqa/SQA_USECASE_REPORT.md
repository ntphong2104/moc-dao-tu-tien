# BẢNG PHÂN CÔNG & BIỆN LUẬN LÝ DO KIỂM THỬ CHO 9 USE CASE

Báo cáo này giải trình với Hội đồng về việc phân bổ trọn vẹn **9 Use Case** của toàn bộ hệ thống cho 4 thành viên. Với mỗi Use Case, nhóm làm rõ: **Áp dụng kỹ thuật gì** và **TẠI SAO** lại chọn kỹ thuật đó.

---

## 1. VŨ CÔNG CHIẾN (Nhóm Khởi tạo & Dữ liệu gốc)
**Phụ trách 2 Use Case:** [UC-01] Liên kết chậu cây, [UC-08] Quản lý loại cây & Ngưỡng MT.

### [UC-01] Liên kết chậu cây
*   **Áp dụng:** Kỹ thuật Hộp đen - Bảng quyết định (Decision Table).
*   **TẠI SAO?** Chức năng liên kết là điểm chạm đầu tiên, đòi hỏi xử lý nhiều điều kiện logic đan chéo (Mã PIN đúng không? Thiết bị đã bị ai liên kết chưa?). Dùng Bảng quyết định giúp liệt kê mọi tổ hợp True/False một cách toán học, đảm bảo không bỏ sót bất kỳ luồng ngách (edge case) nào của nghiệp vụ. (Minh chứng: Nhờ thế đã bắt được lỗi thiếu bẫy `UNIQUE` ở Database gây lỗi 500).

### [UC-08] Quản lý loại cây & Ngưỡng Môi trường
*   **Áp dụng:** Hộp đen - Đoán lỗi (Error Guessing) & Phân tích quy tắc kinh doanh.
*   **TẠI SAO?** Người dùng (Admin) rất dễ cấu hình sai logic thực tế. Việc ép test các trường hợp "Ngưỡng Min lớn hơn Ngưỡng Max" giúp đảm bảo tính hợp lệ của dữ liệu gốc trước khi nạp vào hệ thống để đối chiếu.

---

## 2. NGUYỄN THANH PHONG (Nhóm Lõi Backend & Bảo mật)
**Phụ trách 2 Use Case:** [UC-07] Đăng nhập & Xác thực, [UC-06] Giám sát hệ thống Admin.

### [UC-07] Đăng nhập & Quản lý Tài khoản
*   **Áp dụng:** Kiểm thử Bảo mật (Security Testing) & Hộp trắng.
*   **TẠI SAO?** Đây là chốt chặn đầu tiên của toàn bộ hệ thống. Bắt buộc phải dùng test Hộp trắng để kiểm tra xem mật khẩu có bị lưu plaintext hay không, và cơ chế ký JWT Token có mã hóa đúng chuẩn mã hóa `bcrypt/HS256` không để chống lại lỗ hổng rò rỉ dữ liệu (OWASP).

### [UC-06] Giám sát hệ thống Admin
*   **Áp dụng:** Hộp trắng (Code Coverage) & Shift-Left Testing.
*   **TẠI SAO?** Bảo mật phân quyền không thể test từ UI (vì nút bấm của Admin đã bị ẩn với User thường). Bắt buộc phải viết code Unit Test gọi trực tiếp vào API Backend để đo Độ phủ mã (Coverage). (Minh chứng: Nhờ bypass UI, nhóm bắt được lỗi **Broken Access Control** khi API thiếu Middleware phân quyền Admin).

---

## 3. PHẠM TIẾN ĐẠT (Nhóm Dashboard & Gamification)
**Phụ trách 4 Use Case:** [UC-02] Trạng thái Dashboard, [UC-03] Xu hướng biểu đồ, [UC-04] So sánh xếp hạng, [UC-05] Chỉnh sửa hồ sơ.

### [UC-02] Xem trạng thái Dashboard & [UC-05] Chỉnh sửa hồ sơ cây
*   **Áp dụng:** Phân tích Giá trị biên (Boundary Value).
*   **TẠI SAO?** 
    *   Với UC-02: Dữ liệu nhận vào là các con số (Độ ẩm 0-100%). Test Giá trị biên (Biên -1%, 0%, 100%, 101%) là cách mạnh nhất để bắt lỗi thuật toán nội suy.
    *   Với UC-05: Đầu vào là chuỗi (String). Kỹ thuật Giá trị biên đặc biệt hiệu quả để bắt lỗi nhập quá 50 ký tự, tránh tình trạng Tràn bộ đệm (Buffer Overflow) hoặc vỡ Layout của UI.

### [UC-03] Theo dõi xu hướng biểu đồ History & [UC-04] Leaderboard
*   **Áp dụng:** Phân vùng tương đương (Equivalence Partitioning) & Kiểm thử Hiệu năng (Performance).
*   **TẠI SAO?** Vẽ biểu đồ yêu cầu truy vấn hàng chục ngàn dòng lịch sử từ Database. Việc dùng Phân vùng tương đương để chia các mốc thời gian (24h, 7 ngày, 30 ngày) giúp kiểm thử tải và Hiệu năng. (Minh chứng: Nhờ đó phát hiện được lỗi tràn RAM máy chủ khi có người cố tình nhập `period=365d` để truy vấn dữ liệu của cả 1 năm).

---

## 4. NGUYỄN HỮU NGỌC HOÀNG (Nhóm Tích hợp Thiết bị)
**Phụ trách 1 Use Case cốt lõi:** [UC-10] Gửi dữ liệu cảm biến (Firmware IoT).

### [UC-10] Gửi dữ liệu cảm biến từ phần cứng
*   **Áp dụng:** Kiểm thử Tích hợp (Integration Testing) & Đánh giá Độ tin cậy (Reliability).
*   **TẠI SAO?** Dữ liệu không sinh ra từ bàn phím mà từ môi trường vật lý (đất, nước, mạng WiFi chập chờn). Không thể test độc lập phần mềm mà bắt buộc phải test Tích hợp Hardware-Software. Tiêu chí **Reliability** là sinh mệnh của hệ thống IoT, buộc nhóm phải test việc "Rút điện WiFi" để kiểm chứng cơ chế *Retry* không mất dữ liệu của thiết bị. 
*   (Minh chứng: Khi ép cảm biến vào đất khô cong, nhóm bắt được lỗi hàm `map()` C++ trả về số âm -5% làm sập Backend, từ đó fix bằng hàm `constrain()`).
