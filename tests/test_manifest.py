from __future__ import annotations

import importlib.metadata
from pathlib import Path

import pytest

from specle import __version__
from specle.inventory import scan_managed_inventory
from specle.manifest import (
    ManifestError,
    append_manifest,
    build_manifest_lines,
    detect_installed_version,
    read_manifest_generations,
)

PACKAGE_VERSION = __version__


@pytest.mark.anyio
async def test_package_version_comes_from_distribution_metadata() -> None:
    assert __version__ == importlib.metadata.version("specle")


@pytest.mark.anyio
async def test_builds_stable_release_manifest_lines_from_shared_inventory() -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    lines = build_manifest_lines(
        await scan_managed_inventory(blueprints), PACKAGE_VERSION
    )

    assert lines == tuple(sorted(lines))
    assert any(
        line.startswith(f"{PACKAGE_VERSION}:skill/define/SKILL.md:") for line in lines
    )
    assert any(
        line.startswith(f"{PACKAGE_VERSION}:policies/lifecycle.md:") for line in lines
    )
    assert all("/index.json:" not in line for line in lines)


@pytest.mark.anyio
async def test_appends_missing_lines_without_rewriting_existing_entries(
    tmp_path: Path,
) -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    inventory = await scan_managed_inventory(blueprints)
    output = tmp_path / "manifest"
    expected = build_manifest_lines(inventory, PACKAGE_VERSION)
    output.write_text(f"{expected[0]}\n")

    assert (
        await append_manifest(output, inventory, PACKAGE_VERSION) == len(expected) - 1
    )
    assert output.read_text().splitlines() == list(expected)
    original = output.read_text()
    assert await append_manifest(output, inventory, PACKAGE_VERSION) == 0
    assert output.read_text() == original


@pytest.mark.anyio
async def test_preserves_an_existing_predictable_temporary_path(tmp_path: Path) -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    inventory = await scan_managed_inventory(blueprints)
    output = tmp_path / "manifest"
    existing_temporary = output.with_name(".manifest.tmp")
    existing_temporary.write_text("preserve this\n")

    await append_manifest(output, inventory, PACKAGE_VERSION)

    assert existing_temporary.read_text() == "preserve this\n"


@pytest.mark.anyio
async def test_preserves_a_colliding_temporary_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from specle import manifest

    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    inventory = await scan_managed_inventory(blueprints)
    output = tmp_path / "manifest"
    collision = tmp_path / ".manifest.existing.tmp"
    collision.write_text("preserve this\n")
    identifiers = iter(("existing", "fresh"))

    class Identifier:
        def __init__(self, value: str) -> None:
            self.hex = value

    monkeypatch.setattr(manifest, "uuid4", lambda: Identifier(next(identifiers)))
    await append_manifest(output, inventory, PACKAGE_VERSION)

    assert collision.read_text() == "preserve this\n"
    assert output.is_file()


@pytest.mark.anyio
async def test_rejects_conflicting_checksum_without_rewriting_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "manifest"
    output.write_text(f"{PACKAGE_VERSION}:policies/lifecycle.md:{'0' * 64}\n")
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    with pytest.raises(ManifestError, match="conflicting checksum"):
        await append_manifest(
            output, await scan_managed_inventory(blueprints), PACKAGE_VERSION
        )

    assert output.read_text() == f"{PACKAGE_VERSION}:policies/lifecycle.md:{'0' * 64}\n"


@pytest.mark.anyio
async def test_rejects_malformed_existing_manifest_without_rewriting_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "manifest"
    output.write_text("not-a-manifest-entry\n")
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    with pytest.raises(ManifestError, match="invalid manifest line"):
        await append_manifest(
            output, await scan_managed_inventory(blueprints), PACKAGE_VERSION
        )

    assert output.read_text() == "not-a-manifest-entry\n"


@pytest.mark.anyio
async def test_rejects_invalid_utf8_manifest_without_rewriting_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "manifest"
    output.write_bytes(b"\xff")
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"

    with pytest.raises(ManifestError, match="unable to read manifest"):
        await append_manifest(
            output, await scan_managed_inventory(blueprints), PACKAGE_VERSION
        )

    assert output.read_bytes() == b"\xff"


@pytest.mark.anyio
async def test_rejects_duplicate_identity_without_rewriting_output(
    tmp_path: Path,
) -> None:
    blueprints = Path(__file__).parents[1] / "src" / "specle" / "blueprints"
    inventory = await scan_managed_inventory(blueprints)
    output = tmp_path / "manifest"
    entry = build_manifest_lines(inventory, PACKAGE_VERSION)[0]
    output.write_text(f"{entry}\n{entry}\n")

    with pytest.raises(ManifestError, match="duplicate manifest entry"):
        await append_manifest(output, inventory, PACKAGE_VERSION)

    assert output.read_text() == f"{entry}\n{entry}\n"


@pytest.mark.anyio
async def test_reads_generations_and_reports_exact_likely_and_indeterminate_matches(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "manifest"
    first = "a" * 64
    second = "b" * 64
    manifest.write_text(
        "\n".join(
            (
                f"1.0:skill/define/SKILL.md:{first}",
                f"1.0:policies/testing.md:{second}",
                f"2.0:skill/define/SKILL.md:{second}",
                f"2.0:policies/testing.md:{second}",
            )
        )
        + "\n"
    )

    generations = await read_manifest_generations(manifest)

    assert (
        detect_installed_version(
            {
                Path("skills/define/SKILL.md"): first,
                Path("policies/testing.md"): second,
            },
            generations,
        ).confidence
        == "exact"
    )
    likely = detect_installed_version(
        {Path("skills/define/SKILL.md"): first}, generations
    )
    assert (likely.version, likely.confidence, likely.matched) == ("1.0", "likely", 1)
    assert detect_installed_version({}, generations).confidence == "indeterminate"


@pytest.mark.anyio
async def test_exact_generation_wins_over_a_purely_additive_later_generation(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "manifest"
    checksum = "a" * 64
    added = "b" * 64
    manifest.write_text(
        "\n".join(
            (
                f"1.0:skill/define/SKILL.md:{checksum}",
                f"1.1:skill/define/SKILL.md:{checksum}",
                f"1.1:policies/new.md:{added}",
            )
        )
        + "\n"
    )

    detection = detect_installed_version(
        {Path("skills/define/SKILL.md"): checksum},
        await read_manifest_generations(manifest),
    )

    assert (detection.version, detection.confidence) == ("1.0", "exact")


@pytest.mark.anyio
async def test_equivalent_exact_generations_select_the_latest_release(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "manifest"
    checksum = "a" * 64
    manifest.write_text(
        "\n".join(
            (
                f"1.0:skill/define/SKILL.md:{checksum}",
                f"1.1:skill/define/SKILL.md:{checksum}",
            )
        )
        + "\n"
    )

    detection = detect_installed_version(
        {Path("skills/define/SKILL.md"): checksum},
        await read_manifest_generations(manifest),
    )

    assert (detection.version, detection.confidence) == ("1.1", "exact")


@pytest.mark.anyio
async def test_partial_detection_penalises_missing_and_mismatched_resources(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "manifest"
    first = "a" * 64
    second = "b" * 64
    third = "c" * 64
    manifest.write_text(
        "\n".join(
            (
                f"1.0:skill/define/SKILL.md:{first}",
                f"1.0:policies/testing.md:{second}",
                f"2.0:skill/define/SKILL.md:{first}",
                f"2.0:policies/extra.md:{third}",
            )
        )
        + "\n"
    )

    detection = detect_installed_version(
        {
            Path("skills/define/SKILL.md"): first,
            Path("policies/testing.md"): third,
        },
        await read_manifest_generations(manifest),
    )

    assert (detection.version, detection.confidence, detection.matched) == (
        "2.0",
        "likely",
        1,
    )
