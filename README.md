# Chủ đề → Video vẽ tay bảng trắng

Biến **một chủ đề, một kịch bản hoặc file phụ đề `.srt`** thành video vẽ tay (whiteboard animation) hoàn chỉnh. Nếu đầu vào là chủ đề, AI agent sẽ viết kịch bản, tạo giọng đọc và phụ đề, phân cảnh, tạo ảnh, dựng hiệu ứng bàn tay vẽ rồi xuất MP4.

Phù hợp cho: video kể chuyện ngắn, bài giảng, giải thích kiến thức, nội dung TikTok/Reels/Shorts.

> Phát triển tiếp từ repo gốc [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation) của tác giả 江哥是老登啊. Bản này bổ sung: giọng đọc tiếng Việt (Vbee, Edge TTS), làm video từ chủ đề/kịch bản, chế độ nhịp gọn, gắn phụ đề và tài liệu tiếng Việt.

## Xem thử

**Dự án: Cho đi và nhận lại** — Nam trao chiếc ô duy nhất cho một cậu bé trú mưa; vài tuần sau, một người thợ xa lạ dừng lại giúp Nam sửa xe. Hai cảnh được vẽ lần lượt theo lời kể, từ hành động cho đi đến khi lòng tốt được tiếp nối.

![Demo dự án Cho đi và nhận lại](examples/cho-di-nhan-lai.gif)

Ảnh nét gốc: [cảnh trao ô](examples/cho-di-nhan-lai-scene-01.png) · [cảnh nhận lại](examples/cho-di-nhan-lai-scene-02.png).

**Dự án: Vì sao điện thoại càng dùng càng chậm?** — video giải thích kiến thức làm từ chủ đề: hai cảnh vẽ lần lượt ba nguyên nhân (bộ nhớ đầy, ứng dụng nặng, pin chai) và cách khắc phục, có giọng đọc và phụ đề tiếng Việt.

🎬 [Xem video hoàn chỉnh trên Facebook Reel](https://www.facebook.com/reel/1645434740472048)

## Nó làm được gì

- Viết kịch bản từ một chủ đề và dừng để bạn duyệt.
- Tạo giọng đọc bằng Vbee hoặc Edge TTS, sau đó sinh SRT theo thời lượng giọng thật.
- Đọc SRT và gợi ý chia thành các cảnh dài 20–35 giây.
- Mỗi cảnh là **một ảnh nét vẽ**, được chia thành nhiều **vùng** (nhân vật, đồ vật, bối cảnh).
- Các vùng được vẽ **theo thứ tự lời kể**, không phải từ trái sang phải. Vùng chưa tới lượt thì hoàn toàn ẩn.
- Mỗi vùng vẽ bằng nét bút liền mạch: đi nét đen trước (`ink`), tô màu sau (`color`).
- Có trang xem trước trên trình duyệt để kéo chỉnh vùng, thứ tự, thời gian.
- Render từng cảnh rồi ghép thành một video hoàn chỉnh.
- Tự khớp hình, phụ đề và giọng đọc tiếng Việt.
- Với SRT có sẵn, có chế độ **nhịp gọn** để loại bỏ khoảng lặng thừa.

## Dùng như Skill cho AI agent (khuyên dùng)

Clone repo về máy:

```bash
git clone https://github.com/Cuongyd196/whiteboard-video.git
cd whiteboard-video
```

Mở thư mục `whiteboard-video` bằng AI agent như Codex, Claude Code hoặc Antigravity. Repo đã có sẵn [SKILL.md](SKILL.md), vì vậy bạn chỉ cần yêu cầu agent dùng skill:

```text
Dùng skill whiteboard-video làm video vẽ tay 60 giây về chủ đề "cho đi và nhận lại".
```

Agent sẽ đọc hướng dẫn trong skill, làm từng bước và dừng để bạn duyệt trước khi tiếp tục. Bạn cũng có thể đưa một kịch bản hoặc file SRT có sẵn.

### Bắt đầu từ chủ đề hoặc kịch bản (không cần SRT)

Skill nhận 3 kiểu đầu vào:

| Bạn có | Agent bắt đầu từ |
|---|---|
| **Một chủ đề** ("cho đi và nhận lại") | Viết kịch bản → bạn duyệt |
| **Một kịch bản** (đoạn văn lời dẫn) | Tạo giọng đọc → tự sinh SRT khớp giọng |
| **File SRT** | Chia cảnh (như cũ) |

Với chủ đề hoặc kịch bản, skill làm theo kiểu **giọng đọc dẫn nhịp**: đọc trước, lấy độ dài giọng thật làm mốc phụ đề, rồi mới vẽ theo mốc đó. Video ra **không có khoảng lặng thừa** mà không cần bước "nhịp gọn".

Ví dụ từ chủ đề:

```text
Dùng skill whiteboard-video làm video vẽ tay 60 giây, chủ đề "cho đi và nhận lại".
Kể bằng một câu chuyện ngắn, giọng ấm, kết bằng một câu đọng lại. Giọng Edge nam, có phụ đề.
Trả lời bằng tiếng Việt.
```

Ví dụ từ kịch bản có sẵn:

```text
Dùng skill whiteboard-video làm video hoàn chỉnh từ kịch bản dưới đây.
Giọng Vbee n_hanoi_male_protrainer_education_vc, tốc độ 1.1. Trả lời bằng tiếng Việt.

Cho đi rồi, liệu có nhận lại không?

Chiều ấy, Nam thấy một cậu bé ôm chồng sách đứng trú mưa. ...
```

Các bước agent sẽ đi qua (mỗi bước dừng chờ bạn duyệt):

1. **Kịch bản** (chỉ khi đưa chủ đề) → lưu `script.md`.
2. **Giọng đọc + SRT** → cắt câu, tạo giọng, sinh `input.srt` theo giọng thật. Nghe thử `narration.m4a` rồi duyệt.
3. **Phân cảnh → ảnh nét vẽ → chia vùng → render → ghép** (như quy trình SRT).
4. **Hoàn thiện** → gắn phụ đề + ghép giọng đọc → video cuối.

Mẹo viết kịch bản: mỗi câu ngắn (đọc ≤ 5 giây), có hình ảnh cụ thể (người, đồ vật, hành động) để dễ vẽ; **cách một dòng trống giữa các đoạn** để tạo khoảng nghỉ dài hơn khi đọc.

### Trò chuyện qua từng bước

Agent **dừng lại sau mỗi bước** để bạn duyệt. Trả lời "ok / chốt" để đi tiếp, hoặc nói cần sửa gì — agent chỉ làm lại đúng bước đó.

| Bước | Agent làm | Bạn trả lời (ví dụ) |
|---|---|---|
| 1. Phân cảnh | Đọc SRT, chia cảnh, đề xuất hình cho từng cảnh | "ok" · "gộp thành 2 cảnh" · "cảnh 2 thêm hình chiếc ô" |
| 2. Ảnh nét vẽ | Tạo ảnh hoặc viết prompt vào `IMAGE_PROMPTS.md` | "ok" · "nhân vật Nam ở 2 cảnh phải giống nhau" |
| 3. Chia vùng | Tạo `*.annotation.json`, mở trang xem trước | "ok" · "vẽ cậu bé trước chiếc ô" |
| 4. Ảnh kiểm tra vùng | Xuất ảnh đánh số vùng | "ok" · "vùng 3 rộng thêm sang phải" |
| 5. Chỉnh trên trình duyệt | (Bạn tự kéo chỉnh nếu muốn, bấm Lưu) | "chốt rồi triển" |
| 6. Render từng cảnh | Render MP4, xem khung đầu/giữa/cuối | "ok" · "cảnh 1 vẽ nhanh hơn" |
| 7. Ghép | Ghép thành một video | "ghép thành video hoàn chỉnh" |

> **Ảnh nét vẽ:** nếu agent không tự tạo ảnh được, nó sẽ ghi prompt vào `IMAGE_PROMPTS.md`. Bạn dùng prompt đó với công cụ tạo ảnh (ChatGPT, Gemini…), lưu ảnh đúng tên `scene-01-<tên>.png` vào thư mục dự án rồi báo agent.

### Các yêu cầu hay dùng sau khi có video

```text
Gắn phụ đề vào video.
Thêm giọng đọc bằng Edge TTS.
Thêm giọng đọc Vbee, giọng n_hanoi_male_protrainer_education_vc.
Giọng đọc và hình bớt khoảng lặng cho video hấp dẫn hơn.     ← chế độ nhịp gọn
Nghỉ lâu hơn sau câu "Chiếc ô không trở lại".
Đổi sang giọng nữ vi-VN-HoaiMyNeural.
Cảnh 2 vẽ chiếc ô trước bác thợ.
Thay cây bút, không hiển thị chữ trên thân bút.
```

Agent sẽ tự chọn đúng script, chạy lại phần cần thiết (giọng đã tạo được lấy từ cache, không tốn phí lần 2) và kiểm tra kết quả trước khi báo lại.

### Mẹo để có video đẹp

- **Mỗi cảnh một ý chính**, 20–35 giây. Video 60 giây thường chia 2 cảnh.
- **Mỗi câu phụ đề nên ngắn** (≤ 5 giây đọc) để hình và giọng khớp nhau.
- Yêu cầu hình **tách rời nhau, không chồng lên** — chia vùng dễ, bút vẽ tự nhiên hơn.
- Luôn **xem ảnh kiểm tra vùng** (bước 4) trước khi render — sửa ở đây nhanh hơn nhiều so với render lại.
- Nếu bắt đầu từ chủ đề hoặc kịch bản, SRT đã được tạo theo giọng đọc thật nên không cần chạy **nhịp gọn**. Chế độ này chủ yếu dành cho SRT có sẵn bị dư khoảng lặng.
- Key Vbee để trong `.env`, **không dán key vào khung chat**.

## Cài đặt

Cần có **Python 3.10+** và **ffmpeg** (có trong PATH).

```bash
python scripts/prepare_env.py          # tạo .venv và cài opencv, numpy, av, Pillow, edge-tts
python scripts/prepare_env.py --check  # chỉ kiểm tra; dòng cuối in ENV_PY=<đường dẫn python>
```

Các lệnh bên dưới dùng `<ENV_PY>` là Python trong `.venv`:
- Windows: `.\.venv\Scripts\python.exe`
- macOS/Linux: `.venv/bin/python`

### Cấu hình giọng đọc (tuỳ chọn)

Sao chép file mẫu rồi điền giá trị (`.env` đã nằm trong `.gitignore`, **đừng commit**):

```bash
cp .env.example .env        # Windows PowerShell: Copy-Item .env.example .env
```

Các giá trị chính trong `.env`:

```env
# edge = miễn phí, vbee = trả phí theo ký tự
TTS_PROVIDER=edge

# Vbee: dán nguyên mã giọng copy từ giao diện Vbee
# Edge: vi-VN-NamMinhNeural (nam) hoặc vi-VN-HoaiMyNeural (nữ)
TTS_VOICE=vi-VN-NamMinhNeural

# Tốc độ đọc: 1.0 = bình thường, 1.1 = nhanh hơn 10%
TTS_SPEED=1.1

# Chỉ cần khi dùng Vbee
VBEE_APP_ID=...
VBEE_ACCESS_TOKEN=...
```

## Quy trình làm một video

Luồng đầy đủ khi đầu vào là **một chủ đề**. Mỗi bước hoàn thành, agent sẽ **dừng lại để bạn duyệt** rồi mới làm bước tiếp theo.

| Bước | Việc cần làm | Kết quả |
|---|---|---|
| 0a | Viết kịch bản từ chủ đề | `script.md` |
| 0b | Tạo giọng đọc, lấy thời lượng giọng thật để sinh phụ đề | `narration.m4a`, `input.srt` |
| 1 | Đọc SRT, chia cảnh và đề xuất hình cho từng cảnh | Bảng phân cảnh |
| 2 | Tạo ảnh nét vẽ 16:9, nền kem `#F5EBD7` | `scene-XX-<tên>.png` |
| 3 | Xem ảnh, chia vùng theo mạch kể và mở trang xem trước | `scene-XX-<tên>.annotation.json` |
| 4 | Xuất ảnh đánh số để kiểm tra vùng và thứ tự vẽ | `scene-XX-<tên>-regions.png` |
| 5 | Chỉnh vùng, thứ tự và thời gian trên trang xem trước | File annotation đã cập nhật |
| 6 | Render và kiểm tra từng cảnh | `scene-XX-<tên>-whiteboard.mp4` |
| 7 | Ghép các cảnh theo đúng thứ tự | Video hình hoàn chỉnh |
| 8 | Gắn phụ đề và ghép giọng đọc đã tạo ở bước 0b | Video cuối |

Nếu đầu vào là **kịch bản**, bắt đầu từ bước 0b. Nếu đầu vào là **SRT**, bắt đầu từ bước 1; bước 8 chỉ tạo hoặc ghép giọng đọc khi bạn yêu cầu.

### Thư mục dự án

```text
assets/whiteboard/<tên-dự-án>/
├── script.md                          # kịch bản khi bắt đầu từ chủ đề/kịch bản
├── narration.m4a                      # giọng đọc hoàn chỉnh
├── input.srt
├── scene-01-<tên>.png                  # ảnh nét vẽ
├── scene-01-<tên>.annotation.json      # chia vùng + thời gian (cùng tên với ảnh)
├── scene-01-<tên>-whiteboard.mp4       # video cảnh 1
└── tts-cache/                          # giọng đọc đã tạo (dùng lại, không tốn phí lần 2)
```

Ảnh và file JSON **phải cùng tên**: `scene-01-demo.png` ↔ `scene-01-demo.annotation.json`.

## Dùng thủ công bằng lệnh

Không dùng agent? Chạy trực tiếp các script theo thứ tự dưới đây.

**0. (Nếu bắt đầu từ kịch bản) Kịch bản → SRT theo giọng đọc**

```bash
# Cắt kịch bản thành câu, ra SRT nháp; dòng cuối in PAUSES=1=0.8,8=0.8,... (câu cuối mỗi đoạn)
python scripts/script_to_srt.py script.md --output draft.srt

# Tạo giọng, sinh input.srt theo độ dài giọng thật (thêm một --pause cho mỗi mục trong PAUSES)
<ENV_PY> scripts/tts_narration.py draft.srt --output narration.m4a --provider edge \
  --retime-out input.srt --pause 1=0.8 --pause 8=0.8
```

Từ đây dùng `input.srt` cho các bước bên dưới; ở bước 7 giọng đọc được lấy lại từ cache.

**1. Đọc phụ đề, gợi ý chia cảnh**

```bash
python scripts/parse_srt.py input.srt --target-sec 30 --min-sec 25 --max-sec 35
```

**2. Xuất ảnh kiểm tra vùng**

```bash
<ENV_PY> scripts/render_annotation_preview.py <ảnh.png> <ảnh.annotation.json> <ảnh-regions.png>
```

**3. Chỉnh sửa trực quan** — mở `assets/preview.html` bằng Chrome/Edge → bấm "Mở thư mục" → chọn thư mục dự án. Kéo khung để sửa vùng, kéo danh sách để đổi thứ tự, sửa thời gian bắt đầu/kết thúc, rồi bấm Lưu.

**4. Render một cảnh**

```bash
<ENV_PY> scripts/render_stream_whiteboard.py <ảnh.png> <ảnh.annotation.json> <ra.mp4> assets/drawing-hand.png \
  --ink-path skeleton --color-fill contour-wipe
```

- `--ink-path grid` (mặc định, ổn định) hoặc `skeleton` (bám nét hơn, hợp với ảnh nét rõ).
- `--color-fill contour-wipe` (quét theo viền, mặc định) hoặc `brush` (tô theo nét bút).

**5. Ghép các cảnh**

```bash
<ENV_PY> scripts/merge_scenes.py --inputs canh1.mp4 canh2.mp4 --output final.mp4
```

**6. Gắn phụ đề vào video** (chữ xám trên nền màu giấy)

```bash
ffmpeg -i final.mp4 -vf "subtitles=input.srt:force_style='FontName=Arial,FontSize=15,PrimaryColour=&H00303030,OutlineColour=&H10D7EBF5,BorderStyle=3,Outline=6,Shadow=0,MarginV=14'" \
  -c:v libx264 -crf 20 -pix_fmt yuv420p final-sub.mp4
```

**7. Thêm giọng đọc**

```bash
# Edge TTS (miễn phí)
<ENV_PY> scripts/tts_narration.py input.srt --output narration.m4a --video final-sub.mp4 --provider edge

# Vbee (dán mã giọng copy từ Vbee)
<ENV_PY> scripts/tts_narration.py input.srt --output narration.m4a --video final-sub.mp4 \
  --provider vbee --voice n_hanoi_male_protrainer_education_vc
```

Kết quả: `final-sub-voice.mp4`. Mỗi câu được đặt đúng mốc phụ đề; câu nào đọc dài hơn khung thời gian sẽ được tăng tốc nhẹ và có cảnh báo. Khoảng lặng đầu/cuối của mỗi câu được cắt tự động (tắt bằng `--no-trim`).

**8. Nhịp gọn — bỏ khoảng lặng thừa**

Khi phụ đề chia đều (ví dụ 5 giây/câu) nhưng giọng đọc ngắn hơn, video sẽ có nhiều chỗ im lặng. Cách xử lý: lấy độ dài giọng thật làm chuẩn, rồi co thời gian vẽ theo.

```bash
# a) Tạo giọng + SRT mới theo độ dài giọng thật
<ENV_PY> scripts/tts_narration.py input.srt --output narration.m4a --provider edge \
  --retime-out input.tight.srt --gap 0.3 --pause 6=0.8 --tail 1.0

# b) Co thời gian vẽ trong các file annotation (file gốc giữ nguyên, ra file *.tight.annotation.json)
<ENV_PY> scripts/retime_annotations.py --old-srt input.srt --new-srt input.tight.srt \
  --annotations scene-01-a.annotation.json scene-02-b.annotation.json

# c) Render lại các cảnh bằng *.tight.annotation.json, ghép, gắn phụ đề input.tight.srt,
#    rồi chạy bước 7 với input.tight.srt (giọng lấy từ cache, không tạo lại)
```

- `--gap 0.3`: nghỉ 0,3 giây giữa các câu.
- `--pause 6=0.8`: sau câu số 6 nghỉ lâu hơn (0,8 giây) để tạo điểm nhấn. Dùng được nhiều lần.
- `--tail 1.0`: giữ hình hoàn chỉnh 1 giây ở cuối video.

Ví dụ thực tế: video 60 giây rút còn khoảng 38 giây, giọng đọc gần như liên tục, bút luôn vẽ đúng thứ đang được kể.

## Chia vùng (file annotation.json)

Toạ độ tính bằng **pixel nguyên** trên ảnh gốc (gốc toạ độ ở góc trên bên trái). Thứ tự vẽ nên theo mạch: **bối cảnh → nhân vật/đồ vật chính → hành động/biến đổi → phản ứng/kết quả**.

```json
{
  "sceneId": "scene-01",
  "canvas": { "width": 1672, "height": 941 },
  "storyBasis": "Tóm tắt nội dung cảnh",
  "sceneDurationMs": 30000,
  "elements": [
    {
      "id": "boy",
      "label": "Cậu bé ôm sách",
      "sequence": 1,
      "narrativeRole": "Người đang cần giúp đỡ",
      "subtitle": "Chiều ấy, Nam thấy một cậu bé ôm chồng sách đứng trú mưa.",
      "region": { "x": 180, "y": 405, "width": 285, "height": 465 },
      "reveal": {
        "direction": "top_to_bottom",
        "startMs": 300,
        "durationMs": 4800,
        "maskPaddingPx": 0,
        "protectedRegions": []
      },
      "handPath": { "start": [322, 405], "end": [322, 869], "easing": "easeInOut" }
    }
  ]
}
```

| Trường | Ý nghĩa |
|---|---|
| `canvas` | Kích thước ảnh gốc, phải khớp chính xác |
| `sceneDurationMs` | Tổng thời lượng cảnh (ms) |
| `sequence` | Thứ tự vẽ, bắt đầu từ 1 |
| `subtitle` | Câu phụ đề ứng với vùng này |
| `region` | Khung chữ nhật của vùng |
| `reveal.startMs` / `durationMs` | Lúc bắt đầu vẽ và thời gian vẽ vùng (2/3 đi nét, 1/3 tô màu) |
| `protectedRegions` | Các khung **không được vẽ** trong vùng này (để dành cho vùng vẽ sau), dùng khi các vùng chồng nhau |
| `direction`, `handPath` | Chỉ dùng cho trang xem trước; nét bút thật do trình render tự tính |

Mẹo: vùng vẽ sau luôn được tự động trừ ra khỏi vùng vẽ trước, nên vùng nền lớn (ví dụ cả khung hình) sẽ không làm lộ nhân vật trước lượt.

## Quy chuẩn hình ảnh

- Nền giấy màu kem `#F5EBD7`, nét phác xám đậm, tối giản, nhiều khoảng trống.
- Chỉ dùng chút đỏ, cam, xanh dương làm điểm nhấn.
- **Không** có chữ, số, logo trong ảnh; không ảnh chụp, 3D hay nền rối.
- Các nhân vật/đồ vật nên tách nhau để dễ chia vùng.

## Kiểm tra trước khi xuất bản

- Khung hình đầu tiên là nền giấy trơn, chưa lộ nét nào.
- Giữa video: vùng chưa tới lượt không bị lộ ra.
- Bút luôn nằm sát nét đang vẽ.
- Cuối mỗi cảnh giữ hình hoàn chỉnh ít nhất 0,5 giây.
- Giọng đọc khớp với phụ đề và hình đang vẽ.

## Cấu trúc thư mục

```text
whiteboard-video/
├── SKILL.md                          # quy trình đầy đủ cho AI agent
├── vbee.md                           # hướng dẫn API Vbee
├── assets/
│   ├── drawing-hand.png              # ảnh bàn tay cầm bút
│   └── preview.html                  # trang xem trước / chỉnh sửa
├── examples/                         # ví dụ minh hoạ
├── scripts/
│   ├── script_to_srt.py              # cắt kịch bản thành câu → SRT nháp
│   ├── parse_srt.py                  # đọc phụ đề, gợi ý chia cảnh
│   ├── render_annotation_preview.py  # ảnh kiểm tra vùng
│   ├── render_stream_whiteboard.py   # render video vẽ tay
│   ├── merge_scenes.py               # ghép các cảnh
│   ├── tts_narration.py              # giọng đọc Vbee / Edge TTS
│   ├── retime_annotations.py         # co thời gian vẽ theo giọng đọc
│   └── prepare_env.py                # cài môi trường
└── agents/openai.yaml
```

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `You have exceeded the API TTS quota` | Tài khoản Vbee hết quota API → nạp thêm hoặc dùng `--provider edge` |
| `缺少 VBEE_APP_ID / VBEE_ACCESS_TOKEN` | Chưa khai báo key Vbee trong `.env` |
| `需要系统 ffmpeg / ffprobe` | Cài ffmpeg và thêm vào PATH |
| Phụ đề bị đè lên nét vẽ | Dùng lệnh gắn phụ đề ở trên (có nền màu giấy sau chữ) |
| Nhân vật lộ ra trước lượt | Thêm `protectedRegions` hoặc sửa `region` cho khớp hơn |

## Giấy phép

MIT License — xem [LICENSE](LICENSE).

Dự án gốc: [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation) của tác giả 江哥是老登啊 (Douyin, Bilibili), phát hành theo MIT License. Bản này bổ sung giọng đọc tiếng Việt, làm video từ chủ đề/kịch bản, chế độ nhịp gọn và tài liệu tiếng Việt.
