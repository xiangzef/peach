"""标准库错误取证；在配置与第三方依赖加载前可用。"""
from __future__ import annotations

import faulthandler
import ipaddress
import json
import logging
import os
import platform
import re
import sys
import tempfile
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import __version__

_log_dir: Path | None = None
_fault_stream = None
_write_lock = threading.RLock()
_hooks_installed = False


def redact(value: str) -> str:
    """去掉网址、本机路径、地址与凭据值，保留异常类型和错误码。"""
    text = str(value).encode("utf-8", errors="backslashreplace").decode("utf-8")
    text = re.sub(r"(?i)\b(?:https?|ftp|file)://[^\s<>\"']+", "<url>", text)
    text = re.sub(r"(?i)\b(?:bearer|basic)\s+[\w+/=.-]+", "<credential>", text)
    text = re.sub(r"(?im)(\b(?:cookie|set-cookie|authorization)[\"']?\s*:\s*)[^\r\n]*", r"\1<redacted>", text)
    text = re.sub(
        r"(?i)([\"']?(?:password|passwd|token|api[_-]?key|secret|cookie|authorization|access[_-]?key)"
        r"[\"']?\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;}]+)",
        r"\1<redacted>", text,
    )
    text = re.sub(r"(?i)(?:[a-z]:[\\/]|\\\\)[^\r\n\"'<>]*", "<path>", text)
    text = re.sub(r"(?<![\w<:])/(?!api(?:/|\b)|healthz\b)(?:[^\r\n\"'<>/]+/)+[^\r\n\"'<>]*", "<path>", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", text)
    def ipv6(match):
        try:
            ipaddress.IPv6Address(match[0])
            return "<ip>"
        except ValueError:
            return match[0]
    text = re.sub(r"(?<![\w:])(?:[\da-fA-F]{0,4}:){2,}[\da-fA-F:.%]*", ipv6, text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "<email>", text)
    return text


def log_directories() -> list[Path]:
    """配置日志目录不可写时使用当前用户临时目录。"""
    result = []
    if _log_dir is not None:
        result.append(_log_dir)
    try:
        from .settings_file import discover_data_root
        root, _ = discover_data_root()
        result.append(root / "logs")
    except Exception:
        pass
    try:
        result.append(Path(tempfile.gettempdir()) / "Peach" / "logs")
    except OSError:
        pass
    return list(dict.fromkeys(result))


def scrub(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {key: "<redacted>" if re.search(
            r"(?i)password|passwd|token|api.?key|secret|cookie|authorization|credential|access.?key", str(key))
                else scrub(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [scrub(item) for item in value]
    return value


def system_facts() -> dict:
    facts = {"peach": __version__, "python": platform.python_version(),
            "os": platform.system(), "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(), "frozen": bool(getattr(sys, "frozen", False)),
            "pid": os.getpid(), "parent_pid": os.getppid()}
    try:
        from .buildinfo import frozen_build
        build = frozen_build()
        if build is not None:
            facts["build"] = {"commit": build.commit, "built_at": build.built_at, "version": build.version}
    except Exception:
        pass
    return facts


def exception_facts(error: BaseException) -> dict:
    frames = []
    seen = set()
    current = error
    chain = []
    while current is not None and id(current) not in seen and len(chain) < 8:
        seen.add(id(current))
        chain.append({"type": type(current).__name__, "message": redact(str(current))[:4000],
                      "winerror": getattr(current, "winerror", None), "errno": getattr(current, "errno", None),
                      "operation": getattr(current, "peach_operation", None),
                      "context": getattr(current, "peach_context", None)})
        for frame in traceback.extract_tb(current.__traceback__)[-40:]:
            frames.append({"file": Path(frame.filename).name, "line": frame.lineno, "function": frame.name})
        current = current.__cause__ or (None if current.__suppress_context__ else current.__context__)
    return {"exception": chain, "frames": frames}


def event(stage: str, error: BaseException | None = None, **fields) -> Path | None:
    record = {"at": datetime.now(timezone.utc).isoformat(), "stage": stage,
              **system_facts(), **fields}
    if error is not None:
        record.update(exception_facts(error))
    payload = json.dumps(scrub(record), ensure_ascii=False, default=str) + "\n"
    with _write_lock:
        for directory in log_directories():
            try:
                directory.mkdir(parents=True, exist_ok=True)
                path = directory / f"errors-{os.getpid()}.log"
                with path.open("a", encoding="utf-8") as stream:
                    stream.write(payload)
                return path
            except OSError:
                continue
    return None


class ErrorHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            error = record.exc_info[1] if record.exc_info else None
            event("logging", error, logger=record.name, level=record.levelname, message=redact(record.getMessage())[:4000])
        except Exception:
            # 取证失败不得递归调用 logging。
            pass


def install(log_dir: Path | None = None) -> None:
    global _hooks_installed, _log_dir, _fault_stream
    if log_dir is not None:
        _log_dir = Path(log_dir)
    if _hooks_installed:
        return
    _hooks_installed = True
    original_main, original_thread, original_unraisable = sys.excepthook, threading.excepthook, sys.unraisablehook

    def main_hook(kind, error, tb):
        event("unhandled-main", error)
        if sys.stderr is not None:
            original_main(kind, error, tb)

    def thread_hook(args):
        if args.exc_type is not SystemExit:
            event("unhandled-thread", args.exc_value, thread=args.thread.name if args.thread else "unknown")
        if sys.stderr is not None:
            original_thread(args)

    def unraisable_hook(args):
        event("unraisable", args.exc_value)
        if sys.stderr is not None:
            original_unraisable(args)

    sys.excepthook, threading.excepthook, sys.unraisablehook = main_hook, thread_hook, unraisable_hook
    if sys.stderr is not None:
        logging.basicConfig()
    logging.getLogger().addHandler(ErrorHandler(level=logging.WARNING))
    for directory in log_directories():
        try:
            directory.mkdir(parents=True, exist_ok=True)
            _fault_stream = (directory / f"crash-{os.getpid()}.log").open("a", encoding="utf-8")
            faulthandler.enable(_fault_stream, all_threads=True)
            break
        except (OSError, RuntimeError):
            if _fault_stream is not None:
                _fault_stream.close()
                _fault_stream = None
    event("entry")


def console_ready() -> None:
    """冻结 CLI 取得标准错误句柄后保留控制台日志。"""
    root = logging.getLogger()
    if sys.stderr is not None and not any(isinstance(handler, logging.StreamHandler)
                                         and handler.stream is sys.stderr for handler in root.handlers):
        root.addHandler(logging.StreamHandler(sys.stderr))


def failure_details(stage: str, error: BaseException) -> str:
    path = event(stage, error)
    try:
        from .support_bundle import save_bundle
        report = save_bundle()
        return f"{error}\n\n诊断报告：{report}"
    except Exception as report_error:
        event("report-failed", report_error)
        return f"{error}\n\n错误日志：{path}" if path else f"{error}\n\n错误日志未能写入，请保留此弹窗。"


def tray_main() -> int:
    install()
    try:
        from .tray import main
        return main()
    except Exception as error:
        message = failure_details("tray-import", error)
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, "Peach 启动失败", 0x10)
        elif sys.stderr is not None:
            print(message, file=sys.stderr)
        return 1


def cli_main() -> int:
    install()
    try:
        from .cli import main
        return main()
    except Exception as error:
        event("cli", error)
        if sys.stderr is not None:
            traceback.print_exc()
        return 1


def asyncio_handler(loop, context) -> None:
    event("unhandled-asyncio", context.get("exception"), message=context.get("message", ""))
    loop.default_exception_handler(context)
