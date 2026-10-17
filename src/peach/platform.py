"""账本来源与本机挂载点之间的受控映射。

账本里的 `asset.path` 一律是 Windows 形态的绝对路径：`R:\\media\\...`（本地硬盘）、
`A:\\...`（PikPak）、`B:\\...`（115）。这是不变量，不随平台改写。

真正会变的是「同一个来源在这台机器上落在哪」。`asset.location` 本来就是挂载点 ID
（`local` / `115` / `pikpak`），设置文件用 `[media.locations]` 声明每个 ID 的账本口径根
（一个来源可以有几个根：两块硬盘都算 `local`），用 `[media.mounts]` 按同样的顺序声明每个
根在本机的落点，翻译按「声明根前缀 → 本机挂载点」进行（ADR-0023 第 2 阶段勘误）。
Windows 上盘符本身就是挂载点，路径原样返回。

没有挂载点的来源会被映射到 `UNMAPPED_ROOT` 下，一定通不过 `allowed_media_roots`
授权，于是该来源整体按「脱盘」处理，而不是意外落到当前工作目录下的同名相对路径。
"""
from __future__ import annotations

import logging
import os
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path, PureWindowsPath

from . import settings_file

LOGGER = logging.getLogger(__name__)

# 未映射来源的落点。刻意选一个不可能存在的绝对路径，让授权和存在性检查都必然失败。
UNMAPPED_ROOT = Path("/nonexistent/peach-unmapped-drive")

#: 运行期覆盖挂载表的环境变量。键是 location ID，不是盘符。
MOUNTS_ENV = "PEACH_MEDIA_MOUNTS"


@lru_cache(maxsize=8)
def _parse_override(raw: str) -> tuple[tuple[str, str], ...]:
    """`PEACH_MEDIA_MOUNTS=local=/Volumes/RESOURCES/media,115=/Volumes/CloudDrive/115` 形式的覆盖。"""
    pairs: list[tuple[str, str]] = []
    for chunk in raw.split(","):
        location, separator, mount = chunk.partition("=")
        location = location.strip()
        if not separator or not location:
            continue
        pairs.append((location, mount.strip()))
    return tuple(pairs)


#: 一个来源的声明根或落点：按顺序一一对应的字符串元组。
Roots = Mapping[str, Sequence[str]]


def location_mounts() -> dict[str, tuple[Path, ...]]:
    """当前生效的「来源 ID → 本机挂载点」，与该来源的声明根按顺序一一对应；
    没有条目表示「本机没有这个来源」。

    基础映射来自设置文件的 `[media.mounts]`（内建默认为空：一台新机器什么都没挂，
    对应资产按脱盘处理）。`MOUNTS_ENV` 每次现读而不是缓存进设置层——测试和临时诊断
    会在运行期改它，缓存住就看不到变化；覆盖值只给一个目录，对应该来源的第一个根。
    """
    merged: dict[str, tuple[str, ...]] = dict(settings_file.active().mounts)
    for location, mount in _parse_override(os.environ.get(MOUNTS_ENV, "")):
        merged[location] = (mount,) if mount else ()
    return {location: tuple(Path(mount) for mount in mounts)
            for location, mounts in merged.items() if mounts}


def location_roots() -> dict[str, tuple[str, ...]]:
    """来源 ID → 账本口径的声明根（至少一个），来自 `[media.locations]`。"""
    return dict(settings_file.active().locations)


def resolve_root(
    raw: str | os.PathLike[str], roots: Roots | None = None,
) -> tuple[str | None, int, tuple[str, ...]]:
    """账本路径属于哪个来源的第几个声明根，以及它在那个根之后的层级。

    翻译和写入侧门槛共用这一段判定，所以它只碰 `PureWindowsPath` 和字符串，
    在两个平台上行为一致、也都能测。声明根重叠时取最长的那个（`R:\\` 与
    `R:\\media` 同时声明时，`R:\\media\\x` 归后者）。大小写不敏感由
    `PureWindowsPath` 负责：账本里写 `R:\\Media`、声明根写 `R:\\media` 是同一处。

    `roots` 缺省取当前生效的 `[media.locations]`。`peach init` 刚写完设置文件时进程里
    那份缓存还是旧的，这种调用方把要用的声明根显式传进来。不属于任何来源时返回
    `(None, -1, ())`。
    """
    text = os.fspath(raw)
    if not is_windows_path(text):
        return None, -1, ()
    candidate = PureWindowsPath(text)
    best: tuple[int, str, int] | None = None
    declared_roots = location_roots() if roots is None else roots
    for location, location_roots_ in declared_roots.items():
        for index, root in enumerate(location_roots_):
            declared = PureWindowsPath(root)
            if candidate == declared or candidate.is_relative_to(declared):
                depth = len(declared.parts)
                if best is None or depth > best[0]:
                    best = (depth, location, index)
    if best is None:
        return None, -1, ()
    return best[1], best[2], candidate.parts[best[0]:]


def resolve_location(
    raw: str | os.PathLike[str], roots: Roots | None = None,
) -> tuple[str | None, tuple[str, ...]]:
    """账本路径属于哪个来源，以及它在声明根之后的层级。判定见 `resolve_root`。"""
    location, _index, tail = resolve_root(raw, roots)
    return location, tail


def root_status(root: Path) -> str:
    """以目录首条读取判断挂载状态；空目录可读也算在线。"""
    try:
        with os.scandir(root) as entries:
            next(iter(entries), None)
    except PermissionError:
        return "permission_denied"
    except FileNotFoundError:
        return "missing"
    except NotADirectoryError:
        return "not_directory"
    except OSError:
        return "unavailable"
    return "ok"


def root_online(root: Path) -> bool:
    """即时确认挂载目录可读；用于文件访问与扫描的安全判断。"""
    return root_status(root) == "ok"




def within_root(path: Path, root: Path) -> bool:
    """路径是否落在授权根内。

    字面比较先走一遍；不匹配时用 inode 比较兜底，因为账本里是 `R:\\Media`
    而授权根是 `/Volumes/RESOURCES/media`，exFAT/NTFS 大小写不敏感、pathlib 不是。
    """
    if path == root or root in path.parents:
        return True
    depth = len(root.parts)
    if len(path.parts) < depth:
        return False
    try:
        return Path(*path.parts[:depth]).samefile(root)
    except OSError:
        return False


def system_volume() -> Path:
    """磁盘闸门看的那块盘。

    CloudDrive 会把下载块缓存到系统盘：Windows 是 `C:`，macOS 是根卷。
    """
    return Path("C:/") if os.name == "nt" else Path("/")


def is_windows_path(raw: str | os.PathLike[str]) -> bool:
    text = os.fspath(raw)
    return len(text) >= 3 and text[0].isalpha() and text[1] == ":" and text[2] in "\\/"


def is_unmapped(path: Path) -> bool:
    return path == UNMAPPED_ROOT or UNMAPPED_ROOT in path.parents


def translate_ledger_path(raw: str | os.PathLike[str]) -> Path:
    """把账本里的 Windows 路径翻译成本机路径；非 Windows 形态原样返回。"""
    text = os.fspath(raw)
    if os.name == "nt" or not is_windows_path(text):
        return Path(text)
    location, index, tail = resolve_root(text)
    if location is not None:
        mounts = location_mounts().get(location, ())
        if index < len(mounts):
            return mounts[index].joinpath(*tail)
    # 没声明过的前缀（例如遗留的 `R:\\Resources\\...`）或没挂载的来源：落到不可达根，
    # 保留盘符和其余层级，方便日志里认出是哪条路径。
    parts = PureWindowsPath(text).parts
    return UNMAPPED_ROOT.joinpath(parts[0][0].upper(), *parts[1:])


def translate_roots(roots) -> tuple[Path, ...]:
    """翻译一组授权根，丢掉本机没有挂载的来源。"""
    translated = [translate_ledger_path(root) for root in roots]
    return tuple(path for path in translated if not is_unmapped(path))
