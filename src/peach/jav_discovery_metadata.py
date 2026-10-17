"""发现卡的可撤回资料边车与固定集合、有硬预算的匿名补齐任务。"""
from __future__ import annotations

import json
import math
import threading
import time
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlsplit

from .catalog_rules import normalise_code_key
from .fsutil import atomic_write_text
from .javdb_public import (PUBLIC_API, PublicBudgetExceeded, PublicRequestBudget, PublicSourceUnavailable,
                          public_cache_scope, cache_checked_at, cache_error)
from .jav_cache import cache_fresh
from .jobs import BackgroundJob

MAX_ITEMS = 100
MAX_RECORDS = 2048
FIELDS = ("id", "number", "title", "release_date", "maker_name", "series_name", "duration", "score", "tags", "actors")


def actor_record(actor):
    from .javdb_public import public_image_url
    record = {key: actor[key] for key in ('id', 'name', 'gender') if key in actor}
    address = str(actor.get('avatar_url') or actor.get('avatar_image') or '')
    record['has_avatar'] = public_image_url(address)
    if record['has_avatar'] and not urlsplit(address).query and not urlsplit(address).fragment:
        record['avatar_image'] = address
    return record


def source_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


class DiscoveryMetadata:
    """缓存只承载来源资料；后台任务不写账本或 task_run。"""

    def __init__(self, path: Path, *, api=PUBLIC_API, clock=time.time):
        self.path, self.api, self.clock = Path(path), api, clock
        self.lock = threading.RLock()
        self.job = BackgroundJob("jav-discovery-metadata")
        self.last_job = None
        self.records = OrderedDict()
        self._load()

    def _load(self):
        try:
            if self.path.stat().st_size > 16 * 1024 * 1024:
                return
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            rows = payload.get("records", {}) if payload.get("version") == 1 else {}
            if isinstance(rows, dict):
                for code, record in list(rows.items())[-MAX_RECORDS:]:
                    if isinstance(record, dict) and isinstance(record.get("movie", {}), dict):
                        self.records[normalise_code_key(code)] = record
        except (OSError, ValueError, TypeError, AttributeError):
            return

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps({"version": 1, "records": self.records}, ensure_ascii=False)
        while len(encoded.encode("utf-8")) > 16 * 1024 * 1024 and self.records:
            self.records.popitem(last=False)
            encoded = json.dumps({"version": 1, "records": self.records}, ensure_ascii=False)
        atomic_write_text(self.path, encoded)

    def remember(self, code, movie=None, *, error="", checked_at=None):
        code = normalise_code_key(code)
        with self.lock:
            previous = self.records.get(code, {})
            projected = {key: movie[key] for key in FIELDS if key in movie} if movie else previous.get("movie", {})
            # 头像仅保存公开静态地址；带签名参数的图片与播放地址不进入资料边车。
            if movie and "actors" in projected:
                projected["actors"] = [actor_record(actor)
                                       for actor in movie.get("actors") or [] if isinstance(actor, dict)][:100]
            self.records[code] = {"movie": projected,
                                  "checked_at": previous.get('checked_at', 0) if error else
                                  self.clock() if checked_at is None else checked_at,
                                  "retry_after": self.clock() + 900 if error else 0, "error": error}
            self.records.move_to_end(code)
            while len(self.records) > MAX_RECORDS:
                self.records.popitem(last=False)
            self._save()

    def peek(self, code):
        with self.lock:
            record = self.records.get(normalise_code_key(code), {})
            movie = dict(record.get("movie", {}))
            fields = {"tags": ("ready" if movie["tags"] else "empty") if isinstance(movie.get("tags"), list) else "unavailable",
                      "source_score": "ready" if source_number(movie.get("score")) is not None else "unavailable",
                      "duration": "ready" if source_number(movie.get("duration")) is not None else "unavailable"}
            state = "ready" if movie and "unavailable" not in fields.values() else "partial" if movie else "pending"
            if not cache_fresh(record.get('checked_at', 0), movie.get('release_date'), self.clock()) and movie:
                state = "stale"
            if record.get("error"):
                state = "stale" if movie else "unavailable"
            return movie, {"metadata_state": state, "metadata_fields": fields,
                           "metadata_message": record.get("error", ""), "metadata_checked_at": record.get("checked_at")}

    def ensure(self, codes, *, refresh=False, job_id=None):
        snapshot = self.job.snapshot() or self.last_job
        # 同一页的轮询只观察固定集合，完成后不会自行领下一批。
        if snapshot and (snapshot["status"] == "running" or
                         (not refresh and snapshot.get('status') != 'complete')):
            return snapshot
        if snapshot and not refresh:
            codes = snapshot['codes']
        codes = list(dict.fromkeys(normalise_code_key(code) for code in codes if code))[:MAX_ITEMS]
        with self.lock:
            pending = [code for code in codes if self.records.get(code, {}).get('retry_after', 0) <= self.clock()
                       and (refresh or not cache_fresh(self.records.get(code, {}).get('checked_at', -1),
                                           self.records.get(code, {}).get('movie', {}).get('release_date'), self.clock()))]
        if snapshot and not pending:
            return snapshot
        budget = PublicRequestBudget()
        initial = {"total": len(codes), "completed": len(codes) - len(pending), "failed": 0,
                   "requests": 0, "bytes": 0, "stop_reason": "", "codes": codes,
                   "budget": {"max_items": MAX_ITEMS, "max_requests": budget.max_requests,
                              "max_bytes": budget.max_bytes, "max_seconds": budget.max_seconds}}

        def work(current_id):
            completed, failed = initial["completed"], 0
            stop_reason = ""
            with public_cache_scope(self.path.parent / 'jav-public'), self.api.request_budget(budget):
                for code in pending:
                    if not self.job.snapshot() or self.job.snapshot()["job_id"] != current_id:
                        return
                    try:
                        movie = self.api.movie(code, refresh=True) if refresh else self.api.movie(code)
                        self.remember(code, movie, checked_at=cache_checked_at('movie:' + code, exact=True))
                        if cache_error('movie:' + code):
                            raise PublicSourceUnavailable(cache_error('movie:' + code))
                        completed += 1
                    except PublicBudgetExceeded:
                        stop_reason = budget.stop_reason
                        break
                    except PublicSourceUnavailable as error:
                        self.remember(code, error=str(error))
                        failed += 1
                        completed += 1
                        if self.api.paused_until > self.api.clock():
                            stop_reason = "source_cooldown"
                    if not self.job.update(current_id, completed=completed, failed=failed,
                                           requests=budget.requests, bytes=budget.bytes, batch=(completed + 9) // 10):
                        return
                    if stop_reason:
                        break
            self.job.update(current_id, status="stopped" if stop_reason else "complete", stop_reason=stop_reason,
                            completed=completed, failed=failed, requests=budget.requests, bytes=budget.bytes)

        return self.job.start(work, initial=initial, restart=bool(snapshot))

    def stop(self):
        self.job.stop()

    def cancel(self, job_id=None):
        snapshot = self.job.snapshot() or self.last_job
        if not snapshot or (job_id and snapshot["job_id"] != job_id):
            return snapshot
        self.job.stop()
        snapshot.update(status="stopped", stop_reason="cancelled")
        self.last_job = snapshot
        return snapshot


def discovery_metadata(contract):
    with contract.cache_lock:
        if not hasattr(contract, "jav_discovery_metadata"):
            contract.jav_discovery_metadata = DiscoveryMetadata(contract.cover_root.parent / "jav-discovery-metadata.json")
        return contract.jav_discovery_metadata
