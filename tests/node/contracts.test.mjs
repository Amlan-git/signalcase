import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import test from "node:test";

import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const schema = JSON.parse(readFileSync("contracts/signalcase.schema.json", "utf8"));
const fixtureNames = readdirSync("contracts/examples")
  .filter((name) => name.endsWith(".json"))
  .sort();

test("all shared fixtures satisfy the canonical schema", () => {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  addFormats(ajv);
  const validate = ajv.compile(schema);

  for (const fixtureName of fixtureNames) {
    const fixture = JSON.parse(
      readFileSync(`contracts/examples/${fixtureName}`, "utf8"),
    );
    assert.equal(
      validate(fixture),
      true,
      `${fixtureName}: ${ajv.errorsText(validate.errors)}`,
    );
  }
});
