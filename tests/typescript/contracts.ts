import type {
  Report,
  SignalCaseFixtureBundle,
} from "../../packages/contracts/typescript/src/index.js";

const reproduced: Report["outcome"] = "reproduced";

export function firstReport(
  bundle: SignalCaseFixtureBundle,
): Report | undefined {
  return bundle.reports[0];
}

export const knownOutcome = reproduced;
