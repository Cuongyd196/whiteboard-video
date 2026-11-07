#!/usr/bin/env python3
"""
SRT 旁白配音：把 SRT 每条字幕合成语音，按字幕时间轴排成一条旁白音轨，
可选直接混入成片 MP4（视频流不重编码）。

三种引擎（--provider，默认读 .env 的 TTS_PROVIDER，未设置时为 cit）：
  cit   CIT Voice Studio 本地离线 API（默认 http://127.0.0.1:8001），POST /api/tts/generate → WAV。
        免费、离线；需先打开 CIT Voice Studio 应用。--voice 为 GET /voices 里的声音名（如 "Hải Đăng"），
        留空则用当前模型的默认声音。其他机器调用需 CIT_API_KEY。
  vbee  POST /api/v1/tts → request_id → 轮询 GET /api/v1/tts/{id} → 下载 audio_link (mp3)
        需要 VBEE_APP_ID / VBEE_ACCESS_TOKEN，按字符计费。
  edge  rany2/edge-tts（微软 Edge 在线朗读，免费），默认声音 vi-VN-NamMinhNeural。
合成结果按 引擎+文本+声音+语速 缓存，重跑不会重复请求。
某条语音长于其时间槽（到下一条字幕开始）时用 atempo 加速塞入，并打印警告。

默认值从项目根 .env / 环境变量读取：
  TTS_PROVIDER（cit | edge | vbee）
  每个引擎一组：<引擎>_VOICE, <引擎>_SPEED（1.0 = 正常语速）
    CIT_VOICE, CIT_SPEED, CIT_BASE_URL（默认 http://127.0.0.1:8001）, CIT_API_KEY（仅局域网其他机器调用时需要）
    EDGE_VOICE, EDGE_SPEED
    VBEE_VOICE, VBEE_SPEED, VBEE_APP_ID, VBEE_ACCESS_TOKEN
  旧版 TTS_VOICE / TTS_SPEED 仍作后备。

用法：
  <ENV_PY> tts_narration.py <字幕.srt> --output narration.m4a [--video final.mp4 --video-out final-voice.mp4]
                            [--provider cit|vbee|edge] [--voice <声音>] [--speed 1.1] [--cache-dir <目录>]
                            [--retime-out tight.srt --gap 0.3 --pause 6=0.8 --tail 1.0] [--no-trim]
  --retime-out：以语音实长重排时间轴（去掉字幕间空白），再用 retime_annotations.py 同步标注。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_srt import parse_srt  # noqa: E402

API_URL = "https://vbee.vn/api/v1/tts"
CALLBACK_URL = "https://example.com/callback"  # API 要求必填，轮询模式下用占位地址
POLL_INTERVAL_S = 2
POLL_MAX = 30
SAMPLE_RATE = 44100

VBEE_DEFAULT_VOICE = "n_hanoi_male_protrainer_education_vc"
EDGE_DEFAULT_VOICE = "vi-VN-NamMinhNeural"
EDGE_COMMA_TRIES = 4  # 原句失败后最多尝试几个加逗号的变体

CIT_DEFAULT_URL = "http://127.0.0.1:8001"
CIT_DEFAULT_VOICE = "Hải Đăng"  # 当前模型没有此声音时（如 Supertonic）回退到模型默认声音
CIT_TIMEOUT_S = 1800  # 长句在 CPU 上可能较慢


def load_dotenv(path: Path) -> None:
    """极简 .env 读取：KEY=VALUE，忽略注释；已存在的环境变量优先。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _request_json(url: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method="POST" if body is not None else "GET",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "whiteboard-video/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def synthesize(text: str, app_id: str, token: str, voice: str, speed: float) -> str:
    """提交合成并轮询，返回 audio_link。"""
    data = _request_json(API_URL, token, {
        "app_id": app_id,
        "input_text": text,
        "voice_code": voice,
        "audio_type": "mp3",
        "speed_rate": speed,
        "callback_url": CALLBACK_URL,
    })
    if data.get("status") != 1:
        raise RuntimeError(f"Vbee 错误: {data.get('error_message') or data.get('error_code')}")
    result = data.get("result") or {}
    if result.get("audio_link"):
        return result["audio_link"]
    request_id = result.get("request_id")
    if not request_id:
        raise RuntimeError("Vbee 未返回 request_id")

    for _ in range(POLL_MAX):
        time.sleep(POLL_INTERVAL_S)
        try:
            status = _request_json(f"{API_URL}/{request_id}", token)
        except urllib.error.URLError:
            continue
        if status.get("status") != 1:
            continue
        res = status.get("result") or {}
        if res.get("status") == "SUCCESS" and res.get("audio_link"):
            return res["audio_link"]
        if res.get("status") == "FAILURE":
            raise RuntimeError(f"Vbee 合成失败: request_id={request_id}")
    raise RuntimeError(f"Vbee 轮询超时 ({POLL_INTERVAL_S * POLL_MAX}s): request_id={request_id}")


class CitClient:
    """CIT Voice Studio 本地 API（文档见 <CIT_BASE_URL>/cit-voice-studio.md）。"""

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, path: str, body: dict | None = None, timeout: float = 10):
        headers = {"User-Agent": "whiteboard-video/1.0"}
        if body is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        req = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None,
            method="POST" if body is not None else "GET",
            headers=headers,
        )
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            raise RuntimeError(f"CIT HTTP {e.code} {path}: {detail}") from None

    def health(self) -> dict:
        with self._request("/health") as resp:
            return json.loads(resp.read().decode("utf-8"))

    def voices(self) -> list[dict]:
        with self._request("/voices") as resp:
            return json.loads(resp.read().decode("utf-8"))

    def synthesize(self, text: str, voice: str | None, speed: float, out: Path) -> None:
        """POST /api/tts/generate → WAV（带 AI-generated 元数据标记，勿删）。"""
        body = {"text": text, "speed": speed, "format": "wav"}
        if voice:
            body["voice_id"] = voice
        with self._request("/api/tts/generate", body, timeout=CIT_TIMEOUT_S) as resp:
            data = resp.read()
        tmp = out.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(out)


def _is_edge_voice(v: str) -> bool:
    return v.endswith("Neural")


def _is_vbee_voice(v: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(_[a-z0-9]+)+", v))


def _edge_variants(text: str) -> list[str]:
    """原句 ×2，再加上在句中附近词间插入逗号的变体（由中间向两侧）。"""
    words = text.split(" ")
    mid = len(words) // 2
    order = sorted(range(1, len(words)), key=lambda k: abs(k - mid))
    commas = [" ".join(words[:k]) + ", " + " ".join(words[k:]) for k in order
              if not words[k - 1].endswith((",", ".", "!", "?", ":", ";"))]
    return [text, text] + commas[:EDGE_COMMA_TRIES]


def synthesize_edge(text: str, voice: str, speed: float, out: Path) -> None:
    """edge-tts 以原速合成，再用 ffmpeg atempo 调语速（保持音高）。

    Edge 服务端对某些越南语句子会固定返回 NoAudioReceived（带 rate 时更常见），
    与网络无关、重试无效，但在句中加一个逗号即可合成。故：不传 rate；原句重试 2 次，
    仍失败则依次尝试在靠近句中的词间插入逗号（只多一个轻微停顿，内容不变）。
    """
    import edge_tts

    raw = out.with_suffix(".raw.mp3")
    for i, variant in enumerate(_edge_variants(text)):
        try:
            edge_tts.Communicate(variant, voice).save_sync(str(raw))
        except edge_tts.exceptions.NoAudioReceived:
            time.sleep(1)
            continue
        if variant != text:
            print(f"  [warn] Edge 无法合成原句，已改为: {variant}")
        break
    else:
        raise RuntimeError(f"Edge 多次返回 NoAudioReceived: {text}")
    if abs(speed - 1.0) < 1e-3:
        raw.replace(out)
        return
    tmp = out.with_suffix(".part.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", _atempo_chain(speed),
         "-c:a", "libmp3lame", "-q:a", "2", str(tmp)],
        check=True,
    )
    raw.unlink(missing_ok=True)
    tmp.replace(out)


def download(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "whiteboard-video/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        tmp = out.with_suffix(".part")
        tmp.write_bytes(resp.read())
        tmp.replace(out)


def probe_duration(path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(res.stdout.strip())


def trim_silence(clip: Path) -> Path:
    """裁掉 TTS 片段首尾静音（Edge 约首 0.25s + 尾 0.8s），保留 50ms/100ms 余量；结果缓存为 .trim.wav。"""
    out = clip.with_suffix(".trim.wav")
    if not out.exists():
        sr = "silenceremove=start_periods=1:start_threshold=-40dB:start_silence={}"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip),
             "-af", f"{sr.format(0.05)},areverse,{sr.format(0.1)},areverse",
             "-ar", str(SAMPLE_RATE), "-ac", "1", str(out)],
            check=True,
        )
    return out


def _atempo_chain(factor: float) -> str:
    """atempo 单级范围 0.5–2.0，超出时串联。"""
    parts = []
    while factor > 2.0:
        parts.append("atempo=2.0")
        factor /= 2.0
    while factor < 0.5:
        parts.append("atempo=0.5")
        factor /= 0.5
    parts.append(f"atempo={factor:.4f}")
    return ",".join(parts)


def build_track(cues: list[dict], clips: list[Path], output: Path, total_ms: int | None) -> None:
    """每条语音放进 [本条开始, 下一条开始) 的时间槽：过长加速，不足补静音，然后顺序拼接。"""
    inputs: list[str] = []
    filters: list[str] = []
    labels: list[str] = []
    first_start = cues[0]["startMs"]
    if first_start > 0:
        filters.append(f"aevalsrc=0:d={first_start / 1000:.3f}:s={SAMPLE_RATE}[lead]")
        labels.append("[lead]")

    for i, (cue, clip) in enumerate(zip(cues, clips)):
        if i + 1 < len(cues):
            slot_ms = cues[i + 1]["startMs"] - cue["startMs"]
        else:
            slot_ms = max(cue["endMs"], total_ms or 0) - cue["startMs"]
        slot_s = slot_ms / 1000
        dur = probe_duration(clip)
        chain = f"[{i}:a]aresample={SAMPLE_RATE},aformat=channel_layouts=mono"
        if dur > slot_s - 0.05:
            factor = dur / (slot_s - 0.05)
            print(f"  [warn] 字幕 {cue['index']} 语音 {dur:.2f}s 超出时间槽 {slot_s:.2f}s，加速 x{factor:.2f}")
            chain += "," + _atempo_chain(factor)
        chain += f",apad,atrim=0:{slot_s:.3f}[c{i}]"
        inputs += ["-i", str(clip)]
        filters.append(chain)
        labels.append(f"[c{i}]")

    filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[out]")
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(filters), "-map", "[out]",
         "-c:a", "aac", "-b:a", "192k", str(output)],
        check=True,
    )


def retime_cues(cues: list[dict], clips: list[Path], gap_s: float, pauses: dict[int, float],
                tail_s: float) -> list[dict]:
    """以语音实长重排时间轴：每条紧接上一条 + gap（指定字幕后用更长停顿），末条后留 tail。"""
    out: list[dict] = []
    cursor = cues[0]["startMs"]
    for i, (cue, clip) in enumerate(zip(cues, clips)):
        dur_ms = round(probe_duration(clip) * 1000)
        end = cursor + dur_ms
        is_last = i + 1 == len(cues)
        hold_ms = round((tail_s if is_last else pauses.get(cue["index"], gap_s)) * 1000)
        out.append({**cue, "startMs": cursor, "endMs": end + (hold_ms if is_last else 0),
                    "durMs": dur_ms})
        cursor = end + hold_ms
    return out


def _fmt_srt_time(ms: int) -> str:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues: list[dict], path: Path) -> None:
    blocks = [f"{c['index']}\n{_fmt_srt_time(c['startMs'])} --> {_fmt_srt_time(c['endMs'])}\n{c['text']}\n"
              for c in cues]
    path.write_text("\n".join(blocks), encoding="utf-8")


def mux(video: Path, audio: Path, output: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{probe_duration(video):.3f}", "-movflags", "+faststart", str(output)],
        check=True,
    )


def main(argv=None) -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    p = argparse.ArgumentParser(description="SRT → 旁白音轨（CIT Voice Studio / Vbee / Edge TTS，可混入成片）")
    p.add_argument("srt", help="字幕文件 (.srt)")
    p.add_argument("--output", required=True, help="旁白音轨输出 (.m4a)")
    p.add_argument("--video", help="要混入旁白的成片 MP4")
    p.add_argument("--video-out", help="带旁白的成片输出路径（默认 <video>-voice.mp4）")
    p.add_argument("--provider", choices=["cit", "vbee", "edge"],
                   default=(os.environ.get("TTS_PROVIDER") or "cit").lower(), help="TTS 引擎（默认 cit）")
    p.add_argument("--voice", help="声音：CIT 声音名（如 'Hải Đăng'，见 GET /voices）、"
                                   "Vbee voice_code，或 Edge 声音名（如 vi-VN-HoaiMyNeural）")
    p.add_argument("--speed", type=float, default=None,
                   help="语速 0.1–1.9（1.0 = 正常；默认读 <引擎>_SPEED）")
    p.add_argument("--cache-dir", help="单条语音缓存目录（默认 <srt 所在目录>/tts-cache）")
    p.add_argument("--retime-out", help="按语音实长重排时间轴，写出紧凑版 SRT（音轨也按新时间轴生成）")
    p.add_argument("--gap", type=float, default=0.3, help="重排时相邻字幕间隔秒数（默认 0.3）")
    p.add_argument("--pause", action="append", default=[], metavar="序号=秒",
                   help="重排时某条字幕之后的停顿，可多次指定，如 --pause 6=0.8")
    p.add_argument("--tail", type=float, default=1.0, help="重排时末条字幕后的停留秒数（默认 1.0）")
    p.add_argument("--no-trim", action="store_true", help="不裁剪每条语音首尾静音")
    args = p.parse_args(argv)
    try:
        pauses = {int(k): float(v) for k, v in (x.split("=", 1) for x in args.pause)}
    except ValueError:
        print("[err] --pause 格式应为 序号=秒，如 6=0.8", file=sys.stderr)
        return 1

    # 每个引擎各自一组配置：CIT_VOICE / CIT_SPEED、EDGE_VOICE / EDGE_SPEED、VBEE_VOICE / VBEE_SPEED。
    # 旧版通用的 TTS_VOICE / TTS_SPEED 仍作后备（TTS_VOICE 仅在格式匹配该引擎时沿用）。
    prefix = args.provider.upper()
    legacy_voice = os.environ.get("TTS_VOICE") or ""
    legacy_ok = {
        "cit": legacy_voice and not _is_edge_voice(legacy_voice) and not _is_vbee_voice(legacy_voice),
        "edge": _is_edge_voice(legacy_voice),
        "vbee": _is_vbee_voice(legacy_voice),
    }[args.provider]
    env_voice = os.environ.get(f"{prefix}_VOICE") or (legacy_voice if legacy_ok else "")
    if args.speed is None:
        try:
            args.speed = float(os.environ.get(f"{prefix}_SPEED") or os.environ.get("TTS_SPEED") or 1.0)
        except ValueError:
            print(f"[err] {prefix}_SPEED 不是数字", file=sys.stderr)
            return 1
    cit: CitClient | None = None
    voice_key = ""
    if args.provider == "cit":
        cit = CitClient(os.environ.get("CIT_BASE_URL") or CIT_DEFAULT_URL,
                        os.environ.get("CIT_API_KEY") or None)
        try:
            health = cit.health()
            names = [v.get("id") for v in cit.voices()]
        except (urllib.error.URLError, RuntimeError, OSError) as e:
            print(f"[err] 无法连接 CIT Voice Studio ({cit.base_url}): {e}\n"
                  "      请先打开 CIT Voice Studio 应用，或改用 --provider edge", file=sys.stderr)
            return 1
        if health.get("status") != "ok":
            print(f"[err] CIT 模型未就绪: {health.get('message', '')}", file=sys.stderr)
            return 1
        # 未指定 = Hải Đăng；模型没有则用模型默认声音（/voices 第一个）
        voice = args.voice or env_voice or (CIT_DEFAULT_VOICE if CIT_DEFAULT_VOICE in names else None)
        if voice and voice not in names:
            print(f"[err] CIT 当前模型没有声音 {voice!r}，可用: {', '.join(names)}", file=sys.stderr)
            return 1
        engine = health.get("engine", "")
        # 缓存键带上模型名：换模型后不会误用旧缓存
        voice_key = f"{voice or (names[0] if names else 'default')}@{engine.split(' ')[0]}"
        print(f"  CIT 引擎: {engine}, {health.get('sample_rate')} Hz, {health.get('device')}")
    elif args.provider == "vbee":
        app_id = os.environ.get("VBEE_APP_ID")
        token = os.environ.get("VBEE_ACCESS_TOKEN")
        if not app_id or not token:
            print("[err] 缺少 VBEE_APP_ID / VBEE_ACCESS_TOKEN（.env 或环境变量）", file=sys.stderr)
            return 1
        # voice_code 原样传给 API
        voice = args.voice or env_voice or VBEE_DEFAULT_VOICE
    else:
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            print("[err] 缺少 edge-tts，先运行 prepare_env.py", file=sys.stderr)
            return 1
        voice = args.voice or env_voice or EDGE_DEFAULT_VOICE
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("[err] 需要系统 ffmpeg / ffprobe", file=sys.stderr)
        return 1
    if not 0.1 <= args.speed <= 1.9:
        print("[err] --speed 需在 0.1–1.9 之间", file=sys.stderr)
        return 1

    srt = Path(args.srt)
    cues = [c for c in parse_srt(srt.read_text(encoding="utf-8-sig")) if c["text"]]
    if not cues:
        print("[err] 未解析到任何字幕条", file=sys.stderr)
        return 1

    cache = Path(args.cache_dir) if args.cache_dir else srt.parent / "tts-cache"
    cache.mkdir(parents=True, exist_ok=True)
    voice_key = voice_key or voice
    print(f"{args.provider} 配音: {len(cues)} 条字幕, 声音 {voice_key}, 语速 {args.speed}")

    clips: list[Path] = []
    for cue in cues:
        key_src = f"{args.provider}|{voice_key}|{args.speed}|{cue['text']}"
        key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()[:12]
        ext = ".wav" if args.provider == "cit" else ".mp3"
        clip = cache / f"cue-{cue['index']:03d}-{key}{ext}"
        if not clip.exists():
            try:
                if cit is not None:
                    cit.synthesize(cue["text"], voice, args.speed, clip)
                elif args.provider == "vbee":
                    download(synthesize(cue["text"], app_id, token, voice, args.speed), clip)
                else:
                    synthesize_edge(cue["text"], voice, args.speed, clip)
            except Exception as e:  # 网络/服务端错误统一报告并退出
                print(f"[err] 字幕 {cue['index']} 合成失败: {e}", file=sys.stderr)
                return 1
            print(f"  字幕 {cue['index']:>2} 合成完成 ({probe_duration(clip):.2f}s): {cue['text'][:40]}")
        else:
            print(f"  字幕 {cue['index']:>2} 使用缓存")
        clips.append(clip if args.no_trim else trim_silence(clip))

    if args.retime_out:
        cues = retime_cues(cues, clips, args.gap, pauses, args.tail)
        retimed = Path(args.retime_out)
        write_srt(cues, retimed)
        print(f"  时间轴重排: {cues[-1]['endMs'] / 1000:.1f}s")
        print(f"SRT={retimed.resolve()}")

    video = Path(args.video) if args.video else None
    total_ms = int(probe_duration(video) * 1000) if video else None
    output = Path(args.output)
    build_track(cues, clips, output, total_ms)
    print(f"AUDIO={output.resolve()}")

    if video:
        video_out = Path(args.video_out) if args.video_out else video.with_name(f"{video.stem}-voice.mp4")
        mux(video, output, video_out)
        print(f"OUTPUT={video_out.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
