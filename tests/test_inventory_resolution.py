from specle.inventory import packaged_distribution_root


def test_packaged_distribution_exposes_skills_and_policies() -> None:
    root = packaged_distribution_root()

    assert root.name == "blueprints"
    assert root.joinpath("AGENTS.md").is_file()
    assert root.joinpath("skills", "define", "SKILL.md").is_file()
    assert root.joinpath("policies", "testing.md").is_file()
