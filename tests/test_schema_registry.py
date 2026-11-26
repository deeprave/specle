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


def test_context_contract_accepts_handoff_collections_and_extensions() -> None:
    instance = {
        "$schema": SCHEMA_IDENTIFIERS["context"],
        "milestones": [
            {
                "date_added": "2026-11-26T10:26:00+11:00",
                "subject": "Completed the initial design",
                "change": "resurrect-context-json",
                "detail": {"why": ["handoff", "continuity"]},
                "agent_note": True,
            }
        ],
        "todos": [
            {
                "date_added": "2026-11-21T20:14:00+10:00",
                "subject": "Consider the local branch model",
                "detail": ["investigate", {"later": None}],
            }
        ],
        "directives": [
            {"subject": "Do not create speculative concurrency handling", "detail": 3}
        ],
        "project_handoff": {"owner": "developer"},
    }

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["context"]


@pytest.mark.parametrize(
    "instance",
    [
        {"$schema": "specle://schemas/context/1.0", "milestones": [{}]},
        {
            "$schema": "specle://schemas/context/1.0",
            "todos": [{"date_added": 1, "subject": ""}],
        },
        {
            "$schema": "specle://schemas/context/1.0",
            "directives": [{"subject": ""}],
        },
    ],
)
def test_context_contract_rejects_invalid_recognised_items(
    instance: dict[str, object],
) -> None:
    with pytest.raises(SchemaRegistryError):
        validate_instance(instance)


def test_context_contract_accepts_a_minimal_document_and_exports_its_schema(
    tmp_path: Path,
) -> None:
    instance = {"$schema": SCHEMA_IDENTIFIERS["context"]}

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["context"]
    destination = tmp_path / "schemas"
    export_schemas(destination)
    assert (destination / "context" / "1.0.json").is_file()


@pytest.mark.parametrize("collection", ["milestones", "todos"])
@pytest.mark.parametrize("value", ["", 1_795_252_440, True])
def test_context_contract_rejects_empty_or_non_string_date_added(
    collection: str, value: object
) -> None:
    instance = {
        "$schema": SCHEMA_IDENTIFIERS["context"],
        collection: [{"date_added": value, "subject": "Recorded"}],
    }

    with pytest.raises(SchemaRegistryError):
        validate_instance(instance)


@pytest.mark.parametrize("collection", ["milestones", "todos"])
@pytest.mark.parametrize(
    "value",
    [
        "Tuesday morning",
        "2026-11-21",
        "2026-11-21T20:14:00Z",
        "2026-11-21T20:14:00",
    ],
)
def test_context_contract_accepts_human_readable_local_date_added(
    collection: str, value: str
) -> None:
    instance = {
        "$schema": SCHEMA_IDENTIFIERS["context"],
        collection: [{"date_added": value, "subject": "Recorded"}],
    }

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["context"]


@pytest.mark.parametrize(
    "instance",
    [
        {"$schema": SCHEMA_IDENTIFIERS["context"], "todos": {}},
        {
            "$schema": SCHEMA_IDENTIFIERS["context"],
            "todos": [
                {
                    "date_added": "2026-11-21T20:14:00+10:00",
                    "subject": "A todo",
                    "change": "",
                }
            ],
        },
    ],
)
def test_context_contract_rejects_invalid_collection_shapes(
    instance: dict[str, object],
) -> None:
    with pytest.raises(SchemaRegistryError):
        validate_instance(instance)


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
        "reference": "https://github.com/deeprave/specle/pull/36",
        "head_branch": "feature/example",
        "target_branch": "main",
        "completion": {
            "reference": "https://github.com/deeprave/specle/pull/36",
            "head_branch": "feature/example",
            "target_branch": "main",
        },
    }

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["change-status"]

    instance["delivery"]["completion"]["commit"] = "abcdef0"

    with pytest.raises(SchemaRegistryError, match="failed additionalProperties"):
        validate_instance(instance)

    del instance["delivery"]["completion"]["commit"]
    instance["delivery"]["completion"]["event"] = "pull-request-open"

    with pytest.raises(SchemaRegistryError, match="failed additionalProperties"):
        validate_instance(instance)

    del instance["delivery"]["completion"]["event"]
    del instance["delivery"]["completion"]["reference"]

    with pytest.raises(SchemaRegistryError, match="failed required"):
        validate_instance(instance)


def test_change_status_accepts_direct_delivery_without_completion_evidence() -> None:
    instance = _change_status(created_at=1_795_252_440)
    instance["delivery"] = {
        "branch": "main",
        "commit": "abcdef0",
        "event": "direct-push",
    }

    assert validate_instance(instance) == SCHEMA_IDENTIFIERS["change-status"]


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

    instance["relationships"][0]["delivery"] = ""

    with pytest.raises(SchemaRegistryError, match="minLength"):
        validate_instance(instance)


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


def test_accepts_agent_meaningful_tracker_locators(tmp_path: Path) -> None:
    assert (
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["tracker-links"],
                "sources": [
                    {
                        "system": "tracker-mcp",
                        "kind": "issue",
                        "id": "42",
                        "url": "mcp://tracker/issues/42",
                    }
                ],
                "destination": {
                    "system": "tracker-mcp",
                    "kind": "issue",
                    "id": "42",
                    "url": "tcp://tracker.internal:9000/issues/42",
                },
            }
        )
        == SCHEMA_IDENTIFIERS["tracker-links"]
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
