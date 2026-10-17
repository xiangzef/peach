"""按时间点抽单帧、把若干帧拼成一张接触印相。

九宫格（`scripts/sheets.py`）和时间轴预览（`timeline_sheets`）要的是同一件事：在给定
时间点取一帧、缩到固定宽度、若干帧拼成一张图。两处各写一份的代价不是重复，而是分叉
——网盘上那批坏色彩元数据的片子只在其中一份里被认出来并重试，另一份就永远少一批图，
而失败形态是「这些片子没有预览」，看不出是哪一份的判据少了一条。
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

#: 部分网盘视频把色彩原色写成 reserved（非法值），swscale 会拒绝缩放；声明为 bt709
#: 只是覆盖坏的元数据，不改动像素。
COLOR_OVERRIDE = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]

#: 只有坏色彩元数据才值得用 bt709 覆盖重试。无条件重试会让网盘超时这类必然失败的文件
#: 每帧都白跑第二次：单帧最坏耗时从 45 秒翻到 90 秒，9 帧就是 13.5 分钟。
COLOR_METADATA_ERROR = re.compile(
    r"(reserved|unsupported|invalid)[^\n]{0,60}(color|primaries|trc|space)"
    r"|(color|primaries|trc|space)[^\n]{0,60}(reserved|unsupported|invalid)",
    re.IGNORECASE,
)


def capture_frame(ffmpeg: str, path: str, timestamp: float, destination: Path, *,
                  width: int = 480, color_override: bool = False,
                  timeout: float = 45) -> tuple[bool, str]:
    """抽一帧，返回（是否成功, stderr）。stderr 用于判断值不值得重试。

    `-ss` 在 `-i` 之前：那是输入端 seek，只解目标附近的帧。放到后面就是从头解码到
    那个时间点，两小时的片子抽最后一帧要几分钟。
    """
    command = [ffmpeg, "-y", "-v", "error", "-rw_timeout", "8000000"]
    if color_override:
        command += COLOR_OVERRIDE
    command += [
        "-ss", f"{timestamp:.2f}", "-i", path, "-frames:v", "1",
        "-vf", f"scale={int(width)}:-1", "-q:v", "4", str(destination),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, timeout=timeout,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except subprocess.TimeoutExpired:
        return False, "ffmpeg timeout"
    ok = destination.is_file() and destination.stat().st_size > 1024
    return ok, (completed.stderr or b"").decode("utf-8", "replace")


def capture_with_retry(ffmpeg: str, path: str, timestamp: float, destination: Path,
                       *, width: int = 480, timeout: float = 45) -> bool:
    """抽一帧；只在错误明说色彩元数据不合法时，带 bt709 声明重试一次。"""
    ok, stderr = capture_frame(ffmpeg, path, timestamp, destination,
                               width=width, timeout=timeout)
    if not ok and COLOR_METADATA_ERROR.search(stderr):
        ok, _ = capture_frame(ffmpeg, path, timestamp, destination,
                              width=width, color_override=True, timeout=timeout)
    return ok


def tile_frames(ffmpeg: str, pattern: str, columns: int, rows: int, destination: Path,
                *, timeout: float = 60) -> bool:
    """把 `pattern`（形如 `dir/s%02d.jpg`）指的那串帧拼成 columns×rows 一张。

    帧要先按连续序号改好名再进来：`image2` 读的是序号序列，中间缺一个号它就在那里停下，
    于是拼出来的图少了后半段，而命令本身照样退出 0。
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, "-y", "-v", "error", "-i", pattern,
         "-filter_complex", f"tile={int(columns)}x{int(rows)}", "-q:v", "4", str(destination)],
        capture_output=True, timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    return destination.is_file() and destination.stat().st_size > 4096
