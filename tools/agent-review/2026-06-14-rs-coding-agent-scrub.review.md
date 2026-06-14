### Summary
Scrubbed RouterShell coding-agent instructions so they remain RouterShell-specific. Removed the PyPNM FastAPI guidance block and replaced remaining PyPNM/CMTS wording with RouterShell-focused guidance.

### Modified Files
- CODING_AGENT.md

### Commands Executed And Results
- `rg -n "PyPNM|FastAPI|pypnm|APIRouter|CMTS|cable modem|src/pypnm|Router files|Prefer POST|time\.sleep" CODING_AGENT.md || true` -> pass, no matches.
- `sed -n '1,260p' CODING_AGENT.md` -> pass, inspected updated instructions.
- `sed -n '1,220p' README.md` -> pass, self-check context reviewed.

### Tests
- `pytest` -> not run; documentation-only CA instruction cleanup.
- `ruff` -> not run; documentation-only CA instruction cleanup.
- `rg` -> pass, no PyPNM/FastAPI-specific wording remains in `CODING_AGENT.md`.

### Notes / Warnings
- The DB backend migration section remains because it references RouterShell design docs, but the PyPNM ownership bullet was removed.

### Remaining TODOs / Follow-Ups
- None.

# FILE: CODING_AGENT.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# AGENTS.md

This file provides guidance for coding agents working in this repository.
Keep it short, accurate, and updated when workflows change.

## Agent Permissions

<environment_context>
    <sandbox_mode>danger-full-access</sandbox_mode>
    <network_access>enabled</network_access>
    <!-- Access is governed by this file and explicit user approval -->
</environment_context>

## Project Basics

- Language: Python (3.10+)
- User shorthand: when Maurice says `RS`, treat it as `RouterShell`.
- This repo is NOT greenfield; extend existing code and patterns.
- Build/test entry points are defined in `pyproject.toml`, `Makefile`, or `scripts/`.
- Read `README.md` first for setup and usage.
- Type checking is strict; avoid `Any` and generic container types.
- Ruff compliance is required (do not auto-format unless explicitly requested).

## External Consumers (Compatibility Contract)

- BareMetalRouterOS may consume RouterShell through Yocto recipes and image builds.
- Preserve public CLI, package, and install behavior unless the user explicitly approves breaking changes.
- If a change affects downstream image integration, call out the cross-repo impact before making it.

## Repo Conventions

- RouterShell implementation code lives under `src/routershell/`.
- Runtime install tooling lives under `install/`.
- Development, release, VM, and operational helpers live under categorized `tools/` directories.
- Keep Linux host mutation workflows guarded, documented, and VM-tested where practical.

## Documentation

- Docs must follow the existing repo docs layout and conventions.
- Update docs alongside code changes (choose the correct location by inspecting the existing docs tree; do not invent parallel structures).
- Do not modify `mkdocs.yml` or navigation unless explicitly required by the task.
- Markdown must render correctly in both MkDocs and GitHub.
- No emojis in documentation.
- Use generic placeholders:
  - MAC: `aa:bb:cc:dd:ee:ff`
  - IP: `192.168.0.100`
- Emojis are allowed only in `install.sh`; they are prohibited everywhere else.
- When adding new terms or acronyms, update `docs/definition/index.md` and keep entries in alphabetical order.
- After completing a task, create a single “agent review” file that concatenates the full contents of all files changed in that task (path and naming should follow existing repo practice).
- Always regenerate the agent review bundle after any subsequent edits so it reflects every changed file.
- When an error is fixed, add or update a FAQ entry with the error and resolution, and add a TODO entry noting the FAQ update requirement.

### Reuse Index

- Agents MUST consult the existing reuse / symbol index under `tools/agent-review/` (if present) before introducing new:
  - types, validators, ID formats, storage conventions, persistence adapters, or config namespaces
- Any deviation requires an explicit gap justification and user approval.

## DB Backend Migration (Locked Decisions)

Agents working on the DB backend refactor MUST follow the locked decisions recorded in the design docs (see `docs/design/db/`):

- Install-time backend selection via `install.sh` flags + interactive default to SQLite.
- Postgres secrets via env var overrides (no plaintext requirement in tracked JSON).
- Idempotent schema apply using shipped DDL assets + seeding `UNKNOWN` sysDescr + default artifact store(s).
- SQLite for single-writer; Postgres recommended for multi-worker / multi-process (especially downstream orchestration use).
- Paths stored in DB are portable (app-root relative), resolved at runtime.
- CI validates SQLite (required) and Postgres (service container, recommended as required).
- JSON ledger persistence is deprecated and removed from runtime paths (optional offline migrator only).

## Configuration

- `system.json` is the single source of truth.
- New configuration namespaces must be implemented as Pydantic BaseModels.
- BaseModels must use one-line `Field(..., description="...")`.
- Avoid generic `str` for semantic identifiers or paths in public models and APIs; use existing RouterShell value objects or add a focused helper type under `src/routershell/lib/`.
- When working with MAC or inet strings, validate using `MacAddress()` or `Inet()` instead of assuming `str(...)` formatting is valid.
- Request override defaults: missing or null means use `system.json` defaults; blank strings are invalid.

## Timestamp Conventions

- All stored timestamps are epoch seconds.
- Convert to ISO-8601 only at display or external response boundaries.

## Coding Guidelines (Strict)

- No generic container imports (`Dict`, `List`, `Tuple`, `Union`).
  Use built-in types and `|`.
- RouterShell is a PEP 561 typed package; keep `src/routershell/py.typed`
  packaged and covered by tests.
- Shared RouterShell type aliases live in
  `src/routershell/lib/common/types.py`.
- Do not create competing type alias modules without explicit approval.
- Ruff selects `F`, `E`, `W`, `I`, `B`, `UP`, `ANN`, `SIM`, and `PERF`
  in `pyproject.toml`.
- Temporary Ruff ignores are allowed only for the existing legacy annotation
  and whitespace backlog; do not add new ignores without approval.
- Modern type syntax is mandatory in touched code: use `list`, `dict`,
  `tuple`, and `X | Y` rather than `List`, `Dict`, `Tuple`, or `Union`.
- Docstrings and comments must use the same modern type spellings so examples
  do not preserve legacy typing forms.
- Public method arguments must not use bare `str` for semantic RouterShell
  values such as interface names, inet addresses, MAC addresses, hostnames,
  bridge names, VLAN names, NAT pool names, DHCP pool names, Wi-Fi policy
  names, SSIDs, or paths. Use the shared aliases in
  `src/routershell/lib/common/types.py`.
- Private method arguments should use those shared semantic aliases when the
  value carries the same domain meaning. Bare `str` is acceptable only for
  genuinely free-form text, command output, log text, or local glue values.
- Public method return annotations must not use bare `bool` for RouterShell
  operation status or predicate results. Use the shared `StatusResult` or
  `PredicateResult` newtypes from `src/routershell/lib/common/types.py`.
- Private method return annotations should use those return newtypes when the
  method exposes operation status or a reusable predicate.
- Avoid `Any` unless unavoidable; isolate and justify its usage.
- Every function argument must be annotated.
- Avoid `None` returns; prefer empty values unless `None` is semantically required.
- Avoid magic numbers; use named constants.
- Prefer `BaseModel` over raw dicts for public/stateful structures (state, configuration, persistence records).
- dicts are allowed only for short-lived internal glue logic.
- Prefer classes with static methods over standalone functions.
- Public methods MUST have detailed docstrings.
- Private methods may have minimal docstrings.
- Avoid method-level debug logs.
- Do not add Ruff ignores (`# noqa`, `# ruff: noqa`). If an ignore is needed, ask for permission first.
- Logging pattern in classes:

  ```python
  self.logger = logging.getLogger(f"{self.__class__.__name__}")
  ```

- Prefer `match/case` over long if/else chains.
- No code should contain 3+ nested loops. 2 nested loops are discouraged unless necessary.
- No one-line if statements (E701).
- Preserve all existing whitespace and alignment.
- Never auto-format or re-align code.
- Do not enforce snake_case; keep existing naming conventions as-is.

## Tests (Mandatory)

- Every phase deliverable MUST include pytest coverage for new or changed behavior.
- Do not claim a phase item is complete unless pytest has been added and executed (or a concrete blocker is documented).
- Tests must remain hermetic: no live host network reconfiguration unless the
  workflow explicitly targets a disposable VM.

## Burndown Governance

- Agents MUST consult the current burndown and DB design docs before implementing work.
- Agents MUST NOT update burndown checkmarks unless explicitly instructed by the user.
- Code written does not imply progress accepted.

## Workflow Rules

- When the user says “train”, read code silently until told otherwise.
- Do not assume missing context; ask.
- Keep changes minimal and scoped.
- Do not refactor unrelated code.
- Avoid destructive commands unless explicitly requested.
- Do not print file contents into chat unless the user explicitly requests it; ask first if unsure.
- Always end tasks with an agent review bundle containing the full contents of all files touched in the task.
- Agent review bundles must start with the standard summary template block below (before any `# FILE:` sections).
- When the user says `CAT_FILES`, create a single bundle file containing the full contents of every file touched in the task, each preceded by `# FILE: <path>`, and provide the `cat` command for the bundle.
- Keep a brief summary of user prompts after any request for a commit message and track changes since the most recent commit message request.
- When asked for a commit message, respond with the format below, keep it succinct, and include all changes since the last commit message request.
- Before changing version behavior or release tooling, review `tools/git/`, `tools/release/`, and `tools/support/bump_version.py` to avoid version-control drift.
- `tools/git/git-save.sh` is the normal save-commit path and accepts `--commit-msg "<commit-msg>"`.
- `tools/release/release.py` is the supported flow for committed release version updates, tags, and pushes.

## Commit Message Format

- If the chat request starts with `commit-msg`, use the message as the value for `./tools/git/git-save.sh --commit-msg "<commit-msg>"`.
- Always include the `./tools/git/git-save.sh --commit-msg` prefix when responding to commit-message requests.
- First line: one-line summary, maximum 50 characters.
- First line must start with one of: `Feature:`, `Bugfix:`, `Docs:`, `Refactor:`, `Test:`, `Tooling:`, `Release:`.
- Detailed description lines are maximum 72 characters per line.
- Every line after the first must start with `-`.
- When the user asks for a commit message, provide plain text for direct paste into the terminal or UI text box.
- Do not wrap commit message suggestions in quotes, backticks, or code fences unless the user explicitly asks for that format.
- Prefer detailed commit messages that describe the current change set clearly.
- Do not default to a one-line commit message when the change set is broad; provide a title plus concise bullet points.
- Avoid redundant wording and avoid repeating the exact prior commit message suggestion unless the diff is unchanged and the user explicitly asks to reuse it.
- If the user asks for "in a text box", return plain text only.
- If the user asks for "in a markdown text box", return the commit message inside a fenced code block with `text`.

### Agent Review Bundle Summary Template (Standard)

Use this Summary block at the very top of every `*.review.md` bundle (before any `# FILE:` sections).

### Summary
<1–3 sentences describing what changed and why. Keep it factual and phase-scoped.>

### Modified Files
- <absolute or repo-relative path 1>
- <path 2>
- <path N>

### Commands Executed And Results
- `<command 1>` → <result (pass/fail + key output)>
- `<command 2>` → <result>
- `<command N>` → <result>

### Tests
- `pytest` → <pass/fail + notes>
- `ruff` → <pass/fail + notes>
- <other> → <pass/fail + notes>

### Notes / Warnings
- <any relevant warnings, deprecations, expected exclusions, or operational notes>
- <or: None>

### Remaining TODOs / Follow-Ups
- <todo 1>
- <todo 2>
- <or: None>

## Repo Hygiene

- License is Apache-2.0; keep SPDX headers aligned with `LICENSE` and `NOTICE`.
- For any modified or newly created file, update the SPDX header year to 2026.
- If a file already has a SPDX year and the year has changed, update it as a range (example: 2025 -> 2025-2026).
- Keep implementation code inside `src/routershell/`; do not add loose root-level Python modules unless they are established project entry points or standard configuration files.
- Treat RouterShell as non-legacy code for packaging decisions; avoid compatibility shims that keep obsolete root-level modules alive unless Maurice explicitly approves them.
- Keep `tools/` organized by category.
- Do not add files directly under `tools/` root.

## Agent Self-Checks

Before responding:

- Re-read this file and `README.md`.
- Confirm pytest coverage exists or is explicitly blocked.
- Confirm pytest and ruff output have no deprecation warnings (treat as failures).
- Confirm changes align to the current phase and do not leak scope.
- Confirm formatting and alignment are preserved.

## Training

When the user requests "train", read the following sources:

- `AGENTS.md`
- `src/routershell/lib/` (RouterShell implementation modules)
- `tools/agent-review/` (all files, if present)
