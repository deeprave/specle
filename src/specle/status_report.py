"""Read-only status reporting for a Specle workspace."""

import json
from datetime import datetime
from pathlib import Path

import anyio
from dateutil.parser import parse

from specle.change_state import read_active_sidecars, read_change_state
from specle.lifecycle import next_lifecycle_action


def _text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(char if char.isprintable() else " " for char in value)


async def _git(target: Path, *args: str) -> bytes | None:
    try:
        result = await anyio.run_process(
            ["git", "--no-optional-locks", "-C", str(target), *args], check=False
        )
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


async def report_status(target: Path, *, markdown: bool = False) -> None:
    """Display current work, local sidecars, Git state and optional context."""
    snapshot = await read_change_state(target)
    records = {record.name: record for record in (*snapshot.active, *snapshot.archived)}
    try:
        selected = _text(
            (
                await (anyio.Path(target) / ".specle" / "current-change").read_text()
            ).strip()
        )
    except FileNotFoundError:
        selected = ""
    print("### Current change\n" if markdown else "Current change")
    if not selected:
        print("No change in progress")
    elif selected not in records:
        print(selected)
    else:
        record = records[selected]
        action = await next_lifecycle_action(record, snapshot.selected_name)
        print(f"`{record.name}`  " if markdown else record.name)
        print(
            f"kind: {_text(record.status.get('kind'))} | status: {_text(record.status.get('status'))} | next: {action or '—'}"
            + ("  " if markdown else "")
        )
        await _dates(record.status, markdown=markdown)
    _, names, diagnostics = await read_active_sidecars(target, snapshot)
    if names or diagnostics:
        print("\n### Sidecars\n" if markdown else "\nSidecars")
    for name in names:
        record = records[name]
        action = await next_lifecycle_action(record, snapshot.selected_name)
        print(f"`{name}`  " if markdown else name)
        print(
            f"kind: {_text(record.status.get('kind'))} | status: {_text(record.status.get('status'))} | next: {action or '—'}"
            + ("  " if markdown else "")
        )
        await _dates(record.status, markdown=markdown)
    for diagnostic in diagnostics:
        print(_text(diagnostic))
    print("\n### Worktree\n" if markdown else "\nWorktree")
    branch = await _git(target, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch is None:
        head = await _git(target, "rev-parse", "--verify", "HEAD")
        print("Branch: detached HEAD" if head else "Branch: unavailable")
    else:
        print(
            f"Branch: {_text(branch.decode(errors='replace').strip())}"
            + ("  " if markdown else "")
        )
    raw = await _git(target, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if raw is None:
        print("Worktree status: unavailable")
    elif not raw:
        print("Clean")
    else:
        counts = dict.fromkeys(
            (
                "modified",
                "added",
                "deleted",
                "renamed",
                "untracked",
                "conflicted",
                "type-changed",
            ),
            0,
        )
        entries = iter(raw.split(b"\0"))
        for entry in entries:
            if not entry:
                continue
            code = entry[:2]
            if code == b"??":
                counts["untracked"] += 1
                continue
            if code in {b"DD", b"AU", b"UD", b"UA", b"DU", b"AA", b"UU"}:
                counts["conflicted"] += 1
                continue
            for marker, label in (
                (b"M", "modified"),
                (b"A", "added"),
                (b"D", "deleted"),
                (b"R", "renamed"),
                (b"T", "type-changed"),
            ):
                if marker in code:
                    counts[label] += 1
            if b"R" in code or b"C" in code:
                next(entries, None)
        print(" | ".join(f"{key}: {value}" for key, value in counts.items()))
    await _context(target, markdown=markdown)


async def _dates(status: dict[str, object], *, markdown: bool) -> None:
    dates = []
    for field in ("created", "activated", "updated", "archived", "cancelled"):
        value = status.get(f"{field}_at")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                date = datetime.fromtimestamp(value).astimezone().date().isoformat()
            except (OverflowError, OSError, ValueError):
                continue
            dates.append(f"{field}: {date}")
    if dates:
        print(" | ".join(dates) + ("  " if markdown else ""))


def _date(value: object) -> str:
    text = _text(value)
    if not text:
        return text
    try:
        return parse(text).date().isoformat()
    except (ValueError, OverflowError):
        return text


async def _context(target: Path, *, markdown: bool) -> None:
    try:
        data = json.loads(
            await (anyio.Path(target) / ".specle" / "context.json").read_text()
        )
    except FileNotFoundError:
        return
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        print("\nContext: unavailable")
        return
    if not isinstance(data, dict):
        return
    keys = [key for key in ("milestones", "todos") if key in data]
    keys.extend(key for key in data if key not in {"milestones", "todos"})
    for key in keys:
        entries = data[key]
        if not isinstance(entries, list) or not entries:
            continue
        objects = [entry for entry in entries if isinstance(entry, dict)]
        if not objects:
            continue
        heading = _text(key)[:78]
        print(f"\n### {heading.capitalize()}\n" if markdown else f"\n{heading}")
        previous_date = None
        previous_name = None
        for entry in objects:
            date = _date(entry.get("date_added"))
            name = _text(entry.get("change" if key == "milestones" else "subject"))
            detail = _text(entry.get("detail")) if key != "milestones" else ""
            subject = _text(entry.get("subject")) if key == "milestones" else ""
            if date != previous_date:
                if date:
                    print(
                        ("\n" if previous_date is not None else "") + f"**{date}**\n"
                        if markdown
                        else date
                    )
                previous_date = date
                previous_name = None
            if name and name != previous_name:
                if markdown:
                    label = f"`{name}`" if key == "milestones" else name
                    print(f"- {label}")
                else:
                    print(f"  {name[:77]}")
            if subject:
                prefix = (
                    ("  - " if name else "- ")
                    if markdown
                    else ("    " if name else "  ")
                )
                print(prefix + subject[: 79 - len(prefix)])
            if detail:
                prefix = (
                    ("  - " if name else "- ")
                    if markdown
                    else ("    " if name else "  ")
                )
                print(prefix + detail[: 79 - len(prefix)])
            previous_name = name
