# Chạy YouArt với số lượt có giới hạn

Đây là quy trình thủ công có kiểm soát. Tên model, khả năng nối Element và giá có thể đổi; đọc giá trực tiếp trên tài khoản trước mỗi lượt. Không dùng các giá ca cũ làm báo giá mới.

1. **Đầu vào:** ảnh toàn thân trong cảnh mới; mặt chính diện, trái, phải; video chuyển động đầy đủ đã kiểm giải mã. Chọn rõ có giữ tiếng nguồn hay không.
2. **Bản thử:** Kling v3.0 Motion Control, ảnh nhân vật + video động tác, Video Framing, chất lượng theo giá đã duyệt. Xem đủ clip, đặc biệt chân/bàn tay và đoạn cuối.
3. **Lập danh sách lỗi:** giây nào, khung nào, mặt/tóc/tay/chân/cảnh sai gì. Chỉ chọn một mục tiêu sửa rõ ràng trước lượt tiếp theo.
4. **Nhận diện:** nếu dùng Face Element, xác minh có output ID/media dùng được và đã nối đúng cổng. “Done” trên thẻ không chứng minh model sau đã nhận được Element.
5. **Lượt sửa:** trong ca này dùng Seedance 2.5 Omni Reference, 20 giây, 1080p, 9:16, Draft OFF, Real Faces ON. Thứ tự ảnh: mặt chính diện → toàn thân/cảnh → mặt trái → mặt phải. Video là clip chuyển động sạch. Không chứng minh Element ID đã nối vào lượt này.
6. **Chọn bản:** so cả bản thử và bản sửa với nguồn. Seedance có thể làm mặt đẹp hơn nhưng đổi bước chân hoặc thời điểm. Giữ cả hai; chọn theo tiêu chí của người dùng.
7. **Hậu kỳ:** loại tiếng ngoài ý muốn, upscale nếu đã chọn bản, kiểm khung nội suy, căn nhạc nguồn, xuất đúng kích thước, giải mã lại file giao.

Không mặc định mọi lỗi đều không tính phí. Đọc trạng thái, lịch sử và số dư. Nếu bị từ chối đầu vào, kiểm file/cổng kết nối trước; không bấm thử lặp vô hạn. Chưa rõ khoản phí nào thì giữ phần dự phòng, không gắn nhãn 0 tùy tiện.

## Ngân sách ca ngày 18/11/2026

| Khoản | Credit ghi nhận |
|---|---:|
| Hỏi giá, agent chuẩn bị/chẩn đoán/xử lý | 56 |
| Face Element | Báo giá 0; không thấy số dư giảm ở lượt legacy |
| 1 Kling thay thế thành công | 456 |
| 1 Seedance thay thế, Real Faces ON | 1.812 |
| 1 Topaz 2×, Smoother Motion ON | 160 |
| Ghép nhạc, so khung, xuất cục bộ | 0 YouArt credit |
| **Tổng / trần đã duyệt** | **2.484 / 3.300** |

Trong 56 credit, 10 là hỏi giá ban đầu, 15 chuẩn bị có lịch sử billing; 16 chẩn đoán và 15 xử lý được suy từ số dư. Đối soát tổng: `10 + 3320 − 846 = 2484`. Còn 816 trong trần dự án, khác số dư tài khoản 846.

Đây là tổng một ca thành công về thực thi, chưa hoàn hảo về hình. Không cam kết gói Pro nào luôn đủ; thời lượng, cấu hình, giá, số lần sửa và credit có sẵn làm thay đổi kết quả. File [budget.json](../templates/budget.json) mặc định chưa có đơn giá để tránh chạy theo giá cũ.
