# Workflow Reference

## Requirement Interview

Use `superpowers:brainstorming` when it is installed. Otherwise ask one focused question at a time and cover:

- problem and business objective;
- target users and core workflows;
- in-scope and out-of-scope behavior;
- technical, platform, budget, and schedule constraints;
- integrations, credentials, sensitive operations, and approvals;
- success signals and measurable acceptance criteria;
- preferred autonomy after design approval.

Summarize the proposed design and obtain approval before implementation. Routine implementation decisions do not require repeated user confirmation after that gate.

## Role Selection

Create only roles justified by independent work or review boundaries. Prefer a small set such as research, implementation, and verification. Do not create roles merely to imitate parallel work.

Before dispatching a role:

1. Create its brief with a concrete outcome.
2. Set allowed and forbidden path patterns.
3. Capture a baseline.
4. Provide the current snapshot, spec, task, and relevant logs.

After return:

1. Run the role audit.
2. Reject or investigate every violation.
3. Run task verification.
4. Record the handoff and evidence.
5. Integrate only verified output.

## Native Capability Fallbacks

- Native goal available: create one main project goal and keep logical role goals in briefs and persistent state.
- Native goal unavailable: use `state.json`, `events.jsonl`, and `snapshot.md` as the durable goal layer.
- Native subagents available: dispatch bounded roles through the host tools.
- Native subagents unavailable: execute bounded role passes sequentially while preserving separate briefs, logs, baselines, and audits.
- Brainstorming Skill unavailable: use the interview protocol above and record the fallback.

Do not claim that an instruction-only fallback is native goal mode or real parallel subagent execution.
