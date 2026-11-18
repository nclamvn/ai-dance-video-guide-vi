# Kiểm chuyển động, nhạc và file giao

## 1. Kiểm đầu vào trước khi sinh hình

```bash
python3 tools/audit_video.py "video-goc.mp4" --out "runs/nguon" --sheets
ffprobe -v error -show_streams -show_format -of json "video-goc.mp4"
```

Giải mã toàn bộ phải kết thúc không lỗi. Đối chiếu PTS và thời lượng track hình/tiếng; không chỉ chia số khung cho fps. `audit.json` PASS chỉ là cấu trúc/điều kiện đã yêu cầu. Metadata UNVERIFIED hoặc review NOT_PERFORMED phải được xử lý riêng, không coi là đạt.

Nếu cần mã hóa lại nguồn hỏng, giữ bản cũ, lưu SHA-256 và ghi rõ đã bỏ mẫu nào, đổi codec/fps hay mất dữ liệu gì. Ưu tiên lấy lại nguồn đầy đủ. Không đóng băng đoạn cuối để che phần bị mất.

## 2. So hình theo thời gian trước khi căn nhạc

Đặt gốc và AI cạnh nhau ở cùng PTS. Rà mở đầu, tay che mặt, hai lần quay đầu, hất tóc, chân đổi trọng tâm, bước tiến và kết thúc. Bảng ảnh thu nhỏ giúp bao phủ clip; phải xem thêm khung gốc ở vùng rủi ro.

Tách ba vấn đề:

- **Nhạc sai điểm bắt đầu:** sửa offset âm thanh.
- **Chuyển động trễ/sớm:** xác nhận qua nhiều mốc rồi chỉnh thời gian hình nếu có chứng cứ; kiểm lại sau chỉnh.
- **Động tác bị đổi/thiếu:** dịch nhạc không sửa được. Cần sửa hình hoặc ghi không đạt.

Tuỳ chọn macOS: `tools/extract_pose.swift` dùng Apple Vision để ước lượng điểm cơ thể cục bộ. Đây là công cụ phụ để xem thời điểm, chưa chứng nhận giải phẫu hay tính đúng từng pixel. Không tự động retime theo keypoint nhiễu.

```bash
swift tools/extract_pose.swift "video-goc.mp4" "runs/pose-goc.json" 0
```

`0` xử lý mọi khung có trong file; giá trị lớn hơn là khoảng lấy mẫu theo giây. Script cần macOS và Swift/Apple SDK; không bắt buộc cho workflow đa nền tảng.

## 3. Xuất dọc 2K rõ kích thước

Quy ước giao trong repo: **1440×2560**, 9:16, H.264/yuv420p, âm thanh AAC khi có nhạc. Ghi kích thước cụ thể thay vì chỉ nói “2K”. Không coi video nâng cấp là 2K gốc.

```bash
ffmpeg -n -i "master.mp4" -map 0:v:0 -map '0:a?' \
  -vf 'scale=1440:2560:flags=lanczos,setsar=1' \
  -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart "video-2k.mp4"
python3 tools/audit_video.py "video-2k.mp4" --out "runs/ban-giao" --sheets
```

Lệnh này giữ nhịp khung đầu vào, **không tạo chuyển động 60 fps**. Chỉ xuất 60 fps nếu đã nội suy và kiểm lỗi; thêm `-r 60` đơn thuần không làm động tác mượt thật.

Khi nội suy qua một chỗ cắt, xem từng khung hai bên. Nếu thay khung lỗi bằng khung sạch liền kề, ghi chỉ số, thời lượng giữ và sự lặp hình; so timeline sau sửa. Không gọi đó là sinh lại động tác.

## 4. Căn nhạc bằng waveform, kiểm lại bằng chuyển động

```bash
python3 tools/sync_music.py --video "video-2k.mp4" --music "nhac.m4a" \
  --reference "video-goc.mp4" --seconds 20 \
  --out "runs/video-co-nhac.mp4" --report "runs/can-nhac.json"
```

Công cụ so nhiều cửa sổ PCM mono 16 kHz, tìm đoạn nhạc tương ứng và độ dịch nhất quán. Thiếu độ tin cậy hoặc có trôi thời gian thì dừng. Nếu biết offset từ đối chiếu thủ công, dùng `--offset-seconds`; số dương nghĩa là cắt phần đầu nhạc, số âm nghĩa là trì hoãn nhạc. Luôn kiểm lại mốc động tác sau mux. Công cụ không tự chứng nhận nhạc đúng với chuyển động AI và không kéo giãn nhạc/video.

Hình được sao chép luồng, nhạc mã hóa AAC. Không ghi đè file có sẵn. File reference phải còn track tiếng tương ứng; chỉ có video im lặng thì không thể căn waveform tự động.


`--seconds 20` là ví dụ demo. Thay bằng thời lượng brief/hình đã kiểm, không mặc định cắt video khác còn 20 giây. Sau ghép, kiểm chính file giao:

```bash
python3 tools/audit_video.py "runs/video-co-nhac.mp4" --out "runs/ban-giao-co-nhac" --sheets
```

## 5. Điều kiện bàn giao

- Metadata/kích thước/codec/âm thanh đúng yêu cầu; giải mã toàn file không lỗi.
- Nhạc đã đo offset sau mã hóa; chuyển động được so riêng với nguồn.
- Lỗi tay/tóc/chân/đoạn thiếu được ghi trong [review](../templates/review.json).
- Tổng chi phí và số lượt được đối soát; không chạy thêm vì “còn credit” nếu hết số lượt duyệt.
- Người dùng xem và nghiệm thu thẩm mỹ. Một ca thành công không chứng minh mọi nhân vật/cảnh khác đều chạy tốt.
