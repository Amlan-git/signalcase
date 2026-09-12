import json
from pathlib import Path

import pytest
from signalcase_contracts import validate_fixture_bundle
from signalcase_contracts.models import SignalCaseFixtureBundle


def test_required_fixture_catalog_exists() -> None:
    """Catch a missing state fixture that would block parallel consumers."""

    fixture_dir = Path("contracts/examples")
    actual = {path.stem for path in fixture_dir.glob("*.json")}

    assert actual == {"blocked", "failed", "reproduced"}


@pytest.mark.parametrize(
    ("fixture_name", "job_status", "report_outcome"),
    [
        ("reproduced", "completed", "reproduced"),
        ("blocked", "completed", "blocked"),
        ("failed", "failed", None),
    ],
)
def test_fixture_is_valid_and_represents_named_state(
    fixture_name: str,
    job_status: str,
    report_outcome: str | None,
) -> None:
    """Catch structurally valid fixtures that portray the wrong UI state."""

    fixture_path = Path("contracts/examples") / f"{fixture_name}.json"
    bundle = json.loads(fixture_path.read_text(encoding="utf-8"))

    validate_fixture_bundle(bundle)

    assert bundle["jobs"][0]["status"] == job_status
    actual_outcome = bundle["reports"][0]["outcome"] if bundle["reports"] else None
    assert actual_outcome == report_outcome


def test_generated_python_models_roundtrip_the_canonical_fixture() -> None:
    """Catch generated Python types that discard or rewrite wire fields."""

    fixture_path = Path("contracts/examples/reproduced.json")
    original = json.loads(fixture_path.read_text(encoding="utf-8"))

    parsed = SignalCaseFixtureBundle.model_validate(original)

    assert parsed.model_dump(mode="json") == original
