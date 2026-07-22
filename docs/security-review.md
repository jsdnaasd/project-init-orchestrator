# Security Review

- Scope: Codex Skill, Python CLI, installer, tests, CI, and generated project policies
- Review date: 2026-07-23
- Result: no unresolved critical or high-severity findings

## Remediated Findings

| Severity | Finding | Remediation | Evidence |
| --- | --- | --- | --- |
| High | Git-ignored `.env` or key files could be absent from a normal visible-file baseline | Add a second ignored-file scan filtered to effective sensitive patterns | `test_audit_detects_gitignored_secret_and_nested_secret` |
| Medium | Symbolic links were skipped, allowing link-target changes to avoid the file hash report | Hash the link target string without following or reading the external target | `test_audit_tracks_symlink_target_and_rejects_policy_drift` |
| Medium | A role policy could be changed after baseline capture | Persist policy and global forbidden patterns in the baseline and require recapture after drift | `test_audit_tracks_symlink_target_and_rejects_policy_drift` |

## Controls Verified

- User path patterns reject absolute paths and `..` traversal.
- Role names are normalized to safe lowercase slugs.
- Sensitive patterns take precedence over broad role allow patterns.
- Nested `.env`, `secrets/`, `.pem`, and `.key` paths are globally forbidden by default.
- JSON state writes use same-directory temporary files and atomic replacement.
- Subprocess calls use argument arrays and never enable a shell.
- The installer moves existing data to a timestamped backup before replacement.
- Recoverable uninstall moves the Skill instead of deleting it.
- Runtime code uses only the Python standard library.
- Source scans found no credential-shaped tokens, private keys, unsafe evaluation, shell execution, or unsafe deserialization patterns.

## Residual Boundaries

- The audit detects changed paths after work; it is not a process sandbox and cannot prevent writes in real time.
- A malicious process with direct access to `.project-init-orchestrator/` could alter policy or baseline files. The intended trust boundary is a cooperative local Codex workflow, not an adversarial multi-user host.
- File hashing does not inspect content for malware or secret values; it only detects path and content changes.
- `shellcheck` was not available in the local environment. `bash -n`, integration tests, temporary installation, backup, reinstall, and uninstall scenarios passed.
