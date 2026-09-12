# Copyable AI coding handoffs

Before each prompt, give the coding assistant access to the repository and the relevant GitHub issue. These prompts delegate coding work to teammates' own assistants; they do not authorize deployment or sharing secrets.

## Amlan — integration lead

Read AGENTS.md and docs/TECHNICAL_SPEC.md, CONTRACTS.md, IMPLEMENTATION_PLAN.md and DEPLOYMENT.md. Own T0 and T4, then coordinate T6/T7. Freeze schemas and fixtures before other owners implement clients. Keep Amplify excluded. Establish verified setup commands and lockfiles. Build scoped API/storage, idempotent launch and reliable async lifecycle. Do not overwrite teammate paths. Propose hosting choice with measured feasibility and cost before provisioning. Open a PR with contract checks, authorization tests and remaining deployment gaps.

## Teammate 1 — frontend

Read AGENTS.md, technical spec, contracts, judge testing and task T1. Own apps/web only. Build workspace creation, conversation input, run/progress, evidence-linked report and export against the frozen fixture bundle first, then API. Fixture mode must be visible. Handle failed/blocked jobs, reconnect, expired evidence URLs and duplicate-click prevention. Keep control credentials out of agent requests. No model/cloud keys in browser. Request shared contract changes through Amlan. Open a focused PR with screenshots and actual UI/type checks.

## Teammate 2 — agent

Read AGENTS.md, spec, contracts and task T3. Own services/agent except coordinate runtime entrypoint with Amlan. Implement Strands investigation using observed browser elements, supplied docs and existing issues. Preserve source references, actual tool evidence, uncertainty and failed attempts. Use bounded tools, cancellation and cleanup. Never inspect sandbox fault flags, source code or evaluator answers. Local adapter first, managed-browser adapter behind same interface. Verify one actual coupon investigation and a normal/blocked control. Do not label a replay passed without running it. Open a PR with emitted report and meaningful test results.

## Teammate 3 — sandbox and evaluation

Read AGENTS.md, spec, contracts, JUDGE_TESTING.md and T2/T5. Own services/sandbox and tests/evaluation. Build isolated storefront state, deterministic coupon and order-filter faults, private control credentials and safe reset. Enforce control denial server-side; no answer flags in frontend assets. Build an independent evaluation harness that checks application state and evidence rather than model self-ratings. Coordinate ordinary sandbox URL and seeded docs with teammate 2 without exposing fault selection. Open a PR with isolation and fault-on/off tests.
