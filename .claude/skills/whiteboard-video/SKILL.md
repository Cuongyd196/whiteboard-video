---
name: whiteboard-video
description: Làm video vẽ tay bảng trắng (whiteboard animation) trên nền giấy màu kem từ một chủ đề, một kịch bản lời dẫn hoặc file phụ đề SRT, ra thành phẩm hoàn chỉnh có giọng đọc và phụ đề. Quy trình - chủ đề → viết kịch bản → tạo giọng đọc sinh SRT theo giọng thật, hoặc đọc SRT → phân cảnh → tạo ảnh nét vẽ cùng phong cách → chia vùng theo mạch truyện (annotation.json / sequence / startMs / protectedRegions) → chỉnh trên trang xem trước → render MP4 bằng nét bút liền mạch (đi nét ink → tô màu color) → ghép cảnh, gắn phụ đề, ghép giọng đọc (Vbee hoặc Edge TTS). Dùng khi người dùng đưa chủ đề, kịch bản/lời dẫn hoặc file SRT và muốn "làm video vẽ tay", "video whiteboard", "video bảng trắng", "biến phụ đề thành video vẽ tay", "từ chủ đề/kịch bản làm video hoàn chỉnh".
---

# Video vẽ tay bảng trắng (lối vào skill cấp dự án)

File này chỉ là lối vào của skill cấp dự án. Toàn bộ quy trình, các điểm dừng xác nhận, quy tắc chia vùng và cách dùng script nằm trong **`SKILL.md` ở thư mục gốc dự án**.

**Trước khi làm bất cứ việc gì, đọc toàn bộ `SKILL.md` ở thư mục gốc dự án và làm đúng theo đó.**

- Mọi lệnh chạy từ thư mục gốc dự án (`scripts/`, `assets/` tính từ thư mục gốc).
- Python: dùng `.venv` ở thư mục gốc (Windows `.venv\Scripts\python.exe`; macOS/Linux `.venv/bin/python`); chưa có thì chạy `python scripts/prepare_env.py` trước.
- Key giọng đọc và giọng mặc định nằm trong `.env` ở thư mục gốc; không chép key vào khung chat hay file khác.
- Mọi trao đổi, phân cảnh, nhãn vùng và ghi chú viết bằng tiếng Việt.
