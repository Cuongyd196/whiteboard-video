---
name: whiteboard-video
description: Làm video vẽ tay bảng trắng (whiteboard animation) trên nền giấy màu kem từ một chủ đề, một kịch bản lời dẫn hoặc file phụ đề SRT, ra thành phẩm hoàn chỉnh có giọng đọc và phụ đề. Quy trình - chủ đề → viết kịch bản → tạo giọng đọc sinh SRT theo giọng thật, hoặc đọc SRT → phân cảnh → tạo ảnh nét vẽ cùng phong cách → chia vùng theo mạch truyện (annotation.json / sequence / startMs / protectedRegions) → chỉnh trên trang xem trước → render MP4 bằng nét bút liền mạch (đi nét ink → tô màu color) → ghép cảnh, gắn phụ đề, ghép giọng đọc (Vbee hoặc Edge TTS). Dùng khi người dùng đưa chủ đề, kịch bản/lời dẫn hoặc file SRT và muốn "làm video vẽ tay", "video whiteboard", "video bảng trắng", "biến phụ đề thành video vẽ tay", "từ chủ đề/kịch bản làm video hoàn chỉnh".
---

# Video vẽ tay bảng trắng từ SRT (mặt nạ theo vùng + nét bút liền mạch)

Biến phụ đề thành video vẽ tay. **Dàn dựng** theo cơ chế mặt nạ từng vùng: các vùng hiện ra lần lượt theo mạch truyện, vùng chưa tới lượt bị ẩn hoàn toàn, chỗ chồng lấn được bảo vệ bằng `protectedRegions`. **Cách vẽ** là nét bút liền mạch: trong phạm vi được phép của mỗi vùng, đầu bút trượt liên tục theo khung xương/lưới để đi nét (`ink`) rồi tô màu (`color`). Mọi vùng dùng chung một canvas, vùng đã vẽ xong được giữ lại.

**Ngôn ngữ:** mọi lời giải thích, phân cảnh, nhãn vùng (`label`), `narrativeRole`, ghi chú, kịch bản và giao diện gửi cho người dùng đều viết bằng **tiếng Việt**, trừ khi người dùng yêu cầu ngôn ngữ khác.

Khác với kiểu nhảy từng khung hay xoá hình chữ nhật, nét bút ở đây **chảy liền mạch**. Khác với kiểu vẽ cả ảnh một lượt, skill này vẽ **theo từng vùng ứng với phụ đề**, nên kiểm soát được thứ tự và thời điểm xuất hiện của từng đối tượng.

## Tham số mặc định

| Hạng mục | Yêu cầu mặc định |
|---|---|
| Nền giấy | Ảnh tạo ra dùng màu giấy cũ kem ấm (`#F5EBD7`). Khi render, lấy mẫu màu nền ở gần bốn góc ảnh gốc (thụt vào trong); cấm nền trắng tinh. |
| Cách vẽ | Mỗi vùng vẽ bằng nét liền: đi nét `ink` (phác nét) → tô `color` (trả lại màu gốc), tỉ lệ thời gian `ink:color = 2:1`. |
| Đường bút | `--ink-path grid` (lưới, mặc định, ổn định) hoặc `skeleton` (bám khung xương, hợp với ảnh nét rõ). |
| Kiểu tô màu | `--color-fill contour-wipe` (quét theo viền, mặc định) hoặc `brush` (tô theo vệt bút). |
| Vùng chưa vẽ | Phạm vi được phép của một vùng = khung `region` trừ đi các vùng vẽ sau và `protectedRegions`; vùng chưa tới lượt ẩn hoàn toàn. |
| Nguồn thời lượng | `sceneDurationMs` của mỗi ảnh lấy từ khoảng thời gian phụ đề của cảnh đó (nên 20–35 giây/cảnh). |
| Khung chỉnh sửa | Trang xem trước mặc định hiện mọi khung vùng có đánh số; khung này không thuộc nội dung video. |

## Quy chuẩn hình ảnh (bắt buộc)

Mọi ảnh gốc của các cảnh phải cùng một ngôn ngữ hình ảnh. Trước khi tạo ảnh, đưa đầy đủ các yêu cầu sau vào prompt; tạo xong kiểm tra lại từng điều:

- **Phong cách và bố cục:** minh hoạ vẽ tay tối giản, kiểu phác thảo bút chì/bút mực, thẩm mỹ nét vẽ tiết chế giống Notion. Ưu tiên truyền đạt ý, không cầu kỳ tả thực; bố cục đơn giản, nền sạch, nhiều khoảng trống; cảm xúc nhẹ nhàng, rõ ràng. Nét vẽ, nhân vật, màu sắc thống nhất trong cả loạt.
- **Màu sắc và chất liệu:** nền giấy màu kem `#F5EBD7`, nét phác xám đậm; chỉ dùng **đỏ, cam, xanh dương** làm điểm nhấn ít ỏi. Không dùng màu nhấn khác, màu quá rực hay chất liệu phức tạp.
- **Nhân vật và đồ vật:** thể hiện bằng đường viền đơn giản, ít nét, chừa khoảng trống; nhấn vào quan hệ/biến đổi/ý chính, không vào tỉ lệ, chất liệu, chi tiết thật.
- **Tuyệt đối cấm:** bất kỳ chữ, từ, chữ cái, số, font hay nhãn nào trong ảnh cảnh; cảm giác tả thực, chi tiết ảnh chụp, hiệu ứng 3D, chất liệu tranh sơn; cảnh phức tạp, nền dày đặc, trang trí rườm rà, màu quá rực.
- **Ngoại lệ bàn tay vẽ:** nếu người dùng nói rõ chữ trên thân bút trong `drawing-hand.png` là dấu nhận diện của họ và muốn giữ, thì được giữ; nó không tính là chữ trong ảnh cảnh. Khi chưa có xác nhận đó, coi như ảnh không được có chữ.

## Điểm dừng xác nhận (bắt buộc)

Trong quy trình mặc định, **sau mỗi bước phải dừng lại và chờ người dùng xác nhận rõ ràng** rồi mới sang bước tiếp. Trước khi được xác nhận, không được tạo ảnh, annotation, ảnh xem trước, video hay file ghép của bước sau. Không được coi "chưa trả lời", "đã cho phép chung chung trước đó" hay "người dùng không phản đối" là xác nhận. Khi người dùng yêu cầu sửa bước trước, chỉ làm lại đúng bước đó, xong lại chờ xác nhận.

Ngoại lệ duy nhất: **tạo xong file annotation JSON thì phải lập tức mở trang xem trước và nạp thư mục chứa JSON đó**. Việc này thuộc kết quả của bước 3, không cần chờ xác nhận riêng. Nếu File System Access API của trình duyệt đòi thao tác của người dùng, dùng giao diện trình duyệt chọn đúng thư mục đã biết; không được vì thế mà hỏi thêm xác nhận hay bảo người dùng tự mở.

## Ba kiểu đầu vào

| Người dùng đưa | Bắt đầu từ bước |
|---|---|
| **Chủ đề** (một câu, một ý tưởng) | Bước 0a: viết kịch bản |
| **Kịch bản / lời dẫn** (đoạn văn) | Bước 0b: tạo giọng đọc, sinh SRT |
| **File SRT** | Bước 1 (quy trình gốc); làm xong có thể thêm bước 8 |

Khi bắt đầu từ chủ đề hoặc kịch bản, dùng **giọng đọc dẫn nhịp**: tạo giọng trước, lấy độ dài giọng thật để sinh SRT; phân cảnh và thời gian vẽ đều theo SRT này, nên video tự nhiên không có khoảng lặng thừa, không cần bước nhịp gọn.

## Quy trình

0a. **Viết kịch bản (chỉ khi đầu vào là chủ đề).** Dựa vào chủ đề, thời lượng mục tiêu (mặc định 60 giây, khoảng 180–220 từ tiếng Việt), người xem và giọng văn, viết lời dẫn: một câu mở gây tò mò → thân (câu chuyện/luận điểm) → một câu kết đọng lại. Mỗi câu đọc không quá khoảng 5 giây, dễ minh hoạ (có người, vật, hành động cụ thể); giữa các đoạn cách một dòng trống (cuối đoạn sẽ nghỉ lâu hơn). Lưu vào `assets/whiteboard/<tên-dự-án>/script.md`, kèm một câu thông điệp chính. **Xong thì dừng, chờ người dùng duyệt kịch bản.**

0b. **Tạo giọng đọc, sinh SRT (đầu vào chủ đề/kịch bản).** Chỉ làm sau khi kịch bản được duyệt:
   ```bash
   python scripts/script_to_srt.py script.md --output draft.srt        # cắt câu; dòng cuối PAUSES=…
   <ENV_PY> scripts/tts_narration.py draft.srt --output narration.m4a \
       --retime-out input.srt --pause <từng mục trong PAUSES>            # độ dài giọng thật → mốc chính thức
   ```
   `input.srt` là phụ đề cho mọi bước sau; `narration.m4a` là giọng đọc cuối cùng (bước 8 dùng lại cache). Báo cho người dùng: cách cắt câu, tổng thời lượng, giọng đã dùng, và mời nghe thử `narration.m4a`. Giọng/tốc độ/engine lấy theo `.env` (`TTS_PROVIDER` / `TTS_VOICE` / `TTS_SPEED`); người dùng chỉ định thì dùng `--provider` / `--voice` / `--speed`. **Xong thì dừng, chờ người dùng duyệt giọng đọc và cách cắt câu.**

1. **Đọc phụ đề, lên phương án hình (chưa tạo ảnh).** Dùng `scripts/parse_srt.py` tách SRT thành từng câu và gợi ý chia cảnh 20–35 giây/cảnh. Từ đó đưa ra phương án: mỗi cảnh có số thứ tự, ý chính, đối tượng trong hình, khoảng phụ đề tương ứng và `sceneDurationMs`. Mỗi cảnh chỉ một ý chính. **Xong thì dừng, chờ duyệt phương án.**
2. **Tạo ảnh nét vẽ.** Chỉ làm sau khi phương án được duyệt. Theo "Quy chuẩn hình ảnh", tạo từng ảnh 16:9 nền giấy kem `#F5EBD7`, các đối tượng cách nhau đủ rộng để dễ chia vùng; không có chữ, ảnh chụp phức tạp, đối tượng chồng lên nhau hay yếu tố trái quy chuẩn. Nếu không tự tạo ảnh được, ghi prompt từng cảnh vào `IMAGE_PROMPTS.md` và nhờ người dùng tạo, lưu đúng tên `scene-XX-<tên>.png`. **Xong thì dừng, cho xem ảnh và chờ duyệt.**
3. **Đọc phụ đề trước, xem ảnh sau, rồi chia vùng và mở trang xem trước.** Chỉ làm sau khi ảnh được duyệt. Đọc phụ đề của cảnh, **thực sự mở xem ảnh** và lấy kích thước pixel gốc; không được đoán hình chỉ từ phụ đề, cũng không được xếp thứ tự máy móc theo vị trí. Rút ra các sự kiện trong phụ đề, gắn từng đối tượng nhìn thấy trong ảnh với sự kiện, xếp thứ tự vẽ theo mạch "bối cảnh → nhân vật/đồ vật chính → hành động, xung đột hoặc biến đổi → phản ứng/kết quả". Sau đó tạo `<tên-ảnh>.annotation.json`. Tạo xong, lập tức mở `assets/preview.html` bằng trình duyệt mặc định và dùng nút "Mở thư mục" nạp **thư mục chứa file annotation** (toàn bộ `<tên>.png` + `<tên>.annotation.json`); không được chỉ đưa đường dẫn hay bảo người dùng tự làm. **Trang xem trước đã nạp xong thì dừng, chờ duyệt annotation và bản xem trước.**
4. **Xuất ảnh kiểm tra vùng.** Chỉ làm sau khi annotation được duyệt. Dùng `render_annotation_preview.py` xuất ảnh đánh số/hướng vẽ, đối chiếu: thứ tự vùng khớp mạch truyện, mọi vùng nằm trong ảnh, đối tượng chồng lấn đã được `protectedRegions` bảo vệ. **Xong thì dừng, chờ duyệt ảnh kiểm tra.**
5. **Chỉnh và lưu trên trang xem trước.** Chỉ làm sau khi ảnh kiểm tra được duyệt, trên trang xem trước đã mở và nạp đúng thư mục. Mặc định (chưa phát) hiện ảnh đầy đủ và các khung vùng. Canvas là **bản mô phỏng bằng hình chữ nhật**: kéo cạnh/góc để sửa `region`; khung bên phải sửa tên, hướng, **bắt đầu (ms) / kết thúc (ms)** (thời lượng = kết thúc − bắt đầu, chỉ đọc) và **phụ đề**; kéo danh sách để **đổi thứ tự** (tự đánh lại `sequence`); chọn vùng nào thì phụ đề tương ứng được tô sáng; kéo thanh thời gian hoặc bấm phát để xem (vùng chưa tới lượt không hiện); `direction` chỉ ảnh hưởng bản mô phỏng. Sửa xong bấm "Lưu cảnh này / Lưu tất cả" để ghi lại `.annotation.json` gốc (kèm `subtitle` của từng vùng, và đặt `sceneDurationMs` = thời điểm vùng cuối kết thúc + 0,5 giây). **Lưu xong thì dừng, chờ duyệt annotation và thời gian cuối cùng.**
6. **Render bằng dòng lệnh.** Chỉ làm sau khi annotation và thời gian được duyệt. Dùng `render_stream_whiteboard.py` render từng cảnh ra MP4, kiểm tra ba thời điểm: mở đầu, giữa một vùng có chồng lấn, và cuối cảnh. **Xong thì dừng, chờ duyệt video từng cảnh.**
7. **Ghép các cảnh (khi có nhiều cảnh).** Chỉ làm sau khi mọi cảnh được duyệt. Dùng `merge_scenes.py` ghép theo thứ tự thành một video. **Xong thì dừng, chờ duyệt video ghép.**
8. **Gắn phụ đề + ghép giọng đọc (mặc định với đầu vào chủ đề/kịch bản; với đầu vào SRT thì làm khi người dùng yêu cầu).** Chỉ làm sau khi video ghép được duyệt. Trước hết dùng filter `subtitles` của ffmpeg gắn `input.srt` vào hình (nền phụ đề màu giấy để không đè nét vẽ, xem mục "Lệnh" bước 8), sau đó chạy `tts_narration.py input.srt --video <video có phụ đề>` để ghép giọng (lấy từ cache, không gọi lại API). Kiểm tra khung đầu/giữa/cuối và phân bố khoảng lặng (`silencedetect`), bảo đảm giọng, phụ đề và hình khớp nhau. **Xong thì dừng, bàn giao video cuối.**

## Thư mục dự án

Tạo trong dự án của người dùng:

```text
assets/whiteboard/<tên-dự-án>/
  script.md                            # kịch bản (nếu bắt đầu từ chủ đề/kịch bản)
  input.srt                            # phụ đề chính thức
  scene-01-<tên>.png
  scene-01-<tên>.annotation.json       # cùng tên với png
  scene-01-<tên>-whiteboard.mp4        # video cảnh
  scene-01-<tên>-preview.mp4           # đoạn xem thử (trang xem trước tạo, độ phân giải thấp)
  tts-cache/                           # giọng đọc từng câu (dùng lại, không tốn phí lần 2)
```

Ảnh và cấu hình phải cùng tên: `foo.png` ↔ `foo.annotation.json`. Trang xem trước dựa vào đó để tự nạp cấu hình.

## Xếp thứ tự theo nghĩa và toạ độ pixel (bắt buộc)

1. **Căn cứ đọc:** trước khi chia vùng phải có cả phụ đề lẫn ảnh gốc đã được mở xem. Thiếu một trong hai thì hỏi trước, không được tạo annotation.
2. **Căn cứ thứ tự:** `sequence`, `startMs` và `label` phải phản ánh trình tự sự kiện trong phụ đề, không chỉ theo trái→phải, trên→dưới hay độ nổi bật.
3. **Căn cứ toạ độ:** mỗi vùng ghi `x`, `y`, `width`, `height` bằng số nguyên pixel trên hệ toạ độ ảnh gốc, gốc ở góc trên bên trái; cấm phần trăm, tỉ lệ, toạ độ ước lượng hay bỏ trống kích thước. `canvas.width` / `canvas.height` phải bằng đúng kích thước pixel ảnh gốc.
4. **Trường của mỗi vùng:** gồm `sequence`, `narrativeRole`, `subtitle`, `region`, `reveal`, `handPath`. `narrativeRole` mô tả bằng tiếng Việt vai trò của vùng trong mạch truyện; `subtitle` lưu câu phụ đề ứng với vùng (lấy từ SRT, để trang xem trước liên kết và dùng về sau); `sequence` liên tục từ 1.
5. **Kiểm tra:** trước khi xuất ảnh kiểm tra, xem từng vùng có nằm trong ảnh, có phủ đúng đối tượng, có khớp sự kiện phụ đề không; đối tượng chồng lấn phải được `protectedRegions` bảo vệ rồi mới vẽ.

## Mô hình thời gian (riêng cho cách vẽ nét liền)

- **Tổng thời lượng cảnh** `sceneDurationMs` lấy từ khoảng phụ đề của cảnh (`scenes[].sceneDurationMs` của `parse_srt.py`).
- **Các vùng vẽ nối tiếp:** chỉ có một cây bút, nên các vùng trong cùng cảnh nên **nối tiếp nhau về thời gian** (`startMs` không chồng lên nhau): vùng sau bắt đầu tại `startMs + durationMs` của vùng trước (có thể thêm 100–300 ms nghỉ). Nếu `startMs` chồng nhau, renderer vẫn xử lý theo thứ tự, nhưng nhìn sẽ không còn là vẽ song song.
- **Trong một vùng, ink → color:** `durationMs` của mỗi vùng được chia `ink:color = 2:1` thành đoạn đi nét và đoạn tô màu. `durationMs` lấy từ **thời gian bắt đầu/kết thúc** trên trang xem trước (kết thúc − bắt đầu), có thể khớp với thời lượng câu phụ đề tương ứng; ước lượng ban đầu có thể dùng 150 pixel/giây × quãng đường vẽ.
- **Giữ hình cuối:** vẽ xong mọi vùng thì tự kéo dài tới `sceneDurationMs`, bảo đảm cuối cảnh giữ ảnh hoàn chỉnh ít nhất 0,5 giây.
- `reveal.direction` với cách vẽ nét liền **không quyết định nét bút thật** (nét bút do khung xương/lưới tự sinh), chỉ dùng cho bản mô phỏng trên trang xem trước; giữ lại để trang xem trước hoạt động.

## Bất biến của mặt nạ (tầng dàn dựng, bắt buộc)

- Tại thời điểm `t`, một vùng chỉ được hiện các pixel khi `reveal.startMs ≤ t` và không vượt quá tiến độ vẽ hiện tại; vùng chưa bắt đầu không được lộ bất kỳ nét, mảng màu hay hình ảnh nào.
- **Phạm vi được phép** của mỗi vùng = khung `region` trừ đi `region` của **mọi vùng vẽ sau**, rồi trừ tiếp `reveal.protectedRegions` của chính nó. Nét bút bị giới hạn trong phạm vi này nên vùng sau không bị lộ sớm.
- `protectedRegions` dùng cùng hệ toạ độ pixel nguyên như `region`, dùng khi khung quá rộng, đối tượng chồng nhau hoặc nét nền có thể lộ ra.
- Renderer đã thực hiện đúng trình tự "chỉ vẽ trong phạm vi được phép → vùng sau và vùng bảo vệ tự nhiên không bị chạm"; bản mô phỏng trên trang xem trước dùng phép trừ `destination-out` tương đương để minh hoạ cùng cách dàn dựng.

## Ví dụ cấu hình

```json
{
  "sceneId": "scene-01",
  "canvas": { "width": 1672, "height": 941 },
  "storyBasis": "Tóm tắt các sự kiện trong phụ đề của cảnh",
  "sceneDurationMs": 9000,
  "elements": [
    {
      "id": "boy",
      "label": "Cậu bé ôm sách",
      "sequence": 1,
      "narrativeRole": "Người đang cần giúp đỡ",
      "subtitle": "Chiều ấy, Nam thấy một cậu bé ôm chồng sách đứng trú mưa.",
      "type": "character",
      "region": { "x": 180, "y": 405, "width": 285, "height": 465 },
      "reveal": { "direction": "top_to_bottom", "startMs": 300, "durationMs": 2600, "maskPaddingPx": 0, "protectedRegions": [] },
      "handPath": { "start": [322, 405], "end": [322, 869], "easing": "easeInOut" }
    }
  ]
}
```

> `direction` / `handPath` chỉ dùng cho bản mô phỏng trên trang xem trước; nét bút trong video do renderer tự sinh, không cần chỉnh kỹ.

## Lệnh

Mọi script render chạy bằng Python trong `.venv` của skill (cô lập thư viện). `<ENV_PY>` là `.venv\Scripts\python.exe` (Windows) hoặc `.venv/bin/python` (macOS/Linux).

1. **Chuẩn bị môi trường** (lần đầu hoặc khi thiếu thư viện):
   ```bash
   python scripts/prepare_env.py --check   # chỉ kiểm tra; thành công thì dòng cuối in ENV_PY=<đường dẫn>
   python scripts/prepare_env.py           # thiếu thì tạo .venv và cài opencv-python/numpy/av/Pillow/edge-tts
   ```
2. **Kịch bản → SRT nháp** (đầu vào chủ đề/kịch bản): cắt theo câu (lời thoại trong ngoặc kép không bị tách, câu quá dài cắt ở dấu phẩy, câu quá ngắn gộp với câu sau); dòng tiêu đề `#` và dòng trống không được đọc; dòng trống chia đoạn, dòng cuối `PAUSES=` liệt kê số thứ tự câu cuối mỗi đoạn, dùng làm các tham số `tts_narration.py --pause`.
   ```bash
   python scripts/script_to_srt.py script.md --output draft.srt [--max-chars 80] [--min-chars 12]
   ```
3. **Đọc phụ đề + gợi ý chia cảnh:**
   ```bash
   python scripts/parse_srt.py <phụ-đề.srt> --target-sec 30 --min-sec 25 --max-sec 35
   ```
4. **Ảnh kiểm tra vùng (đánh số):**
   ```bash
   <ENV_PY> scripts/render_annotation_preview.py <ảnh> <annotation> <ảnh-kiểm-tra>
   ```
5. **Trang xem trước (không cần server):** mở `assets/preview.html` bằng Chrome / Edge, bấm "Mở thư mục" chọn thư mục → nạp mọi ảnh + annotation cùng tên → kéo chỉnh → "Lưu" ghi lại file gốc. Ghi trực tiếp cần File System Access API (Chrome/Edge); trình duyệt khác thì tải về rồi chép đè thủ công. Render vẫn chạy bằng dòng lệnh (bước 6).
6. **Render một cảnh:**
   ```bash
   <ENV_PY> scripts/render_stream_whiteboard.py <ảnh> <annotation> <ra.mp4> assets/drawing-hand.png \
       [--ink-path grid|skeleton] [--color-fill contour-wipe|brush] [--total-ms <mili-giây>]
   ```
   Không có `--total-ms` thì dùng `sceneDurationMs` trong annotation. Dòng cuối in `OUTPUT=<đường dẫn>`.
7. **Ghép các cảnh:**
   ```bash
   <ENV_PY> scripts/merge_scenes.py --inputs canh1.mp4 canh2.mp4 canh3.mp4 --output final.mp4
   ```
8. **Gắn phụ đề** (chữ xám đậm trên nền màu giấy, không đè nét vẽ):
   ```bash
   ffmpeg -i final.mp4 -vf "subtitles=input.srt:force_style='FontName=Arial,FontSize=15,PrimaryColour=&H00303030,OutlineColour=&H10D7EBF5,BorderStyle=3,Outline=6,Shadow=0,MarginV=14'" \
       -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart final-sub.mp4
   ```
   Trên Windows, đường dẫn trong `subtitles=` nên là đường dẫn tương đối (tránh dấu hai chấm của ổ đĩa bị hiểu nhầm là cú pháp filter).
9. **Giọng đọc:** tạo giọng từng câu theo SRT, khớp mốc thời gian rồi ghép vào video (không render lại hình). Engine `--provider vbee|edge` (mặc định theo `TTS_PROVIDER` trong `.env`): `vbee` cần `VBEE_APP_ID` / `VBEE_ACCESS_TOKEN`, tính phí theo ký tự, `--voice` là **mã giọng đầy đủ** copy từ giao diện Vbee (gửi nguyên văn cho API); `edge` dùng [rany2/edge-tts](https://github.com/rany2/edge-tts), miễn phí, mặc định `vi-VN-NamMinhNeural` (nữ: `vi-VN-HoaiMyNeural`). Tốc độ `--speed` (1.0 = bình thường; với Edge, 1.1 → `+10%`). Giọng từng câu được lưu ở `<thư-mục-srt>/tts-cache/`, chạy lại không gọi API lần nữa.
   ```bash
   <ENV_PY> scripts/tts_narration.py <phụ-đề.srt> --output narration.m4a --video final-sub.mp4 \
       [--provider vbee|edge] [--voice <mã-giọng>] [--speed 1.1]
   ```
   Dòng cuối in `OUTPUT=<video có giọng>` (mặc định `<video>-voice.mp4`). Câu nào dài hơn khung thời gian thì tự tăng tốc và cảnh báo. Mặc định cắt khoảng lặng đầu/cuối mỗi câu (tắt bằng `--no-trim`).
10. **Nhịp gọn (tuỳ chọn, cho đầu vào SRT có nhiều khoảng lặng):** sắp lại phụ đề theo độ dài giọng thật, rồi co giãn thời gian vẽ trong annotation theo từng đoạn tuyến tính; render lại thì hình và giọng khớp nhau, gần như không có khoảng trống:
    ```bash
    <ENV_PY> scripts/tts_narration.py input.srt --output narration.m4a --provider edge \
        --retime-out input.tight.srt --gap 0.3 --pause 6=0.8 --tail 1.0
    <ENV_PY> scripts/retime_annotations.py --old-srt input.srt --new-srt input.tight.srt \
        --annotations canh1.annotation.json canh2.annotation.json   # ra <tên>.tight.annotation.json, file gốc giữ nguyên
    ```
    Sau đó render các cảnh bằng `.tight.annotation.json`, ghép, gắn phụ đề `input.tight.srt`, rồi chạy bước 9 với `input.tight.srt` (giọng lấy từ cache).

## Kiểm tra chất lượng

Trước/sau khi render, xác nhận:

- Khung đầu tiên là nền giấy kem sạch, chưa lộ nét nào.
- Đã đọc phụ đề tương ứng và thực sự xem ảnh gốc; `canvas` khớp kích thước ảnh, mọi `region` là pixel nguyên và nằm trong ảnh.
- `sequence`, `startMs` khớp trình tự sự kiện trong phụ đề; số thứ tự/nhãn/vùng trên ảnh kiểm tra lấy từ cùng một file annotation.
- Kiểm tra ba thời điểm: mở đầu, giữa một vùng chồng lấn, sau khi vẽ xong mọi vùng — vùng chưa vẽ không lộ, vùng bảo vệ không rò, khung cuối hiện đủ ảnh gốc.
- Đầu bút bám sát nét đang vẽ; ảnh nét rõ có thể dùng `--ink-path skeleton` cho nét bám hơn.
- Vẽ xong mọi vùng thì giữ ảnh hoàn chỉnh ít nhất 0,5 giây.
- Ghép nhiều cảnh xong, thứ tự và thời lượng khớp phân cảnh.
- Có giọng đọc: giọng, phụ đề và hình khớp nhau; không có khoảng lặng dài ngoài các chỗ nghỉ cố ý.

Muốn đổi hiệu ứng thì chỉnh annotation (vùng/thứ tự/thời gian) trên trang xem trước (`assets/preview.html`) và lưu trước, rồi mới render bằng dòng lệnh; đừng render đi render lại khi chưa sửa gì.
