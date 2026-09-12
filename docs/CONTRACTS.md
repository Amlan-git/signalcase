# Shared contracts — version 1

These wire formats are the coordination baseline. T0 maintains the canonical JSON Schema and generated Python/TypeScript models. No team may independently rename fields. All IDs are server-issued UUID strings, all timestamps UTC RFC3339, money integer minor units. The `contracts/examples` directory contains synthetic state fixtures for parallel development.

The canonical schema is `contracts/signalcase.schema.json`. Generated consumers are `packages/contracts/python/signalcase_contracts/models.py` and `packages/contracts/typescript/src/generated.ts`. Python cross-record validation lives in `signalcase_contracts.validation`.

## Data records

- Conversation: id, workspace_id, source (string), external_id (string or null), text, created_at.
- Document: id, workspace_id, title, text, version (string). Source passages use document_id and exact quote.
- ExistingIssue: id, workspace_id, title, description, status.
- Job: id, workspace_id, status, created_at, updated_at, deadline_at, input (conversation_ids, max_groups, seed_version), group_ids (array), report_ids (array), error (null or Error), metrics. Persisting the bounded input and sandbox seed version makes evaluation runs traceable.
- Group: id, workspace_id, conversation_ids, claim (string), prerequisites (array of strings), unknowns (array of strings).
- Event: id, job_id, workspace_id, sequence (positive integer), created_at, kind (phase|action|observation|warning|completion), message, evidence_ids.
- Evidence: id, job_id, workspace_id, session_id, kind (screenshot|dom|action|document_excerpt|calculation), created_at, storage_key, sha256, mime_type, summary, document_id, quote. Browser/action evidence has a non-null session_id; document excerpts have a null session_id and preserve the exact source passage through document_id and quote.
- Report: id, job_id, workspace_id, group_id, title, outcome, interpretation, source_conversation_ids, expected (text, document_ids, assumption boolean), actual (text, evidence_ids), steps (ordered array of action/observation/evidence_ids), attempts (array of session_id/result/evidence_ids), duplicate_candidates (array of issue_id/reason), limitations (string array), proposed_acceptance_checks (string array), evidence_ids, replay_status (not_generated|not_run|passed|failed). Every report, observation, step and attempt cites recorded evidence. A passed replay requires at least two distinct session IDs with distinct session-linked evidence.
- Metrics: model_calls, browser_actions, input_tokens, output_tokens, duration_ms, estimated_model_cost_usd_micros (integer or null). Cost uses millionths of one US dollar so small model charges remain precise without floating-point money. Unknown usage/cost stays null, never zero. All counts nonnegative.
- Error: code, message, retryable. Codes: INVALID_INPUT, UNAUTHORIZED, NOT_FOUND, WORKSPACE_BUSY, MODEL_UNAVAILABLE, BROWSER_FAILED, DEADLINE_EXCEEDED, WORKER_LOST, STORAGE_FAILED, CONTRACT_INVALID.

Report outcomes and interpretation enums are defined in TECHNICAL_SPEC.md. No arbitrary confidence percentages. Proposed acceptance checks are suggestions, not executed tests.
`observed_defect` requires documented expected behavior (`assumption:false` with a supplied document); an unsupported customer expectation can remain `possible_feature_gap` or `unresolved`.

## Public API

All endpoints except health/session bootstrap require workspace authorization. Same-origin preferred; exact frontend origin allowed if separated. API never accepts arbitrary agent runtime ARN or arbitrary target URL from a client.

| Method and route | Request | Success |
|---|---|---|
| GET /api/health | none | 200 {status:"ok", contract_version:"1"} |
| POST /api/workspaces | supplied demo access credential | 201 {workspace_id, access_token, control_token}; no token logging |
| POST /api/workspaces/{id}/conversations | {conversations:[{source,external_id,text}]} | 201 {conversation_ids:[]} |
| POST /api/workspaces/{id}/jobs | {conversation_ids:[], max_groups:1..3}; Idempotency-Key header | 202 {job_id,status:"queued"} |
| GET /api/workspaces/{id}/jobs/{job_id} | none | 200 Job |
| GET /api/workspaces/{id}/jobs/{job_id}/events?after=N | sequence cursor default 0 | 200 {events:[],next_cursor:N} |
| GET /api/workspaces/{id}/reports/{report_id} | none | 200 Report |
| GET /api/workspaces/{id}/evidence/{evidence_id} | none | 200 {url,expires_at,mime_type} |
| POST /api/workspaces/{id}/jobs/{job_id}/cancel | none | 202 {cancel_requested:true} |
| DELETE /api/workspaces/{id} | no active job; control authorization | 204 |

Errors: {error:Error}. Invalid input 400; authorization 401/403; missing resource 404 without cross-workspace disclosure; conflict 409; upstream unavailable 503. Poll every 2 seconds while active and stop at a terminal state. Client shows a timeout/reconnect state on network failure, not an invented job result.

## Internal interfaces

Agent invocation: {contract_version:"1",job_id,workspace_id,conversation_ids,max_groups,sandbox_url}. Backend resolves sandbox URL. Runtime retrieves authorized inputs by workspace; credentials never reside in the invocation's model-visible text.

Storage adapter operations: put_record(collection,id,record), get_record(collection,id), put_evidence(metadata,bytes), append_event(event), request_cancel(job_id), is_cancel_requested(job_id). All adapters are constructed with workspace scope. Cloud adapter uses S3, local adapter filesystem. Launch locking/idempotency belong to API storage operations, not the model.

Evidence keys: workspaces/{workspace_id}/jobs/{job_id}/evidence/{evidence_id}; reports and job snapshots under their corresponding workspace prefix. Event keys contain zero-padded sequence to preserve ordering.

## Sandbox interface

Ordinary routes: /store/{workspace_id}, cart, checkout, orders. No production payments. Backend validates scoped storefront credential independently of URL.

Separate control routes: POST /control/workspaces/{id}/configure {coupon_loss:boolean,filter_boundary:boolean,deny_orders:boolean}; POST /control/workspaces/{id}/reset. Control requires control_token; reset/configure return 409 while an investigation is active. A reset increments seed_version; every job records the version it investigated in its persisted input metadata.

Evaluation reads fault state using a separate credential that is absent from agent deployment. Storefront assets, docs, errors and API responses must not expose fault flags or answer keys.

## Frozen examples

Amlan owns `contracts/examples/reproduced.json`, `blocked.json`, and `failed.json`. They use valid UUIDs and are validated by both Python and Node tests. Schema CI rejects additional fields, missing required fields, invalid enums and negative metrics; Python validation rejects cross-record dangling references and workspace violations. Breaking changes require a schema version bump and coordinated consumer PRs.
