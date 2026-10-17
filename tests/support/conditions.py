"""按设计只在某个平台上成立的用例条件，以及外部前置条件缺失时的处理。"""

from __future__ import annotations

import os
from typing import NoReturn
import unittest


def missing_prerequisite(reason: str) -> NoReturn:
    """缺 Node、依赖、ffmpeg 或浏览器这类外部前置条件时调用。

    本机没装时显式跳过，免得整个测试域红掉让人绕过入口。CI 的 runner 由工作流负责
    装齐，缺了就是工作流写错：跳过会让用例在 CI 里永远不执行，所以那里判失败。
    """
    if os.environ.get("GITHUB_ACTIONS") == "true":
        raise AssertionError(f"CI 缺少前置条件，工作流应当装好：{reason}")
    raise unittest.SkipTest(reason)


#: 声明根（`[media.locations]`）一律是 Windows 盘符，扫描与落库也只在 Windows 上
#: 发生（ADR-0023、`peach-cross-platform`）。拿临时目录当声明根的用例因此只在 Windows 上
#: 跑得通：那里的临时路径本身就是 Windows 形态，`resolve_root` 认得；POSIX 临时路径
#: 不是账本口径的路径，写入侧门槛会把它当成「不在任何声明根下」拒掉。要让这些用例在
#: macOS 上也跑，得先让 `translate_ledger_path` 在 Windows 上也过 `[media.mounts]`——那是
#: 产品行为的改动，不是测试的事。
windows_ledger_roots = unittest.skipUnless(os.name == "nt", "声明根是 Windows 盘符")
