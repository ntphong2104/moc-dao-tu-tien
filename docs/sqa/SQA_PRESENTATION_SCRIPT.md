# KỊCH BẢN THUYẾT TRÌNH DEEP-DIVE: UC-07 VÀ UC-06
*(Dành riêng cho Phong - Bám sát kỹ thuật và Code thực tế)*

Kịch bản này đi sâu vào **"Under the hood" (Bản chất kỹ thuật)**, tuân thủ đúng yêu cầu nhấn mạnh kỹ thuật test của nhóm và bổ sung lý thuyết tính Code Coverage.

---

## MỞ MÀN
"Chào thầy và các bạn, nối tiếp phần của Hoàng, em là Phong, phụ trách việc thiết lập **Trái tim Bảo mật** của hệ thống thông qua 2 Use Case cốt lõi: [UC-07] Đăng nhập Xác thực và [UC-06] Giám sát Admin. 
Vì đây là 2 tính năng nhạy cảm nhất, em không test Hộp đen trên giao diện Web mà áp dụng **Kiểm thử Hộp trắng (White-box)** kết hợp **Kiểm thử Bảo mật (Security Testing)**."

---

## PHẦN 1: [UC-07] ĐĂNG NHẬP VÀ XÁC THỰC (AUTHENTICATION)

**🗣️ Lời thoại thuyết trình:**
"Đầu tiên là tính năng Đăng nhập (UC-07). Dự án của tụi em sử dụng chuẩn **Google OAuth2** kết hợp cấp phát **JWT (JSON Web Token)** để quản lý phiên đăng nhập. Mã JWT được Backend tự ký bằng thuật toán mã hóa `HS256`.

**👉 ĐỂ KIỂM THỬ USE CASE NÀY, EM DÙNG KỸ THUẬT MOCKING VÀ WHITE-BOX:**
Thay vì lên Web bấm nút Đăng nhập (mất thời gian và phụ thuộc mạng), em sử dụng framework `pytest` kết hợp với kỹ thuật **Mocking**. 
*   **Em test bằng Mock DB:** Em tự viết một cái Database giả lập trên RAM (`MockAsyncSession`) để cắt đứt kết nối với Database thật. Điều này giúp Unit Test chạy cực nhanh và độc lập.
*   **Em test sinh Token:** Code tự động gọi hàm sinh Token, sau đó em dùng chính thư viện mã hóa giải mã ngược lại để Assert (kỳ vọng) xem bên trong có chứa đúng ID và Role (Quyền) hay không.
*   **Em test lỗ hổng bảo mật:** Ca kiểm thử giả lập một cái Token đã hết hạn (Expired). Kết quả là hàm `decode_token` ngay lập tức ném ra lỗi. Chứng tỏ Use Case này chặn đứng hoàn toàn các Token cũ do Hacker chôm được."

> 💻 **HÀNH ĐỘNG DEMO TRỰC TIẾP (UC-07):**
> Vừa dứt câu, gõ lệnh: `pytest tests/test_auth_service.py -v`

---

## PHẦN 2: [UC-06] GIÁM SÁT ADMIN VÀ LỖ HỔNG PHÂN QUYỀN

**🗣️ Lời thoại thuyết trình:**
"Tiếp theo là **[UC-06] Giám sát Admin**. Mối nguy hiểm lớn nhất của các hệ thống có Admin là lỗ hổng **Broken Access Control (Nằm Top 1 OWASP)** - tức là User thường vượt rào làm chuyện của Admin.
Về mặt công nghệ, em dùng tính năng **Dependency Injection** của framework FastAPI để tạo ra một cái khiên chắn tên là `get_admin_user`. Bất kỳ API nào của Admin cũng phải đi qua cái khiên này.

**👉 ĐỂ KIỂM THỬ USE CASE NÀY, EM DÙNG KỸ THUẬT SECURITY TESTING VÀ EXCEPTION HANDLING:**
Cách test của em là: Trong Unit Test, em tạo một Token hợp lệ nhưng bên trong gắn `role = "user"`. Sau đó em gọi lệnh truy cập thẳng vào API Xóa Thiết Bị của Admin (Bỏ qua giao diện Web). 
Đúng như thiết kế, bài test tự động nhận về một ngoại lệ với mã lỗi **HTTP 403 Forbidden (Cấm truy cập)**. 

Điều này minh chứng: Use Case này đã được bảo vệ hoàn hảo. Dù Frontend có làm lộ nút bấm Xóa, hay Hacker mò được đường link API, thì tầng lõi Backend vẫn chặn đứng dữ liệu hoàn toàn."

> 💻 **HÀNH ĐỘNG DEMO TRỰC TIẾP (UC-06):**
> Vừa dứt câu, gõ lệnh: `pytest tests/test_dependencies.py -v`

---

## CHỐT LẠI KẾT QUẢ ĐẠT ĐƯỢC
**🗣️ Lời thoại thuyết trình:**
"Bằng việc tuân thủ chặt chẽ triết lý *Shift-Left Testing (Test từ sớm)*, em đã tự tay viết **128 bài Unit Test** rải đều khắp hệ thống. 
*(Hành động: Gõ lệnh `pytest --cov=app --cov-branch --cov-report=term-missing` để show ra bảng 100%)*.

Thưa thầy, kết quả là toàn bộ lõi xử lý nghiệp vụ `app/` của Backend (đặc biệt là cụm Phân quyền Auth và Admin do em phụ trách) đã được quét với tiêu chuẩn khắt khe nhất là **Độ phủ nhánh (Branch Coverage)**. Hệ thống ghi nhận **1247 dòng lệnh** và **170 nhánh if/else** đều đạt **Độ phủ 100% tuyệt đối, không trượt một nhánh nào**. Đây là minh chứng rõ nhất cho chất lượng phần mềm được kiểm soát từ gốc! Em xin nhường lời cho bạn Đạt ạ."

---

## PHỤ LỤC: CÂU HỎI BẢO VỆ VÀ KIẾN THỨC CỐT LÕI (TRẢ LỜI THẦY)

Dưới đây là phần kiến thức trang bị để bạn tự tin trả lời khi bị thầy phản biện:

**1. Thầy hỏi: "Cách tính Độ phủ mã (Code Coverage) của em là như thế nào? Số 100% đó ở đâu ra?"**
*   **Trả lời:** *"Dạ thưa thầy, công cụ `pytest-cov` đo lường thông qua 2 chỉ số: Độ phủ lệnh (Statement Coverage) và Độ phủ nhánh (Branch Coverage). Như trên báo cáo thầy thấy, lõi Backend của nhóm em có 1247 dòng lệnh và 170 nhánh rẽ (if/else, try/except). Khi chạy 128 bài Unit Test, các hàm test đã kích hoạt và chạy qua đầy đủ 100% các dòng lệnh và nhánh rẽ này mà không bỏ sót bất kỳ luồng nào ạ."*

**2. Thầy hỏi: "Thế Độ phủ nhánh (Branch Coverage) khác gì Độ phủ lệnh bình thường?" (Câu hỏi 10 điểm)**
*   **Trả lời:** *"Dạ thưa thầy! Đo lường nhánh (Branch Coverage) khắt khe hơn rất nhiều. Công thức là: **(Số nhánh rẽ if/else đã chạy / Tổng số nhánh trong code) * 100%**. 
Ví dụ: Khi viết API phân quyền có lệnh `if (role != admin)`, tụi em bắt buộc phải viết 2 bài test riêng biệt: Một bài cung cấp đúng quyền Admin để đi tiếp, và một bài cố tình cung cấp quyền User thường để chui vào nhánh ném lỗi `HTTP 403 Forbidden`. Chỉ khi cả 2 nhánh (True và False) đều được mã test quét qua thì công cụ mới đánh giá là phủ 100% nhánh code đó. Việc này giúp nhóm bịt kín mọi lỗ hổng logic ngầm ạ."*

**3. Thầy hỏi: "Tại sao em chỉ test thư mục `app/` (lệnh `--cov=app`) mà không test toàn bộ dự án?"**
*   **Trả lời:** *"Dạ thưa thầy, thư mục `app/` chứa toàn bộ 100% logic nghiệp vụ của Backend nên em dồn toàn lực phủ 100% nhánh vào đây. Những file nằm ngoài như `main.py` (chỉ chứa lệnh khởi chạy server uvicorn) thuộc về Môi trường vận hành (Operation Environment), việc test nó không mang lại giá trị SQA mà chỉ tốn tài nguyên vô ích ạ."*

**4. Thầy hỏi: "Lỗi Broken Access Control ở UC-06 là gì?"**
*   **Trả lời:** *"Dạ là lỗ hổng khi hệ thống quên không kiểm tra quyền của người dùng (vd: quên check `role == admin`). Người dùng A có thể dùng API thao tác sửa dữ liệu của Admin. Đây là lỗ hổng bảo mật phổ biến nhất thế giới, nằm Top 1 của bảng xếp hạng **OWASP Top 10** ạ."*
