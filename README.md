# Làm video nhảy AI từ video tham chiếu

Hướng dẫn tiếng Việt để thay nhân vật, trang phục và bối cảnh, giữ điệu nhảy tham chiếu, rồi kiểm chuyển động, ghép nhạc và xuất video. Học từ [Lonely / self-media-guide](https://github.com/lonely-dance-lab/self-media-guide), kết hợp một ca chạy thật trên YouArt.

## Các bước ngắn gọn

1. **Chọn mẫu:** xem cấu trúc, người xem, nhịp và lý do muốn làm lại. Chọn thứ vẫn hấp dẫn khi đổi nhân vật; dữ liệu chưa có thì ghi chưa biết.
2. **Khóa yêu cầu:** ghi nhân vật trưởng thành, trang phục, cảnh, điệu nhảy, thời lượng, nhạc, độ phân giải và trần chi phí vào [brief](templates/brief.json).
3. **Kiểm nguồn đầy đủ:** giải mã toàn video, kiểm thời lượng hình và tiếng. Không dùng đoạn tải hỏng hoặc nhầm clip 20 giây là bản gốc 28 giây.
4. **Chuẩn bị ảnh:** một ảnh toàn thân trong cảnh mới và 3–4 góc mặt nhất quán. Ảnh nâng lên 4K phải ghi là ảnh upscale.
5. **Chạy bản thử:** dùng ảnh toàn thân + video chuyển động sạch với Kling Motion Control; xem động tác trước khi trả tiền cho lượt sửa.
6. **Sửa có mục tiêu:** nếu mặt trôi, thêm góc mặt, thử Face Element hoặc Seedance Omni/Real Faces theo khả năng nối dữ liệu thực tế. Kiểm lại cả điệu nhảy sau sửa mặt.
7. **So khung với nguồn:** đặt hai video cạnh nhau ở cùng PTS, rà tay, tóc, xoay người, bàn chân và đoạn cuối. Chưa đạt thì ghi lỗi; không coi lượt sửa đắt hơn là mặc nhiên tốt hơn.
8. **Xuất 2K và rà hình:** có thể dùng Topaz rồi xuất dọc **1440×2560**. Nếu lên 60 fps, kiểm bóng ma qua chỗ cắt và chuyển động nhanh.
9. **Ghép nhạc và kiểm file giao:** căn waveform với âm thanh nguồn, rồi đối chiếu mốc động tác và giải mã lại bản có nhạc. Nhạc khớp waveform không chứng minh động tác sinh ra đã khớp.
10. **Lưu bằng chứng:** ảnh/prompt, cấu hình, báo giá, số lượt, số dư, lỗi còn lại và quyết định chọn bản. Dừng đúng trần được duyệt.

## Đọc tiếp / dùng công cụ

- [Phương pháp của tác giả và phần bổ sung](docs/01-phuong-phap.md)
- [Quy trình YouArt và giới hạn ngân sách](docs/02-youart.md)
- [Kiểm video, ghép nhạc và xuất 2K](docs/03-kiem-dinh-va-xuat.md)
- [Ca thực nghiệm: nhân vật tím, Quận 1 ban đêm](examples/quan-1-ban-dem.md)
- [Prompt mẫu](prompts/yeu-cau-video.md) · [Mẫu review](templates/review.json) · [Nguồn và giấy phép](SOURCES.md)

Yêu cầu: Python 3, FFmpeg; thêm FFprobe để đọc metadata và NumPy để tự căn nhạc. Trên macOS có thể cài `brew install ffmpeg` và cài NumPy trong môi trường Python đang dùng. Các script chỉ xử lý **cục bộ**, không gọi YouArt hoặc tự tiêu credit.

```bash
python3 tools/audit_video.py "video.mp4" --out "runs/kiem-nguon" --sheets
python3 tools/budget.py templates/budget.json
python3 tools/sync_music.py --video "video-2k.mp4" --music "nhac.m4a" \
  --reference "video-goc-day-du.mp4" --seconds 20 \
  --out "runs/video-co-nhac.mp4" --report "runs/can-nhac.json"
```

Tạo `video-2k.mp4` theo [hướng dẫn xuất](docs/03-kiem-dinh-va-xuat.md) trước lệnh ghép. `--seconds 20` chỉ là ví dụ ca demo: thay bằng thời lượng brief đã kiểm; không cắt nguồn đầy đủ còn 20 giây vì sao chép lệnh. Giải mã lại **file có nhạc** sau mux.

**Tình trạng:** đã chạy được demo thật, kiểm soát chi phí và ghép nhạc. Chưa chứng minh giữ chính xác mọi động tác hoặc tóc/mặt ở mọi khung. Bản thử 20 giây không đủ chuyển động cho nguồn đầy đủ 28,10 giây; xem ca thực nghiệm trước khi áp dụng.

Repo không chứa video, nhạc, ảnh riêng hoặc dữ liệu tài khoản. MIT cho mã/tài liệu, giữ ghi công Lonely; giấy phép này không cấp quyền đối với media bên ngoài.
