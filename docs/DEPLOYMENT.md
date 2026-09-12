# Deployment and cost decisions

## Fixed decisions

Amplify excluded. Low-traffic hackathon, no assumed AWS credits. Strands required. Bedrock + AgentCore Runtime/Browser + S3 are proposed hosted components, not yet provisioned. Development uses local adapters and fixture tests. Model inference, browser/runtime consumption and storage may incur charges even with no public traffic.

## Hosting resolution gate (T0/T4, Amlan)

Frontend hosting remains unselected by the user. Prefer a static host already available to the team. Candidates: Cloudflare Pages or Vercel static hosting, subject to current plan eligibility. A static host cannot execute Python/browser jobs. API and sandbox need compute independently.

For a concrete AWS fallback, package the small Python API and sandbox backend behind API Gateway + Lambda, with static storefront assets on the frontend host and sandbox state in scoped S3 objects. This adds usage-based services; it is an implementation option, not already approved deployment. Avoid synchronous agent execution inside Lambda. The launch endpoint invokes a runtime entrypoint that registers background work and returns promptly. Verify full continuation after response before selecting this path.

Alternatively run API and sandbox on one existing persistent server the team already controls. This is viable only if it stays available during judging and can reach AWS services securely. Do not choose a paid always-on instance merely because traffic is low.

Decision criteria: existing access, working async invocation, supported region/model, judge availability, setup effort and measured cost. Record selected host/region/model/versions after the probe; until then no teammate should couple UI or agent logic to a particular frontend host.

## Runtime and browser feasibility probe

Verify model tool calling, start an isolated browser, reach the hosted sandbox, save/retrieve a screenshot, run a registered async task past its HTTP response, close browser/session and read persisted evidence. Test credentials are separate for API, agent and controls. Verify allowed origins and IAM scope. Do not assume ordinary runtime filesystem is durable.

## Cost controls

No free-credit assumption. Limit model context to relevant docs, use DOM inspection before screenshots, cap calls/actions/deadlines, stop browser sessions in finally blocks, and avoid public unrestricted job launch. Judge access must remain usable without arbitrary evaluation quotas. Billing alerts are notifications, not hard spending caps. Application limits bound individual jobs, not all possible AWS charges.

Benchmark one real investigation before budgeting total development + repeated evaluation + judging runs. Formula: model input/output token charges + browser/runtime resource usage + storage/requests/logging/hosting. Record model price source and region. No fixed dollar total is promised.

## Release and operations

- Pin source revision, dependency locks and deployment identifiers.
- Supply .env.example with names only: AWS_REGION, BEDROCK_MODEL_ID, EVIDENCE_BUCKET, AGENT_RUNTIME_ARN, BROWSER_ID, SANDBOX_ORIGIN, API_ORIGIN, DEMO_ACCESS_SECRET. Keep actual values in secret configuration; never commit keys.
- Prefer short-lived IAM roles over static keys. Browser must not receive API/cloud credentials.
- CI uses fixtures. Deployment is manually triggered by lead after review; no production permissions on external PRs.
- Health check, one fresh live investigation, report download and workspace isolation are release gates.
- Preserve availability through judging end. Cleanup afterwards: stop sessions, remove hosted compute and gateway resources, expire evidence, remove test secrets, and inspect remaining billable resources. Deleting a frontend does not delete its backend.

## Primary references

- [Runtime async processing](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-long-run.html)
- [Runtime sessions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html)
- [Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
- [AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)

Consult exact pinned SDK docs during implementation; these references do not prove the proposed deployment has been tested.
