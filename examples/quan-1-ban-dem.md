# Ca chạy thật: nhân vật tím, sân thượng Quận 1 ban đêm

Ngày 18/11/2026. Nhân vật hư cấu trưởng thành, tóc bob nâu, áo crop top tím, quần cargo, giày trắng. Cảnh sân thượng đêm lấy cảm hứng Quận 1; video chuyển động tham chiếu do người dùng cung cấp.

| Giai đoạn | Kết quả thực tế |
|---|---|
| Ảnh chuẩn | 2160×3840 nâng từ 941×1672, không phải 4K gốc |
| Nguồn ban đầu | File tải bị hỏng cuối; bản sạch chỉ còn 472 khung, 19,666667 giây, 24 fps |
| Kling | 1072×1920, 30 fps, 590 khung, 19,666667 giây; mặt/tóc lỗi khi quay nhanh |
| Seedance sửa | 1080×1920, 24 fps, 481 khung, 20,041667 giây; mặt tự nhiên hơn ở một số góc, tóc vẫn phồng, bước cuối đổi |
| Âm thanh Seedance | Vẫn có AAC dù yêu cầu im lặng; đã bỏ bằng sao chép luồng hình |
| Topaz | Upscale 2160×3840, nội suy 60 fps, 1.200 khung, 20 giây; phát sinh bóng ma đầu clip |
| Sửa cục bộ | Thay khung 2 và 3, đếm từ 0, bằng khung sạch 4; giữ 1.200 vị trí và 20 giây |
| Bản giao có nhạc | 1440×2560, 60 fps, 20 giây, AAC stereo; hình sao chép nguyên luồng bản 2K đã kiểm |
| Tổng | 2.484/3.300 YouArt credit, không có phí dịch vụ mới cho ghép nhạc/so khung |

## Phát hiện sau khi người dùng gửi lại nguồn đầy đủ

Nguồn đầy đủ có 669 khung hình, timeline kèm nhạc 28,096 giây. Kiểm giải mã qua toàn file không lỗi. Phải đọc PTS, không suy thời lượng chỉ bằng 669/24.

Đã trích tư thế bằng Apple Vision ở 669 khung nguồn (664 khung nhận được tư thế) và toàn bộ 1.200 khung AI; xem thêm bảng đối chiếu theo thời gian. Trong vùng 1–18,5 giây, tìm độ dịch chung ±0,4 giây, bước 1/60 giây, cho giá trị lỗi tư thế thấp nhất ở 0 giây. Một số cửa sổ cục bộ gợi ý lệch 1–4 khung AI, nhưng có nhiễu và biến đổi dáng. Không tự sửa timeline theo điểm nhiễu.

Nhạc người dùng gửi khớp waveform nguồn, cần bù khoảng 4,8 ms. Sau mã hóa AAC, năm cửa sổ 3 giây từ giây 3 tới 18 khớp ở độ dịch 0 với tương quan khoảng 0,994–0,996. Kiểm waveform và kiểm tư thế là hai phép đo khác nhau.

**Kết luận:** đã chứng minh thực thi, quản chi phí, xuất file và căn timeline nhạc. Chưa đạt tóc nhất quán, mọi động tác giống gốc hoặc đủ 28,10 giây. Không có chuyển động AI cho hơn 8 giây cuối; không giả bằng lặp cảnh/đóng băng. Chưa đo phản hồi người xem và chưa benchmark trên nhân vật khác.

## Bài học có thể áp dụng

1. Lấy nguồn đầy đủ và kiểm riêng hình/tiếng trước khi trả tiền sinh video.
2. Lưu bản thử để thấy rõ lượt sửa đã cải thiện gì và làm xấu gì.
3. Xác minh đường nối Element, không chỉ nhìn trạng thái Done.
4. So biên đạo sau sửa mặt và so bóng ma sau nội suy.
5. Chốt nhạc bằng waveform **và** mốc động tác; không dùng waveform để chứng nhận chuyển động.
6. Kết thúc ở giới hạn được duyệt, giao cả lỗi còn lại để người dùng quyết định tiếp.

Media, lịch sử tài khoản và ảnh màn hình riêng không được đưa vào repo công khai. Các số trong ca là ghi chép thực chạy; không phải bảng giá dịch vụ hiện tại.
