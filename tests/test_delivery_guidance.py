from pathlib import Path


def test_complete_guidance_separates_direct_and_branch_finalisation() -> None:
    complete = _blueprint("complete")

    assert "Do not add `delivery.completion`" in complete
    assert (
        "containing only the original PR `reference`, `head_branch`, and `target_branch`"
        in complete
    )
    assert "Do not write an archival commit SHA or completion event." in complete
    assert "determine and perform only the first missing phase" in complete


def test_complete_guidance_requires_the_current_delivery_phase_branch() -> None:
    complete = _blueprint("complete")

    assert "Require the checkout to equal that phase branch." in complete
    assert "do not stash, switch, or infer why the branches differ" in complete
    assert "<delivery-branch>-complete" in complete
    assert "only permitted second PR" in complete


def test_archived_records_are_immutable_to_triage_and_resolve() -> None:
    triage = _blueprint("triage")
    resolve = _blueprint("resolve")

    assert "Archived records do not enter triage." in triage
    assert "Do not modify an archived record." in triage
    assert "archived exception" not in resolve


def _blueprint(name: str) -> str:
    return (
        Path(__file__).parents[1]
        / "src"
        / "specle"
        / "blueprints"
        / "skills"
        / name
        / "SKILL.md"
    ).read_text()
