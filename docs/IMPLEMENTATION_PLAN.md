# SignalCase Implementation Plan

> **For agentic workers:** Use a task-by-task execution workflow with review between tasks. If available, use superpowers:executing-plans; use subagent-driven-development only when delegated execution is explicitly requested. Steps use checkboxes for tracking.

**Goal:** Deliver a working complaint-to-evidence investigation that judges can independently test.

**Architecture:** React calls a small authenticated API that launches a Python Strands job. The job uses a browser against an isolated store and persists evidence; judge controls and evaluator remain outside agent access.

**Tech Stack:** React/TypeScript, Python/Strands/Pydantic, Playwright, Bedrock, AgentCore Runtime/Browser, S3. No Amplify.

**Spec:** TECHNICAL_SPEC.md and CONTRACTS.md.

## Global constraints

Synthetic data only. Strands performs real tool orchestration. No Amplify. No arbitrary external websites. Evidence is durable outside ephemeral sessions. One active job per workspace. No model credentials in the frontend. No claim of successful verification without execution.

This is a build-order and acceptance plan, not a claim that implementation code or commands exist. Each task's owner writes the concrete module-level test cases against the frozen contract before implementation. T0 establishes runnable scripts before downstream work; no guessed SDK calls are prescribed here.

### T0 — Freeze contracts and working skeleton (Amlan; first merge)

Files: contracts/*.schema.json, contracts/examples/*.json, packages/contracts/, pyproject.toml, uv.lock, package.json, package-lock.json, .github/workflows/ci.yml, .env.example.

Consumes: CONTRACTS.md. Produces: schema-validated records, generated TS/Python models, verified bootstrap and lint/test scripts.

- [x] Install compatible pinned Python/Node dependencies; record exact versions.
- [x] Write canonical schemas and complete fixture bundles for reproduced, blocked and failed states.
- [x] Verify schema rejection for missing evidence, invalid outcome and negative counts.
- [x] Generate shared language models; prove roundtrip compatibility using the same fixture.
- [x] Define and verify scripts: npm run lint, npm run typecheck, npm test; uv run pytest. Put real commands in README.
- [x] Add CI for these checks with zero paid model calls; no secrets on pull requests.
- [ ] Confirm Bedrock model/region access with an authorized single smoke call and record choice/cost basis. If unauthorized, keep fixture work progressing and document access as a deployment blocker.
- [ ] Reviewer approves contracts; merge before team consumer work.

The Bedrock smoke call remains deferred because no AWS credentials or paid-call authorization have been provided. Contract review remains open until a teammate approves the T0 pull request.

### T1 — Judge interface (Teammate 1; after T0)

Files: apps/web/src/api/client.ts, apps/web/src/pages/Workspace.tsx, Investigation.tsx, Report.tsx, components/EvidenceViewer.tsx, tests/investigation.spec.ts.

Consumes: public API in CONTRACTS.md and frozen fixtures. Produces: workspace, upload, run, progress, report, evidence and reset journey.

- [ ] Write UI tests for queued → running → completed, failed, blocked report, reconnect and expired evidence URL.
- [ ] Build API adapter with explicit fixture mode banner; fixture mode cannot appear as a live run.
- [ ] Implement source/evidence navigation, readable steps and JSON/Markdown export.
- [ ] Connect polling with cursor, stop terminal polling and prevent duplicate launch on double-click.
- [ ] Keep judge control credential out of agent payloads; never render secrets in errors.
- [ ] Verify keyboard operation, narrow screen layout and actual API mode before review.

### T2 — Sandbox and private fault controls (Teammate 3; after T0)

Files: services/sandbox/app.py, store.py, controls.py, fixtures/store.json, tests/test_isolation.py, tests/test_cart.py.

Consumes: sandbox routes and workspace IDs. Produces: deterministic store, private configurable faults and reset.

- [ ] Create seed: item price 10,000 minor units, valid SAVE10 discount 10%, expired OLD10. Two units with SAVE10 should total 18,000 before any separately documented charges; use no taxes/shipping in MVP.
- [ ] Write a check that coupon_loss enabled yields 20,000 after changing quantity, disabled yields 18,000.
- [ ] Implement storefront controls and order filter fixture: seed ORD-A at 2026-09-01T00:00:00Z, ORD-B at 2026-09-02T12:00:00Z and ORD-C at 2026-09-03T00:00:00Z. Document date filters as inclusive whole UTC days. Filtering Sep 1 through Sep 2 returns ORD-A and ORD-B normally; filter_boundary enabled incorrectly excludes ORD-A. Record seed IDs in evaluator fixtures, not model instructions.
- [ ] Verify expired coupon behaves as documented, missing access denies orders, and workspaces cannot read each other's state.
- [ ] Verify agent credentials get 403 on configure/reset; frontend assets contain no fault flags.
- [ ] Publish ordinary app docs and sample complaints; keep evaluator assertions inaccessible to agent deployment.

### T3 — Investigator and evidence (Teammate 2; after T0, integrates T2)

Files: services/agent/runner.py, tools/browser.py, tools/search.py, evidence.py, report.py, adapters/local_browser.py, adapters/agentcore_browser.py, tests/test_report.py, tests/test_limits.py.

Consumes: invocation, Group, Document, ExistingIssue and browser sandbox. Produces: Events, Evidence, Reports and Metrics.

- [ ] Write deterministic validation tests for dangling evidence, undocumented expectations and false replay_status.
- [ ] Implement tool adapters and instrument action/evidence capture before model orchestration.
- [ ] Implement Strands loop with explicit tool boundaries and injected storage adapter.
- [ ] Implement group/source preservation, doc search and duplicate candidates.
- [ ] Implement action/call/deadline limits, cancellation checks and cleanup in finally blocks.
- [ ] Run an authorized live coupon investigation; manually compare observed amounts and source citations.
- [ ] Verify normal and blocked scenarios without forcing a defect conclusion.

### T4 — API, storage and hosted execution (Amlan; after T0)

Files: services/api/app.py, auth.py, jobs.py, storage.py, services/agent/runtime_entrypoint.py, infra/, tests/test_jobs.py.

Consumes: frozen API + agent invocation. Produces: authorized persistent job lifecycle.

- [ ] Test cross-workspace denial, duplicate launch idempotency and simultaneous launch conflict.
- [ ] Implement local store first, S3 adapter second; one active marker with conditional writes.
- [ ] Implement runtime background-task registration and prompt return; verify a job continues after HTTP response and browser tab closes.
- [ ] Persist snapshots/events and partial evidence. Enforce terminal timeout for abandoned jobs.
- [ ] Deploy only after cost authorization and provider compatibility smoke tests; log exact setup in DEPLOYMENT.md.
- [ ] Prove authenticated UI → API → runtime → browser → sandbox → S3 → report on hosted infrastructure.

### T5 — Independent evaluation (Teammate 3; integrates T2/T3/T4)

Files: tests/evaluation/scenarios.json, evaluate.py, results/, docs/EVALUATION_RESULTS.md.

- [ ] Implement matrix in JUDGE_TESTING.md, including fault-off and direct admin-access attempts.
- [ ] Evaluate actual emitted artifacts and application state, not model self-ratings.
- [ ] Run repeated trials with varied complaint wording. Record raw counts, failures and seed/version.
- [ ] Produce report replay instructions with evidence provenance.
- [ ] Keep results marked unmeasured until live execution completes.

### T6 — Integrate and freeze (all; Amlan coordinates)

- [ ] Run complete judge journey in fresh browser/workspace, including reset and second run.
- [ ] Confirm no fixture mode is presented as live, no credentials are leaked, and failed jobs remain inspectable.
- [ ] Pin deployment revision and verify restart/reload behaviour.
- [ ] Fix blocking integration issues before optional features. Cut duplicate search before cutting reliable browser evidence if time is insufficient; update public scope honestly.

### T7 — Submission (Amlan; teammates review)

- [ ] Complete SUBMISSION.md checklist, public license, setup guide and architecture.
- [ ] Record ≤5-minute video using actual live outcomes; include one uncertainty/blocker case.
- [ ] Provide judge credentials privately in submission instructions, not public repository.
- [ ] Confirm free working access through judging end; preserve resources accordingly.

## Suggested sequencing

First shared work block: T0 and cloud feasibility probes. Next block: T1/T2/T3 in parallel and T4 by lead. Following block: one integrated scenario, then T5/T6. Final block: submission and availability checks. These are ordering recommendations, not duration guarantees. The deadline is Sep 15, 2026 at 05:30 Asia/Kolkata; prioritize the vertical slice immediately.
