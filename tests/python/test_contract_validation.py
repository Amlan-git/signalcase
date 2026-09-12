from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
import signalcase_contracts
from signalcase_contracts import ContractValidationError, validate_fixture_bundle

WORKSPACE_ID = "11111111-1111-4111-8111-111111111111"
JOB_ID = "22222222-2222-4222-8222-222222222222"
CONVERSATION_ID = "33333333-3333-4333-8333-333333333333"
DOCUMENT_ID = "44444444-4444-4444-8444-444444444444"
GROUP_ID = "55555555-5555-4555-8555-555555555555"
SCREENSHOT_ID = "66666666-6666-4666-8666-666666666666"
REPLAY_SCREENSHOT_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaab"
DOCUMENT_EVIDENCE_ID = "77777777-7777-4777-8777-777777777777"
SESSION_ONE_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaac"
SESSION_TWO_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaad"
EVENT_ID = "88888888-8888-4888-8888-888888888888"
REPORT_ID = "99999999-9999-4999-8999-999999999999"


def valid_bundle() -> dict[str, object]:
    """Return a hand-checked, source-linked reproduced investigation."""

    return {
        "contract_version": "1",
        "conversations": [
            {
                "id": CONVERSATION_ID,
                "workspace_id": WORKSPACE_ID,
                "source": "support_chat",
                "external_id": "CHAT-42",
                "text": "SAVE10 disappeared when I changed quantity to two.",
                "created_at": "2026-09-12T12:00:00Z",
            }
        ],
        "documents": [
            {
                "id": DOCUMENT_ID,
                "workspace_id": WORKSPACE_ID,
                "title": "Coupon policy",
                "text": "SAVE10 gives ten percent off eligible items until checkout.",
                "version": "1",
            }
        ],
        "existing_issues": [],
        "groups": [
            {
                "id": GROUP_ID,
                "workspace_id": WORKSPACE_ID,
                "conversation_ids": [CONVERSATION_ID],
                "claim": "Changing quantity removes the documented discount.",
                "prerequisites": ["Eligible item", "SAVE10 accepted"],
                "unknowns": [],
            }
        ],
        "evidence": [
            {
                "id": SCREENSHOT_ID,
                "job_id": JOB_ID,
                "workspace_id": WORKSPACE_ID,
                "session_id": SESSION_ONE_ID,
                "kind": "screenshot",
                "created_at": "2026-09-12T12:01:00Z",
                "storage_key": (
                    f"workspaces/{WORKSPACE_ID}/jobs/{JOB_ID}/evidence/{SCREENSHOT_ID}"
                ),
                "sha256": "a" * 64,
                "mime_type": "image/png",
                "summary": "Cart shows two items at 20,000 minor units after SAVE10.",
                "document_id": None,
                "quote": None,
            },
            {
                "id": REPLAY_SCREENSHOT_ID,
                "job_id": JOB_ID,
                "workspace_id": WORKSPACE_ID,
                "session_id": SESSION_TWO_ID,
                "kind": "screenshot",
                "created_at": "2026-09-12T12:01:30Z",
                "storage_key": (
                    f"workspaces/{WORKSPACE_ID}/jobs/{JOB_ID}/evidence/{REPLAY_SCREENSHOT_ID}"
                ),
                "sha256": "c" * 64,
                "mime_type": "image/png",
                "summary": "Fresh cart session again shows 20,000 minor units after SAVE10.",
                "document_id": None,
                "quote": None,
            },
            {
                "id": DOCUMENT_EVIDENCE_ID,
                "job_id": JOB_ID,
                "workspace_id": WORKSPACE_ID,
                "session_id": None,
                "kind": "document_excerpt",
                "created_at": "2026-09-12T12:00:30Z",
                "storage_key": (
                    f"workspaces/{WORKSPACE_ID}/jobs/{JOB_ID}/evidence/{DOCUMENT_EVIDENCE_ID}"
                ),
                "sha256": "b" * 64,
                "mime_type": "text/plain",
                "summary": "Coupon policy states SAVE10 remains active until checkout.",
                "document_id": DOCUMENT_ID,
                "quote": "SAVE10 gives ten percent off eligible items until checkout.",
            },
        ],
        "events": [
            {
                "id": EVENT_ID,
                "job_id": JOB_ID,
                "workspace_id": WORKSPACE_ID,
                "sequence": 1,
                "created_at": "2026-09-12T12:01:00Z",
                "kind": "observation",
                "message": "Observed discount missing after quantity changed.",
                "evidence_ids": [SCREENSHOT_ID],
            }
        ],
        "reports": [
            {
                "id": REPORT_ID,
                "job_id": JOB_ID,
                "workspace_id": WORKSPACE_ID,
                "group_id": GROUP_ID,
                "title": "SAVE10 is removed after quantity change",
                "outcome": "reproduced",
                "interpretation": "observed_defect",
                "source_conversation_ids": [CONVERSATION_ID],
                "expected": {
                    "text": "Two eligible items retain the ten-percent discount.",
                    "document_ids": [DOCUMENT_ID],
                    "assumption": False,
                },
                "actual": {
                    "text": "The cart total changed to 20,000 minor units.",
                    "evidence_ids": [SCREENSHOT_ID],
                },
                "steps": [
                    {
                        "action": "Apply SAVE10, then set quantity to two.",
                        "observation": "The discount line disappeared.",
                        "evidence_ids": [SCREENSHOT_ID],
                    }
                ],
                "attempts": [
                    {
                        "session_id": SESSION_ONE_ID,
                        "result": "Observed 20,000.",
                        "evidence_ids": [SCREENSHOT_ID],
                    },
                    {
                        "session_id": SESSION_TWO_ID,
                        "result": "Observed 20,000 again in a fresh cart session.",
                        "evidence_ids": [REPLAY_SCREENSHOT_ID],
                    },
                ],
                "duplicate_candidates": [],
                "limitations": ["Tested in the supplied sandbox only."],
                "proposed_acceptance_checks": [
                    "Changing quantity preserves SAVE10 for eligible items."
                ],
                "evidence_ids": [
                    SCREENSHOT_ID,
                    REPLAY_SCREENSHOT_ID,
                    DOCUMENT_EVIDENCE_ID,
                ],
                "replay_status": "passed",
            }
        ],
        "jobs": [
            {
                "id": JOB_ID,
                "workspace_id": WORKSPACE_ID,
                "status": "completed",
                "created_at": "2026-09-12T12:00:00Z",
                "updated_at": "2026-09-12T12:02:00Z",
                "deadline_at": "2026-09-12T12:10:00Z",
                "input": {
                    "conversation_ids": [CONVERSATION_ID],
                    "max_groups": 1,
                    "seed_version": 1,
                },
                "group_ids": [GROUP_ID],
                "report_ids": [REPORT_ID],
                "error": None,
                "metrics": {
                    "model_calls": 8,
                    "browser_actions": 12,
                    "input_tokens": 2400,
                    "output_tokens": 800,
                    "duration_ms": 120000,
                    "estimated_model_cost_usd_micros": None,
                },
            }
        ],
    }


def test_contract_package_exposes_fixture_validator() -> None:
    """Catch removal of the public fixture-validation boundary."""

    assert callable(getattr(signalcase_contracts, "validate_fixture_bundle", None))


def test_valid_source_linked_bundle_is_accepted() -> None:
    """Catch rejection of a complete cross-linked investigation fixture."""

    validate_fixture_bundle(valid_bundle())


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda bundle: bundle["reports"][0].update(outcome="certainly_a_bug"), "outcome"),
        (
            lambda bundle: bundle["jobs"][0]["metrics"].update(model_calls=-1),
            "model_calls",
        ),
        (
            lambda bundle: bundle["jobs"][0]["metrics"].update(estimated_model_cost_usd_micros=0.5),
            "estimated_model_cost_usd_micros",
        ),
        (lambda bundle: bundle["reports"][0].update(unexpected=True), "unexpected"),
        (
            lambda bundle: bundle["conversations"][0].update(created_at="last Tuesday"),
            "created_at",
        ),
        (
            lambda bundle: bundle["conversations"][0].update(text="x" * 10_001),
            "text",
        ),
    ],
)
def test_schema_rejects_invalid_wire_values(mutation: object, message: str) -> None:
    """Catch acceptance of invalid enums, metrics, fields, and timestamps."""

    bundle = valid_bundle()
    mutation(bundle)  # type: ignore[operator]

    with pytest.raises(ContractValidationError, match=message):
        validate_fixture_bundle(bundle)


def test_report_rejects_unknown_evidence_reference() -> None:
    """Catch reports claiming evidence that was never recorded."""

    bundle = valid_bundle()
    bundle["reports"][0]["actual"]["evidence_ids"] = [  # type: ignore[index]
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    ]

    with pytest.raises(ContractValidationError, match="unknown evidence"):
        validate_fixture_bundle(bundle)


def test_model_cost_uses_integer_usd_micros() -> None:
    """Catch floating-point money entering the shared contract."""

    schema_path = Path(__file__).parents[2] / "contracts" / "signalcase.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    properties = schema["$defs"]["Metrics"]["properties"]

    assert "estimated_model_cost_usd" not in properties
    assert properties["estimated_model_cost_usd_micros"] == {
        "type": ["integer", "null"],
        "minimum": 0,
    }


def test_group_rejects_unknown_customer_source() -> None:
    """Catch complaint groups that lose their source conversation."""

    bundle = valid_bundle()
    bundle["groups"][0]["conversation_ids"] = [  # type: ignore[index]
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    ]

    with pytest.raises(ContractValidationError, match="unknown conversation"):
        validate_fixture_bundle(bundle)


def test_non_assumption_requires_a_known_document() -> None:
    """Catch expected behavior presented as documented without a source."""

    bundle = valid_bundle()
    bundle["reports"][0]["expected"]["document_ids"] = [  # type: ignore[index]
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    ]

    with pytest.raises(ContractValidationError, match="unknown document"):
        validate_fixture_bundle(bundle)


def test_replay_cannot_pass_without_two_attempts() -> None:
    """Catch a repeatability claim based on only one observed attempt."""

    bundle = valid_bundle()
    bundle["reports"][0]["attempts"] = bundle["reports"][0]["attempts"][:1]  # type: ignore[index]

    with pytest.raises(ContractValidationError, match="replay_status.*two attempts"):
        validate_fixture_bundle(bundle)


def test_reproduced_report_requires_recorded_evidence() -> None:
    """Catch a reproduced result made entirely from unsupported text."""

    bundle = valid_bundle()
    report = bundle["reports"][0]  # type: ignore[index]
    report["actual"]["evidence_ids"] = []
    report["steps"] = []
    report["attempts"] = [
        {"session_id": SESSION_ONE_ID, "result": "Claimed result one.", "evidence_ids": []},
        {"session_id": SESSION_TWO_ID, "result": "Claimed result two.", "evidence_ids": []},
    ]
    report["evidence_ids"] = []
    report["replay_status"] = "passed"

    with pytest.raises(ContractValidationError, match="evidence"):
        validate_fixture_bundle(bundle)


def test_passed_replay_rejects_reused_attempt_evidence() -> None:
    """Catch repeatability claims that cite the same recorded run twice."""

    bundle = valid_bundle()
    bundle["reports"][0]["attempts"][1]["evidence_ids"] = [SCREENSHOT_ID]  # type: ignore[index]

    with pytest.raises(ContractValidationError, match="fresh|distinct|reuse"):
        validate_fixture_bundle(bundle)


def test_passed_replay_requires_distinct_sessions() -> None:
    """Catch two attempt labels that point to the same browser session."""

    bundle = valid_bundle()
    bundle["reports"][0]["attempts"][1]["session_id"] = SESSION_ONE_ID  # type: ignore[index]

    with pytest.raises(ContractValidationError, match="distinct fresh session"):
        validate_fixture_bundle(bundle)


def test_attempt_evidence_must_match_its_session() -> None:
    """Catch fresh-session labels attached to artifacts from another run."""

    bundle = valid_bundle()
    bundle["reports"][0]["attempts"][1]["session_id"] = (  # type: ignore[index]
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaae"
    )

    with pytest.raises(ContractValidationError, match="evidence.*fresh session"):
        validate_fixture_bundle(bundle)


def test_observed_defect_requires_documented_expected_behavior() -> None:
    """Catch a customer expectation being promoted to a defect specification."""

    bundle = valid_bundle()
    report = bundle["reports"][0]  # type: ignore[index]
    report["expected"] = {
        "text": "The customer expects the discount to remain.",
        "document_ids": [],
        "assumption": True,
    }

    with pytest.raises(ContractValidationError, match="observed_defect.*documented"):
        validate_fixture_bundle(bundle)


def test_job_contract_persists_seeded_input_metadata() -> None:
    """Catch loss of the seed version and bounded source selection for a job."""

    schema_path = Path(__file__).parents[2] / "contracts" / "signalcase.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    job = schema["$defs"]["Job"]
    job_input = schema["$defs"]["JobInput"]

    assert "input" in job["required"]
    assert job_input["required"] == ["conversation_ids", "max_groups", "seed_version"]
    assert job_input["properties"]["seed_version"] == {"type": "integer", "minimum": 1}


def test_job_input_rejects_unknown_customer_source() -> None:
    """Catch persisted job metadata that cannot trace back to an input conversation."""

    bundle = valid_bundle()
    bundle["jobs"][0]["input"]["conversation_ids"] = [  # type: ignore[index]
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    ]

    with pytest.raises(ContractValidationError, match="unknown conversation"):
        validate_fixture_bundle(bundle)


def test_job_cannot_exceed_its_persisted_group_limit() -> None:
    """Catch job output that exceeds the bounded input recorded at launch."""

    bundle = valid_bundle()
    bundle["jobs"][0]["input"]["max_groups"] = 1  # type: ignore[index]
    bundle["jobs"][0]["group_ids"] = [  # type: ignore[index]
        GROUP_ID,
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaf",
    ]

    with pytest.raises(ContractValidationError, match="max_groups"):
        validate_fixture_bundle(bundle)


def test_report_group_must_be_listed_on_its_job() -> None:
    """Catch a report attached to work the job does not claim to process."""

    bundle = valid_bundle()
    bundle["jobs"][0]["group_ids"] = []  # type: ignore[index]

    with pytest.raises(ContractValidationError, match="report group.*job"):
        validate_fixture_bundle(bundle)


def test_report_must_be_listed_on_its_job() -> None:
    """Catch an orphan report omitted from the job snapshot."""

    bundle = valid_bundle()
    bundle["jobs"][0]["report_ids"] = []  # type: ignore[index]

    with pytest.raises(ContractValidationError, match="report.*job report_ids"):
        validate_fixture_bundle(bundle)


def test_cross_workspace_evidence_is_rejected() -> None:
    """Catch evidence crossing the workspace boundary of its job."""

    bundle = valid_bundle()
    bundle["evidence"][0]["workspace_id"] = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"  # type: ignore[index]

    with pytest.raises(ContractValidationError, match="workspace"):
        validate_fixture_bundle(bundle)


def test_duplicate_event_sequence_is_rejected() -> None:
    """Catch ambiguous event ordering within one investigation."""

    bundle = valid_bundle()
    duplicate = deepcopy(bundle["events"][0])  # type: ignore[index]
    duplicate["id"] = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    bundle["events"].append(duplicate)  # type: ignore[union-attr]

    with pytest.raises(ContractValidationError, match="duplicate event sequence"):
        validate_fixture_bundle(bundle)
