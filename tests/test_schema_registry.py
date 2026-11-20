from __future__ import annotations

import json
from pathlib import Path

import pytest

from specle.schema_registry import (
    SCHEMA_IDENTIFIERS,
    SchemaRegistryError,
    export_schemas,
    load_schema,
    validate_instance,
)


def test_loads_packaged_spec_status_schema() -> None:
    schema = load_schema(SCHEMA_IDENTIFIERS["spec-status"])

    assert schema["$id"] == SCHEMA_IDENTIFIERS["spec-status"]
    assert (
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["spec-status"],
                "kind": "change",
                "status": "defined",
                "progress": {},
                "verification": {"status": "not-run"},
                "review": {"status": "not-run"},
                "delivery": None,
                "relationships": [],
                "dependencies": [],
            }
        )
        == SCHEMA_IDENTIFIERS["spec-status"]
    )


def test_rejects_unknown_and_invalid_contract_instances() -> None:
    with pytest.raises(SchemaRegistryError, match="missing string"):
        validate_instance({})
    with pytest.raises(SchemaRegistryError, match="unknown schema"):
        validate_instance({"$schema": "https://example.invalid/schema"})
    with pytest.raises(SchemaRegistryError, match="failed required"):
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["spec-status"],
                "kind": "change",
                "status": "defined",
            }
        )


def test_exports_complete_schema_tree_safely(tmp_path: Path) -> None:
    destination = tmp_path / "schemas"

    assert export_schemas(destination) == destination
    assert (destination / "spec-status" / "1.0.json").is_file()
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
                "outcome_spec": None,
            }
        )
    destination = tmp_path / "schemas"
    export_schemas(destination)
    assert (
        json.loads((destination / "registry.json").read_text())[
            SCHEMA_IDENTIFIERS["spec-status"]
        ]
        == "spec-status/1.0.json"
    )
    file_destination = tmp_path / "file"
    file_destination.write_text("old")
    export_schemas(file_destination, force=True)
    assert (file_destination / "registry.json").is_file()
