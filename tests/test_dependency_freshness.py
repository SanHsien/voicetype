"""依賴新鮮度工具的解析、判斷與報告測試。"""

from pathlib import Path

from tools import check_dependency_freshness as freshness


def test_parse_requirements_reads_bounds_and_source_files(tmp_path: Path):
    win = tmp_path / "requirements-win.txt"
    cuda = tmp_path / "requirements-cuda-win.txt"
    win.write_text("PyQt6>=6.6.0,<7\nopenai>=1.30.0,<3  # cloud\n", encoding="utf-8")
    cuda.write_text("nvidia-cudnn-cu12>=8.9.2,<10\n", encoding="utf-8")

    packages = freshness.parse_requirements((win, cuda))

    assert packages["pyqt6"]["minimum"] == "6.6.0"
    assert packages["pyqt6"]["upper"] == {"operator": "<", "version": "7"}
    assert packages["openai"]["requirement"] == "openai>=1.30.0,<3"
    assert packages["nvidia-cudnn-cu12"]["files"] == ["requirements-cuda-win.txt"]


def test_collect_status_does_not_read_installed_environment(monkeypatch):
    packages = {
        "example": {
            "name": "example",
            "minimum": "1.0.0",
            "upper": {"operator": "<", "version": "2"},
            "requirement": "example>=1.0.0,<2",
            "files": ["requirements-win.txt"],
        }
    }
    monkeypatch.setattr(freshness, "fetch_pypi_version", lambda _name: "1.4.0")

    row = freshness.collect_status(packages)[0]

    assert row["outdated"] is True
    assert row["blocked_by_upper"] is False
    assert row["check_failed"] is False


def test_marks_new_major_as_blocked_by_upper_bound(monkeypatch):
    packages = {
        "example": {
            "name": "example",
            "minimum": "1.0.0",
            "upper": {"operator": "<", "version": "2"},
            "requirement": "example>=1.0.0,<2",
            "files": ["requirements-win.txt"],
        }
    }
    monkeypatch.setattr(freshness, "fetch_pypi_version", lambda _name: "2.1.0")

    row = freshness.collect_status(packages)[0]

    assert row["outdated"] is True
    assert row["blocked_by_upper"] is True


def test_versions_with_only_trailing_zero_difference_are_equal():
    assert freshness.is_newer_version("1.14.0", "1.14") is False
    assert freshness.is_newer_version("1.14.1", "1.14") is True


def test_marks_lookup_failure_for_attention(monkeypatch):
    packages = freshness.parse_requirements(
        [Path(__file__).resolve().parent.parent / "requirements-win.txt"]
    )
    monkeypatch.setattr(freshness, "fetch_pypi_version", lambda _name: None)

    rows = freshness.collect_status(packages)

    assert rows
    assert all(row["check_failed"] for row in rows)


def test_render_markdown_explains_manual_review_policy():
    report = freshness.render_markdown(
        [
            {
                "name": "PyQt6",
                "minimum": "6.6.0",
                "upper": {"operator": "<", "version": "7"},
                "requirement": "PyQt6>=6.6.0,<7",
                "files": ["requirements-win.txt"],
                "latest": "7.0.0",
                "outdated": True,
                "blocked_by_upper": True,
                "check_failed": False,
            }
        ]
    )

    assert "有新版主線，需評估相容性" in report
    assert "不自動合併依賴 PR" in report
    assert "（installed）" not in report
