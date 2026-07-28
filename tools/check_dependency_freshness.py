#!/usr/bin/env python3
"""檢查 VoxProse 直接依賴是否有較新版本。

此工具只讀取 requirements-win.txt / requirements-cuda-win.txt 的宣告與
PyPI JSON API，不讀取目前電腦已安裝的套件版本，確保本機與 GitHub Actions
產生一致結果。它只輸出維護報告，不會自行修改依賴或建立 Release。
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILES = (
    ROOT / "requirements-win.txt",
    ROOT / "requirements-cuda-win.txt",
)

_PACKAGE_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*(.*)$")
_SPECIFIER_RE = re.compile(
    r"(>=|>|<=|<|==|~=)\s*([0-9][0-9A-Za-z.!+_-]*(?:\.[0-9A-Za-z!+_-]+)*)"
)


def normalize_package_name(package_name: str) -> str:
    """依 Python 套件名稱規則正規化連字號、底線與大小寫。"""
    return re.sub(r"[-_.]+", "-", package_name).lower()


def parse_version(text: str) -> tuple:
    """將一般 PyPI 版本轉成可比較的數值 tuple。

    本專案直接依賴目前使用一般數字版本或 calendar version；PyPI JSON 的
    ``info.version`` 只回傳穩定最新版，因此不需要完整實作 PEP 440 resolver。
    """
    parts = []
    for piece in (text or "").strip().lstrip("vV").split("."):
        match = re.match(r"(\d+)", piece)
        parts.append(int(match.group(1)) if match else 0)
    return tuple(parts) if parts else (0,)


def is_newer_version(latest: str, current: str) -> bool:
    """latest 是否比 current 新。"""
    return parse_version(latest) > parse_version(current)


def parse_requirements(paths: Iterable[Path]) -> "Dict[str, Dict[str, object]]":
    """解析直接依賴、最低版本、上限與來源檔案。"""
    packages: "Dict[str, Dict[str, object]]" = {}
    for path in paths:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or line.startswith(("-", "http://", "https://")):
                continue
            match = _PACKAGE_RE.match(line)
            if not match:
                continue
            name = match.group(1)
            specifiers = _SPECIFIER_RE.findall(match.group(2))
            minimum = next(
                (version for operator, version in specifiers if operator in {">=", ">", "==", "~="}),
                "",
            )
            upper = next(
                (
                    {"operator": operator, "version": version}
                    for operator, version in specifiers
                    if operator in {"<", "<="}
                ),
                None,
            )
            normalized = normalize_package_name(name)
            packages[normalized] = {
                "name": name,
                "minimum": minimum,
                "upper": upper,
                "requirement": line,
                "files": [path.name],
            }
    return packages


def fetch_pypi_version(package_name: str, timeout: float = 10.0) -> Optional[str]:
    """回傳 PyPI 最新穩定版本；查不到時回傳 None。"""
    req = urllib.request.Request(
        f"https://pypi.org/pypi/{package_name}/json",
        headers={"Accept": "application/json", "User-Agent": "voxprose-dependency-check"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310 - 固定 https
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("info", {}).get("version")
    except Exception:
        return None


def is_blocked_by_upper_bound(version: str, upper: Optional[Dict[str, str]]) -> bool:
    """version 是否被 requirements 的版本上限排除。"""
    if not upper:
        return False
    candidate = parse_version(version)
    ceiling = parse_version(upper["version"])
    if upper["operator"] == "<":
        return candidate >= ceiling
    return candidate > ceiling


def collect_status(
    packages: "Dict[str, Dict[str, object]]",
) -> "List[Dict[str, object]]":
    """收集 repo 宣告基線、PyPI 最新版與維護狀態。"""
    rows = []
    for package in packages.values():
        minimum = str(package["minimum"])
        latest = fetch_pypi_version(str(package["name"]))
        check_failed = not minimum or latest is None
        outdated = bool(minimum and latest and is_newer_version(latest, minimum))
        blocked = bool(latest and is_blocked_by_upper_bound(latest, package.get("upper")))
        rows.append(
            {
                **package,
                "latest": latest or "unknown",
                "outdated": outdated,
                "blocked_by_upper": blocked,
                "check_failed": check_failed,
            }
        )
    return rows


def render_markdown(rows: "List[Dict[str, object]]") -> str:
    """輸出 GitHub issue 與 Actions summary 可讀的 Markdown。"""
    lines = [
        "# VoxProse 依賴新鮮度檢查",
        "",
        "| 套件 | Repo 宣告範圍 | PyPI 最新 | 狀態 |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        if row["check_failed"]:
            status = "檢查失敗"
        elif row["blocked_by_upper"]:
            status = "有新版主線，需評估相容性"
        elif row["outdated"]:
            status = "可更新版本基線"
        else:
            status = "OK"
        files = "、".join(f"`{name}`" for name in row["files"])
        lines.append(
            f"| `{row['name']}` | `{row['requirement']}`（{files}） "
            f"| `{row['latest']}` | {status} |"
        )
    lines.extend(
        [
            "",
            "本報告只比較 repo 宣告與 PyPI，不使用 runner 或維護者電腦目前安裝的版本，",
            "因此每次執行結果可重現。版本上限外的新主線只表示「需要評估」，不代表可以",
            "直接升級。",
            "",
            "## 處理流程",
            "",
            "1. 查看同批 Dependabot PR、套件 changelog、Python 3.10–3.14 wheel 與 Windows 相容性。",
            "2. 執行期、PyQt6、Whisper、ONNX Runtime、CUDA 與 GitHub Actions 更新一律人工審查；",
            "   本 repo 不自動合併依賴 PR。",
            "3. 通過完整 CI；會影響錄音、STT、CUDA、UI 或打包鏈時，再完成對應 Windows",
            "   實機／Release 驗證後合併。",
            "4. 追蹤依賴皆更新且沒有 open Dependabot PR 時，排程會自動關閉維護 issue。",
        ]
    )
    return "\n".join(lines) + "\n"


def write_github_output(
    outdated: bool,
    check_failed: bool,
    report_path: Path,
) -> None:
    """寫入 GitHub Actions output。"""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"outdated={'true' if outdated else 'false'}\n")
        output.write(f"check_failed={'true' if check_failed else 'false'}\n")
        output.write(f"needs_attention={'true' if outdated or check_failed else 'false'}\n")
        output.write(f"report_path={report_path.as_posix()}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="檢查 VoxProse requirements-win.txt / requirements-cuda-win.txt 是否有新版"
    )
    parser.add_argument(
        "--output",
        default="dependency-freshness-report.md",
        help="Markdown 報告輸出路徑",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="同時寫入 GitHub Actions output",
    )
    args = parser.parse_args()

    packages = parse_requirements(REQUIREMENTS_FILES)
    if not packages:
        print("[WARN] 未解析到任何依賴套件，requirements 檔案是否存在？", file=sys.stderr)

    rows = collect_status(packages)
    report = render_markdown(rows)
    output_path = Path(args.output)
    output_path.write_text(report, encoding="utf-8")
    print(report)

    outdated = any(bool(row["outdated"]) for row in rows)
    check_failed = not rows or any(bool(row["check_failed"]) for row in rows)
    if args.github_output:
        write_github_output(outdated, check_failed, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
