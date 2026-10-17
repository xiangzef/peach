"""预览 HLS 的持久清单与媒体分片，浏览器仅取得本机对象 ID。"""
from __future__ import annotations

import hashlib
import json
from urllib.parse import urljoin, urlsplit

import m3u8

from .fsutil import atomic_write_text
from .http import public_https_url

PLAYLIST_REFRESH_SECONDS = 300

class PreviewCache:
    def __init__(self, cache):
        self.cache = cache

    def register(self, code: str, url: str, *, identity: str = "", playlist: bool | None = None,
                 media_type: str = "") -> str:
        if not public_https_url(url):
            raise ValueError("预览来源不可用")
        ref = hashlib.sha256((identity or url).encode()).hexdigest()
        path = self.cache.folder("preview:" + code) / (ref + ".source.json")
        value = {"url": url, "playlist": playlist if playlist is not None else urlsplit(url).path.lower().endswith(".m3u8")}
        if media_type == 'video/mp4':
            value['media_type'] = media_type
        try:
            current = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            current = None
        if current != value:
            atomic_write_text(path, json.dumps(value), mode=0o600)
        return ref

    def source(self, code: str, ref: str) -> dict:
        ref = ref.removesuffix(".m3u8")
        if len(ref) != 64 or any(char not in "0123456789abcdef" for char in ref):
            raise ValueError("预览对象不存在")
        path = self.cache.folder("preview:" + code) / (ref + ".source.json")
        return json.loads(path.read_text(encoding="utf-8"))

    def playlist(self, code: str, ref: str, fetch) -> bytes:
        url = self.source(code, ref)["url"]
        def download():
            body = fetch(url)
            if not body.decode("utf-8").removeprefix(chr(0xFEFF)).lstrip().startswith("#EXTM3U"):
                raise ValueError("预览清单未取得")
            return body
        generation = hashlib.sha256(url.encode()).hexdigest()
        body = self.cache.bytes(f"preview:{code}:{ref}:playlist:{generation}", download,
                                ttl=PLAYLIST_REFRESH_SECONDS)
        playlist = m3u8.loads(body.decode("utf-8").removeprefix(chr(0xFEFF)), uri=url)
        nested = [*playlist.playlists, *playlist.iframe_playlists, *playlist.media]
        objects = [*playlist.segments, *nested, *playlist.keys, *playlist.session_keys, *playlist.segment_map]
        for obj in objects:
            if obj is None or not getattr(obj, "uri", None):
                continue
            source = urljoin(url, obj.uri)
            item = self.register(code, source, playlist=any(obj is row for row in nested))
            obj.uri = f"/jav-preview/{code}/{item}{'.m3u8' if any(obj is row for row in nested) else ''}"
        # 每个段的 init_section 是同一格式的独立对象，必须一同投影。
        for segment in playlist.segments:
            obj = segment.init_section
            if obj and obj.uri and not obj.uri.startswith("/jav-preview/"):
                obj.uri = f"/jav-preview/{code}/{self.register(code, urljoin(url, obj.uri))}"
        return playlist.dumps().encode("utf-8")
