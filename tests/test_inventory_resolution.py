from pathlib import Path

from specle.inventory import (
    discover_steering,
    packaged_distribution_root,
    packaged_skills_root,
)


def test_locates_packaged_skill_inventory() -> None:
    root = packaged_skills_root()

    assert root.joinpath("spec", "SKILL.md").is_file()


def test_packaged_distribution_exposes_skills_and_steering() -> None:
    root = packaged_distribution_root()

    assert root.name == "blueprints"
    assert root.joinpath("AGENTS.md").is_file()
    assert root.joinpath("skills", "spec", "SKILL.md").is_file()
    assert root.joinpath("steering", "testing.md").is_file()


def test_discovers_packaged_steering_documents() -> None:
    steering_root = (
        Path(__file__).parents[1] / "src" / "specle" / "blueprints" / "steering"
    )

    steering = discover_steering(steering_root)

    assert [path.name for path in steering] == [
        "automation.md",
        "context.md",
        "delivery.md",
        "lifecycle.md",
        "review.md",
        "testing.md",
    ]
