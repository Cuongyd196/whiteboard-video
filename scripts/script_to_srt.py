#!/usr/bin/env python3
"""
剧本 → 草稿 SRT：把一段旁白剧本（.txt / .md）按句切成字幕条，写出带估算时间的 SRT。

用途：从「主题/剧本」起步时的第一步。草稿 SRT 只用于切句，真实时间轴随后由
  tts_narration.py --retime-out 按语音实长重排（配音驱动节奏）。

切句规则：
  - 按句末标点（. ! ? … 以及中文 。！？）断句，引号跟随所在句子；
  - 超过 --max-chars 的句子再按逗号/分号切开；
  - 过短的句子（< --min-chars）并入下一句；
  - 以 # 开头的行（Markdown 标题）和空行不朗读；空行分段 → 段末字幕建议更长停顿。
估算时长：按 --cps 字符/秒，至少 1.5 秒。

用法：
  python script_to_srt.py <剧本.txt> --output draft.srt [--max-chars 80] [--min-chars 12] [--cps 14]
末行输出 PAUSES=<序号=秒,...>（段落末尾字幕），可直接展开为 tts_narration.py 的 --pause 参数。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 一句 = 尽量短的文本 + 句末标点（连同收尾引号/括号），其后是空白或段尾
_SENTENCE = re.compile(r".+?(?:[.!?…。！？]+[\"”’»)\]]*(?=\s|$)|$)")
_CLAUSE_END = re.compile(r"(?<=[,;:，；：])\s+")


def _fmt(ms: int) -> str:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _quote_open(text: str) -> bool:
    return text.count("“") > text.count("”") or text.count('"') % 2 == 1


def _split_long(sentence: str, max_chars: int) -> list[str]:
    if len(sentence) <= max_chars:
        return [sentence]
    parts, cur = [], ""
    for clause in _CLAUSE_END.split(sentence):
        if cur and len(cur) + 1 + len(clause) > max_chars:
            parts.append(cur)
            cur = clause
        else:
            cur = f"{cur} {clause}".strip()
    if cur:
        parts.append(cur)
    return parts


def split_script(text: str, max_chars: int, min_chars: int) -> list[tuple[str, bool]]:
    """返回 [(字幕文本, 是否段落末尾)]。"""
    paragraphs, buf = [], []
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            continue
        buf.append(line)
    if buf:
        paragraphs.append(" ".join(buf))

    cues: list[tuple[str, bool]] = []
    for para in paragraphs:
        pieces: list[str] = []
        pending = ""
        for sent in _SENTENCE.findall(para):
            pending = f"{pending} {sent.strip()}".strip()
            if _quote_open(pending):  # 引号内的多句台词不拆开
                continue
            pieces.extend(_split_long(pending, max_chars))
            pending = ""
        if pending:
            pieces.extend(_split_long(pending, max_chars))
        pieces = [p for p in pieces if p]
        merged: list[str] = []
        for p in pieces:
            if merged and len(merged[-1]) < min_chars and len(merged[-1]) + 1 + len(p) <= max_chars:
                merged[-1] = f"{merged[-1]} {p}"
            else:
                merged.append(p)
        cues.extend((m, i == len(merged) - 1) for i, m in enumerate(merged))
    return cues


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="剧本 → 草稿 SRT（按句切分，估算时间）")
    p.add_argument("script", help="旁白剧本 (.txt / .md)")
    p.add_argument("--output", required=True, help="草稿 SRT 输出路径")
    p.add_argument("--max-chars", type=int, default=80, help="单条字幕最长字符数（默认 80）")
    p.add_argument("--min-chars", type=int, default=12, help="短于此长度的句子并入下一句（默认 12）")
    p.add_argument("--cps", type=float, default=14.0, help="估算语速：字符/秒（默认 14）")
    p.add_argument("--para-pause", type=float, default=0.8, help="段落末尾建议停顿秒数（默认 0.8）")
    args = p.parse_args(argv)

    text = Path(args.script).read_text(encoding="utf-8-sig")
    cues = split_script(text, args.max_chars, args.min_chars)
    if not cues:
        print("[err] 剧本中没有可朗读的文字", file=sys.stderr)
        return 1

    blocks, cursor, pauses = [], 0, []
    for i, (cue, para_end) in enumerate(cues, 1):
        dur = max(1500, round(len(cue) / args.cps * 1000))
        blocks.append(f"{i}\n{_fmt(cursor)} --> {_fmt(cursor + dur)}\n{cue}\n")
        cursor += dur
        if para_end and i < len(cues):
            pauses.append(f"{i}={args.para_pause}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(blocks), encoding="utf-8")

    print(f"字幕条: {len(cues)}  估算时长: {cursor / 1000:.1f}s", file=sys.stderr)
    for i, (cue, para_end) in enumerate(cues, 1):
        print(f"  {i:>2}{' ¶' if para_end else '  '} {cue}", file=sys.stderr)
    print(f"SRT={out.resolve()}")
    print(f"PAUSES={','.join(pauses)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
