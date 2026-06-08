# Cẩm Nang Ôn Tập SQA Chuyên Sâu Mảng Backend (Cho Buổi Bảo Vệ)

Tài liệu này tổng hợp toàn bộ các khái niệm SQA (Đảm bảo chất lượng phần mềm) chuyên sâu áp dụng riêng cho tầng Backend. Bạn hãy nắm vững các khái niệm này để bảo vệ đồ án một cách xuất sắc.

---

## 1. Phương pháp Kiểm thử Lõi (Testing Methods)

### A. White-box Testing (Kiểm thử Hộp trắng)
Khác với Tester Hộp đen chỉ nhìn vào màn hình bấm giao diện, Tester Backend dùng Hộp trắng để "soi" trực tiếp cấu trúc mã nguồn.
*   **Định nghĩa:** Phương pháp kiểm tra cấu trúc bên trong (internal logic), thuật toán và luồng dữ liệu của code.
*   **Unit Test (Kiểm thử đơn vị):** Viết các đoạn mã độc lập (dùng `pytest` trong Python, `Jest` trong Node.js) để gọi trực tiếp các hàm (functions) của Backend xem đầu vào/đầu ra có đúng thiết kế không, mà không cần qua giao diện web.
*   **Độ phủ mã (Code Coverage):** Thước đo xem có bao nhiêu phần trăm số dòng code đã được Unit Test chạy qua. Thường chia làm các mức độ:
    *   *Statement Coverage:* Độ phủ câu lệnh.
    *   *Branch Coverage:* Độ phủ nhánh logic (`if/else`). VD: Nếu có lệnh `if A else B`, test phải đủ 2 case đi vào cả A và B mới tính là 100% Branch Coverage.
*   **Tại sao không cần 100% Coverage?** Việc cố đạt 100% gây lãng phí thời gian vào các tệp cấu hình (Config) ít quan trọng. Chuẩn ngành (Industry Standard) thường chỉ yêu cầu mức **80-85%** và áp dụng chiến lược **Risk-based Testing** (Tập trung test kỹ các module cốt lõi như Thanh toán, Phân quyền, Tính điểm).

### B. Integration Testing (Kiểm thử Tích hợp)
*   **Định nghĩa:** Kiểm tra xem các module trong Backend, hoặc Backend với hệ thống bên ngoài, có "nói chuyện" được với nhau không.
*   **Trong Backend, Integration Test thường test cái gì?**
    *   Backend ↔ Database (Kiểm tra câu lệnh SQL có lưu đúng dữ liệu không).
    *   Backend ↔ IoT/Phần cứng (Kiểm tra broker MQTT có nhận/gửi đúng gói tin không).

---

## 2. Tiêu chuẩn ISO 25010 Áp Dụng Cho Backend

ISO 25010 là bộ tiêu chuẩn quốc tế về chất lượng phần mềm. 4 tiêu chí cốt lõi thường bị hội đồng vặn hỏi nhất đối với Backend là:

### A. Security (Bảo mật)
Hệ thống phải có chốt chặn an toàn bất chấp Frontend có lỏng lẻo hay không.
*   **OWASP Top 10:** Danh sách 10 lỗi bảo mật nguy hiểm nhất. Ở Backend hay dính:
    *   **Broken Access Control:** Lỗi phân quyền. (VD: API dành cho Admin nhưng không kiểm tra Token `role`, dẫn đến User thường gọi thẳng URL qua Postman để phá hoại).
    *   **Injection (SQLi):** Không lọc đầu vào, bị tiêm mã độc SQL vào Database. Dùng ORM (như SQLAlchemy) là cách phòng chống tốt nhất.
*   **Secure by Design:** Kiến trúc được thiết kế an toàn ngay từ đầu (bọc Middleware, mã hóa mật khẩu bằng `bcrypt`) chứ không đợi tới lúc có lỗi mới chắp vá.

### B. Performance Efficiency (Hiệu năng)
*   **Lỗi N+1 Query:** Lỗi kinh điển của Backend khi truy vấn Database. (VD: Lấy 100 user, lại chạy thêm 100 vòng lặp SQL để lấy tên cây của từng user -> Gây nghẽn mạng). Khắc phục bằng *Eager Loading* (`JOIN` bảng).
*   **Nghẽn RAM (Buffer Overflow/Out of Memory):** Nếu API cho phép query lịch sử từ 10 năm trước mà Backend không chặn (Phân vùng tương đương/Giá trị biên) thì hệ thống sẽ kéo hàng triệu dòng Data lên RAM, gây sập server (Crash).

### C. Reliability (Độ tin cậy)
*   **Tính toàn vẹn dữ liệu (Data Integrity):** Ngăn chặn lưu dữ liệu rác. Bắt buộc tạo ràng buộc (Constraints) ở thẳng Database như `UNIQUE`, `NOT NULL`, `Foreign Key`. Dù code API có lỗi thì Database vẫn chặn được.
*   **Khả năng chịu lỗi (Fault Tolerance):** Khi kết nối Database đứt, hoặc phần cứng gửi thông số ảo (âm 5%), Backend không được phép "chết trân" (Crash) mà phải báo lỗi duyên dáng (Graceful Degradation) bằng mã lỗi `HTTP 500/400`.

### D. Functional Suitability (Tính phù hợp tính năng)
*   **Tính chính xác của chức năng (Functional Correctness):** Đây là tiêu chí cơ bản nhất. Backend phải tính toán đúng logic nghiệp vụ. (VD: Cây đủ 100 điểm thì phải thăng cấp từ Phàm Mộc lên Linh Mộc, tính sai điểm Tu Vi là vi phạm tiêu chí này).
*   **Cách kiểm thử:** Áp dụng Hộp đen (Bảng quyết định - Decision Table) để liệt kê mọi quy tắc kinh doanh, kết hợp với Hộp trắng (Unit Test) để ép hàm tính toán chạy qua các trường hợp logic phức tạp.

---

## 3. Tư duy SQA Hiện Đại (Mindset)

Nếu bạn nêu được các thuật ngữ này, giáo viên sẽ đánh giá tư duy kỹ sư của bạn rất cao:

### A. TDD (Test-Driven Development)
*   Phát triển phần mềm hướng kiểm thử. Lập trình viên viết *Kịch bản Test (Unit Test)* TRƯỚC, nó sẽ báo đỏ (Fail) do chưa có code thật. Sau đó mới viết *Code API* sao cho Test báo xanh (Pass).
*   Lợi ích: Code rất sạch, dễ bảo trì, và không bị dư thừa logic (chỉ viết code vừa đủ để qua bài test).

### B. Shift-Left Testing (Kiểm thử Dịch Trái)
*   Trong chu trình phát triển (SDLC) vẽ từ Trái sang Phải: *Lấy Yêu cầu -> Thiết kế -> Code -> Test -> Triển khai*.
*   Cách cũ: Đợi đến khâu cuối cùng (bên Phải) mới Test. Rất tốn kém nếu phát hiện sai kiến trúc từ đầu.
*   *Shift-Left:* Kéo khâu kiểm thử về "Bên Trái". Tức là vừa Code xong dòng nào là viết Unit Test dòng đó. Kiểm tra bảo mật ngay từ lúc vẽ lược đồ Backend (Secure by Design).

### C. CI/CD (Continuous Integration / Continuous Deployment)
*   **CI (Tích hợp liên tục):** Mỗi khi lập trình viên gõ code xong và đẩy lên Git (Push/Pull Request), hệ thống (như GitHub Actions) sẽ tự động chạy toàn bộ bộ Test (Automated Testing). Chỉ khi nào tất cả 84% Test Case đều PASS (màu xanh) thì mới cho phép gộp code vào nhánh chính (`develop/main`).
*   Đây là "Vòng kim cô" tự động của quy trình SQA hiện đại, thay thế cho con người phải ngồi chạy test thủ công.
