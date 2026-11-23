from __future__ import annotations

import json
from datetime import timedelta, timezone
from pathlib import Path

import pytest

from specle.schema_registry import (
    SCHEMA_IDENTIFIERS,
    SchemaRegistryError,
    export_schemas,
    load_schema,
    normalize_change_timestamp,
    validate_instance,
)


def test_loads_packaged_change_status_schema() -> None:
    schema = load_schema(SCHEMA_IDENTIFIERS["change-status"])

    assert schema["$id"] == SCHEMA_IDENTIFIERS["change-status"]
    assert (
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["change-status"],
                "kind": "change",
                "status": "defined",
                "created_at": 1_795_252_440,
                "activated_at": None,
                "progress": {},
                "verification": {"status": "not-run"},
                "review": {"status": "not-run"},
                "delivery": None,
                "relationships": [],
                "dependencies": [],
            }
        )
        == SCHEMA_IDENTIFIERS["change-status"]
    )


def test_uses_package_owned_schema_identifiers(tmp_path: Path) -> None:
    assert all(
        identifier.startswith("specle://schemas/")
        for identifier in SCHEMA_IDENTIFIERS.values()
    )

    destination = tmp_path / "schemas"
    export_schemas(destination)
    registry = json.loads((destination / "registry.json").read_text())

    assert all(identifier.startswith("specle://schemas/") for identifier in registry)


def test_rejects_unknown_and_invalid_contract_instances() -> None:
    with pytest.raises(SchemaRegistryError, match="missing string"):
        validate_instance({})
    with pytest.raises(SchemaRegistryError, match="unknown schema"):
        validate_instance({"$schema": "https://example.invalid/schema"})
    with pytest.raises(SchemaRegistryError, match="failed required"):
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["change-status"],
                "kind": "change",
                "status": "defined",
            }
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-11-21T20:14:00", 1_795_252_440),
        ("2026-11-21T20:14:00+10:00", 1_795_256_040),
        (1_763_724_840_000, 1_763_724_840),
        (1_763_724_840_000_000_000, 1_763_724_840),
    ],
)
def test_normalizes_supported_change_timestamps(
    value: str | int, expected: int
) -> None:
    assert (
        normalize_change_timestamp(value, local_timezone=timezone(timedelta(hours=11)))
        == expected
    )


def test_rejects_date_only_timestamp_input() -> None:
    with pytest.raises(SchemaRegistryError, match="timestamp"):
        normalize_change_timestamp("2026-11-21")


def test_change_status_validation_rejects_noncanonical_durable_timestamp() -> None:
    instance = _change_status(created_at="not-a-timestamp")

    with pytest.raises(SchemaRegistryError, match="failed type"):
        validate_instance(instance)


def test_change_status_validates_optional_lifecycle_timestamps() -> None:
    instance = _change_status(created_at=1_795_252_440)
    instance["updated_at"] = 1_795_252_441
    instance["archived_at"] = 1_795_252_442.5

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["change-status"]

    instance["updated_at"] = "tomorrow"

    with pytest.raises(SchemaRegistryError, match="failed type"):
        validate_instance(instance)


def test_change_status_validates_completion_delivery_evidence() -> None:
    instance = _change_status(created_at=1_795_252_440)
    instance["delivery"] = {
        "completion": {
            "reference": "https://github.com/deeprave/specle/pull/36",
            "head_branch": "feature/example-completion",
            "target_branch": "main",
            "event": "pull-request-open",
        }
    }

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["change-status"]

    del instance["delivery"]["completion"]["event"]

    with pytest.raises(SchemaRegistryError, match="failed required"):
        validate_instance(instance)


def test_change_status_accepts_a_concurrent_delivery_relationship() -> None:
    instance = _change_status(created_at=1_795_252_440)
    instance["relationships"] = [
        {
            "change": "fix-example",
            "type": "bugfix",
            "delivery": "with-related-change",
        }
    ]

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["change-status"]


def _change_status(*, created_at: str | float) -> dict[str, object]:
    return {
        "$schema": SCHEMA_IDENTIFIERS["change-status"],
        "kind": "change",
        "status": "defined",
        "created_at": created_at,
        "activated_at": None,
        "progress": {},
        "verification": {"status": "not-run"},
        "review": {"status": "not-run"},
        "delivery": None,
        "relationships": [],
        "dependencies": [],
    }


def test_exports_complete_schema_tree_safely(tmp_path: Path) -> None:
    destination = tmp_path / "schemas"

    assert export_schemas(destination) == destination
    assert (destination / "change-status" / "1.0.json").is_file()
    with pytest.raises(SchemaRegistryError, match="already exists"):
        export_schemas(destination)

    (destination / "obsolete.json").write_text("obsolete")
    export_schemas(destination, force=True)

    assert not (destination / "obsolete.json").exists()


def test_enforces_contract_constraints_and_exports_registry(tmp_path: Path) -> None:
    with pytest.raises(SchemaRegistryError, match="failed anyOf"):
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["tracker-links"],
                "sources": [],
                "destination": {
                    "system": "github",
                    "kind": "issue",
                    "id": "1",
                    "url": "not-a-canonical-url",
                },
            }
        )
    with pytest.raises(SchemaRegistryError, match="failed enum"):
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["findings"],
                "question": "q",
                "hypothesis": "h",
                "effort": "S",
                "scope": "s",
                "status": "bad",
                "findings": [],
                "recommendations": [],
                "risks": [],
                "outcome_change": None,
            }
        )
    destination = tmp_path / "schemas"
    export_schemas(destination)
    assert (
        json.loads((destination / "registry.json").read_text())[
            SCHEMA_IDENTIFIERS["change-status"]
        ]
        == "change-status/1.0.json"
    )
    file_destination = tmp_path / "file"
    file_destination.write_text("old")
    export_schemas(file_destination, force=True)
    assert (file_destination / "registry.json").is_file()
