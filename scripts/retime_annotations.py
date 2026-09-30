#!/usr/bin/env python3
"""
按新字幕时间轴重排多幕标注的时序（配合 tts_narration.py --retime-out 使用）。

原理：新旧 SRT 字幕一一对应，取每条字幕的开始时刻（及末条结束）作为锚点，
在锚点之间分段线性映射 旧全局时间 → 新全局时间。各幕按给定顺序首尾相接
（全局起点 = 前面各幕 sceneDurationMs 之和），元素的 startMs / 结束时刻与
幕边界都经映射后换回幕内时间；区域、顺序、方向等不变。

输出写到新文件（默认 <名称>.tight.annotation.json），不覆盖原标注。

用法：
  python retime_annotations.py --old-srt input.srt --new-srt input.tight.srt \
      --annotations scene-01.annotation.json scene-02.annotation.json [--suffix .tight]
"""
from __future__ import annotations

import argparse
import bisect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_srt import parse_srt  # noqa: E402

END_HOLD_MS = 500  # 所有区域画完后至少停留完整原图的时长


def build_mapper(old: list[dict], new: list[dict]):
    xs = [c["startMs"] for c in old] + [old[-1]["endMs"]]
    ys = [c["startMs"] for c in new] + [new[-1]["endMs"]]

    def mapper(t: float) -> int:
        if t <= xs[0]:
            return round(ys[0] + (t - xs[0]))
        if t >= xs[-1]:
            return round(ys[-1] + (t - xs[-1]))
        i = bisect.bisect_right(xs, t) - 1
        span = xs[i + 1] - xs[i]
        k = (t - xs[i]) / span if span else 0.0
        return round(ys[i] + k * (ys[i + 1] - ys[i]))

    return mapper


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="按新字幕时间轴重排标注时序")
    p.add_argument("--old-srt", required=True, help="标注原本依据的 SRT")
    p.add_argument("--new-srt", required=True, help="重排后的 SRT")
    p.add_argument("--annotations", nargs="+", required=True, help="按播放顺序的 .annotation.json")
    p.add_argument("--suffix", default=".tight", help="输出文件名后缀（默认 .tight）")
    args = p.parse_args(argv)

    old = parse_srt(Path(args.old_srt).read_text(encoding="utf-8-sig"))
    new = parse_srt(Path(args.new_srt).read_text(encoding="utf-8-sig"))
    if len(old) != len(new) or not old:
        print(f"[err] 新旧字幕条数不一致: {len(old)} vs {len(new)}", file=sys.stderr)
        return 1
    remap = build_mapper(old, new)

    old_offset = 0
    for ann_path in map(Path, args.annotations):
        ann = json.loads(ann_path.read_text(encoding="utf-8"))
        old_dur = ann["sceneDurationMs"]
        new_start, new_end = remap(old_offset), remap(old_offset + old_dur)

        last_end = 0
        for el in ann["elements"]:
            rv = el["reveal"]
            g0 = old_offset + rv["startMs"]
            s, e = remap(g0) - new_start, remap(g0 + rv["durationMs"]) - new_start
            rv["startMs"], rv["durationMs"] = s, max(1, e - s)
            last_end = max(last_end, s + rv["durationMs"])
        ann["sceneDurationMs"] = max(new_end - new_start, last_end + END_HOLD_MS)

        out = ann_path.with_name(ann_path.name.replace(".annotation.json", f"{args.suffix}.annotation.json"))
        out.write_text(json.dumps(ann, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {ann_path.name}: {old_dur / 1000:.1f}s → {ann['sceneDurationMs'] / 1000:.1f}s  => {out.name}")
        old_offset += old_dur
    return 0


if __name__ == "__main__":
    sys.exit(main())
