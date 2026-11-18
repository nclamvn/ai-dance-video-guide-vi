#!/usr/bin/env python3
"""Căn waveform nhạc theo tiếng nguồn, mux cục bộ; không chứng nhận chuyển động."""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

RATE = 16000


def run(ffmpeg, args):
    p = subprocess.run([ffmpeg, "-hide_banner", "-v", "error", "-xerror"] + args,
                       capture_output=True)
    if p.returncode or p.stderr.strip():
        raise ValueError(p.stderr.decode(errors="replace")[-2000:] or "FFmpeg failed")
    return p.stdout


def pcm(ffmpeg, path):
    data = run(ffmpeg, ["-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(RATE),
                        "-f", "f32le", "-"])
    return np.frombuffer(data, dtype="<f4").astype(np.float64)


def match_window(music, reference):
    """Return start sample, normalized score and separated alternative score."""
    y = reference - reference.mean()
    if len(music) < len(y) or np.dot(y, y) < 1e-9:
        raise ValueError("Nhạc quá ngắn hoặc cửa sổ nguồn gần như im lặng")
    n = 1 << (len(music) + len(y) - 1).bit_length()
    corr = np.fft.irfft(np.fft.rfft(music, n) * np.fft.rfft(y[::-1], n), n)
    corr = corr[len(y) - 1:len(music)]
    sums = np.r_[0.0, np.cumsum(music)]
    squares = np.r_[0.0, np.cumsum(music * music)]
    energy = squares[len(y):] - squares[:-len(y)]
    energy -= (sums[len(y):] - sums[:-len(y)]) ** 2 / len(y)
    scores = corr / np.sqrt(np.maximum(energy, 1e-20) * np.dot(y, y))
    best = int(np.argmax(scores))
    # A repeat elsewhere in the song is ambiguous; exclude a local 0.1s neighbourhood.
    separated = scores.copy()
    separated[max(0, best - RATE // 10):best + RATE // 10 + 1] = -1
    return best, float(scores[best]), float(np.max(separated))


def estimate_offset(music, original, seconds):
    usable = min(len(original) / RATE, seconds)
    width = min(3.0, usable / 4)
    if usable < 4:
        raise ValueError("Cần ít nhất 4 giây tiếng nguồn để tự căn; dùng offset thủ công nếu đã kiểm")
    starts = np.linspace(min(1.0, usable / 10), usable - width, 6)
    checks = []
    for start in starts:
        begin = round(start * RATE)
        sample, score, alternative = match_window(music, original[begin:begin + round(width * RATE)])
        checks.append({"source_start_seconds": begin / RATE,
                       "music_start_seconds": sample / RATE,
                       "offset_seconds": (sample - begin) / RATE,
                       "correlation": score, "separated_alternative_score": alternative})
    offset = float(np.median([c["offset_seconds"] for c in checks]))
    coherent = [c for c in checks if abs(c["offset_seconds"] - offset) <= .001]
    confident = len(coherent) >= 5 and min(c["correlation"] for c in coherent) >= .8
    unique = len([c for c in coherent if c["correlation"] - c["separated_alternative_score"] >= .05]) >= 4
    return offset, bool(confident and unique), checks


def video_hash(ffmpeg, path):
    return run(ffmpeg, ["-i", str(path), "-map", "0:v:0", "-c:v", "copy", "-f", "hash",
                        "-hash", "sha256", "-"]).decode().strip()


def video_seconds(ffmpeg, path):
    progress = run(ffmpeg, ["-nostats", "-progress", "pipe:1", "-i", str(path),
                           "-map", "0:v:0", "-an", "-f", "null", "-"]).decode()
    fields = dict(line.split("=", 1) for line in progress.splitlines() if "=" in line)
    if fields.get("progress") != "end" or int(fields.get("frame", "0")) <= 0:
        raise ValueError("Không giải mã đủ video để xác định thời lượng")
    return int(fields["out_time_us"]) / 1_000_000


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--music", type=Path, required=True)
    p.add_argument("--reference", type=Path)
    p.add_argument("--seconds", type=float, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--offset-seconds", type=float,
                   help="Dương: cắt đầu nhạc; âm: trì hoãn nhạc. Chỉ dùng sau đối chiếu thủ công.")
    a = p.parse_args()
    try:
        ffmpeg = a.ffmpeg or shutil.which("ffmpeg")
        if not ffmpeg:
            raise ValueError("Thiếu FFmpeg; đặt trên PATH hoặc truyền --ffmpeg")
        if not math.isfinite(a.seconds) or a.seconds <= 0:
            raise ValueError("seconds phải hữu hạn và dương")
        if a.seconds > 600:
            raise ValueError("Giới hạn công cụ clip ngắn: 600 giây")
        if a.out.exists() or a.report.exists():
            raise ValueError("File đầu ra/report đã tồn tại; chọn tên mới")
        for f in [a.video, a.music] + ([a.reference] if a.reference else []):
            if not f.is_file():
                raise ValueError("Không tìm thấy file: " + str(f))
        if a.offset_seconds is None and not a.reference:
            raise ValueError("Cần --reference có tiếng để tự căn, hoặc --offset-seconds đã kiểm")
        duration = video_seconds(ffmpeg, a.video)
        if a.seconds > duration + .002:
            raise ValueError(f"Yêu cầu {a.seconds}s nhưng hình chỉ có {duration}s; không kéo dài bằng tiếng")
        music = pcm(ffmpeg, a.music)
        original = pcm(ffmpeg, a.reference) if a.reference else None
        report = {"scope": "Waveform timing only, not movement certification or human listening review",
                  "seconds_requested": a.seconds, "video_decoded_seconds": duration, "jobs_submitted": 0,
                  "music_file": a.music.name, "video_file": a.video.name,
                  "reference_file": a.reference.name if a.reference else None}
        if a.offset_seconds is None:
            offset, confidence, checks = estimate_offset(music, original, a.seconds)
            report.update({"mode": "automatic", "confidence_gate": confidence, "windows": checks})
            if not confidence:
                a.report.parent.mkdir(parents=True, exist_ok=True)
                a.report.write_text(json.dumps({**report, "status": "STOP_UNCERTAIN"}, indent=2) + "\n")
                print("Dừng: các cửa sổ không khớp đủ chắc chắn. Xem report và kiểm thủ công.")
                return 1
        else:
            offset = a.offset_seconds
            if not math.isfinite(offset):
                raise ValueError("offset phải hữu hạn")
            report["mode"] = "manual_offset_not_automatically_certified"
        if max(offset, 0) >= len(music) / RATE:
            raise ValueError("Offset nằm ngoài nhạc")
        if len(music) / RATE - max(offset, 0) + max(-offset, 0) < a.seconds - .002:
            raise ValueError("Nhạc không đủ dài cho thời lượng yêu cầu")
        if -offset >= a.seconds:
            raise ValueError("Nhạc sẽ bắt đầu sau khi video kết thúc")
        if offset >= 0:
            audio = f"asetpts=PTS-STARTPTS,atrim=start={offset:.9f},asetpts=PTS-STARTPTS"
        else:
            audio = f"asetpts=PTS-STARTPTS,adelay={-offset * 1000:.9f}:all=1"
        audio += f",atrim=duration={a.seconds:.9f},asetpts=PTS-STARTPTS"
        a.out.parent.mkdir(parents=True, exist_ok=True)
        before = video_hash(ffmpeg, a.video)
        run(ffmpeg, ["-n", "-i", str(a.video), "-i", str(a.music), "-filter_complex", f"[1:a]{audio}[a]",
                     "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                     "-ar", "44100", "-t", str(a.seconds), "-movflags", "+faststart", str(a.out)])
        after = video_hash(ffmpeg, a.out)
        # Stream-copy hash equality is expected only when not intentionally trimming video.
        report.update({"status": "MUXED_REVIEW_REQUIRED", "offset_seconds": offset,
                       "video_bitstream_before": before, "video_bitstream_after": after,
                       "video_bitstream_unchanged": before == after,
                       "output_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()})
        if original is not None:
            final = pcm(ffmpeg, a.out)
            check_end = min(len(final), len(original), round(a.seconds * RATE))
            correlations = []
            for start in np.linspace(RATE, max(RATE, check_end - 2 * RATE), 5).astype(int):
                x = final[start:min(start + RATE, check_end)]
                y = original[start:start + len(x)]
                if len(x) and np.std(x) > 1e-7 and np.std(y) > 1e-7:
                    correlations.append({"source_seconds": start / RATE,
                                         "zero_lag_correlation": float(np.corrcoef(x, y)[0, 1])})
            report["post_mux_waveform_checks"] = correlations
            if a.offset_seconds is None and (not correlations or min(c["zero_lag_correlation"] for c in correlations) < .8):
                report["status"] = "MUXED_POSTCHECK_UNCERTAIN"
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report["status"] == "MUXED_POSTCHECK_UNCERTAIN" else 0
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        print(json.dumps({"status": "ERROR", "error": str(e)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
