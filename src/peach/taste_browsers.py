"""本机浏览器读取配置，保存在私有历史库中，与已导入记录分开管理。"""
from __future__ import annotations

import hashlib
import socket
import sqlite3
from contextlib import closing
from pathlib import Path


def _key(path: Path) -> str:
    return hashlib.sha256(f"{socket.gethostname()}\0{str(path.resolve()).casefold()}".encode()).hexdigest()


def _paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    return sorted({item for name in ("History", "places.sqlite", "History.db")
                   for pattern in (name, f"*/{name}") for item in path.glob(pattern)
                   if item.is_file()})[:200]


def _validate(path: Path) -> str:
    from .taste_history import _readonly_uri
    try:
        with closing(sqlite3.connect(_readonly_uri(path), uri=True)) as db:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    except sqlite3.OperationalError as error:
        if "locked" in str(error).casefold():
            raise ValueError("历史文件正在使用，请退出该浏览器后添加") from error
        raise ValueError("浏览器历史文件未取得，请检查资料目录") from error
    for engine, required in (("chrome", {"urls", "visits"}), ("firefox", {"moz_places", "moz_historyvisits"}),
                             ("safari", {"history_items", "history_visits"})):
        if required <= tables:
            return engine
    raise ValueError("请选择浏览器历史文件或包含浏览器资料的目录")


def _registered_browsers(store_path):
    """读取当前设备的配置，历史格式只在配置保存时迁移。"""
    if store_path.is_file():
        from .taste_history import _readonly_uri
        with closing(sqlite3.connect(_readonly_uri(store_path), uri=True)) as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='browser_sync'").fetchone():
                columns = {row[1] for row in db.execute("PRAGMA table_info(browser_sync)")}
                engine = "engine" if "engine" in columns else "'auto'"
                return list(db.execute(f"SELECT id,name,path,enabled,{engine} FROM browser_sync WHERE host=?", (socket.gethostname(),)))
    return []


def browser_sources(store_path: Path) -> list[dict]:
    from .taste_history import discover_history_sources
    entries = {}
    for source in discover_history_sources():
        root = source.root or source.path
        key = _key(root)
        entries[key] = {"id": key, "name": source.browser.title(), "path": str(root),
                        "enabled": True, "automatic": True, "engine": source.engine or "safari"}
    for key, name, path, enabled, engine in _registered_browsers(store_path):
        entries[key] = {"id": key, "name": name, "path": path, "enabled": bool(enabled),
                        "automatic": key in entries, "engine": engine}
    for entry in entries.values():
        paths = _paths(Path(entry["path"]))
        entry["profiles"] = len(paths)
        entry["available"] = bool(paths)
    return sorted(entries.values(), key=lambda row: (row["name"].casefold(), row["id"]))


def configure_browser(store_path: Path, operation: str, body: dict) -> None:
    from .taste_history import _open_history_store
    entries = {row["id"]: row for row in browser_sources(store_path)}
    if operation == "add":
        name = str(body.get("name") or "").strip()
        raw_path = str(body.get("path") or "").strip()
        if not name or len(name) > 80 or not raw_path or len(raw_path) > 1024:
            raise ValueError("请填写浏览器名称和资料目录")
        path = Path(raw_path).expanduser().resolve()
        paths = _paths(path)
        if not paths:
            raise ValueError("目录中未找到浏览器历史文件")
        engines = [_validate(history) for history in paths]
        entry = {"id": _key(path), "name": name, "path": str(path), "enabled": True,
                 "engine": engines[0] if len(set(engines)) == 1 else "auto"}
    elif operation in ("disable", "enable"):
        entry = entries.get(str(body.get("id") or ""))
        if not entry:
            raise ValueError("浏览器来源不存在")
        entry["enabled"] = operation == "enable"
    else:
        raise ValueError("浏览器操作无效")
    with _open_history_store(store_path, None) as (db, _, _):
        db.execute("CREATE TABLE IF NOT EXISTS browser_sync("
                   "id TEXT PRIMARY KEY,host TEXT NOT NULL,name TEXT NOT NULL,path TEXT NOT NULL,enabled INTEGER NOT NULL,engine TEXT NOT NULL DEFAULT 'auto')")
        if "engine" not in {row[1] for row in db.execute("PRAGMA table_info(browser_sync)")}:
            db.execute("ALTER TABLE browser_sync ADD COLUMN engine TEXT NOT NULL DEFAULT 'auto'")
        db.execute("INSERT INTO browser_sync(id,host,name,path,enabled,engine) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
                   "name=excluded.name,path=excluded.path,enabled=excluded.enabled,engine=excluded.engine",
                   (entry["id"], socket.gethostname(), entry["name"], entry["path"], int(entry["enabled"]), entry["engine"]))
        db.commit()


def enabled_history_sources(store_path: Path):
    from .taste_history import HistorySource
    unique = {}
    for browser in browser_sources(store_path):
        if browser["enabled"]:
            for path in _paths(Path(browser["path"])):
                engine = {"History": "chrome", "places.sqlite": "firefox", "History.db": "safari"}.get(path.name, browser["engine"])
                unique.setdefault(str(path.resolve()).casefold(), HistorySource(
                    browser["name"].casefold(), path.parent.name, path, engine=engine))
    return list(unique.values())
