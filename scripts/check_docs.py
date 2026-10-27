#!/usr/bin/env python3
"""仓库自检：编码、BOM、换行、JSON/YAML 有效性、站内链接、旧域名残留、
未被引用的 fixture、没有被 README 收录的文档。

设计目标是「本地和 CI 跑的命令完全一样」：

    python3 scripts/check_docs.py

任何一项失败都以非 0 退出。历史上这个仓库踩过的坑（GBK 文档、BOM、死链、代码块里的假链接）
都在这里变成了检查项，避免复发。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".py",
    ".toml",
    ".txt",
    ".cfg",
    ".ini",
}
TEXT_FILENAMES = {".editorconfig", ".gitignore", ".gitattributes", "LICENSE"}

# 旧域名允许出现的位置：这些文件是「故意提到它」的历史记录
LEGACY_DOMAIN = "beta.noyteam.online"
LEGACY_ALLOWED = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "scripts/check_docs.py",
    "openapi.yaml",
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(\s*)(```+|~~~+)")
INLINE_CODE_LINK_RE = re.compile(r"\]\(https?://")

errors: list[str] = []
checked = 0
markdown: dict[Path, str] = {}


def fail(path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def iter_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_FILENAMES:
            yield path


def check_encoding(path: Path, raw: bytes) -> str | None:
    """返回解码后的文本；失败时记录错误。"""
    if raw.startswith(b"\xef\xbb\xbf"):
        fail(path, "含 UTF-8 BOM（编辑器请保存为「UTF-8 无 BOM」）")
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(path, f"不是合法 UTF-8（偏移 {exc.start}）：{exc.reason}。多半是被保存成了 GBK")
        return None
    if b"\r\n" in raw:
        fail(path, "含 CRLF 换行（请统一为 LF）")
    return text


def check_markdown(path: Path, text: str) -> None:
    in_fence = False
    fence_marker = ""
    for lineno, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if match:
            marker = match.group(2)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker[0] == fence_marker[0] and len(marker) >= len(fence_marker):
                in_fence = False
            continue

        if in_fence:
            # 代码块里不该出现 Markdown 链接语法：复制出来就是坏的
            if INLINE_CODE_LINK_RE.search(line):
                fail(path, f"第 {lineno} 行：代码块里出现 Markdown 链接语法，请改回纯 URL")
            continue

        for target in LINK_RE.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel = target.split("#", 1)[0]
            if not rel:
                continue
            resolved = (path.parent / rel).resolve()
            if not resolved.exists():
                fail(path, f"第 {lineno} 行：站内链接指向不存在的路径 {target}")


def check_legacy_domain(path: Path, text: str) -> None:
    rel = path.relative_to(ROOT).as_posix()
    if rel in LEGACY_ALLOWED:
        return
    for lineno, line in enumerate(text.splitlines(), 1):
        if LEGACY_DOMAIN in line:
            fail(path, f"第 {lineno} 行仍在使用旧域名 {LEGACY_DOMAIN}，请改成 https://noymanga.com")


def check_yaml(path: Path, text: str) -> None:
    try:
        import yaml  # noqa: PLC0415  (可选依赖，装了才检查)
    except ImportError:
        return
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as exc:
        fail(path, f"YAML 解析失败：{exc}")


def check_fixture_usage() -> None:
    """每个 fixture 都应该至少被一份文档引用，避免堆积没人看的样例。"""
    corpus = "\n".join(markdown.values())
    for path in sorted((ROOT / "fixtures").glob("*.json")):
        if path.name not in corpus:
            fail(path, "没有任何文档引用这个 fixture（要么补链接，要么删掉）")


def check_doc_index() -> None:
    """docs/ 下的每份文档都应该能从 README 找到入口。"""
    readme = markdown.get(ROOT / "README.md", "")
    for path in sorted((ROOT / "docs").rglob("*.md")):
        name = path.relative_to(ROOT).as_posix()
        if path.name not in readme and name not in readme:
            fail(path, f"README 里没有指向它的链接（{name}）")


def main() -> int:
    global checked
    for path in iter_files():
        raw = path.read_bytes()
        text = check_encoding(path, raw)
        if text is None:
            continue
        checked += 1

        if path.suffix.lower() in {".md", ".markdown"}:
            check_markdown(path, text)
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                fail(path, f"JSON 解析失败：{exc}")
        if path.suffix.lower() in {".yaml", ".yml"}:
            check_yaml(path, text)
        if path.suffix.lower() in {".md", ".markdown"}:
            markdown[path] = text
        check_legacy_domain(path, text)

    check_fixture_usage()
    check_doc_index()

    if errors:
        print(f"✗ 自检失败，共 {len(errors)} 个问题（已检查 {checked} 个文件）：\n")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(
        f"✓ 自检通过：{checked} 个文件 —— 编码 / BOM / 换行 / JSON / YAML / "
        f"站内链接 / 旧域名 / fixture 引用 / 文档索引 全部正常"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
