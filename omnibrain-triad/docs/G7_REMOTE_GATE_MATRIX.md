# G7 — Public-safe preflight governance

The Sentinel Preflight and Jev Shadow policy are deliberately generic and read-only.

## Public repository boundary

Do **not** commit cross-repository inventories, private repository names, private issue/PR URLs, branch names, commit SHAs, local paths, worktrees, manifests, access tokens, credentials, source excerpts, personal records, or cloud account identifiers to this public repository.

The previously published G7 remote-baseline JSON files and private project status matrix were removed from the current branch in security remediation G8. **This deletion does not purge their contents from Git commit history, pull request diffs, forks, caches, archives or clones.** Remediation beyond the current tree requires a coordinated history rewrite and credential/data exposure review; no destructive force push is performed automatically.

For local reconciliation, keep the G7/G8 full inventory **only in a private audit workspace**, off Git, or an access-controlled repository reviewed by its owner. The consumer in `tools/compare_remote_heads.py` accepts the complete CSV as a runtime argument; it does not need the CSV to be committed.

## Generic gate ownership and limitations

| Gate | Required proof | Automatic approval |
| --- | --- | --- |
| Remote Git | Independent API attestation with pinned refs | NO |
| Local Git | Read-only census of worktrees, stashes and refs | NO |
| Canonical authority | Owner-signed constitutional revision | NO |
| Cross-system E2E | Pinned source bytes and contract test | NO |
| Human-scientific | Qualified review and controlled experiment | NO |
| Rights and privacy | Owner rights assessment and data handling | NO |
| Production security | Deployment owner review and release gate | NO |

- `PASS_REPORTED` is never equivalent to `VERIFIED`.
- The Jev adapter has **no provider connection and no authorization**; it remains an offline shadow contract.
- A successful CI verifies software tests, not scientific efficacy, rights, consent or deployed permissions.
- Remote and local snapshots must not be conflated; even identical Git SHAs by directory name do not attest repository origin.
- An empty remote repository does not imply no local work.

The complete private project-level closeout and local handoff are deliberately **not distributed** through this public repository.
