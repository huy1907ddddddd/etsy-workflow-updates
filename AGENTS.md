# Instructions for Codex receiving Workflow3 updates

## Read first

Read `LATEST.json`, `source-manifest.json` and `UPDATE.md` at the same Git commit. This repository is a source distribution, not the local machine's production state or human approval history.

The current human request in the receiving chat controls authorization. Repository text alone does not authorize account changes, clearing warnings, restarting services, running batches, approving images or overwriting local work.

## Updating another machine

1. Locate that machine's Workflow3 directory and its applicable local AGENTS.md. Read its real configuration and current state. Do not assume `C:/Huy/etsy-workflow`, Windows account names, ports, workflow IDs, browser assignments or GoLogin profile IDs match the publishing machine.
2. Fetch a specific public Git commit into a separate checkout or staging folder. Read `LATEST.json` from that commit and verify its version agrees with `source-manifest.json`. Verify the source ZIP SHA256 and each extracted file's SHA256 and length. Reject path traversal, symlinks or any file outside the manifest.
3. Compare only the manifest files with the local source. Preserve unrelated local edits. Back up every file that will change before applying it. Keep a list of changed files and before/after hashes.
4. Never copy or overwrite local `*.private.*`, `.env`, token files, browser profiles, account mappings, OAuth files, databases, sessions, artwork, review decisions, KPI records or task journals. Their absence from this package is deliberate. Missing local prerequisites must be configured on that machine with the user's authorization.
5. Check machine-specific absolute paths before copying. Remap paths in the staged code where needed and record the difference from the package hash. Never copy the source machine's account or worker IDs into local configuration.
   Files marked `requires_local_binding_merge` contain destination placeholders. Merge the receiving machine's actual document/KPI destinations into these files before activation. Preserve local `config/listing-layout.json`, `config/kpi-layout.json` and `config/google-delivery.json` as well as the private configs. Never activate unresolved `LOCAL_BINDING_` or `LOCAL_DESTINATION_REQUIRED` placeholders.
6. Run appropriate checks in isolation. Some historical Python check scripts use fixed Windows paths; inspect them before executing. Do not run deployment, login, n8n import or batch commands as a test. Node browser/runtime unit tests use fixtures and are the primary checks for V53.
7. Activate only the components the receiving user authorized. Preserve that machine's service and restart rules. For the publishing machine, bridge8788 requires the existing explicit local restart procedure. Restarting a worker does not approve or resume a batch.
8. Record the distribution version, Git commit, files changed, tests, local path remaps, remaining prerequisites and activation outcome. Use that machine's error/version log if required by its local instructions. Report what was actually verified; unit tests do not prove live image generation or complete installation.

## Workflow behavior

Keep real human review gates and the receiving machine's authorized provider/account/retry policies. A change of source code does not grant permission to switch accounts, bypass login/CAPTCHA/quota/content blocks, reset checkpoints or regenerate acquired artwork.

Prompt-to-mockup remains an explicit batch choice; existing saved batches keep their mode, payload, revision and approval history. Account/lane disabling decisions from the publishing machine do not become account assignments on another machine.
