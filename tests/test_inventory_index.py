from pathlib import Path

from specle.inventory import SkillMetadata, build_skill_index


def test_builds_a_stable_grouped_index_for_installed_skills(tmp_path: Path) -> None:
    skills_root = tmp_path / ".agents" / "skills"
    index = build_skill_index(
        (
            _skill("zeta", "Unknown", tmp_path),
            _skill("build", "Implementation", tmp_path),
            _skill("analyse", "Discovery", tmp_path),
            _skill("alpha", "Unknown", tmp_path),
        ),
        skills_root,
    )

    assert [group["name"] for group in index["groups"]] == [
        "Discovery",
        "Implementation",
        "Unknown",
    ]
    assert [skill["name"] for skill in index["groups"][-1]["skills"]] == [
        "alpha",
        "zeta",
    ]
    assert index["groups"][0]["skills"] == [
        {
            "name": "analyse",
            "specle_group": "Discovery",
            "description": "Analyse description.",
            "usage": "Use analyse.",
            "resource": (skills_root / "analyse" / "SKILL.md").as_uri(),
        }
    ]


def _skill(name: str, group: str, root: Path) -> SkillMetadata:
    return SkillMetadata(
        name=name,
        specle_group=group,
        description=f"{name.title()} description.",
        usage=f"Use {name}.",
        requires=(),
        path=root / name / "SKILL.md",
    )
