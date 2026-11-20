from pathlib import Path

from specle.inventory import SkillMetadata, build_skill_index
from specle.schema_registry import SCHEMA_IDENTIFIERS


def test_builds_a_stable_grouped_index_for_installed_skills(tmp_path: Path) -> None:
    index = build_skill_index(
        (
            _skill("zeta", "Unknown", tmp_path),
            _skill("build", "Implementation", tmp_path),
            _skill("analyse", "Discovery", tmp_path),
            _skill("alpha", "Unknown", tmp_path),
        )
    )

    assert [group["name"] for group in index["groups"]] == [
        "Discovery",
        "Implementation",
        "Unknown",
    ]
    assert index["$schema"] == SCHEMA_IDENTIFIERS["skill-index"]
    assert [skill["name"] for skill in index["groups"][-1]["skills"]] == [
        "alpha",
        "zeta",
    ]
    assert index["groups"][0]["skills"] == [
        {
            "name": "analyse",
            "description": "Analyse description.",
            "usage": "Use analyse.",
        }
    ]


def test_index_does_not_depend_on_skill_locations(tmp_path: Path) -> None:
    left = build_skill_index((_skill("spec", "Planning", tmp_path / "left"),))
    right = build_skill_index((_skill("spec", "Planning", tmp_path / "right"),))

    assert left == right


def _skill(name: str, group: str, root: Path) -> SkillMetadata:
    return SkillMetadata(
        name=name,
        specle_group=group,
        description=f"{name.title()} description.",
        usage=f"Use {name}.",
        requires=(),
        path=root / name / "SKILL.md",
    )
