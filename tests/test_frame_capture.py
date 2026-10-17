"""按时间点抽单帧、把若干帧拼成一张接触印相。九宫格与时间轴预览共用这一份。"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from peach import frame_capture


class _Completed:
    def __init__(self, stderr: bytes = b""):
        self.stderr = stderr
        self.returncode = 0


class CaptureFrameTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="frame-capture-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        self.commands: list[list[str]] = []

    def _run(self, produce: bool = True, stderr: bytes = b""):
        def fake(command, **options):
            self.assertEqual(options["creationflags"],
                             subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            self.commands.append(list(command))
            if produce:
                Path(command[-1]).write_bytes(b"x" * 2048)
            return _Completed(stderr)
        return patch.object(frame_capture.subprocess, "run", fake)

    def test_the_seek_happens_before_the_input_so_only_that_part_is_decoded(self):
        """`-ss` 放到 `-i` 后面就是从头解码到那个时间点，两小时的片子抽最后一帧要几分钟。"""
        with self._run():
            ok, _ = frame_capture.capture_frame("ffmpeg", "movie.mp4", 61.5,
                                                self.root / "one.jpg", width=320)
        self.assertTrue(ok)
        command = self.commands[0]
        self.assertLess(command.index("-ss"), command.index("-i"))
        self.assertIn("scale=320:-1", command)
        self.assertNotIn("bt709", command)

    def test_a_frame_too_small_to_be_a_picture_does_not_count_as_taken(self):
        """命令退出 0 不等于出了图。写了个几百字节的壳，页面上就是一块灰。"""
        def fake(command, **_kwargs):
            Path(command[-1]).write_bytes(b"x" * 64)
            return _Completed()
        with patch.object(frame_capture.subprocess, "run", fake):
            ok, _ = frame_capture.capture_frame("ffmpeg", "movie.mp4", 1.0,
                                                self.root / "small.jpg")
        self.assertFalse(ok)

    def test_a_timeout_is_reported_as_a_failure_not_an_exception(self):
        def fake(_command, **_kwargs):
            raise subprocess.TimeoutExpired("ffmpeg", 45)
        with patch.object(frame_capture.subprocess, "run", fake):
            ok, stderr = frame_capture.capture_frame("ffmpeg", "movie.mp4", 1.0,
                                                     self.root / "late.jpg")
        self.assertFalse(ok)
        self.assertEqual(stderr, "ffmpeg timeout")

    def test_only_bad_color_metadata_is_worth_a_second_try(self):
        """无条件重试会让网盘超时这类必然失败的文件每帧白跑第二次：单帧最坏耗时从
        45 秒翻到 90 秒，9 帧就是 13.5 分钟。"""
        for stderr, attempts in (
            (b"[swscale] Unsupported color primaries: reserved", 2),
            (b"color_trc reserved is invalid", 2),
            (b"Error opening input: Input/output error", 1),
            (b"", 1),
        ):
            self.commands = []
            with self._run(produce=False, stderr=stderr):
                ok = frame_capture.capture_with_retry("ffmpeg", "movie.mp4", 1.0,
                                                      self.root / "retry.jpg")
            self.assertFalse(ok)
            self.assertEqual(len(self.commands), attempts, stderr)
            if attempts == 2:
                self.assertIn("bt709", self.commands[1])


class TileFramesTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="frame-tile-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def test_the_grid_size_reaches_the_filter(self):
        seen: list[list[str]] = []

        def fake(command, **options):
            self.assertEqual(options["creationflags"],
                             subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            seen.append(list(command))
            Path(command[-1]).write_bytes(b"x" * 8192)
            return _Completed()

        with patch.object(frame_capture.subprocess, "run", fake):
            made = frame_capture.tile_frames("ffmpeg", str(self.root / "s%03d.jpg"), 10, 7,
                                             self.root / "out" / "000.jpg")
        self.assertTrue(made)
        self.assertIn("tile=10x7", seen[0])

    def test_a_tile_that_did_not_land_is_not_reported_as_made(self):
        with patch.object(frame_capture.subprocess, "run",
                          lambda command, **_kwargs: _Completed()):
            made = frame_capture.tile_frames("ffmpeg", str(self.root / "s%03d.jpg"), 3, 3,
                                             self.root / "out" / "000.jpg")
        self.assertFalse(made)


if __name__ == "__main__":
    unittest.main()
