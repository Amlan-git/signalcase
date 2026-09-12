# Contract source of truth

`signalcase.schema.json` is the canonical wire schema. The example bundles exercise reproduced, blocked, and infrastructure-failed states without real customer data.

Python adds cross-record checks for source/evidence references, workspace boundaries, storage keys, duplicate event sequences, and replay claims. JSON Schema remains responsible for record shape, required fields, formats, limits, and enums.

After editing the schema, regenerate and verify both consumers:

```bash
uv run datamodel-codegen
npm run contracts:generate
uv run pytest
npm test
uv run datamodel-codegen --check
npm run contracts:check
```

Do not edit generated Python or TypeScript models directly. Breaking contract changes require a version increase and coordinated consumer updates.
