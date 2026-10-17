"""文案只描述最终状态：界面字串、注释、docstring、测试名与文档的门槛检查。

被否掉的做法和「改动前后对比」不属于交付物。一段写着「以前是 X，现在改成 Y」的注释
要求读者先装载一个已经不存在的版本，才能读懂现在这一版；而它讲的那个 X 在代码里已经
没有任何对应物，无法核对，也无法失效。约束本身（为什么现在是 Y）要留下，走向那里的
路径不要留。

判据落在词表上，逐行报告。合法的例外是**以真实事故为内容**的条目：
`docs/HANDOFF.md` 的事故记录、技能里的「已知陷阱」、`AGENTS.md` 的「常犯错误」。
它们的内容就是那次失败本身，删掉等于丢掉证据。这类行在行尾加放行标记：

    Markdown   <!-- copy-lint-disable-line -->
    Python     # copy-lint-disable-line
    JavaScript // copy-lint-disable-line

放行必须逐行、显式；没有目录级或词表级豁免。
"""
from __future__ import annotations

import argparse
import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DISABLE_MARKER = "copy-lint-disable-line"

#: 中文词表。收的是**指向先前状态的时间标记**——它们后面跟的一定是一个读者无法
#: 核对、也无法失效的旧版本。功能性否定词不收：`不再抄一份`、`不装配`、`原样返回`
#: 说的是现在成立的约束或现在的行为，2026-09-03 全树校准里它们十次里有七次合法，
#: 收进来只会逼人满树贴放行标记。
CHINESE_RULES: tuple[tuple[str, str], ...] = (
    (r"以前", "只写现在是什么"),
    (r"原来(?!源)", "只写现在是什么"),
    (r"原本|原先|本来是|之前是", "只写现在是什么"),
    (r"曾经|早先", "只写现在成立的事实"),
    (r"第[一二三]版|初版|上一版|换过[两三四]版",
     "只写当前实现，版本演进属于 Git 历史"),
    (r"实测(?:只|下来|发现)", "只写结论本身，不写它是怎么被测出来的"),
    (r"[不别没](?:装|用|要|是|取)原样", "只说现在装的是什么"),
    (r"现在改|改回原", "只写现在的行为，不写改动方向"),
)

#: 英文词表。大小写不敏感。同样只收时间标记。
ENGLISH_RULES: tuple[tuple[str, str], ...] = (
    (r"\bno longer\b", "state the constraint that holds now"),
    (r"\bpreviously\b|\bformerly\b", "state the current behavior"),
    (r"\bused to\b", "state the current behavior"),
)

#: 测试函数名。名字是契约声明，不是变更说明。
#:
#: `_instead_of_` 与 `_not_the_` 不收：`..._takes_the_intersection_not_the_union`
#: 对比的是同一份输入下的另一种可能行为，读者不需要知道任何历史就能核对，是好名字。
TEST_NAME_RULES: tuple[tuple[str, str], ...] = (
    (r"_no_longer_", "名字写现在成立的契约"),
    (r"_previously_|_formerly_|_used_to_", "名字写现在成立的契约"),
)

_ALL_PROSE_RULES = tuple(
    (re.compile(pattern, re.IGNORECASE), message)
    for pattern, message in (*CHINESE_RULES, *ENGLISH_RULES)
)
_TEST_NAME_RULES = tuple(
    (re.compile(pattern), message) for pattern, message in TEST_NAME_RULES
)

#: 词表在这两个文件的正文里必须能被写出来，否则规则无法自我描述。
SELF_DESCRIBING: frozenset[str] = frozenset({
    "scripts/check_copy_final_state.py",
    "tests/test_copy_final_state.py",
})

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    term: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: 「{self.term}」 — {self.message}"


def _scan_text(path: str, line_no: int, text: str) -> list[Finding]:
    if DISABLE_MARKER in text:
        return []
    return [Finding(path, line_no, match.group(0), message)
            for pattern, message in _ALL_PROSE_RULES
            for match in pattern.finditer(text)]


def scan_lines(path: str, source: str, *, skip_code_fences: bool) -> list[Finding]:
    """逐行扫描。Markdown 的围栏代码块是命令与输出原文，不适用文案规则。"""
    found: list[Finding] = []
    fence: str | None = None
    for line_no, raw in enumerate(source.splitlines(), start=1):
        if skip_code_fences:
            fence_match = FENCE_RE.match(raw)
            if fence_match:
                delimiter = fence_match.group(1)
                if fence is None:
                    fence = delimiter
                elif delimiter[0] == fence[0] and len(delimiter) >= len(fence):
                    fence = None
                continue
            if fence is not None:
                continue
        found.extend(_scan_text(path, line_no, raw))
    return found


def scan_python(path: str, source: str) -> list[Finding]:
    """注释、docstring、字符串字面量与测试函数名，其余标识符不看。

    按 token 而不是按行，是为了让 `legacy_id` 这样的变量名不进结果：它是被执行的
    值，不是给人读的叙述。字符串字面量要看——命令行帮助和页面文案也住在里面。
    """
    found: list[Finding] = []
    lines = source.splitlines()
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return scan_lines(path, source, skip_code_fences=False)
    for token in tokens:
        if token.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        start = token.start[0]
        for offset, piece in enumerate(token.string.splitlines()):
            line_no = start + offset
            physical = lines[line_no - 1] if line_no <= len(lines) else piece
            if DISABLE_MARKER in physical:
                continue
            found.extend(_scan_text(path, line_no, piece))
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test"):
            continue
        physical = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
        if DISABLE_MARKER in physical:
            continue
        for pattern, message in _TEST_NAME_RULES:
            if pattern.search(node.name):
                found.append(Finding(path, node.lineno, pattern.pattern, message))
    return found


def targets(root: Path) -> list[Path]:
    picked: list[Path] = [root / "AGENTS.md", root / "README.md"]
    picked.extend(sorted((root / "docs").glob("*.md")))
    picked.extend(sorted((root / ".claude" / "skills").glob("*/SKILL.md")))
    picked.extend(sorted((root / "web").glob("*.html")))
    for suffix in ("*.ts", "*.tsx", "*.js"):
        picked.extend(sorted((root / "frontend" / "src").rglob(suffix)))
    for directory in ("src", "scripts", "tests"):
        picked.extend(sorted((root / directory).rglob("*.py")))
    seen: dict[Path, None] = {}
    for path in picked:
        if path.is_file():
            seen.setdefault(path.resolve(), None)
    return list(seen)


def scan_repo(root: Path = ROOT) -> list[Finding]:
    found: list[Finding] = []
    for path in targets(root):
        rel = path.relative_to(root).as_posix()
        if rel in SELF_DESCRIBING:
            continue
        source = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            found.extend(scan_python(rel, source))
        else:
            found.extend(scan_lines(rel, source, skip_code_fences=path.suffix == ".md"))
    return sorted(found, key=lambda item: (item.path, item.line, item.term))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    findings = scan_repo(Path(args.root).resolve())
    for finding in findings:
        print(finding)
    if findings:
        print(f"FAIL: {len(findings)} 处文案在叙述被否掉的做法或改动前后对比。")
        return 1
    print("PASS: 文案只描述最终状态。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
