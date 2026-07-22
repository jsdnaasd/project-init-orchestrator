# Project Init Orchestrator Evaluation Report

- Tool version: 0.2.0
- Behavioral scenarios: 10
- Passed: 10
- Scenario success rate: 100%
- Boundary audit scenario pass rate: 100%

These are deterministic local scenarios, not claims about model quality or production reliability.

| Scenario | Category | Result | Evidence |
| --- | --- | --- | --- |
| empty-initialization | initialization | PASS | All required control and state artifacts were created. |
| idempotent-rerun | idempotency | PASS | A second run produced no file changes. |
| preserve-existing-agents | idempotency | PASS | Existing AGENTS.md content was preserved byte-for-byte. |
| invalid-transition | state-machine | PASS | The initialized-to-complete shortcut was rejected. |
| allowed-boundary | boundary-audit | PASS | A change inside src/** passed the role audit. |
| forbidden-boundary | boundary-audit | PASS | A forbidden sensitive path was detected. |
| outside-scope | boundary-audit | PASS | A change outside src/** was detected. |
| readiness-gate | validation | PASS | Unresolved requirements prevented implementation readiness. |
| read-only-inspection | inspection | PASS | Inspection detected Python and performed no writes. |
| context-snapshot | context | PASS | A two-event source log produced a concise recoverable snapshot. |

## Reproduce

```bash
python3 scripts/run_evaluations.py
```
