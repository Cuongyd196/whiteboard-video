# Chiếc ô đi một vòng

Trạng thái: người dùng đã duyệt lời dẫn, phân cảnh, hai ảnh và chốt preview. Đã hoàn thành bước 4: tạo scene-01-regions.png và scene-02-regions.png bằng môi trường .venv; đã xem ảnh kiểm tra vùng và sửa phông nhãn tiếng Việt trong script. Các vùng nằm trong ảnh; renderer loại vùng vẽ sau khỏi vùng trước để bảo vệ phần chồng lấn. Chờ duyệt ảnh kiểm tra theo bước 4 của SKILL.md. Chưa xuất MP4. Môi trường .venv đã cài đủ OpenCV, NumPy, PyAV, Pillow.

Video vẽ tay 60 giây, khung ngang xấp xỉ 16:9 (ảnh 1672 × 941) theo mặc định của dự án. Ngôn ngữ: tiếng Việt. Dùng renderer Python của dự án srt-whiteboard-animation. Ảnh: scene-01-trao-o.png và scene-02-nhan-lai.png, mỗi ảnh có file .annotation.json cùng tên. Chưa tạo giọng đọc hoặc MP4. Prompt đầy đủ lưu trong IMAGE_PROMPTS.md. Bản preview-local.html là ảnh chụp cấu hình tại lúc tạo; muốn sửa và ghi trực tiếp vào JSON gốc, dùng nút mở thư mục trong trang preview để chọn thư mục dự án này.

Thông điệp: sự tử tế có thể được tiếp nối giữa những người xa lạ; cho đi không bảo đảm được đền đáp. Người thợ là người khác, không phải cậu bé đã nhận ô.

## Lời dẫn

Cho đi rồi, liệu có nhận lại không?

Chiều ấy, Nam thấy một cậu bé ôm chồng sách đứng trú mưa. Anh đưa cậu chiếc ô duy nhất của mình. “Cầm lấy nhé. Sách ướt thì tiếc lắm.” Cậu bé hỏi cách trả ô. Nam chỉ cười, rồi chạy vào màn mưa. Chiếc ô không trở lại. Nam cũng dần quên chuyện ấy.

Vài tuần sau, xe anh hỏng giữa đường vắng. Một bác thợ dừng lại, cúi xuống nối giúp sợi dây bị đứt. Nam ngỏ ý trả công. Bác xua tay: “Trước cũng có người giúp tôi.” Nghe vậy, anh chợt nhớ chiếc ô hôm ấy.

Cho đi không phải một lời hẹn sẽ được trả lại. Nhưng mỗi lần giúp nhau, ta làm cuộc đời bớt lạnh đi một chút.

## Phân cảnh

| Cảnh | Thời gian | Phụ đề | sceneDurationMs | Ý chính | Hình ảnh và thứ tự vẽ |
|---|---|---|---|---|---|
| scene-01 | 00:00–00:30 | 1–6 | 30000 | Giúp người mà không đòi đáp lại | Vài nét mưa và mái hiên → cậu bé ôm sách → Nam trao ô màu xanh → một cụm nhỏ tách biệt cho thấy Nam chạy dưới mưa. Giữ hình hoàn chỉnh ở cuối cảnh. |
| scene-02 | 00:30–01:00 | 7–12 | 30000 | Đón nhận và tiếp nối sự tử tế | Nam cạnh xe máy hỏng → bác thợ với dụng cụ cúi sửa xe → cử chỉ cảm ơn → hình chiếc ô nhỏ trong bong bóng hồi tưởng → ba bàn tay nối nhau làm hình kết. Giữ hình hoàn chỉnh ít nhất 0,5 giây. |

## Mỹ thuật

Nền giấy kem #F5EBD7; nét phác xám đậm, tối giản, nhiều khoảng trống. Màu xanh dịu của chiếc ô là điểm nhấn xuyên suốt; có thể thêm chút cam ở áo người thợ. Nam giữ nguyên kiểu tóc và trang phục qua hai cảnh. Không chữ, số, nhãn, logo trong ảnh minh họa; không ảnh thật, 3D hay nền dày đặc. Các cụm hình tách nhau để thuận tiện chia vùng vẽ.

## Nhịp và âm thanh dự kiến

Lời dẫn ấm, chậm vừa, có khoảng nghỉ sau “Chiếc ô không trở lại” và trước câu kết. Mốc SRT hiện là nhịp biên tập dự kiến, chưa căn theo bản thu. Nhạc piano nhẹ và tiếng mưa là định hướng, chưa có tệp âm thanh. Phụ đề lưu riêng trong input.srt; renderer hiện tại không tự tạo giọng đọc.
