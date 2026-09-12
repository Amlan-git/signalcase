/* Generated from contracts/signalcase.schema.json. Do not edit directly. */

export type Uuid = string;
export type NonEmptyString = string;
export type Timestamp = string;
/**
 * @minItems 1
 */
export type UuidList = [Uuid, ...Uuid[]];
export type StringList = string[];
export type Evidence = {
  [k: string]: unknown;
} & {
  id: Uuid;
  job_id: Uuid;
  workspace_id: Uuid;
  session_id: Uuid | null;
  kind: "screenshot" | "dom" | "action" | "document_excerpt" | "calculation";
  created_at: Timestamp;
  storage_key: NonEmptyString;
  sha256: string;
  mime_type: NonEmptyString;
  summary: NonEmptyString;
  document_id: Uuid | null;
  quote: string | null;
};
export type UuidList1 = Uuid[];
/**
 * @minItems 1
 */
export type UuidList2 = [Uuid, ...Uuid[]];
export type ExpectedBehavior = {
  [k: string]: unknown;
} & {
  text: NonEmptyString;
  document_ids: UuidList1;
  assumption: boolean;
};
/**
 * @minItems 1
 */
export type UuidList3 = [Uuid, ...Uuid[]];
/**
 * @minItems 1
 */
export type UuidList4 = [Uuid, ...Uuid[]];
/**
 * @minItems 1
 */
export type UuidList5 = [Uuid, ...Uuid[]];
/**
 * @minItems 1
 */
export type UuidList6 = [Uuid, ...Uuid[]];
export type Job = {
  [k: string]: unknown;
} & {
  id: Uuid;
  workspace_id: Uuid;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  created_at: Timestamp;
  updated_at: Timestamp;
  deadline_at: Timestamp;
  input: JobInput;
  group_ids: UuidList1;
  report_ids: UuidList1;
  error: Error | null;
  metrics: Metrics;
};
/**
 * @minItems 1
 */
export type UuidList7 = [Uuid, ...Uuid[]];

export interface SignalCaseFixtureBundle {
  contract_version: "1";
  /**
   * @maxItems 100
   */
  conversations: Conversation[];
  documents: Document[];
  existing_issues: ExistingIssue[];
  groups: Group[];
  evidence: Evidence[];
  events: Event[];
  reports: Report[];
  jobs: Job[];
}
export interface Conversation {
  id: Uuid;
  workspace_id: Uuid;
  source: NonEmptyString;
  external_id: string | null;
  text: string;
  created_at: Timestamp;
}
export interface Document {
  id: Uuid;
  workspace_id: Uuid;
  title: NonEmptyString;
  text: NonEmptyString;
  version: NonEmptyString;
}
export interface ExistingIssue {
  id: Uuid;
  workspace_id: Uuid;
  title: NonEmptyString;
  description: NonEmptyString;
  status: NonEmptyString;
}
export interface Group {
  id: Uuid;
  workspace_id: Uuid;
  conversation_ids: UuidList;
  claim: NonEmptyString;
  prerequisites: StringList;
  unknowns: StringList;
}
export interface Event {
  id: Uuid;
  job_id: Uuid;
  workspace_id: Uuid;
  sequence: number;
  created_at: Timestamp;
  kind: "phase" | "action" | "observation" | "warning" | "completion";
  message: NonEmptyString;
  evidence_ids: UuidList1;
}
export interface Report {
  id: Uuid;
  job_id: Uuid;
  workspace_id: Uuid;
  group_id: Uuid;
  title: NonEmptyString;
  outcome: "reproduced" | "not_reproduced" | "blocked";
  interpretation: "observed_defect" | "possible_feature_gap" | "documented_behavior" | "unresolved";
  source_conversation_ids: UuidList2;
  expected: ExpectedBehavior;
  actual: ActualBehavior;
  /**
   * @minItems 1
   */
  steps: [InvestigationStep, ...InvestigationStep[]];
  /**
   * @minItems 1
   */
  attempts: [Attempt, ...Attempt[]];
  duplicate_candidates: DuplicateCandidate[];
  limitations: StringList;
  proposed_acceptance_checks: StringList;
  evidence_ids: UuidList6;
  replay_status: "not_generated" | "not_run" | "passed" | "failed";
}
export interface ActualBehavior {
  text: NonEmptyString;
  evidence_ids: UuidList3;
}
export interface InvestigationStep {
  action: NonEmptyString;
  observation: NonEmptyString;
  evidence_ids: UuidList4;
}
export interface Attempt {
  session_id: Uuid;
  result: NonEmptyString;
  evidence_ids: UuidList5;
}
export interface DuplicateCandidate {
  issue_id: Uuid;
  reason: NonEmptyString;
}
export interface JobInput {
  conversation_ids: UuidList7;
  max_groups: number;
  seed_version: number;
}
export interface Error {
  code:
    | "INVALID_INPUT"
    | "UNAUTHORIZED"
    | "NOT_FOUND"
    | "WORKSPACE_BUSY"
    | "MODEL_UNAVAILABLE"
    | "BROWSER_FAILED"
    | "DEADLINE_EXCEEDED"
    | "WORKER_LOST"
    | "STORAGE_FAILED"
    | "CONTRACT_INVALID";
  message: NonEmptyString;
  retryable: boolean;
}
export interface Metrics {
  model_calls: number;
  browser_actions: number;
  input_tokens: number;
  output_tokens: number;
  duration_ms: number;
  estimated_model_cost_usd_micros: number | null;
}
