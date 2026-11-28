import json
import subprocess
from pathlib import Path

import anyio
import pytest

from specle.main import main


def test_status_reports_context_and_git_without_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".specle").mkdir()
    (tmp_path / ".specle" / "context.json").write_text(
        json.dumps(
            {
                "milestones": [
                    {
                        "date_added": "2026-11-28T12:30:00+11:00",
                        "change": "example",
                        "detail": "x" * 60,
                    }
                ],
                "todos": [{"date_added": "2026-11-27", "subject": "do something"}],
                "ideas": [{"date_added": "2026-11-26", "subject": "idea"}],
            }
        )
    )
    (tmp_path / "secret-name").write_text("test")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    output = capsys.readouterr().out
    assert "No change in progress" in output
    assert "2026-11-28" in output and "12:30" not in output
    assert "x" * 60 in output
    assert "do something" in output and "idea" in output
    assert output.index("milestones") < output.index("todos") < output.index("ideas")
    assert "secret-name" not in output
    assert all(len(line) < 80 for line in output.splitlines() if "2026-11-" in line)


def test_status_reports_invalid_selector_without_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".specle").mkdir()
    selector = tmp_path / ".specle" / "current-change"
    selector.write_text("bad/name\n")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    assert "Invalid" in capsys.readouterr().out
    assert selector.read_text() == "bad/name\n"


def test_status_reports_selected_change_and_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / ".specle"
    for name, kind, status, relationships in [
        (
            "example",
            "change",
            "building",
            [
                {
                    "change": "fix-example",
                    "type": "bugfix",
                    "delivery": "with-related-change",
                }
            ],
        ),
        ("fix-example", "bugfix", "building", []),
    ]:
        directory = root / "changes" / name
        directory.mkdir(parents=True)
        (directory / "status.json").write_text(
            json.dumps(
                {
                    "$schema": "specle://schemas/change-status/1.0",
                    "kind": kind,
                    "status": status,
                    "created_at": 1795830894,
                    "activated_at": None,
                    "progress": {},
                    "verification": {"status": "not-run"},
                    "review": {"status": "not-run"},
                    "delivery": None,
                    "dependencies": [],
                    "relationships": relationships,
                }
            )
        )
    (root / "current-change").write_text("example\n")
    (root / "current-sidecars").write_text("fix-example\n")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    output = capsys.readouterr().out
    assert "example\nkind: change | status: building | next: build" in output
    assert (
        "Sidecars\nfix-example\nkind: bugfix | status: building | next: build" in output
    )
    assert output.count("fix-example") == 1
    assert "created_at:" in output
    assert "Branch: unavailable" in output


def test_status_reports_git_rename_and_detached_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True
    )
    (tmp_path / "old name").write_text("contents")
    subprocess.run(["git", "-C", str(tmp_path), "add", "old name"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "initial",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "checkout", "-q", "--detach"], check=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "mv", "old name", "new name"], check=True
    )
    (tmp_path / "untracked").write_text("contents")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    output = capsys.readouterr().out
    assert "detached HEAD" in output
    assert "renamed: 1" in output and "untracked: 1" in output
    assert "old name" not in output and "new name" not in output


def test_status_shows_archived_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / ".specle"
    archive = root / "archive" / "finished"
    archive.mkdir(parents=True)
    (archive / "status.json").write_text(
        json.dumps(
            {
                "$schema": "specle://schemas/change-status/1.0",
                "kind": "change",
                "status": "complete",
                "created_at": 1,
                "activated_at": None,
                "archived_at": 2,
                "progress": {},
                "verification": {"status": "not-run"},
                "review": {"status": "not-run"},
                "delivery": None,
                "dependencies": [],
                "relationships": [],
            }
        )
    )
    (root / "current-change").write_text("finished\n")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    output = capsys.readouterr().out
    assert "finished\nkind: change | status: complete | next:" in output
    assert "archived_at:" in output


def test_status_groups_consecutive_context_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / ".specle"
    root.mkdir()
    (root / "context.json").write_text(
        json.dumps(
            {
                "ideas": [{"date_added": "2026-11-27", "subject": "Idea"}],
                "milestones": [
                    {
                        "date_added": "2026-11-28T01:00:00",
                        "change": "example",
                        "detail": "First",
                    },
                    {
                        "date_added": "2026-11-28T02:00:00",
                        "change": "example",
                        "detail": "Second",
                    },
                    {"date_added": "2026-11-28", "change": "other", "detail": "Third"},
                ],
                "todos": [
                    {
                        "date_added": "2026-11-27",
                        "subject": "Task",
                        "detail": "More detail",
                    }
                ],
            }
        )
    )
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    output = capsys.readouterr().out
    assert "2026-11-28\n  example\n    First\n    Second\n  other\n    Third" in output
    assert "  Task\n    More detail" in output
    assert output.index("milestones") < output.index("todos") < output.index("ideas")


def test_status_uses_registry_without_requiring_a_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / ".specle"
    sidecar = root / "changes" / "fix-alone"
    sidecar.mkdir(parents=True)
    (sidecar / "status.json").write_text(
        json.dumps(
            {
                "$schema": "specle://schemas/change-status/1.0",
                "kind": "refactor",
                "status": "building",
                "created_at": 1,
                "activated_at": None,
                "progress": {},
                "verification": {"status": "not-run"},
                "review": {"status": "not-run"},
                "delivery": None,
                "dependencies": [],
                "relationships": [],
            }
        )
    )
    (root / "current-sidecars").write_text("fix-alone\n")
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status"])
    assert (
        "Sidecars\nfix-alone\nkind: refactor | status: building | next: build"
        in capsys.readouterr().out
    )


def test_status_markdown_outputs_headings_and_context_bullets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / ".specle"
    root.mkdir()
    (root / "context.json").write_text(
        json.dumps(
            {
                "todos": [
                    {
                        "date_added": "2026-11-28",
                        "subject": "Do work",
                        "detail": "Details",
                    }
                ],
                "milestones": [
                    {
                        "date_added": "2026-11-28",
                        "change": "example",
                        "detail": "Finished",
                    }
                ],
            }
        )
    )
    monkeypatch.chdir(tmp_path)
    anyio.run(main, ["status", "--markdown"])
    output = capsys.readouterr().out
    assert "### Current change" in output
    assert "### Worktree" in output
    assert "### Milestones" in output
    assert "**2026-11-28**" in output
    assert "- `example`" in output and "  - Finished" in output
    assert "- Do work" in output and "  - Details" in output
    assert output.index("### Milestones") < output.index("### Todos")
