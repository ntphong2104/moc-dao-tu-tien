# KỊCH BẢN THUYẾT TRÌNH DEEP-DIVE: UC-07 VÀ UC-06
*(Dành riêng cho Phong - Bám sát kỹ thuật và Code thực tế)*

Kịch bản này đi sâu vào **"Under the hood" (Bản chất kỹ thuật)**. Giáo viên rất thích nghe những từ khóa kỹ thuật này vì nó chứng minh bạn thực sự hiểu code chạy như thế nào.

---

## MỞ MÀN
"Chào thầy và các bạn, nối tiếp phần của Hoàng, em là Phong, phụ trách việc thiết lập **Trái tim Bảo mật** của hệ thống thông qua 2 Use Case cốt lõi: [UC-07] Đăng nhập Xác thực và [UC-06] Giám sát Admin. 
Vì đây là 2 tính năng nhạy cảm nhất, em không test Hộp đen trên giao diện Web mà áp dụng **Kiểm thử Hộp trắng (White-box)** kết hợp **Kiểm thử Bảo mật (Security Testing)**."

---

## PHẦN 1: [UC-07] ĐĂNG NHẬP VÀ XÁC THỰC (AUTHENTICATION)

**🗣️ Lời thoại thuyết trình:**
"Đầu tiên là tính năng Đăng nhập (UC-07). Dự án của tụi em sử dụng chuẩn **Google OAuth2** kết hợp cấp phát **JWT (JSON Web Token)** để quản lý phiên đăng nhập. Mã JWT được Backend tự ký bằng thuật toán mã hóa `HS256` với Secret Key ẩn trong máy chủ.

**Vậy em đã test nó như thế nào?**
Thay vì lên Web bấm nút Đăng nhập bằng Google (mất thời gian và phụ thuộc mạng), em sử dụng framework `pytest` kết hợp với kỹ thuật **Mocking**. 
*   **Thứ nhất (Mock DB):** Em tự viết một cái Database giả lập trên RAM (`MockAsyncSession`) để cắt đứt kết nối với Database thật. Điều này giúp Unit Test chạy cực nhanh và độc lập.
*   **Thứ hai (Test sinh Token):** Em viết code tự động gọi hàm `create_access_token`. Sau đó dùng chính thư viện mã hóa giải mã ngược lại cái Token đó ra để kiểm tra xem bên trong có chứa đúng ID và Role (Quyền) của người dùng hay không.
*   **Thứ ba (Test lỗ hổng bảo mật):** Em tạo ra một ca kiểm thử giả lập một cái Token đã hết hạn (Expired). Kết quả là hàm `decode_token` ngay lập tức ném ra lỗi. Điều này chứng minh hệ thống sẽ không bao giờ chấp nhận các Token cũ do Hacker chôm được."

---

## PHẦN 2: [UC-06] GIÁM SÁT ADMIN VÀ LỖ HỔNG PHÂN QUYỀN

**🗣️ Lời thoại thuyết trình:**
"Tiếp theo, em dùng chính cái Role (Quyền) được mã hóa trong JWT đó để giải quyết bài toán của **[UC-06] Giám sát Admin**.

Mối nguy hiểm lớn nhất của các hệ thống có Admin là lỗ hổng **Broken Access Control (Nằm Top 1 OWASP)** - tức là User thường vượt rào làm chuyện của Admin.
Về mặt công nghệ, em sử dụng tính năng **Dependency Injection** của framework FastAPI để tạo ra một cái khiên chắn tên là `get_admin_user`. Bất kỳ API nào của Admin cũng phải đi qua cái khiên này.

**Cách em test lỗ hổng này:**
Trong Unit Test, em tạo một Token hợp lệ nhưng bên trong gắn `role = "user"`. Sau đó em gọi lệnh truy cập vào API Xóa Thiết Bị của Admin. 
Đúng như thiết kế của tính năng, bài test tự động nhận về một ngoại lệ (Exception) với mã lỗi **HTTP 403 Forbidden (Cấm truy cập)**. 
*(Hành động: Bạn có thể bật Postman lên bắn Token user thường vào API Admin để show dòng chữ 403 Forbidden đỏ chót ra).*

Điều này minh chứng rằng: Kể cả khi Frontend có lỡ làm lộ nút bấm Xóa, hay Hacker tìm được đường link API của Admin, thì ngay tại tầng lõi Backend, dữ liệu đã bị chặn đứng hoàn toàn."

---

## CHỐT LẠI KẾT QUẢ ĐẠT ĐƯỢC
**🗣️ Lời thoại thuyết trình:**
"Bằng việc tuân thủ chặt chẽ triết lý *Shift-Left Testing (Test từ sớm)*, em đã tự tay viết **128 bài Unit Test** rải đều khắp hệ thống. 
*(Hành động: Trình chiếu Terminal lệnh pytest lên)*

Thưa thầy, kết quả là toàn bộ các file xử lý nghiệp vụ, đặc biệt là cụm Phân quyền Auth và Admin của UC-06 và UC-07 do em phụ trách đã đạt **Độ phủ mã (Code Coverage) 100% tuyệt đối**. Tổng toàn bộ dự án đạt Coverage **99%**. Đây là minh chứng rõ nhất cho chất lượng phần mềm được kiểm soát từ tận gốc rễ ạ!
Phần cốt lõi đã an toàn, em xin nhường lời cho bạn Đạt lên trình bày về luồng phân tích biểu đồ ạ."

---

## TỪ KHÓA BỎ TÚI NẾU BỊ HỎI VẶN:
1. **JWT (JSON Web Token):** Cấu tạo gồm 3 phần (Header, Payload, Signature). Nhóm dùng JWT vì nó Stateless (Không cần lưu session vào RAM server), giúp server chạy nhanh hơn.
2. **Kỹ thuật Mocking là gì?** Là tạo ra đối tượng giả (Fake Object). Ví dụ test API Login mà gọi DB thật thì chậm, nên tự fake một cái DB trên RAM trả về kết quả luôn để tiết kiệm thời gian test.
3. **Tại sao Dependency Injection an toàn?** Vì nó ép mọi request muốn vào API thì PHẢI chạy qua cái hàm kiểm tra quyền trước. Dev không thể "quên" check quyền được.
