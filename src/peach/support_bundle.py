"""无需服务或第三方依赖的脱敏诊断包。"""
from __future__ import annotations

import io
import argparse
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from . import error_reporting

LOG_NAMES = ("tray.log", "tray-lifecycle.log", "tray-setup.err.log", "tray-setup.out.log",
             "tray-http.err.log", "tray-http.out.log", "tray-https.err.log", "tray-https.out.log")
TAIL_BYTES = 96 * 1024


def redact_log(text: str) -> str:
    """JSON 行按字段脱敏，保留异常链；普通文本按行处理。"""
    lines = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            lines.append(error_reporting.redact(line))
        else:
            lines.append(json.dumps(error_reporting.scrub(value), ensure_ascii=False))
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def bundle_bytes(*, report: dict | None = None, config=None) -> bytes:
    facts = {"created_at": datetime.now(timezone.utc).isoformat(), "system": error_reporting.system_facts()}
    directories = error_reporting.log_directories()
    try:
        from . import settings_file
        config = config or settings_file.load_config()
        facts["configuration"] = {"status": "available", "present": config.present,
                                  "port": config.server.port}
        directories.insert(0, config.directory("logs"))
    except Exception as error:
        facts["configuration"] = {"status": "unavailable", **error_reporting.exception_facts(error)}
    if report:
        # 报告分享仅保留系统检查，库清单、媒体挂载明细和来源原文留在本机页面。
        facts["checks"] = {key: {field: value.get(field) for field in ("status", "reason", "action")}
                           for key, value in report.get("checks", {}).items()
                           if key not in ("media_mounts",)}
    output = io.BytesIO()
    entries = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, directory in enumerate(dict.fromkeys(directories)):
            try:
                candidates = [directory / name for name in LOG_NAMES]
                candidates += sorted(directory.glob("errors-*.log"), key=lambda path: path.stat().st_mtime, reverse=True)[:8]
                candidates += sorted(directory.glob("crash-*.log"), key=lambda path: path.stat().st_mtime, reverse=True)[:4]
            except OSError:
                continue
            for path in candidates:
                if path.is_symlink() or not path.is_file():
                    continue
                try:
                    with path.open("rb") as stream:
                        size = stream.seek(0, os.SEEK_END)
                        stream.seek(max(0, size - TAIL_BYTES))
                        raw = stream.read(TAIL_BYTES)
                    text = raw.decode("utf-8", errors="replace")
                    if size > TAIL_BYTES:
                        text = text.partition("\n")[2]
                    archive.writestr(f"logs/{index}-{path.name}", redact_log(text))
                    entries.append({"name": path.name, "truncated": size > TAIL_BYTES})
                except OSError as error:
                    entries.append({"name": path.name, "status": type(error).__name__})
        facts["logs"] = entries
        archive.writestr("report.json", json.dumps(error_reporting.scrub(facts), ensure_ascii=False, indent=2))
    return output.getvalue()


def save_bundle(destination: Path | None = None) -> Path:
    payload = bundle_bytes()
    if destination is not None:
        with Path(destination).open("xb") as stream:
            stream.write(payload)
        return Path(destination)
    name = datetime.now(timezone.utc).strftime("peach-support-%Y%m%d-%H%M%S-%f.zip")
    for directory in error_reporting.log_directories():
        try:
            directory.mkdir(parents=True, exist_ok=True)
            target = directory / name
            with target.open("xb") as stream:
                stream.write(payload)
            return target
        except OSError:
            continue
    raise OSError("诊断报告无法写入数据目录或临时目录")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="保存本机脱敏诊断包，无需启动 Peach 服务")
    parser.add_argument("destination", nargs="?", type=Path)
    args = parser.parse_args(argv)
    print(save_bundle(args.destination))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
