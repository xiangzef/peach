"""Kodi/Jellyfin 影片及单集 NFO 的本地边车适配。"""
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .catalog_rules import release_code_from_text
from .scan import VIDEO


def directory_files(directory: Path) -> dict[str, Path]:
    """目录里的普通文件，按 casefold 文件名索引。

    走 `os.scandir`：Windows 的目录列表自带类型，`is_file()` 不再逐个 stat。网盘挂载上
    一次 stat 就是一趟往返，几百个文件的文件夹用 `iterdir()` 要付几百趟。
    """
    with os.scandir(directory) as entries:
        return {entry.name.casefold(): Path(entry.path) for entry in entries if entry.is_file()}


POSTER_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tbn')
_NUMBERED = re.compile(r'(.*\D|)(\d+)(\D*)')


def _numbered_image_set(stem: str, files: dict[str, Path]) -> bool:
    """`stem` 是不是一组连号文件里的一个号，而同组别的号只有图片、没有视频。

    批量改名的图集把正片和图片编进同一组号：`(1).mp4` 旁边是 `(1).jpg` 到 `(119).jpg`，
    同名的那张只是图集第一张，不是海报。多部番号放一个目录时 `ABC-124.jpg` 有自己的
    `ABC-124.mp4`，不算图集。
    """
    match = _NUMBERED.fullmatch(stem.casefold())
    if match is None:
        return False
    videos = {path.stem.casefold() for path in files.values() if path.suffix.lower() in VIDEO}
    for path in files.values():
        other = _NUMBERED.fullmatch(path.stem.casefold())
        if (path.suffix.lower() in POSTER_EXTENSIONS and other is not None
                and other.group(1, 3) == match.group(1, 3) and other.group(2) != match.group(2)
                and path.stem.casefold() not in videos):
            return True
    return False


def sidecars(video: Path, files: dict[str, Path] | None = None):
    """`video` 旁边的 NFO 与海报候选；`files` 是调用方已列好的同目录索引，省掉再列一遍。"""
    files = directory_files(video.parent) if files is None else files
    single = sum(path.suffix.lower() in VIDEO for path in files.values()) == 1
    nfo = files.get((video.stem + '.nfo').casefold())
    if nfo is None and single:
        nfo = files.get('movie.nfo')
    names = [video.stem + '-poster']
    if not _numbered_image_set(video.stem, files):
        names.append(video.stem)
    if single:
        names.extend(['poster', 'folder', 'cover'])
    posters = [files[name.casefold() + extension] for name in names
               for extension in POSTER_EXTENSIONS
               if name.casefold() + extension in files]
    return nfo, posters


def read_nfo(path: Path):
    """保留完整原文；拒绝 DTD，并限制 XML 的输入体积。"""
    with path.open('rb') as handle:
        raw = handle.read(1024 * 1024 + 1)
    # XML 的 UTF-16/32 编码包含零字节；声明检查同样覆盖这些编码。
    declarations = raw.replace(b'\x00', b'').upper()
    if len(raw) > 1024 * 1024 or b'<!DOCTYPE' in declarations or b'<!ENTITY' in declarations:
        raise ValueError('NFO 文件过大或包含实体声明')
    root = ET.fromstring(raw)
    if root.tag not in {'movie', 'episodedetails', 'musicvideo'}:
        raise ValueError('NFO 不是影片或单集资料')
    def text(*keys):
        return next(((root.findtext(key) or '').strip() for key in keys
                     if (root.findtext(key) or '').strip()), '')
    identifiers = [node.text for node in root.findall('uniqueid')
                   if node.get('type', '').lower() in {'javboss', 'jav', 'javid', 'dvdid', 'num'}]
    identifiers.extend([text('num'), text('sorttitle')])
    # 通用 id 常是 IMDb/TMDb；仅明确的番号形状参与 JAV 身份识别。
    for value in [text('id'), *(node.text or '' for node in root.findall('uniqueid'))]:
        if re.fullmatch(r'(?:[A-Za-z]{2,12}[-_]\d{2,8}|FC2[-_](?:PPV[-_])?\d+)', value.strip(), re.I):
            identifiers.append(value)
    codes = {code for value in identifiers if (code := release_code_from_text(value or ''))}
    if len(codes) > 1:
        raise ValueError('NFO 包含多个不同番号')
    genres = list(dict.fromkeys(node.text.strip() for key in ('genre', 'tag')
                  for node in root.findall(key) if node.text and node.text.strip()))
    payload = dict(id=next(iter(codes), ''), title=text('title', 'localtitle', 'name'),
        original_title=text('originaltitle'), maker=text('studio'),
        series=text('set/name', 'set', 'showtitle'),
        release_date=text('premiered', 'releasedate', 'aired'),
        director=text('director'), runtime=text('runtime'),
        actresses=[{'japanese_name': (node.findtext('name') or '').strip()}
                   for node in root.findall('actor')], genres=genres, local_tags=genres,
        nfo_kind=root.tag, source_generator=text('generator'),
        local_art=text('art/poster', 'thumb[@aspect="poster"]', 'thumb'))
    return payload, raw


def local_art(video: Path, payload: dict):
    """仅读取影片所在目录内的本地图片，远端引用保留在原文。"""
    value = payload.get('local_art', '')
    if not value or '://' in value:
        return None
    path = (video.parent / value).resolve()
    if path.is_relative_to(video.parent.resolve()) and path.is_file():
        return path
    return None
