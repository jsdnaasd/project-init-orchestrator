# Architecture

Project Init Orchestrator separates reasoning from deterministic project governance.

```mermaid
flowchart TD
    U[User objective] --> S[Codex Skill]
    S --> I[Requirement interview and design approval]
    S --> N[Native goal and subagent tools when available]
    S --> C[Standard-library Python CLI]
    C --> A[AGENTS.md, spec, tasks, briefs and work logs]
    C --> P[config.json and role path policies]
    C --> E[events.jsonl and state.json]
    E --> X[Compact context snapshot]
    P --> B[Baseline and changed-file audit]
    A --> V[Readiness and completion validation]
    B --> L{Loop gate}
    V --> L
    L -->|incomplete or failed| S
    L -->|direct evidence complete| D[Completion]
```

## Responsibility Split

| Layer | Responsibility | Explicit Non-Responsibility |
| --- | --- | --- |
| Codex Skill | Triggering, interview protocol, native tool use, orchestration decisions | Does not create new runtime capabilities |
| `pio.py` | File generation, state transitions, event persistence, snapshots, path audits, validation | Does not perform LLM reasoning or run in the background |
| Project documents | Human-readable goal, scope, roles, tasks, decisions, and evidence | Do not enforce policies by themselves |
| Native Codex tools | Goal persistence and real subagent dispatch when exposed by the host | Availability is not guaranteed by the Skill |

## Persistent Project Memory

The event log is the lossless history. `snapshot.md` is a deterministic, bounded view of current state and recent events. Regenerating the snapshot never deletes events, which makes context recovery inspectable instead of relying only on chat history.

## Boundary Model

Role policies use explicit allow and forbid patterns. A baseline captures visible file hashes before delegation. The post-work audit compares hashes and classifies every changed path. This detects scope violations; it does not sandbox a process or prevent operating-system-level writes.
