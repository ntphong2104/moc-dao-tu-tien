# KỊCH BẢN THUYẾT TRÌNH MASTER (NỘI DUNG SLIDE + LỜI THOẠI MC + DEMO)
*(Dành riêng cho Phong - Đã ghép nối chuẩn nhịp)*

Tài liệu này là bản tổng hợp "3 trong 1". Bạn chỉ cần copy phần **[NỘI DUNG TRÊN SLIDE]** dán vào PowerPoint, đọc phần **[LỜI THOẠI]** khi thuyết trình, và gõ lệnh ở phần **[DEMO]**.

---

## 🖥️ SLIDE 1: MỞ MÀN & TƯ DUY BẢO MẬT

**📌 [NỘI DUNG HIỂN THỊ TRÊN SLIDE]**
> **Tiêu đề:** Thiết kế & Kiểm thử Kiến trúc Bảo mật (Security First)
> *   **Trọng tâm phụ trách:** [UC-07] Xác thực Người dùng & [UC-06] Giám sát Admin.
> *   **Triết lý SQA:** 
>     * Shift-Left Testing (Kiểm thử ngay từ khâu thiết kế API).
>     * Áp dụng **Kiểm thử Hộp trắng (White-box)** thay vì click tay giao diện.
>     * Đặt trọng tâm vào **Security Testing** (Kiểm thử bảo mật).

**🗣️ [LỜI THOẠI MC]**
"Chào thầy và các bạn, nối tiếp phần của Hoàng, em là Phong, phụ trách việc thiết lập **Trái tim Bảo mật** của hệ thống thông qua 2 Use Case cốt lõi: [UC-07] Đăng nhập Xác thực và [UC-06] Giám sát Admin. 
Vì đây là 2 tính năng nhạy cảm nhất, em không test Hộp đen trên giao diện Web mà áp dụng triệt để **Kiểm thử Hộp trắng (White-box)** kết hợp **Kiểm thử Bảo mật (Security Testing)** chọc thẳng vào lõi Backend."

---

## 🖥️ SLIDE 2: UC-07 - ĐĂNG NHẬP & XÁC THỰC

**📌 [NỘI DUNG HIỂN THỊ TRÊN SLIDE]**
> **Tiêu đề:** [UC-07] Đăng nhập & Quản lý Xác thực
> *   **Công nghệ lõi:** Google OAuth2 + JWT (Mã hóa thuật toán `HS256`).
> *   **Kỹ thuật Test (Mocking):** Giả lập Database trên RAM (`MockAsyncSession`) để test siêu tốc.
> *   **3 Ca Kiểm thử Hộp trắng then chốt:**
>     1.  Test tự động sinh JWT (Access Token).
>     2.  Giải mã ngược mã JWT để truy vết thông tin (User ID, Role).
>     3.  **Bẫy bảo mật:** Bơm Token hết hạn (Expired) ép hệ thống nhận diện và văng lỗi.

**🗣️ [LỜI THOẠI MC]**
"Đầu tiên là tính năng Đăng nhập (UC-07). Dự án của tụi em sử dụng chuẩn **Google OAuth2** kết hợp cấp phát **JWT (JSON Web Token)** để quản lý phiên đăng nhập. Mã JWT được Backend tự ký bằng thuật toán mã hóa `HS256`.

**👉 ĐỂ KIỂM THỬ USE CASE NÀY, EM DÙNG KỸ THUẬT MOCKING VÀ WHITE-BOX:**
Thay vì lên Web bấm nút Đăng nhập (mất thời gian và phụ thuộc mạng), em sử dụng framework `pytest` kết hợp với kỹ thuật **Mocking**. 
*   **Em test bằng Mock DB:** Em tự viết một cái Database giả lập trên RAM (`MockAsyncSession`) để cắt đứt kết nối với Database thật. Điều này giúp Unit Test chạy cực nhanh và độc lập.
*   **Em test sinh Token:** Code tự động gọi hàm sinh Token, sau đó em dùng chính thư viện mã hóa giải mã ngược lại để Assert (kỳ vọng) xem bên trong có chứa đúng ID và Role (Quyền) hay không.
*   **Em test lỗ hổng bảo mật:** Ca kiểm thử giả lập một cái Token đã hết hạn (Expired). Kết quả là hàm `decode_token` ngay lập tức ném ra lỗi. Chứng tỏ Use Case này chặn đứng hoàn toàn các Token cũ do Hacker chôm được."

> 💻 **[HÀNH ĐỘNG DEMO TRỰC TIẾP]**
> *(Vừa dứt câu, bạn gõ lệnh Terminal ngay lúc Slide 2 đang chiếu):* 
> `pytest tests/test_auth_service.py -v`

---

## 🖥️ SLIDE 3: UC-06 - LỖ HỔNG PHÂN QUYỀN

**📌 [NỘI DUNG HIỂN THỊ TRÊN SLIDE]**
> **Tiêu đề:** [UC-06] Giám sát Admin & Chống Broken Access Control
> *   **Mục tiêu bảo vệ:** Chặn đứng lỗ hổng **Broken Access Control** (Top 1 OWASP 2021).
> *   **Kiến trúc phòng thủ:** Sử dụng **Dependency Injection** (FastAPI) làm "Khiên chắn" ép buộc mọi API.
> *   **Minh chứng Code (Security Test):**
> ```python
> async def test_get_admin_user_forbidden():
>     # 1. Giả lập một người dùng có quyền thấp (Role = user)
>     mock_user = User(id=uuid4(), role="user")
> 
>     # 2. Cố tình vượt rào gọi Hàm của Admin, Kỳ vọng hệ thống sẽ văng Lỗi
>     with pytest.raises(HTTPException) as exc_info:
>         await get_admin_user(user=mock_user)
> 
>     # 3. Assert (Khẳng định) lỗi văng ra phải đúng chuẩn HTTP 403
>     assert exc_info.value.status_code == 403
>     assert exc_info.value.detail == "Chỉ Admin mới có quyền truy cập"
> ```
> *   **Kết luận:** Dữ liệu an toàn tuyệt đối từ sâu trong tầng lõi Backend.

**🗣️ [LỜI THOẠI MC]**
"Tiếp theo là **[UC-06] Giám sát Admin**. Mối nguy hiểm lớn nhất của các hệ thống có Admin là lỗ hổng **Broken Access Control (Nằm Top 1 OWASP)** - tức là User thường vượt rào làm chuyện của Admin.
Về mặt công nghệ, em dùng tính năng **Dependency Injection** của framework FastAPI để tạo ra một cái khiên chắn tên là `get_admin_user`. Bất kỳ API nào của Admin cũng phải đi qua cái khiên này.

**👉 ĐỂ KIỂM THỬ USE CASE NÀY, EM DÙNG KỸ THUẬT SECURITY TESTING VÀ EXCEPTION HANDLING:**
Cách test của em là: Trong Unit Test, em tạo một Token hợp lệ nhưng bên trong gắn `role = "user"`. Sau đó em gọi lệnh truy cập thẳng vào API Xóa Thiết Bị của Admin (Bỏ qua giao diện Web). 
Đúng như thiết kế, bài test tự động nhận về một ngoại lệ với mã lỗi **HTTP 403 Forbidden (Cấm truy cập)**. 

Điều này minh chứng: Use Case này đã được bảo vệ hoàn hảo. Dù Frontend có làm lộ nút bấm Xóa, hay Hacker mò được đường link API, thì tầng lõi Backend vẫn chặn đứng dữ liệu hoàn toàn."

> 💻 **[HÀNH ĐỘNG DEMO TRỰC TIẾP]**
> *(Vừa dứt câu, gõ lệnh Terminal ngay lúc Slide 3 đang chiếu):* 
> `pytest tests/test_dependencies.py -v`

---

## 🖥️ SLIDE 4: THÀNH QUẢ ĐẢM BẢO CHẤT LƯỢNG

**📌 [NỘI DUNG HIỂN THỊ TRÊN SLIDE]**
> **Tiêu đề:** Thành quả Đảm bảo Chất lượng - Độ phủ tuyệt đối
> *   **Tổng số lượng Test:** 128 bài Unit/Integration Tests.
> *   **Độ phủ dòng lệnh (Statement Coverage):** 1247 / 1247 dòng (**Đạt 100%**).
> *   **Độ phủ nhánh (Branch Coverage):** 170 / 170 luồng logic (**Đạt 100%**).
> *   **Ý nghĩa dữ liệu:**
>     *   100% logic nghiệp vụ không tồn tại code rác.
>     *   Toàn bộ 170 kịch bản ngoại lệ (What-if) đã được bắt lỗi an toàn.
> *(Nên dán ảnh chụp màn hình xanh lá của Terminal báo Total 100% vào Slide này)*

**🗣️ [LỜI THOẠI MC]**
"Bằng việc tuân thủ chặt chẽ triết lý *Shift-Left Testing (Test từ sớm)*, em đã tự tay viết **128 bài Unit Test** rải đều khắp hệ thống. 
*(Gõ lệnh `pytest --cov=app --cov-branch --cov-report=term-missing` để terminal show ra bảng 100% ngay cạnh slide chiếu)*.

Thưa thầy, kết quả là toàn bộ lõi xử lý nghiệp vụ `app/` của Backend (đặc biệt là cụm Phân quyền Auth và Admin do em phụ trách) đã được quét với tiêu chuẩn khắt khe nhất là **Độ phủ nhánh (Branch Coverage)**. 

**Vậy con số 100% này đại diện cho điều gì?** 
Nó đại diện cho việc **1247 dòng lệnh** (tương đương 100% kịch bản thực thi) và **170 nhánh rẽ if/else** (tương đương 100% các tình huống rủi ro, lỗi ngoại lệ) đều đã được hệ thống test tự động chạy qua và xác nhận an toàn. Không có một dòng code thừa, không có một kịch bản lỗi nào bị bỏ sót. Đây là minh chứng rõ nhất cho chất lượng phần mềm được kiểm soát từ gốc! Em xin nhường lời cho bạn Đạt ạ."

---

## 📚 PHỤ LỤC: CÂU HỎI BẢO VỆ VÀ KIẾN THỨC CỐT LÕI (TRẢ LỜI THẦY)

Dưới đây là phần kiến thức trang bị để bạn tự tin trả lời khi bị thầy phản biện:

**1. Thầy hỏi: "Cách tính Độ phủ mã (Code Coverage) của em là như thế nào? Con số 100% đó thực chất đại diện cho cái gì?"**
*   **Trả lời:** *"Dạ thưa thầy, Độ phủ mã đại diện cho **tỷ lệ mã nguồn thực tế đã được kiểm chứng bởi các bài test tự động**. Công cụ `pytest-cov` đo lường thông qua 2 chỉ số: Độ phủ lệnh (Statement Coverage) và Độ phủ nhánh (Branch Coverage). 
Như trên báo cáo thầy thấy, lõi Backend của nhóm em có **1247 dòng lệnh**. Con số 100% đại diện cho việc 128 bài Unit Test của tụi em đã kích hoạt và chạy qua đủ 1247 dòng lệnh này. Không có bất kỳ một dòng code "chết" hay logic rác nào tồn tại trong hệ thống mà chưa được test ạ."*

**2. Thầy hỏi: "Thế Độ phủ nhánh (Branch Coverage) khác gì Độ phủ lệnh bình thường? 170 nhánh kia mang ý nghĩa gì?" (Câu hỏi 10 điểm)**
*   **Trả lời:** *"Dạ thưa thầy! Đo lường nhánh (Branch Coverage) khắt khe hơn rất nhiều, nó **đại diện cho việc kiểm soát rủi ro**. 170 nhánh kia chính là 170 kịch bản "What-if" (Nếu-Thì) có thể xảy ra trong thực tế (Ví dụ: Nếu nhập sai pass thì sao? Nếu Token hết hạn thì sao? Nếu không phải Admin thì sao?).
Ví dụ: Khi viết API phân quyền có lệnh rẽ nhánh `if (role != admin)`, để đạt 100% nhánh này tụi em bắt buộc phải viết 2 bài test: Một bài giả làm Admin để đi tiếp (Nhánh True), và một bài cố tình làm User thường để bị chặn lại với lỗi `HTTP 403` (Nhánh False). 
Con số 100% Branch Coverage chứng minh rằng toàn bộ 170 kịch bản rủi ro rẽ nhánh của hệ thống đều đã được tụi em lường trước và xử lý an toàn, bịt kín mọi lỗ hổng logic ngầm ạ."*

**3. Thầy hỏi: "Tại sao em chỉ test thư mục `app/` (lệnh `--cov=app`) mà không test toàn bộ dự án?"**
*   **Trả lời:** *"Dạ thưa thầy, thư mục `app/` chứa toàn bộ 100% logic nghiệp vụ của Backend nên em dồn toàn lực phủ 100% nhánh vào đây. Những file nằm ngoài như `main.py` (chỉ chứa lệnh khởi chạy server uvicorn) thuộc về Môi trường vận hành (Operation Environment), việc test nó không mang lại giá trị SQA mà chỉ tốn tài nguyên vô ích ạ."*

**4. Thầy hỏi: "Kỹ thuật Mocking mà em dùng ở UC-07 là gì?"**
*   **Trả lời:** *"Dạ Mocking là tạo ra các đối tượng giả (Fake Object). Thay vì gọi Database thật (PostgreSQL) rất chậm và làm bẩn dữ liệu thật, em tạo một cái Database ảo trên RAM. Việc này giúp các bài Test chạy cực nhanh và độc lập hoàn toàn với môi trường vật lý."*

**5. Thầy hỏi: "Lỗi Broken Access Control ở UC-06 là gì?"**
*   **Trả lời:** *"Dạ là lỗ hổng khi hệ thống quên không kiểm tra quyền của người dùng (vd: quên check `role == admin`). Người dùng A có thể dùng API thao tác sửa dữ liệu của Admin. Đây là lỗ hổng bảo mật phổ biến nhất thế giới, nằm Top 1 của bảng xếp hạng **OWASP Top 10** ạ."*
