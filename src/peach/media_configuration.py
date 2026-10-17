"""媒体来源表单与配置映射；来源 ID 直接沿用扫描及流量策略。"""
from __future__ import annotations

from pathlib import Path, PurePath, PureWindowsPath, PurePosixPath
import shutil
import sys
from typing import Any

from . import platform

SOURCE_OPTIONS = (("local", "本地磁盘"), ("115", "CloudDrive · 115"),
                  ("pikpak", "CloudDrive · PikPak"))


def _windows_installed_names() -> list[str]:
    """从 Windows 安装清单读取软件名称，不读取命令、账户或凭据。"""
    if sys.platform != "win32":
        return []
    import winreg
    names = []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                                    0, winreg.KEY_READ | view) as key:
                    for index in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            with winreg.OpenKey(key, winreg.EnumKey(key, index)) as child:
                                names.append(str(winreg.QueryValueEx(child, "DisplayName")[0]).lower())
                        except OSError:
                            continue
            except OSError:
                continue
    return names


def mount_dependencies(*, system: str | None = None) -> list[dict[str, Any]]:
    """安装证据与挂载在线状态分别检测；只返回当前操作系统需要的依赖。"""
    system = system or sys.platform
    if system == "win32":
        names = _windows_installed_names()
        cloud = any(name.startswith("clouddrive") for name in names)
        driver, installed, url = "WinFsp", any(name.startswith("winfsp") for name in names), "https://winfsp.dev/rel/"
    elif system == "darwin":
        cloud = any((base / app).is_dir() for base in (Path("/Applications"), Path.home() / "Applications")
                    for app in ("CloudDrive.app", "CloudDrive2.app"))
        driver, installed, url = "macFUSE", Path("/Library/Filesystems/macfuse.fs").is_dir(), "https://macfuse.github.io/"
    else:
        return []
    cloud = cloud or any(shutil.which(name) for name in ("clouddrive", "clouddrive2", "CloudDrive"))
    return [{"name": "CloudDrive", "available": bool(cloud), "download_url": "https://www.clouddrive2.com/download.html"},
            {"name": driver, "available": installed, "download_url": url}]


def rows(config, *, windows: bool, probe: bool = False) -> list[dict[str, Any]]:
    result = []
    for location, roots in config.locations.items():
        mounts = config.mounts.get(location, ())
        for index, root in enumerate(roots):
            mount = root if windows else (mounts[index] if index < len(mounts) else "")
            result.append({"location": location, "root": root, "path": mount,
                           "library": config.library_names.get(root) or PureWindowsPath(root).name or root,
                           "library_icon": config.library_icons.get(root, ""),
                           "online": platform.root_online(Path(mount)) if probe and mount else False})
    return result


def validate(raws: object, *, windows: bool) -> tuple[dict, dict, list[str]]:
    """离线来源允许保存；绝对路径、盘符根与来源间重叠在保存前校验。"""
    if not isinstance(raws, list) or not raws or len(raws) > 100:
        return {}, {}, ["请添加 1 到 100 个媒体文件夹"]
    locations: dict[str, list[str]] = {}
    mounts: dict[str, list[str]] = {}
    errors = [""] * len(raws)
    seen: list[tuple[PureWindowsPath, PurePath]] = []
    for index, row in enumerate(raws):
        try:
            if not isinstance(row, dict):
                raise ValueError("媒体来源格式不正确")
            location = row.get("location")
            if not isinstance(location, str) or location not in dict(SOURCE_OPTIONS):
                raise ValueError("请选择本地磁盘、115 或 PikPak")
            text = str(row.get("path", "")).strip()
            root = text if windows else str(row.get("root", "")).strip()
            if any(ord(char) < 32 for char in text + root):
                raise ValueError("路径不能包含控制字符")
            if not platform.is_windows_path(root) or ".." in PureWindowsPath(root).parts:
                raise ValueError("Windows 中的对应路径必须包含盘符，例如 B:\\；网络共享请先映射为 Windows 盘符")
            path = PureWindowsPath(text) if windows else PurePosixPath(text)
            if not text or not (platform.is_windows_path(text) if windows else text.startswith("/")):
                raise ValueError("请填写本机挂载点的绝对路径")
            if ".." in path.parts:
                raise ValueError("挂载点不能包含上级目录 ..")
            declared = PureWindowsPath(root)
            for other_root, other_path in seen:
                if (declared == other_root or declared.is_relative_to(other_root)
                        or other_root.is_relative_to(declared)):
                    raise ValueError("Windows 中的对应路径与另一文件夹重复或重叠")
                if path == other_path or path.is_relative_to(other_path) or other_path.is_relative_to(path):
                    raise ValueError("本机挂载点与另一行重复或重叠")
            seen.append((declared, path))
            locations.setdefault(location, []).append(str(declared))
            if not windows:
                mounts.setdefault(location, []).append(str(path))
        except ValueError as exc:
            errors[index] = str(exc)
    return ({key: tuple(value) for key, value in locations.items()},
            {key: tuple(value) for key, value in mounts.items()},
            errors if any(errors) else [])
