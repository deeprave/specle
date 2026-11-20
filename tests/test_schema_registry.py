from __future__ import annotations

from pathlib import Path

import pytest

from specle.schema_registry import (
    SCHEMA_IDENTIFIERS,
    SchemaRegistryError,
    export_schemas,
    load_schema,
    validate_instance,
)


def test_loads_packaged_schema_with_internal_reference() -> None:
    schema = load_schema(SCHEMA_IDENTIFIERS["context"])

    assert schema["$id"] == SCHEMA_IDENTIFIERS["context"]
    assert "$ref" in str(schema)
    assert (
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["context"],
                "current_spec": {
                    "name": "example",
                    "path": ".specle/specs/example",
                    "status": "defined",
                },
                "recent_specs": [],
                "queued_specs": [],
            }
        )
        == SCHEMA_IDENTIFIERS["context"]
    )


def test_rejects_unknown_and_invalid_contract_instances() -> None:
    with pytest.raises(SchemaRegistryError, match="missing string"):
        validate_instance({})
    with pytest.raises(SchemaRegistryError, match="unknown schema"):
        validate_instance({"$schema": "https://example.invalid/schema"})
    with pytest.raises(SchemaRegistryError, match="current_spec"):
        validate_instance(
            {
                "$schema": SCHEMA_IDENTIFIERS["context"],
                "recent_specs": [],
                "queued_specs": [],
            }
        )


def test_exports_complete_schema_tree_safely(tmp_path: Path) -> None:
    destination = tmp_path / "schemas"

    assert export_schemas(destination) == destination
    assert (destination / "context" / "1.0.json").is_file()
    with pytest.raises(SchemaRegistryError, match="already exists"):
        export_schemas(destination)

    (destination / "obsolete.json").write_text("obsolete")
    export_schemas(destination, force=True)

    assert not (destination / "obsolete.json").exists()
