# SignalCase

SignalCase is a customer evidence agent that turns customer complaints into reproducible, source-linked product issue reports.

**Status:** The offline T0 foundation is complete. The Bedrock access smoke test and human contract review remain open. No product application or deployment exists yet. AWS Amplify is excluded. The target is a low-traffic Professional Agents submission with independently testable results.

**Repository:** https://github.com/Amlan-git/signalcase

## Start here

1. [Technical specification](docs/TECHNICAL_SPEC.md)
2. [Shared contracts](docs/CONTRACTS.md)
3. [Implementation plan](docs/IMPLEMENTATION_PLAN.md)
4. [Judge testing and evaluation](docs/JUDGE_TESTING.md)
5. [Deployment and cost decisions](docs/DEPLOYMENT.md)
6. [Submission checklist and official sources](docs/SUBMISSION.md)
7. [AI coding rules](AGENTS.md) and [copyable teammate prompts](prompts/TEAM_PROMPTS.md)

The application paths described in these documents are planned paths. Do not describe documented features as implemented. T0 provides runnable contract generation, validation, lint, type-check and test commands; product services remain skeletons.

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

## Development foundation

Prerequisites:

- Python 3.12.14 (see `.python-version`)
- Node.js 22.23.2 and npm 10.9.8 (see `.nvmrc` and `package.json`)
- uv 0.12.13

Install the frozen dependencies:

```bash
uv sync --frozen
npm ci
```

Run the offline checks; these commands make no model calls:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy packages/contracts/python/signalcase_contracts
uv run datamodel-codegen --check
uv build
npm test
npm run typecheck
npm run lint
npm run contracts:check
```

When `contracts/signalcase.schema.json` changes, regenerate both language contracts:

```bash
uv run datamodel-codegen
npm run contracts:generate
```

The canonical fixture bundles are `reproduced.json`, `blocked.json`, and `failed.json` under `contracts/examples/`. Python validation adds referential-integrity checks that JSON Schema alone cannot express.

## License

SignalCase is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
