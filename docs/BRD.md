# Business Requirements Document (BRD)
# Dự án: Mộc Đạo Tu Tiên (Flora Cultivation)

> **Phiên bản:** 3.1  
> **Ngày tạo:** 2026-04-09  
> **Cập nhật:** 2026-04-14

---

## 1. Mục tiêu dự án

Xây dựng một hệ thống IoT kết hợp Gamification, biến việc chăm sóc cây xanh tại nhà thành trải nghiệm "Tu Tiên" — nơi chất lượng chăm sóc cây ngoài đời thực được phản ánh qua điểm Tu Vi (EXP) và Cảnh Giới của cây.

## 2. Đối tượng người dùng

- **Người dùng cuối:** Người trồng cây tại nhà muốn có thêm động lực chăm sóc cây thông qua yếu tố game hóa.
- **Admin / Nhà vận hành:** Nhà phát triển hoặc quản trị viên chịu trách nhiệm vận hành, giám sát và cấu hình hệ thống.

## 3. Phạm vi dự án

### 3.1. Hệ thống Đo lường Môi trường
- Thu thập dữ liệu từ các cảm biến IoT gắn trên thiết bị để đo các chỉ số môi trường sống của cây.
- Phân loại chất lượng môi trường thành các mức, từ tốt đến nguy hiểm.
- Loại cảm biến và chỉ số cụ thể sẽ được quy định trong tài liệu kỹ thuật.

### 3.2. Hệ thống Tu Vi (Điểm EXP) & Cảnh Giới
- Điểm Tu Vi tích lũy liên tục theo chu kỳ, phản ánh chất lượng chăm sóc cây.
- Môi trường tốt → cộng điểm; môi trường xấu/nguy hiểm → trừ điểm.
- So sánh dữ liệu thực tế với ngưỡng lý tưởng theo loại cây.
- Khi đạt đủ Tu Vi, cây **đột phá Cảnh Giới** lên bậc cao hơn — tạo mục tiêu ngắn hạn và động lực cho người dùng. Các mốc cảnh giới cụ thể được định nghĩa trong tài liệu kỹ thuật.

### 3.3. Dashboard (Giao diện trạng thái)
- Hiển thị chỉ số môi trường hiện tại từ các cảm biến.
- Hiển thị đánh giá chất lượng môi trường (trực quan bằng màu sắc, icon).
- Hiển thị tổng điểm Tu Vi và Cảnh Giới hiện tại của cây.
- Hiển thị thanh tiến trình tới cảnh giới tiếp theo.

### 3.4. Lịch sử & Biểu đồ xu hướng
- Hiển thị biểu đồ xu hướng các chỉ số môi trường trong khoảng thời gian gần nhất.
- Đánh dấu ngưỡng lý tưởng trên biểu đồ để người dùng dễ so sánh.
- Giúp người dùng nhận ra xu hướng (cây đang tốt lên hay xấu đi) và tác động sau khi điều chỉnh.


### 3.5. Hồ sơ cây & Liên kết chậu cây
- Người dùng liên kết chậu cây với tài khoản qua **Plant Code** (in trên thiết bị) hoặc tự động sinh mã qua **Tự cấp mã nạp mạch (DIY Provisioning)**.
- **Hỗ trợ Đa chậu (Multi-plant):** Một người dùng có thể liên kết và quản lý đồng thời nhiều chậu cây.
- Sau khi liên kết, người dùng đặt tên cho cây và chọn loại cây.
- Người dùng có thể thay đổi thông tin cây (tên, loại cây) sau khi liên kết.
- Mỗi tài khoản quản lý **1 chậu cây**.

### 3.6. Định danh & Xác thực
- Đăng nhập bằng **tài khoản Google**.
- Ghi nhớ phiên đăng nhập.

### 3.7. Bảng xếp hạng (Leaderboard)
- Hiển thị bảng xếp hạng các cây có Tu Vi cao nhất trong hệ thống.
- Tạo yếu tố cạnh tranh nhẹ giữa các người dùng, thúc đẩy động lực chăm sóc cây.

### 3.8. Bảng điều khiển Admin (Admin Dashboard)
- Tổng quan toàn hệ thống: số lượng người dùng, thiết bị đang hoạt động, thiết bị offline, tổng số cây được liên kết.
- Biểu đồ thống kê: số người dùng mới theo ngày/tuần, tỷ lệ thiết bị online/offline, phân bố Cảnh Giới của tất cả cây trong hệ thống.

### 3.9. Quản lý Thiết bị IoT (Device Management)
- Xem danh sách tất cả thiết bị, trạng thái kết nối (online/offline), lần gửi dữ liệu cuối.
- Vô hiệu hóa thiết bị bất thường hoặc bị lỗi.

### 3.10. Quản lý Loại cây & Ngưỡng lý tưởng (Plant Profile Management)
- CRUD (Thêm/Sửa/Xóa) các loại cây được hỗ trợ trong hệ thống.
- Cấu hình ngưỡng lý tưởng (nhiệt độ, độ ẩm, ánh sáng…) cho từng loại cây — thay vì hard-code trong mã nguồn.
- Thay đổi có hiệu lực ngay mà không cần triển khai lại hệ thống.

### 3.11. Cấu hình Tu Vi & Cảnh Giới (EXP & Rank Configuration)
- Cấu hình hệ số cộng/trừ điểm Tu Vi theo mức môi trường.
- Cấu hình các mốc Tu Vi cần thiết để đột phá từng Cảnh Giới.
- Thay đổi có hiệu lực ngay mà không cần cập nhật mã nguồn.


## 4. Ràng buộc & Giả định

| Hạng mục | Nội dung |
|---|---|
| Phần cứng | Thiết bị IoT cắm trực tiếp vào chậu cây thật |
| Loại cây | Cây tuổi thọ dài (Kim Tiền, Lưỡi Hổ…) |
| Phạm vi | 1 tài khoản — 1 chậu cây |

## 5. Tiêu chí chấp nhận (Acceptance Criteria)

### Người dùng cuối
- Cảm biến đo được các chỉ số môi trường và gửi dữ liệu liên tục lên hệ thống.
- Hệ thống phân loại đúng chất lượng môi trường theo ngưỡng của loại cây.
- Điểm Tu Vi được cộng/trừ chính xác theo chất lượng môi trường mỗi chu kỳ.
- Cây tự động đột phá Cảnh Giới khi đạt đủ Tu Vi.
- Dashboard hiển thị đầy đủ: chỉ số, đánh giá, Tu Vi, Cảnh Giới, tiến trình, và biểu đồ xu hướng.
- Người dùng đăng nhập Google, liên kết chậu cây, đặt tên và chọn loại cây thành công.
- Người dùng có thể thay đổi thông tin cây sau khi liên kết.
- Bảng xếp hạng hiển thị đúng thứ tự Tu Vi của các chậu cây.

### Admin / Nhà vận hành
- Admin Dashboard hiển thị đúng số liệu tổng quan (người dùng, thiết bị, cây).
- Admin xem được danh sách thiết bị và trạng thái kết nối realtime.
- Admin thêm/sửa/xóa loại cây và ngưỡng lý tưởng thành công, thay đổi có hiệu lực ngay.
- Admin cấu hình được hệ số Tu Vi và mốc Cảnh Giới mà không cần sửa mã nguồn.

## 6. Ngoài phạm vi (Out of Scope)

Các tính năng sau **không** nằm trong phiên bản này:

- Quản lý nhiều chậu cây trên một tài khoản
- Thông báo đẩy (Push notification) ra ngoài ứng dụng
- Điều khiển tự động (tự tưới nước, tự bật đèn)
- Hỗ trợ đa ngôn ngữ

## 7. Bảng thuật ngữ (Glossary)

| Thuật ngữ | Giải thích |
|---|---|
| **Tu Vi (EXP)** | Điểm kinh nghiệm tích lũy, phản ánh chất lượng chăm sóc cây theo thời gian. Môi trường tốt → cộng Tu Vi, môi trường xấu → trừ Tu Vi |
| **Cảnh Giới** | Cấp bậc (rank) của cây, được thăng cấp khi Tu Vi đạt đủ mốc. Lấy cảm hứng từ hệ thống tu luyện trong tiểu thuyết tiên hiệp |
| **Đột phá** | Sự kiện cây chuyển từ Cảnh Giới hiện tại lên Cảnh Giới tiếp theo khi tích đủ Tu Vi |
| **Plant Code** | Mã định danh duy nhất được in/gắn trên thiết bị IoT, dùng để liên kết chậu cây với tài khoản người dùng |
| **Ngưỡng lý tưởng** | Khoảng giá trị môi trường (nhiệt độ, độ ẩm, ánh sáng…) được coi là tốt nhất cho từng loại cây cụ thể |
| **Dashboard** | Giao diện chính của ứng dụng, hiển thị trạng thái cây, chỉ số môi trường, Tu Vi và Cảnh Giới |
| **IoT** | Internet of Things — mạng lưới thiết bị vật lý được kết nối Internet để thu thập và trao đổi dữ liệu |
| **Gamification** | Ứng dụng các yếu tố trò chơi (điểm, cấp bậc, bảng xếp hạng) vào hoạt động ngoài game để tăng động lực |
