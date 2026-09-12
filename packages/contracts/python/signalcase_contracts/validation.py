"""Validation entry points for shared SignalCase fixture bundles."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class ContractValidationError(ValueError):
    """Raised when a fixture bundle violates the SignalCase contract."""


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    packaged_schema = Path(__file__).with_name("signalcase.schema.json")
    repository_schema = Path(__file__).resolve().parents[4] / "contracts" / "signalcase.schema.json"
    schema_path = packaged_schema if packaged_schema.exists() else repository_schema
    with schema_path.open(encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _records_by_id(bundle: dict[str, Any], collection: str) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for record in bundle[collection]:
        record_id = record["id"]
        if record_id in records:
            raise ContractValidationError(f"duplicate id in {collection}: {record_id}")
        records[record_id] = record
    return records


def _require_reference(
    *,
    record: dict[str, Any],
    field: str,
    index: dict[str, dict[str, Any]],
    kind: str,
) -> dict[str, Any]:
    reference_id = record[field]
    referenced = index.get(reference_id)
    if referenced is None:
        raise ContractValidationError(f"unknown {kind} referenced by {field}: {reference_id}")
    return referenced


def _require_references(
    *,
    record: dict[str, Any],
    field: str,
    index: dict[str, dict[str, Any]],
    kind: str,
) -> list[dict[str, Any]]:
    return [
        _require_reference(record={field: reference_id}, field=field, index=index, kind=kind)
        for reference_id in record[field]
    ]


def _require_same_workspace(owner: dict[str, Any], referenced: dict[str, Any], label: str) -> None:
    if owner["workspace_id"] != referenced["workspace_id"]:
        raise ContractValidationError(f"{label} crosses workspace boundary")


def _validate_cross_references(bundle: dict[str, Any]) -> None:
    conversations = _records_by_id(bundle, "conversations")
    documents = _records_by_id(bundle, "documents")
    issues = _records_by_id(bundle, "existing_issues")
    groups = _records_by_id(bundle, "groups")
    evidence = _records_by_id(bundle, "evidence")
    events = _records_by_id(bundle, "events")
    reports = _records_by_id(bundle, "reports")
    jobs = _records_by_id(bundle, "jobs")

    all_ids: dict[str, str] = {}
    for collection, index in (
        ("conversations", conversations),
        ("documents", documents),
        ("existing_issues", issues),
        ("groups", groups),
        ("evidence", evidence),
        ("events", events),
        ("reports", reports),
        ("jobs", jobs),
    ):
        for record_id in index:
            previous = all_ids.setdefault(record_id, collection)
            if previous != collection:
                raise ContractValidationError(
                    f"id {record_id} is reused across {previous} and {collection}"
                )

    for group in groups.values():
        for conversation in _require_references(
            record=group,
            field="conversation_ids",
            index=conversations,
            kind="conversation",
        ):
            _require_same_workspace(group, conversation, "group conversation")

    for item in evidence.values():
        job = _require_reference(record=item, field="job_id", index=jobs, kind="job")
        _require_same_workspace(item, job, "evidence job")
        expected_prefix = (
            f"workspaces/{item['workspace_id']}/jobs/{item['job_id']}/evidence/{item['id']}"
        )
        if item["storage_key"] != expected_prefix:
            raise ContractValidationError(
                "evidence storage_key does not match its workspace/job/id"
            )
        if item["document_id"] is not None:
            document = _require_reference(
                record=item,
                field="document_id",
                index=documents,
                kind="document",
            )
            _require_same_workspace(item, document, "evidence document")
            if item["quote"] not in document["text"]:
                raise ContractValidationError("document evidence quote is not present in source")

    seen_sequences: set[tuple[str, int]] = set()
    for event in events.values():
        job = _require_reference(record=event, field="job_id", index=jobs, kind="job")
        _require_same_workspace(event, job, "event job")
        sequence_key = (event["job_id"], event["sequence"])
        if sequence_key in seen_sequences:
            raise ContractValidationError(
                f"duplicate event sequence {event['sequence']} for job {event['job_id']}"
            )
        seen_sequences.add(sequence_key)
        for event_evidence in _require_references(
            record=event,
            field="evidence_ids",
            index=evidence,
            kind="evidence",
        ):
            _require_same_workspace(event, event_evidence, "event evidence")
            if event_evidence["job_id"] != event["job_id"]:
                raise ContractValidationError("event evidence belongs to another job")

    for report in reports.values():
        job = _require_reference(record=report, field="job_id", index=jobs, kind="job")
        group = _require_reference(record=report, field="group_id", index=groups, kind="group")
        _require_same_workspace(report, job, "report job")
        _require_same_workspace(report, group, "report group")
        if report["id"] not in job["report_ids"]:
            raise ContractValidationError("report is absent from its job report_ids")
        if report["group_id"] not in job["group_ids"]:
            raise ContractValidationError("report group is absent from its job group_ids")

        for conversation in _require_references(
            record=report,
            field="source_conversation_ids",
            index=conversations,
            kind="conversation",
        ):
            _require_same_workspace(report, conversation, "report conversation")
            if conversation["id"] not in group["conversation_ids"]:
                raise ContractValidationError(
                    "report conversation is not part of its complaint group"
                )

        for document_id in report["expected"]["document_ids"]:
            document = _require_reference(
                record={"document_id": document_id},
                field="document_id",
                index=documents,
                kind="document",
            )
            _require_same_workspace(report, document, "report document")

        if report["interpretation"] == "observed_defect" and report["expected"]["assumption"]:
            raise ContractValidationError("observed_defect requires documented expected behavior")

        if report["replay_status"] == "passed" and len(report["attempts"]) < 2:
            raise ContractValidationError("replay_status passed requires at least two attempts")
        if report["replay_status"] == "passed":
            session_ids = [attempt["session_id"] for attempt in report["attempts"]]
            if len(set(session_ids)) != len(session_ids):
                raise ContractValidationError(
                    "replay_status passed requires distinct fresh session IDs"
                )
            replay_evidence_ids: set[str] = set()
            for attempt in report["attempts"]:
                attempt_evidence_ids = set(attempt["evidence_ids"])
                if replay_evidence_ids.intersection(attempt_evidence_ids):
                    raise ContractValidationError(
                        "replay_status passed cannot reuse evidence across attempts"
                    )
                replay_evidence_ids.update(attempt_evidence_ids)
                for attempt_evidence in _require_references(
                    record=attempt,
                    field="evidence_ids",
                    index=evidence,
                    kind="evidence",
                ):
                    if attempt_evidence["session_id"] != attempt["session_id"]:
                        raise ContractValidationError(
                            "attempt evidence must belong to its fresh session"
                        )

        nested_evidence_ids = set(report["actual"]["evidence_ids"])
        for step in report["steps"]:
            nested_evidence_ids.update(step["evidence_ids"])
        for attempt in report["attempts"]:
            nested_evidence_ids.update(attempt["evidence_ids"])
        all_report_evidence_ids = set(report["evidence_ids"]) | nested_evidence_ids
        for evidence_id in all_report_evidence_ids:
            report_evidence = _require_reference(
                record={"evidence_id": evidence_id},
                field="evidence_id",
                index=evidence,
                kind="evidence",
            )
            _require_same_workspace(report, report_evidence, "report evidence")
            if report_evidence["job_id"] != report["job_id"]:
                raise ContractValidationError("report evidence belongs to another job")
        if not nested_evidence_ids.issubset(set(report["evidence_ids"])):
            raise ContractValidationError("report evidence_ids must include all nested evidence")

        for candidate in report["duplicate_candidates"]:
            issue = _require_reference(
                record=candidate,
                field="issue_id",
                index=issues,
                kind="existing issue",
            )
            _require_same_workspace(report, issue, "duplicate candidate")

    for job in jobs.values():
        if len(job["group_ids"]) > job["input"]["max_groups"]:
            raise ContractValidationError("job group_ids exceed input max_groups")
        input_conversations = _require_references(
            record=job["input"],
            field="conversation_ids",
            index=conversations,
            kind="conversation",
        )
        for conversation in input_conversations:
            _require_same_workspace(job, conversation, "job input conversation")
        input_conversation_ids = set(job["input"]["conversation_ids"])
        for group in _require_references(
            record=job,
            field="group_ids",
            index=groups,
            kind="group",
        ):
            _require_same_workspace(job, group, "job group")
            if not set(group["conversation_ids"]).issubset(input_conversation_ids):
                raise ContractValidationError("job group contains a conversation outside job input")
        for report in _require_references(
            record=job,
            field="report_ids",
            index=reports,
            kind="report",
        ):
            _require_same_workspace(job, report, "job report")
            if report["job_id"] != job["id"]:
                raise ContractValidationError("job report points to another job")


def validate_fixture_bundle(bundle: dict[str, Any]) -> None:
    """Validate wire shape and referential integrity for a fixture bundle."""

    errors = sorted(_validator().iter_errors(bundle), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        raise ContractValidationError(f"schema violation at {location}: {error.message}")
    _validate_cross_references(bundle)
