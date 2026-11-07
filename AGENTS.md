# AGENTS.md

Hướng dẫn cho mọi AI coding agent (Codex, Antigravity, Cursor, GitHub Copilot, Gemini CLI, Claude Code…) làm việc trong repo này.

## Repo này là gì

Skill **whiteboard-video**: biến một chủ đề, kịch bản lời dẫn hoặc file phụ đề `.srt` thành video vẽ tay bảng trắng hoàn chỉnh (giọng đọc + phụ đề).

**Khi người dùng muốn làm / sửa video vẽ tay, video whiteboard, video bảng trắng, hoặc đưa chủ đề / kịch bản / SRT để làm video: đọc toàn bộ [`SKILL.md`](SKILL.md) ở thư mục gốc và làm đúng theo đó**, kể cả các điểm dừng chờ người dùng duyệt sau mỗi bước.

## Quy tắc chung

- Mọi trao đổi, phân cảnh, nhãn vùng, ghi chú viết bằng **tiếng Việt**, trừ khi người dùng yêu cầu khác.
- Mọi lệnh chạy từ thư mục gốc repo.
- Python dùng `.venv` ở thư mục gốc (Windows `.venv\Scripts\python.exe`, macOS/Linux `.venv/bin/python`). Chưa có thì chạy `python scripts/prepare_env.py`.
- Cần `ffmpeg` / `ffprobe` trong PATH.
- Dự án video đặt trong `assets/whiteboard/<tên-dự-án>/`.

## Giọng đọc (TTS)

- Script: `scripts/tts_narration.py`. Engine chọn bằng `TTS_PROVIDER` trong `.env` hoặc `--provider cit|edge|vbee`.
- Mặc định **`cit` = CIT Voice Studio** chạy offline trên máy (`http://127.0.0.1:8001`). Người dùng phải mở ứng dụng trước; kiểm tra bằng `GET /health`. Giọng mặc định `Hải Đăng`; danh sách giọng ở `GET /voices`.
- Mỗi engine một nhóm biến riêng: `CIT_VOICE`/`CIT_SPEED`, `EDGE_VOICE`/`EDGE_SPEED`, `VBEE_VOICE`/`VBEE_SPEED`. Xem `.env.example`.
- Key nằm trong `.env` (đã gitignore). **Không** đọc to, chép hay commit key.

## Lối vào skill theo từng agent

Nội dung skill duy nhất là `SKILL.md` ở thư mục gốc. Các file dưới đây chỉ là lối vào để agent tự phát hiện skill:

| Agent | File |
|---|---|
| Claude Code | `.claude/skills/whiteboard-video/SKILL.md` |
| Codex | `.agents/skills/whiteboard-video/SKILL.md` (+ `agents/openai.yaml`) |
| Antigravity | `.agent/skills/whiteboard-video/SKILL.md` |
| Gemini CLI | `GEMINI.md` → file này |
| Cursor, Copilot, agent khác | `AGENTS.md` (file này) |

**Chỉ sửa `SKILL.md` gốc.** Ba file `SKILL.md` lối vào (và `openai.yaml` của Codex) được sinh tự động, không sửa tay. Sau khi đổi `name` / `description` trong frontmatter, hoặc sửa `agents/openai.yaml`, chạy:

```bash
python scripts/sync_skill_entries.py          # ghi lại các file lối vào
python scripts/sync_skill_entries.py --check  # chỉ kiểm tra (exit 1 nếu lệch)
```
