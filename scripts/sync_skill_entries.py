#!/usr/bin/env python3
"""
Sinh lại các file lối vào skill cho từng AI agent từ SKILL.md ở thư mục gốc.

Chỉ cần sửa SKILL.md gốc (cả frontmatter name/description lẫn quy trình), rồi chạy:
  python scripts/sync_skill_entries.py          # ghi lại các file lối vào
  python scripts/sync_skill_entries.py --check  # chỉ kiểm tra, lệch thì exit 1

File lối vào được sinh:
  .claude/skills/<name>/SKILL.md   Claude Code
  .agents/skills/<name>/SKILL.md   Codex (kèm agents/openai.yaml chép từ agents/openai.yaml gốc)
  .agent/skills/<name>/SKILL.md    Google Antigravity
AGENTS.md / GEMINI.md viết tay, không cần đồng bộ.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIRS = [".claude/skills", ".agents/skills", ".agent/skills"]

BODY = """
# Video vẽ tay bảng trắng (lối vào skill cấp dự án)

File này được sinh tự động bởi `scripts/sync_skill_entries.py` — **đừng sửa trực tiếp**, hãy sửa `SKILL.md` ở thư mục gốc rồi chạy lại script.

File này chỉ là lối vào của skill cấp dự án. Toàn bộ quy trình, các điểm dừng xác nhận, quy tắc chia vùng và cách dùng script nằm trong **`SKILL.md` ở thư mục gốc dự án**.

**Trước khi làm bất cứ việc gì, đọc toàn bộ `SKILL.md` ở thư mục gốc dự án và làm đúng theo đó.**

- Mọi lệnh chạy từ thư mục gốc dự án (`scripts/`, `assets/` tính từ thư mục gốc).
- Python: dùng `.venv` ở thư mục gốc (Windows `.venv\\Scripts\\python.exe`; macOS/Linux `.venv/bin/python`); chưa có thì chạy `python scripts/prepare_env.py` trước.
- Key giọng đọc và giọng mặc định nằm trong `.env` ở thư mục gốc; không chép key vào khung chat hay file khác.
- Mọi trao đổi, phân cảnh, nhãn vùng và ghi chú viết bằng tiếng Việt.
"""


def read_frontmatter(path: Path) -> tuple[str, str]:
    """Trả về (khối frontmatter nguyên văn gồm cả hai dòng ---, name)."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        raise SystemExit(f"[err] {path} thiếu frontmatter ---")
    name = re.search(r"^name:\s*(.+)$", m.group(1), re.M)
    if not name:
        raise SystemExit(f"[err] {path} thiếu trường name")
    return m.group(0).replace("\r\n", "\n"), name.group(1).strip()


def expected_files() -> dict[Path, bytes]:
    front, name = read_frontmatter(ROOT / "SKILL.md")
    entry = (front + BODY).encode("utf-8")
    files = {ROOT / d / name / "SKILL.md": entry for d in AGENT_DIRS}
    yaml = ROOT / "agents" / "openai.yaml"
    if yaml.exists():
        files[ROOT / ".agents/skills" / name / "agents" / "openai.yaml"] = yaml.read_bytes()
    return files


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Đồng bộ file lối vào skill cho các AI agent")
    p.add_argument("--check", action="store_true", help="chỉ kiểm tra, không ghi")
    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

    stale = []
    for path, content in expected_files().items():
        current = path.read_bytes().replace(b"\r\n", b"\n") if path.exists() else None
        if current == content:
            continue
        stale.append(path.relative_to(ROOT).as_posix())
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    if not stale:
        print("Các file lối vào đã khớp với SKILL.md.")
        return 0
    verb = "Lệch" if args.check else "Đã cập nhật"
    print(f"{verb}:\n  " + "\n  ".join(stale))
    if args.check:
        print("Chạy: python scripts/sync_skill_entries.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
