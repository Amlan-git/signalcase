# SignalCase

SignalCase is a customer evidence agent that turns customer complaints into reproducible, source-linked product issue reports.

**Status:** Design and team handoff only. No application, tests, deployment, or GitHub repository has been created. AWS Amplify is excluded. The target is a low-traffic Professional Agents submission with independently testable results.

## Start here

1. [Technical specification](docs/TECHNICAL_SPEC.md)
2. [Shared contracts](docs/CONTRACTS.md)
3. [Implementation plan](docs/IMPLEMENTATION_PLAN.md)
4. [Team ownership and GitHub workflow](docs/TEAM_WORKFLOW.md)
5. [Judge testing and evaluation](docs/JUDGE_TESTING.md)
6. [Deployment and cost decisions](docs/DEPLOYMENT.md)
7. [Submission checklist and official sources](docs/SUBMISSION.md)
8. [AI coding rules](AGENTS.md) and [copyable teammate prompts](prompts/TEAM_PROMPTS.md)

The application paths described in these documents are planned paths. Do not describe documented features as implemented. There are no runnable application commands yet; task T0 establishes and verifies them.

## Proposed repository layout

```text
apps/web/                 React interface (teammate 1)
services/agent/           Strands investigator (teammate 2)
services/sandbox/         Test store and judge controls (teammate 3)
services/api/             Authentication, job launch and read APIs (Amlan)
packages/contracts/      Generated Python/TypeScript contracts (Amlan)
contracts/               Canonical JSON Schemas and fixtures (Amlan)
tests/evaluation/         Hidden-answer harness (teammate 3)
infra/                   Deployment definitions (Amlan)
prompts/                 AI development handoffs
```

**License:** MIT or Apache-2.0 must be selected and added before submission. This documentation does not claim a license has already been applied.
