### Summary
Aligned RouterShell licensing with PyPNM by switching package metadata and SPDX headers from GPL-2.0-or-later to Apache-2.0. Replaced the root LICENSE with Apache License 2.0 text, added a RouterShell NOTICE file, and documented the license in README and agent guidance.

### Modified Files
- CODING_AGENT.md
- LICENSE
- NOTICE
- README.md
- doc/faq.md
- pyproject.toml
- tools/reference/tools-layout.md
- tools/release/check_version.py
- tools/release/release.py
- tools/release/test-runner.py
- tools/support/bump_version.py

### Commands Executed And Results
- `python3 - <<PY ... tomllib license metadata check ... PY` -> pass, license metadata ok
- `python3 tools/release/check_version.py` -> pass, RouterShell and pyproject versions both 0.1.0
- `python3 -m py_compile tools/support/bump_version.py tools/release/check_version.py tools/release/release.py tools/release/test-runner.py` -> pass
- `bash -c 'source tools/git/git-common.sh; rs_run_quality_gates'` -> pass available gates; pytest and ruff skipped for system Python because they are not installed there
- `/tmp/routershell-root-clean-check/bin/python -m pytest` -> pass, 4 tests
- `/tmp/routershell-root-clean-check/bin/python -m ruff check tools/support/bump_version.py tools/release/check_version.py tools/release/release.py tools/release/test-runner.py` -> pass
- `/tmp/routershell-root-clean-check/bin/python -m build` -> pass, sdist and wheel built with LICENSE and NOTICE included
- `grep -R "SPDX-License-Identifier: GPL\|GPL-2.0\|GNU GENERAL PUBLIC LICENSE" ...` -> pass, no active-file matches outside historical review bundles and LICENSE exclusion

### Tests
- `pytest` -> pass, 4 tests
- `ruff` -> pass for touched Python tooling files
- `build` -> pass through the project test virtual environment

### Notes / Warnings
- Historical files under `tools/agent-review/` still contain past GPL references as old task snapshots.
- System Python does not have `pytest`, `ruff`, or `build`; the project test virtual environment was used for those checks.

### Remaining TODOs / Follow-Ups
- None

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

- PyPNM is the authoritative engine and is consumed by downstream repos (example: PyPNM-CMTS).
- Preserve public API stability unless the user explicitly approves breaking changes.
- Do not embed downstream app concerns into PyPNM (keep PyPNM reusable and transport-agnostic).
- If a change affects downstream repos, call it out explicitly before making it.

## Repo Conventions (PyPNM)

- Persistence is filesystem-based artifacts plus metadata persistence per the DB backend design:
  - Binaries and derived artifacts remain on disk under `.data/` roots.
  - Transaction/group/operation metadata is DB-backed (SQLite or Postgres) per `docs/design/db/`.
- DB backend selection is owned by PyPNM at install time (no runtime “auto switching”).
- SQLite is intended for single-writer deployments (standalone/lab/demo).
- Postgres is recommended for multi-worker / multi-process deployments.

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

- PyPNM owns persistence, schema initialization, and DB APIs.
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
- Avoid generic `str` for semantic identifiers or paths in public models and APIs; use an existing semantic type or add a new alias in `src/pypnm/lib/types.py`.
- When working with MAC or inet strings, validate using `MacAddress()` or `Inet()` instead of assuming `str(...)` formatting is valid.
- Request override defaults: missing or null means use `system.json` defaults; blank strings are invalid.

## Timestamp Conventions

- All stored timestamps are epoch seconds.
- Convert to ISO-8601 only at display or external response boundaries.

## Coding Guidelines (Strict)

- No generic container imports (`Dict`, `List`, `Tuple`, `Union`).
  Use built-in types and `|`.
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

## FastAPI Guidelines (PyPNM)

- Router files must be lean:
  - `router.py` contains routing glue only (APIRouter configuration, endpoint registration, HTTP status translation).
  - No business logic in `router.py`. Business logic must live in `service.py` for that route group (same folder) or a shared service module if reused.
- All request/response bodies must be Pydantic BaseModels.
- Prefer POST for payload submission and endpoint contracts (PyPNM default).
  - Allow GET only where already present or clearly appropriate (health, readiness, version, status).
- Reuse shared models under the existing `src/pypnm/api/common/` structure (inspect current tree before adding anything new).
- Do not block request paths with `time.sleep()`.

## Tests (Mandatory)

- Every phase deliverable MUST include pytest coverage for new or changed behavior.
- Do not claim a phase item is complete unless pytest has been added and executed (or a concrete blocker is documented).
- Tests must remain hermetic: no live CMTS/cable modem dependencies.

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
- Keep implementation code inside packages such as `routershell/` or `lib/`; do not add loose root-level Python modules unless they are established project entry points or standard configuration files.
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
- `docs/design/db/` (all files)
- `src/pypnm/lib/` (DB/persistence + config helpers)
- `src/pypnm/api/` (routing/service patterns, where applicable)
- `tools/agent-review/` (all files, if present)

# FILE: LICENSE
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2025 Maurice Garcia

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

# FILE: NOTICE
RouterShell
Copyright (c) 2026 Maurice Garcia

This product includes software developed by Maurice Garcia for the RouterShell
project.

Attribution requirement:
If you distribute this software in source or binary form, you must retain this
NOTICE file and the LICENSE file, and include the following acknowledgment in a
location appropriate for third-party notices (for example, in documentation,
README, or UI credits):

  "RouterShell"

# FILE: README.md
# RouterShell (WORK IN PROGRESS)

RouterShell is an open-source, IOS-like CLI distribution written in Python 3. It is designed to provide a flexible and user-friendly command-line interface for network administrators and enthusiasts, offering a comprehensive range of networking features and capabilities tailored to diverse needs.

**Key Features of RouterShell:**

1. **Interface Configurations:** RouterShell supports a variety of interface configurations, including:
   - **Loopback Interfaces:** Ideal for testing and diagnostics, loopback interfaces are easy to set up and provide a versatile tool for network validation.
   - **Physical Interfaces:** Compatibility with Ethernet, USB, wireless (WiFi and cellular) interfaces, making it adaptable to various hardware environments.
   - **Bridging:** Enables the connection of different network segments, which is beneficial in creating complex network topologies.
   - **VLAN Support:** Facilitates network segmentation and organization, which is crucial for larger, more intricate networks.

2. **Tunneling:** RouterShell includes support for tunneling protocols, such as GRE (Generic Routing Encapsulation), allowing the creation of point-to-point and point-to-multipoint tunnels. This feature enables the encapsulation of packets for secure and efficient transport across different network segments, which is useful in VPNs and cross-network communication.

3. **NAT (Network Address Translation) Support:** Provides NAT functionality, essential for translating private IP addresses to public IP addresses, commonly required in both home and enterprise network setups. This feature helps in conserving public IP addresses and adds a layer of security by masking internal network structures.

4. **Access Control List (ACL) and Firewall Support:** RouterShell supports ACLs and firewall functionalities, offering enhanced network security by controlling incoming and outgoing traffic based on predefined rules. This is crucial for protecting network resources and managing data flow effectively.

RouterShell aims to provide a comprehensive CLI experience similar to traditional network operating systems, with the flexibility and extensibility of Python, making it a valuable tool for managing and automating network environments.


Regarding its intended use:

- **Quick Router Deployment:** RouterShell is designed to expedite router setup using a minimal Linux image, a valuable feature when rapid deployment is crucial.

- **Router-on-a-Stick Configuration:** RouterShell supports the "router-on-a-stick" configuration, useful for scenarios requiring network segmentation.

- **Compatibility with Embedded Router Distributions:** While initially developed with a focus on Ubuntu, RouterShell's lower layers are designed to be OS-agnostic, potentially allowing compatibility with various lightweight Linux distributions.

In conclusion, RouterShell is a router CLI distribution with features well-suited for specific network setups and security requirements. However, it is crucial to thoroughly assess your specific networking needs and consider whether RouterShell aligns with them before selecting it as your networking solution. Its comprehensive feature set, including NAT support and access control list/firewall support, makes it a versatile choice for network administrators and enthusiasts looking to configure and manage network infrastructure efficiently.

## Table of Contents

- [Global Privileged EXEC Commands](doc/cli/global_priv_exec_cmd.md): Learn about global privileged EXEC commands for system-level tasks.

- [ARP (Address Resolution Protocol)](doc/cli/configure/arp.md): Understand ARP and how it works in RouterShell.

- [Bridge Configuration](doc/cli/configure/bridge.md): Configure and manage bridges in RouterShell.

- [DHCPv4/v6 Configuration](doc/cli/configure/dhcp.md): Explore DHCP (Dynamic Host Configuration Protocol) setup for IPv4 and IPv6.

- [Interface Configuration](doc/cli/configure/config.md): Configure and manage network interfaces in RouterShell.

- [NAT (Network Address Translation)](doc/cli/configure/nat.md): Set up Network Address Translation for your RouterShell router.

- [Route Configuration](doc/cli//configureroute.md): Understand the routing and how to configure it in RouterShell.

- [VLAN Configuration](doc/cli//configurevlan.md): Configure and manage VLANs in your RouterShell network.

- [System Configuration](doc/cli/global/system.md): Learn about system-level configuration options in RouterShell.

- [Wireless Configuration](doc/cli/configure/wireless.md): Explore wireless network configuration in RouterShell.

## Router Configuration Examples

Explore a variety of router configuration examples to help you get started with RouterShell:

These examples cover scenarios like configuring a four-port bridge with VLAN support, setting up a four-port switch, and configuring NAT for a two-port setup. You can access the detailed instructions and information in the respective configuration files.

- [Four-Port Bridge with VLAN Configuration](doc/cli/four_port_bridge_vlan_config.md): This example guides you through setting up a four-port bridge with VLAN support, allowing for network segmentation and efficient traffic management.

- [Four-Port Switch Configuration](doc/cli/four_port_switch_config.md): Learn how to configure a four-port switch, which is essential for creating a network with multiple connected devices.

- [Two-Port NAT Configuration](doc/cli/two_port_nat_config.md): Understand how to set up Network Address Translation (NAT) for a two-port router, enabling the translation of private IP addresses to public IP addresses.

These configuration examples serve as practical guides to help you implement specific networking setups with RouterShell. Refer to the linked documentation files for step-by-step instructions and detailed explanations.

Feel free to explore these examples and adapt them to your networking needs. If you have any questions or need further assistance, don't hesitate to contact our community or project team. Thank you for choosing RouterShell!

## Additional Resources

Please select the specific documentation file you are interested in from the table of contents above to access detailed information and instructions for configuring and using RouterShell.

If you have any questions or need further assistance, please feel free to reach out to our community or project team. Thank you for choosing RouterShell!

- [RouterShell FAQ](doc/faq.md)

## Linux Runtime Install

[README INSTALLATION](install/README.md)

RouterShell includes a generic installer for non-embedded Linux hosts such as
Ubuntu, Debian, Fedora, RHEL-compatible systems, and openSUSE. Embedded and
BusyBox-style targets are intentionally out of scope for this installer.

Production install is the default.
The installer captures a root-only baseline snapshot under
`/var/lib/routershell/baseline` before making install changes.

Test installer changes in a disposable VM before running them on a development
workstation. Use `--development` only when testing editable installs with dev
dependencies; see [RouterShell VM Install Testing](tools/vm/README.md).

```bash
sudo ./install/install.sh
routershell
```

## Run RouterShell From Source

```bash
python3 -m routershell
```

Run the factory reset workflow from source with:

```bash
python3 -m routershell --factory-reset
```

## Python Development Install

RouterShell now includes Python packaging metadata in `pyproject.toml`.
For local development, use an isolated virtual environment and install the
project in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

After installation, run the CLI entry point:

```bash
routershell
```

Factory reset is also exposed as a console entry point:

```bash
routershell-factory-reset
```

Build distribution artifacts with:

```bash
python -m build
```

Run validation with:

```bash
python -m pytest
python -m ruff check .
```

## Git Helpers

Git helper scripts live under `tools/git/`:

```bash
./tools/git/git-save.sh --commit-msg "Update RouterShell"
./tools/git/git-push.sh --commit-msg "Update RouterShell"
```

See [RouterShell Git Helpers](tools/git/README.md) for save, push, and guarded branch
history reset workflows.

## Tools

Operational and development tools are grouped under `tools/` by purpose.
Review [RouterShell Tools Layout](tools/reference/tools-layout.md) before
running scripts that can alter disks, networking, packages, or services.

## Release Helpers

Release helper scripts live under `tools/release/`:

```bash
./tools/release/check_version.py
./tools/release/release.py --next patch --dry-run
```

See [RouterShell Release Helpers](tools/release/README.md) for version checks,
dry runs, releases, and commit reports.

## License

RouterShell is licensed under the [Apache License 2.0](LICENSE). Distributions
must retain the [NOTICE](NOTICE) file.

## [TODO](todo.md)

# FILE: doc/faq.md
# RouterShell FAQ

## Install fails with setuptools InvalidConfigError

If `sudo ./install/install.sh --development` fails while getting editable
build requirements and reports this error:

```text
setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions
```

Update RouterShell to a version whose `pyproject.toml` uses the SPDX
`license = "Apache-2.0"` expression without deprecated license classifiers,
then rerun the installer:

```bash
sudo ./install/install.sh --development
```

This error is raised by newer setuptools releases during package metadata
validation.

# FILE: pyproject.toml
# SPDX-License-Identifier: Apache-2.0

[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "routershell"
version = "0.1.0"
description = "IOS-like Python CLI distribution for Linux router configuration workflows."
readme = "README.md"
requires-python = ">=3.10"
license = "Apache-2.0"
license-files = ["LICENSE", "NOTICE"]
authors = [
    { name = "Maurice Garcia" },
]
keywords = [
    "cli",
    "linux",
    "networking",
    "router",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: System Administrators",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: System :: Networking",
    "Topic :: System :: Systems Administration",
]
dependencies = [
    "argcomplete>=3.0",
    "beautifulsoup4>=4.12",
    "cmd2>=2.4",
    "jc>=1.25",
    "prettytable>=3.0",
    "prompt-toolkit>=3.0",
    "pyte>=0.8",
    "tabulate>=0.9",
]

[project.optional-dependencies]
dev = [
    "build>=1.2",
    "pytest>=8.0",
    "ruff>=0.5",
    "twine>=5.0",
]

[project.scripts]
routershell = "routershell.cli:main"
routershell-factory-reset = "routershell.cli:factory_reset"

[project.urls]
Homepage = "https://github.com/mgarcia01752/RouterShell"
Repository = "https://github.com/mgarcia01752/RouterShell"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["routershell*", "lib*"]
namespaces = true

[tool.setuptools.package-data]
"lib.db.sqlite_db" = ["*.sql"]
"lib.network_services.dhcp.dnsmasq" = ["*.conf"]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = [
    "tests",
]

[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "W",
]

# FILE: tools/reference/tools-layout.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell Tools Layout

Tools are grouped by purpose so destructive host operations are easier to
identify before running them.

## Categories

- `agent-review/`: Coding-agent review bundles for completed tasks.
- `dev/`: Local development cleanup helpers.
- `disk/`: Disk inspection, formatting, and boot media helpers. These can be
  destructive.
- `examples/`: Example generators and usage demonstrations. Examples should not
  modify system files unless an explicit output path or flag is provided.
- `git/`: RouterShell Git save, push, and branch-history helpers.
- `hardware/`: Host hardware inspection helpers.
- `network/`: Network lab and interface mutation helpers. These can change host
  links, routes, firewall state, and wireless services.
- `reference/`: Captured command references and static notes.
- `release/`: Version checks, release automation, and release reports.
- `services/`: Service setup, teardown, and simulation helpers. These can
  install, remove, start, or stop host services.
- `support/`: Small support helpers used by release or workflow scripts.
- `vm/`: Disposable VM workflows for installer testing.

## Safety

Review scripts under `disk/`, `network/`, and `services/` before running them.
Prefer disposable VM testing for workflows that can alter host networking,
packages, disks, or service state.

# FILE: tools/release/check_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""Verify RouterShell version consistency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import tomllib


class VersionCheckTool:
    """Verify version consistency between the package and pyproject.toml."""

    MAX_ROOT_SEARCH_DEPTH: int = 6
    PYPROJECT_RELATIVE: str = "pyproject.toml"
    EXIT_OK: int = 0
    EXIT_ERROR: int = 1
    EXIT_MISMATCH: int = 2

    @staticmethod
    def _find_project_root(start_path: Path) -> Path:
        """Walk upwards to locate pyproject.toml, fallback to start path."""
        current = start_path
        for _ in range(VersionCheckTool.MAX_ROOT_SEARCH_DEPTH):
            if (current / VersionCheckTool.PYPROJECT_RELATIVE).is_file():
                return current
            if current.parent == current:
                break
            current = current.parent
        return start_path

    @staticmethod
    def _read_version_from_pyproject(path: Path) -> str:
        """Extract the project version value from pyproject.toml."""
        try:
            with path.open("rb") as handle:
                pyproject = tomllib.load(handle)
        except OSError:
            return ""

        project = pyproject.get("project", {})
        version = project.get("version", "")
        if not isinstance(version, str):
            return ""
        return version

    @staticmethod
    def _read_version_from_package(root_path: Path) -> str:
        """Read the runtime package version."""
        if str(root_path) not in sys.path:
            sys.path.insert(0, str(root_path))
        try:
            import routershell
        except ImportError:
            return ""
        return routershell.__version__

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser for the version check tool."""
        parser = argparse.ArgumentParser(
            description="Verify that the RouterShell package and pyproject.toml carry the same version."
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print results as JSON.",
        )
        return parser

    @staticmethod
    def _emit_text(package_version: str, pyproject_version: str, status: str) -> None:
        """Emit human-readable output."""
        if status == "error":
            print("Version check failed: unable to read one or more version values.")
        print(f"routershell package: {package_version or 'missing'}")
        print(f"pyproject.toml: {pyproject_version or 'missing'}")
        if status == "mismatch":
            print("Version mismatch detected.")
        if status == "ok":
            print("Version match confirmed.")

    @staticmethod
    def _emit_json(package_version: str, pyproject_version: str, status: str) -> None:
        """Emit JSON output."""
        payload = {
            "package": package_version,
            "pyproject": pyproject_version,
            "match": status == "ok",
            "status": status,
        }
        print(json.dumps(payload, ensure_ascii=True))

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Print versions from tracked files and return a status code."""
        script_dir = Path(__file__).resolve().parent
        root_path = VersionCheckTool._find_project_root(script_dir)
        pyproject_path = root_path / VersionCheckTool.PYPROJECT_RELATIVE

        package_version = VersionCheckTool._read_version_from_package(root_path)
        pyproject_version = VersionCheckTool._read_version_from_pyproject(pyproject_path)

        if not package_version or not pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(package_version, pyproject_version, "error")
            else:
                VersionCheckTool._emit_text(package_version, pyproject_version, "error")
            return VersionCheckTool.EXIT_ERROR

        if package_version != pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(package_version, pyproject_version, "mismatch")
            else:
                VersionCheckTool._emit_text(package_version, pyproject_version, "mismatch")
            return VersionCheckTool.EXIT_MISMATCH

        if options.json:
            VersionCheckTool._emit_json(package_version, pyproject_version, "ok")
        else:
            VersionCheckTool._emit_text(package_version, pyproject_version, "ok")
        return VersionCheckTool.EXIT_OK


if __name__ == "__main__":
    parser = VersionCheckTool._build_parser()
    args = parser.parse_args()
    sys.exit(VersionCheckTool.run(args))

# FILE: tools/release/release.py
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""RouterShell release automation."""

from __future__ import annotations

import argparse
import atexit
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Final

BUMP_SCRIPT_PATH: Final[Path] = Path("tools/support") / "bump_version.py"
PYPROJECT_FILE_PATH: Final[Path] = Path("pyproject.toml")
README_FILE_PATH: Final[Path] = Path("README.md")
DOCS_ROOT: Final[Path] = Path("doc")
WORKFLOWS_DIR: Final[Path] = Path(".github") / "workflows"
README_TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r'TAG="v\d+\.\d+\.\d+(?:-rc\d+)?"')

VERSION_PART_SEPARATOR: Final[str] = "."
EXPECTED_VERSION_PARTS: Final[int] = 3
MAJOR_INDEX: Final[int] = 0
MINOR_INDEX: Final[int] = 1
PATCH_INDEX: Final[int] = 2
RC_SUFFIX_PREFIX: Final[str] = "-rc"
RC_DEFAULT_NUMBER: Final[int] = 1

REPORT_DIR_NAME: Final[str] = "release-reports"
REPORT_FILE_PREFIX: Final[str] = "release-report"
REPORT_SECTIONS: Final[list[str]] = [
    "Docs",
    "CLI",
    "Database",
    "Networking",
    "Services",
    "Install",
    "Packaging",
    "Tests",
    "Tools",
]
REPORT_HEADERS: Final[list[str]] = ["Section", "Files Changed"]

SUMMARY: dict[str, str] = {}
RELEASE_LOG_DIR: Path | None = None


def _run(
    cmd: list[str],
    check: bool = True,
    *,
    label: str | None = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command, capturing output for logging on failure."""
    if capture_output:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    else:
        proc = subprocess.run(cmd, text=True, check=False)

    if proc.returncode != 0:
        if capture_output:
            _log_command_failure(label or Path(cmd[0]).name, proc)
        if check:
            raise subprocess.CalledProcessError(proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr)
    return proc


def _init_release_logging() -> None:
    """Create a temporary directory for failed-command logs."""
    global RELEASE_LOG_DIR
    if RELEASE_LOG_DIR is not None:
        return
    logs_dir = Path(REPORT_DIR_NAME) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    RELEASE_LOG_DIR = Path(tempfile.mkdtemp(prefix="routershell-release-logs-", dir=str(logs_dir)))
    print(f"[release] Command failures will be logged under: {RELEASE_LOG_DIR}")


def _sanitize_label(label: str) -> str:
    """Return a filesystem-safe label."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", label.strip().lower())
    return safe or "cmd"


def _log_command_failure(label: str, result: subprocess.CompletedProcess[str]) -> None:
    """Write stdout and stderr for a failed command."""
    if RELEASE_LOG_DIR is None:
        return
    safe_label = _sanitize_label(label)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = RELEASE_LOG_DIR / f"{safe_label}-{timestamp}.log"
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    args = result.args if isinstance(result.args, list | tuple) else [str(result.args)]
    log_path.write_text(
        f"$ {' '.join(str(arg) for arg in args)}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}\n",
        encoding="utf-8",
    )
    print(f"[release] {label} failed; see {log_path}")


def _format_state(state: str) -> str:
    """Format a release step state."""
    return state.upper()


def _print_status(label: str, state: str) -> None:
    """Record and print a release step status."""
    SUMMARY[label] = state
    print(f"{_format_state(state)} {label}")


def _print_release_summary() -> None:
    """Print the final release step summary."""
    if not SUMMARY:
        return
    print("\nRelease step summary:")
    for label, state in SUMMARY.items():
        print(f" {_format_state(state)} {label}")
    if RELEASE_LOG_DIR:
        print(f"Failure logs, if any, stored in: {RELEASE_LOG_DIR}")


atexit.register(_print_release_summary)


def _ensure_git_repo() -> None:
    """Ensure the current directory is inside a git repository."""
    result = _run(["git", "rev-parse", "--is-inside-work-tree"], check=False, label="git-repo")
    if result.returncode != 0:
        print("ERROR: release must run inside a git repository.", file=sys.stderr)
        sys.exit(1)


def _ensure_clean_worktree() -> None:
    """Ensure the git working tree has no uncommitted changes."""
    result = _run(["git", "status", "--porcelain"], check=False, label="git-status")
    output = (result.stdout or "").strip()
    if output:
        print("ERROR: Working tree is not clean. Commit or stash changes first.", file=sys.stderr)
        sys.exit(1)


def _get_current_branch() -> str:
    """Return the current branch name."""
    result = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], label="git-branch")
    return result.stdout.strip()


def _ensure_release_branch_allowed() -> None:
    """Fail fast unless running on an allowed release branch."""
    current_branch = _get_current_branch()
    if current_branch not in ("main", "hot-fix"):
        print("ERROR: release can only be performed on 'main' or 'hot-fix'.", file=sys.stderr)
        sys.exit(1)


def _get_head_commit() -> str:
    """Return the current HEAD commit."""
    result = _run(["git", "rev-parse", "HEAD"], label="git-rev-parse")
    return result.stdout.strip()


def _get_previous_commit() -> str | None:
    """Return the previous commit if one exists."""
    result = _run(["git", "rev-parse", "HEAD~1"], check=False, label="git-rev-parse-prev")
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _collect_commit_files(commit: str) -> list[str]:
    """Collect file paths touched by a commit."""
    result = _run(["git", "show", "--pretty=format:", "--name-only", commit], label="git-show")
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _classify_path(path: str) -> str:
    """Classify a changed path for release reporting."""
    normalized = path.replace("\\", "/").lower()
    if normalized.startswith("doc/") or normalized == "readme.md":
        return "Docs"
    if normalized.startswith("lib/cli/") or normalized.startswith("src/") or normalized == "routershell/cli.py":
        return "CLI"
    if normalized.startswith("lib/db/"):
        return "Database"
    if normalized.startswith("lib/network_manager/"):
        return "Networking"
    if normalized.startswith("lib/network_services/") or normalized.startswith("lib/system/"):
        return "Services"
    if normalized.startswith("install/") or normalized == "start.sh":
        return "Install"
    if normalized in {"pyproject.toml", "routershell/_version.py", "routershell/__init__.py"}:
        return "Packaging"
    if normalized.startswith("tests/"):
        return "Tests"
    if normalized.startswith("tools/"):
        return "Tools"
    return "Other"


def _summarize_sections(paths: list[str]) -> dict[str, int]:
    """Count changed files by report section."""
    counts = {section: 0 for section in REPORT_SECTIONS}
    counts["Other"] = 0
    for path in paths:
        section = _classify_path(path)
        counts[section] = counts.get(section, 0) + 1
    return counts


def _render_markdown_table(counts: dict[str, int]) -> str:
    """Render a markdown table for section counts."""
    rows = [(section, str(counts.get(section, 0))) for section in REPORT_SECTIONS]
    if counts.get("Other", 0) > 0:
        rows.append(("Other", str(counts["Other"])))
    lines = [f"| {REPORT_HEADERS[0]} | {REPORT_HEADERS[1]} |", "| --- | --- |"]
    lines.extend(f"| {section} | {count} |" for section, count in rows)
    return "\n".join(lines)


def _collect_workflows() -> list[tuple[str, str]]:
    """Collect GitHub workflow names and paths."""
    if not WORKFLOWS_DIR.exists():
        return []
    workflows: list[tuple[str, str]] = []
    for path in sorted(list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))):
        workflows.append((path.name, os.path.relpath(path, Path.cwd())))
    return workflows


def _write_release_report(commit: str, version: str, tag_name: str, branch: str, report_mode: str) -> Path:
    """Write a markdown release or commit report."""
    report_dir = Path(REPORT_DIR_NAME)
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = report_dir / f"{REPORT_FILE_PREFIX}-{version}-{timestamp}.md"
    files = sorted(_collect_commit_files(commit))
    counts = _summarize_sections(files)
    workflows = _collect_workflows()

    lines = [
        f"# RouterShell {report_mode} report",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Branch: {branch}",
        f"- Source commit: `{commit}`",
        f"- Release version: `{version}`",
        f"- Release tag: `{tag_name}`",
        "",
        "## Workflows",
        "",
    ]
    if workflows:
        lines.extend(f"- `{name}` (`{path}`)" for name, path in workflows)
    else:
        lines.append("_No workflows found._")

    lines.extend(["", "## Change Summary", "", _render_markdown_table(counts), "", "## Files", ""])
    if files:
        lines.extend(f"- `{path}`" for path in files)
    else:
        lines.append("_No files detected._")
    lines.append("")

    if SUMMARY:
        lines.extend(["## Release Step Summary", ""])
        lines.extend(f"- {state.upper()} {label}" for label, state in SUMMARY.items())
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def _read_pyproject_version() -> str:
    """Read the [project].version value from pyproject.toml."""
    if not PYPROJECT_FILE_PATH.exists():
        print(f"ERROR: pyproject.toml not found: {PYPROJECT_FILE_PATH}", file=sys.stderr)
        sys.exit(1)
    text = PYPROJECT_FILE_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if not match:
        print(f"ERROR: Could not find [project].version in {PYPROJECT_FILE_PATH}.", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def _validate_version_string(version: str) -> None:
    """Validate MAJOR.MINOR.PATCH version strings."""
    core_version = version.split(RC_SUFFIX_PREFIX, 1)[0]
    parts = core_version.split(VERSION_PART_SEPARATOR)
    if len(parts) != EXPECTED_VERSION_PARTS or not all(part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'. Expected MAJOR.MINOR.PATCH.", file=sys.stderr)
        sys.exit(1)


def _parse_version_parts(version: str) -> list[int]:
    """Parse a semantic version into numeric parts."""
    _validate_version_string(version)
    core_version = version.split(RC_SUFFIX_PREFIX, 1)[0]
    return [int(part) for part in core_version.split(VERSION_PART_SEPARATOR)]


def _compute_next_version(current_version: str, mode: str) -> str:
    """Compute the next semantic version."""
    parts = _parse_version_parts(current_version)
    match mode:
        case "major":
            parts[MAJOR_INDEX] += 1
            parts[MINOR_INDEX] = 0
            parts[PATCH_INDEX] = 0
        case "minor":
            parts[MINOR_INDEX] += 1
            parts[PATCH_INDEX] = 0
        case "patch":
            parts[PATCH_INDEX] += 1
        case _:
            print(f"ERROR: Unsupported next mode '{mode}'.", file=sys.stderr)
            sys.exit(1)
    return VERSION_PART_SEPARATOR.join(str(part) for part in parts)


def _update_version_files(new_version: str) -> None:
    """Update pyproject.toml via support tooling."""
    if not BUMP_SCRIPT_PATH.exists():
        print(f"ERROR: Version bump script not found: {BUMP_SCRIPT_PATH}", file=sys.stderr)
        sys.exit(1)
    _run([sys.executable, str(BUMP_SCRIPT_PATH), new_version, "--version-files-only"], label="bump-version")


def _update_readme_tag(new_tag: str) -> None:
    """Rewrite TAG placeholders to the new release tag in README and docs."""
    paths = [README_FILE_PATH]
    if DOCS_ROOT.exists():
        paths.extend(path for path in DOCS_ROOT.rglob("*.md") if path.is_file())

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        updated_text, count = README_TAG_PATTERN.subn(f'TAG="{new_tag}"', text)
        if count:
            path.write_text(updated_text, encoding="utf-8")
            print(f"Updated TAG placeholders in {path} to {new_tag}")


def _ensure_virtualenv() -> None:
    """Ensure release is running inside a virtual environment."""
    if os.environ.get("VIRTUAL_ENV"):
        return
    if getattr(sys, "base_prefix", sys.prefix) != sys.prefix:
        return
    print("ERROR: Release must run inside a Python virtual environment.", file=sys.stderr)
    print("Suggested setup:", file=sys.stderr)
    print("  python3 -m venv .venv && . .venv/bin/activate && python -m pip install -e '.[dev]'", file=sys.stderr)
    sys.exit(1)


def _run_tests(skip_tests: bool) -> None:
    """Run pytest unless skipped."""
    if skip_tests:
        _print_status("Tests", "skip")
        return
    result = _run([sys.executable, "-m", "pytest"], check=False, label="pytest")
    if result.returncode != 0:
        print("ERROR: pytest failed. Aborting release.", file=sys.stderr)
        _print_status("Tests", "fail")
        sys.exit(result.returncode)
    _print_status("Tests", "pass")


def _run_ruff(skip_ruff: bool) -> None:
    """Run Ruff unless skipped."""
    if skip_ruff:
        _print_status("Ruff", "skip")
        return
    result = _run([sys.executable, "-m", "ruff", "check", "."], check=False, label="ruff")
    if result.returncode != 0:
        print("ERROR: Ruff failed. Aborting release.", file=sys.stderr)
        _print_status("Ruff", "fail")
        sys.exit(result.returncode)
    _print_status("Ruff", "pass")


def _run_build(skip_build: bool) -> None:
    """Run python -m build unless skipped."""
    if skip_build:
        _print_status("Build", "skip")
        return
    result = _run([sys.executable, "-m", "build"], check=False, label="build")
    if result.returncode != 0:
        print("ERROR: build failed. Aborting release.", file=sys.stderr)
        _print_status("Build", "fail")
        sys.exit(result.returncode)
    _print_status("Build", "pass")


def _run_version_check() -> None:
    """Run the release version consistency check."""
    result = _run([sys.executable, "tools/release/check_version.py"], check=False, label="check-version")
    if result.returncode != 0:
        print(result.stdout or "", end="")
        print(result.stderr or "", end="", file=sys.stderr)
        _print_status("Version check", "fail")
        sys.exit(result.returncode)
    _print_status("Version check", "pass")


def _commit_version_bump(new_version: str) -> None:
    """Commit version bump files."""
    _run(["git", "add", str(PYPROJECT_FILE_PATH), str(README_FILE_PATH), str(DOCS_ROOT)], label="git-add")
    _run(["git", "commit", "-m", f"Release {new_version}"], label="git-commit")


def _create_tag(new_version: str, tag_prefix: str, tag_suffix: str = "") -> str:
    """Create an annotated git tag."""
    tag_name = f"{tag_prefix}{new_version}{tag_suffix}"
    _run(["git", "tag", "-a", tag_name, "-m", f"Release {new_version}"], label="git-tag")
    return tag_name


def _push_branch_and_tag(branch: str, tag_name: str) -> None:
    """Push release branch and tag."""
    _run(["git", "push", "origin", branch], label="git-push-branch")
    _run(["git", "push", "origin", tag_name], label="git-push-tag")


def _build_parser() -> argparse.ArgumentParser:
    """Build the release CLI parser."""
    parser = argparse.ArgumentParser(description="Automate a RouterShell release.")
    parser.add_argument("--version", help="Explicit release version in MAJOR.MINOR.PATCH format.")
    parser.add_argument("--next", choices=["major", "minor", "patch"], help="Compute the next version.")
    parser.add_argument("--branch", default="main", help="Branch to release from.")
    parser.add_argument("--tag-prefix", default="v", help="Prefix for git tags.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest.")
    parser.add_argument("--skip-ruff", action="store_true", help="Skip Ruff.")
    parser.add_argument("--skip-build", action="store_true", help="Skip python -m build.")
    parser.add_argument("--test-release", action="store_true", help="Run checks and restore previous version.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without modifying files.")
    parser.add_argument("--last-commit-report", action="store_true", help="Generate a report for HEAD~1.")
    parser.add_argument("--latest-commit-report", action="store_true", help="Generate a report for HEAD.")
    return parser


def main() -> None:
    """Run RouterShell release automation."""
    _ensure_git_repo()
    args = _build_parser().parse_args()

    if args.last_commit_report and args.latest_commit_report:
        print("ERROR: report modes cannot be combined.", file=sys.stderr)
        sys.exit(1)

    current_branch = _get_current_branch()
    if args.last_commit_report or args.latest_commit_report:
        target_commit = _get_previous_commit() if args.last_commit_report else _get_head_commit()
        if not target_commit:
            print("ERROR: unable to resolve report commit.", file=sys.stderr)
            sys.exit(1)
        version = _read_pyproject_version()
        mode = "last-commit" if args.last_commit_report else "latest-commit"
        report_path = _write_release_report(target_commit, version, "n/a", current_branch, mode)
        print(f"Commit report saved to {report_path}")
        return

    current_version = _read_pyproject_version()

    if args.version and args.next:
        print("ERROR: --version and --next cannot be used together.", file=sys.stderr)
        sys.exit(1)

    new_version = args.version if args.version else _compute_next_version(current_version, args.next or "patch")
    _validate_version_string(new_version)
    if new_version == current_version:
        print(f"No change: version is already {current_version}.")
        return

    release_tag = f"{args.tag_prefix}{new_version}"
    if args.dry_run:
        print("Dry run: the following actions would be performed:")
        print("  1) Ensure git working tree is clean")
        print(f"  2) Update version {current_version} -> {new_version}")
        print(f"  3) Update README/doc TAG placeholders to {release_tag}")
        print("  4) Run version check")
        if not args.skip_tests:
            print("  5) Run pytest")
        if not args.skip_ruff:
            print("  6) Run Ruff")
        if not args.skip_build:
            print("  7) Build distribution artifacts")
        if args.test_release:
            print(f"  8) Restore version files back to {current_version}")
        else:
            print(f"  8) Commit version bump, tag {release_tag}, and push")
        return

    _ensure_release_branch_allowed()
    if args.branch != current_branch:
        print(
            f"ERROR: --branch must match the current branch ({current_branch}); got {args.branch}.",
            file=sys.stderr,
        )
        sys.exit(1)
    _ensure_virtualenv()
    _init_release_logging()
    _ensure_clean_worktree()

    print(f"Current version: {current_version}")
    print(f"Planned version: {new_version}")
    answer = input("Proceed with release? [y/N]: ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted.")
        sys.exit(1)

    report_commit = _get_head_commit()
    _update_version_files(new_version)
    _update_readme_tag(release_tag)
    _run_version_check()
    _run_tests(args.skip_tests)
    _run_ruff(args.skip_ruff)
    _run_build(args.skip_build)

    if args.test_release:
        print("Restoring version files after test release.")
        _update_version_files(current_version)
        _update_readme_tag(f"{args.tag_prefix}{current_version}")
        _print_status("Commit", "skip")
        _print_status("Tag", "skip")
        _print_status("Push", "skip")
        return

    _commit_version_bump(new_version)
    tag_name = _create_tag(new_version, args.tag_prefix)
    _push_branch_and_tag(args.branch, tag_name)
    _print_status("Release report", "pass")
    report_path = _write_release_report(report_commit, new_version, tag_name, args.branch, "release")
    print(f"Release report saved to {report_path}")
    print(f"Release {new_version} completed on branch '{args.branch}' with tag '{tag_name}'.")


if __name__ == "__main__":
    main()

# FILE: tools/release/test-runner.py
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""RouterShell unittest discovery runner."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TestResult:
    """Container for individual test file results."""

    file_path: str
    tests_run: int
    failures: int
    errors: int
    skipped: int
    success: bool
    duration: float


@dataclass
class TestSummary:
    """Container for overall test execution summary."""

    total_files: int
    successful_files: int
    failed_files: int
    total_tests: int
    total_failures: int
    total_errors: int
    total_skipped: int
    total_duration: float
    results: list[TestResult]


class RouterShellTestRunner:
    """Discover and run unittest-compatible tests."""

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser."""
        parser = argparse.ArgumentParser(description="Run RouterShell unittest tests.")
        parser.add_argument("--tests-dir", default="tests", help="Directory containing tests.")
        parser.add_argument("--pattern", default="test_*.py", help="Test file pattern.")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
        parser.add_argument("--failfast", action="store_true", help="Stop on first failure.")
        parser.add_argument("--json-report", action="store_true", help="Write a JSON report.")
        parser.add_argument("--output-dir", default="test_reports", help="Report output directory.")
        return parser

    @staticmethod
    def _discover(tests_dir: Path, pattern: str) -> list[Path]:
        """Discover test files."""
        if not tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {tests_dir}")
        return sorted(tests_dir.rglob(pattern))

    @staticmethod
    def _run_file(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run tests from one file."""
        start = time.time()
        loader = unittest.TestLoader()
        suite = loader.discover(str(path.parent), pattern=path.name)
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1, failfast=failfast)
        result = runner.run(suite)
        tests_run = result.testsRun
        errors = len(result.errors)
        failures = len(result.failures)

        if tests_run == 0:
            function_result = RouterShellTestRunner._run_function_tests(path, verbose, failfast)
            tests_run = function_result.tests_run
            errors = errors + function_result.errors
            failures = failures + function_result.failures

        return TestResult(
            file_path=str(path),
            tests_run=tests_run,
            failures=failures,
            errors=errors,
            skipped=len(result.skipped),
            success=failures == 0 and errors == 0,
            duration=time.time() - start,
        )

    @staticmethod
    def _run_function_tests(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run pytest-style module-level test functions without pytest."""
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            return TestResult(str(path), 0, 0, 1, 0, False, 0.0)

        module = importlib.util.module_from_spec(spec)
        project_root = Path.cwd()
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path = original_path

        functions = [
            value
            for name, value in vars(module).items()
            if name.startswith("test_") and callable(value)
        ]
        failures = 0
        errors = 0
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        for function in functions:
            try:
                function()
                if verbose:
                    print(f"PASS {function.__name__}")
            except AssertionError:
                failures = failures + 1
                traceback.print_exc()
                if failfast:
                    break
            except Exception:
                errors = errors + 1
                traceback.print_exc()
                if failfast:
                    break
        sys.path = original_path

        return TestResult(
            file_path=str(path),
            tests_run=len(functions),
            failures=failures,
            errors=errors,
            skipped=0,
            success=failures == 0 and errors == 0,
            duration=0.0,
        )

    @staticmethod
    def _write_json(summary: TestSummary, output_dir: Path) -> None:
        """Write a JSON test report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "summary": {
                "total_files": summary.total_files,
                "successful_files": summary.successful_files,
                "failed_files": summary.failed_files,
                "total_tests": summary.total_tests,
                "total_failures": summary.total_failures,
                "total_errors": summary.total_errors,
                "total_skipped": summary.total_skipped,
                "total_duration": summary.total_duration,
            },
            "results": [result.__dict__ for result in summary.results],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON report generated: {output_path}")

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Run discovered tests and return a process status."""
        tests_dir = Path(options.tests_dir)
        start = time.time()
        test_files = RouterShellTestRunner._discover(tests_dir, options.pattern)
        if not test_files:
            print(f"No test files found matching {options.pattern!r} in {tests_dir}.")
            return 1

        results: list[TestResult] = []
        for path in test_files:
            print(f"Running {path}...")
            result = RouterShellTestRunner._run_file(path, options.verbose, options.failfast)
            results.append(result)
            if options.failfast and not result.success:
                break

        summary = TestSummary(
            total_files=len(results),
            successful_files=sum(1 for result in results if result.success),
            failed_files=sum(1 for result in results if not result.success),
            total_tests=sum(result.tests_run for result in results),
            total_failures=sum(result.failures for result in results),
            total_errors=sum(result.errors for result in results),
            total_skipped=sum(result.skipped for result in results),
            total_duration=time.time() - start,
            results=results,
        )

        print("\nTest summary")
        print(f"Files: {summary.successful_files}/{summary.total_files} passed")
        passed_tests = summary.total_tests - summary.total_failures - summary.total_errors
        print(f"Tests: {passed_tests}/{summary.total_tests} passed")
        print(f"Failures: {summary.total_failures}")
        print(f"Errors: {summary.total_errors}")
        print(f"Skipped: {summary.total_skipped}")
        print(f"Duration: {summary.total_duration:.3f}s")

        if options.json_report:
            RouterShellTestRunner._write_json(summary, Path(options.output_dir))

        return 0 if summary.failed_files == 0 else 1


def main() -> int:
    """Run the RouterShell unittest runner."""
    parser = RouterShellTestRunner._build_parser()
    try:
        return RouterShellTestRunner.run(parser.parse_args())
    except KeyboardInterrupt:
        print("Test execution interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

# FILE: tools/support/bump_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""Inspect or update the RouterShell project version."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

import tomllib

PYPROJECT_FILE_PATH: Final[Path] = Path("pyproject.toml")
DOC_TAG_ROOT: Final[Path] = Path("doc")
VERSION_PART_SEPARATOR: Final[str] = "."
EXPECTED_VERSION_PARTS: Final[int] = 3
MAJOR_INDEX: Final[int] = 0
MINOR_INDEX: Final[int] = 1
PATCH_INDEX: Final[int] = 2
TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r'TAG="v\d+\.\d+\.\d+(?:-rc\d+)?"')


def _validate_version_string(version: str) -> None:
    """Validate that the version string matches MAJOR.MINOR.PATCH."""
    core_version = version.split("-rc", 1)[0]
    parts = core_version.split(VERSION_PART_SEPARATOR)
    if len(parts) != EXPECTED_VERSION_PARTS or not all(part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'. Expected MAJOR.MINOR.PATCH.", file=sys.stderr)
        sys.exit(1)


def _read_current_version(pyproject_file: Path) -> str:
    """Read the current version from pyproject.toml."""
    if not pyproject_file.exists():
        print(f"ERROR: pyproject.toml not found: {pyproject_file}", file=sys.stderr)
        sys.exit(1)

    with pyproject_file.open("rb") as handle:
        pyproject = tomllib.load(handle)

    project = pyproject.get("project", {})
    version = project.get("version", "")
    if not isinstance(version, str) or not version:
        print(f"ERROR: Could not find [project].version in {pyproject_file}.", file=sys.stderr)
        sys.exit(1)
    return version


def _write_new_pyproject_version(pyproject_file: Path, new_version: str) -> None:
    """Write the new version into pyproject.toml [project].version."""
    if not pyproject_file.exists():
        print(f"ERROR: pyproject.toml not found: {pyproject_file}", file=sys.stderr)
        sys.exit(1)

    text = pyproject_file.read_text(encoding="utf-8")
    updated_text, count = re.subn(
        r'^(\s*version\s*=\s*)"[^"]+"',
        rf'\g<1>"{new_version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        print(f"ERROR: Could not replace [project].version in {pyproject_file}.", file=sys.stderr)
        sys.exit(1)
    pyproject_file.write_text(updated_text, encoding="utf-8")


def _update_tag_tokens(tag: str) -> None:
    """Rewrite TAG=\"vX.Y.Z\" occurrences in README and doc/*.md files."""
    paths = [Path("README.md")]
    if DOC_TAG_ROOT.exists():
        paths.extend(path for path in DOC_TAG_ROOT.rglob("*.md") if path.is_file())

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        updated_text, count = TAG_PATTERN.subn(f'TAG="{tag}"', text)
        if count:
            path.write_text(updated_text, encoding="utf-8")


def _compute_next_version(current_version: str, mode: str) -> str:
    """Compute the next version by incrementing the requested component."""
    _validate_version_string(current_version)
    parts = [int(part) for part in current_version.split("-rc", 1)[0].split(VERSION_PART_SEPARATOR)]

    match mode:
        case "major":
            parts[MAJOR_INDEX] = parts[MAJOR_INDEX] + 1
            parts[MINOR_INDEX] = 0
            parts[PATCH_INDEX] = 0
        case "minor":
            parts[MINOR_INDEX] = parts[MINOR_INDEX] + 1
            parts[PATCH_INDEX] = 0
        case "patch":
            parts[PATCH_INDEX] = parts[PATCH_INDEX] + 1
        case _:
            print(f"ERROR: Unsupported --next mode '{mode}'.", file=sys.stderr)
            sys.exit(1)

    return VERSION_PART_SEPARATOR.join(str(part) for part in parts)


def main() -> None:
    """CLI entry point for inspecting or updating the RouterShell version."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or update the [project].version field in pyproject.toml. "
            "Version format: MAJOR.MINOR.PATCH."
        )
    )
    parser.add_argument("version", nargs="?", help="Explicit version to set, e.g. 0.2.0.")
    parser.add_argument("--current", action="store_true", help="Show the current version and exit.")
    parser.add_argument("--next", choices=["major", "minor", "patch"], help="Compute and apply the next version.")
    parser.add_argument(
        "--version-files-only",
        action="store_true",
        help="Update only version files; skip README/doc tag rewrites.",
    )

    args = parser.parse_args()

    if args.current:
        if args.version is not None or args.next is not None:
            print("ERROR: --current cannot be combined with a version argument or --next.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(PYPROJECT_FILE_PATH)
        print(f"Current version: {current}")
        sys.exit(0)

    if args.next is not None:
        if args.version is not None:
            print("ERROR: --next cannot be combined with an explicit version argument.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(PYPROJECT_FILE_PATH)
        new_version = _compute_next_version(current, args.next)
    elif args.version is not None:
        current = _read_current_version(PYPROJECT_FILE_PATH)
        new_version = args.version
        _validate_version_string(new_version)
    else:
        print("ERROR: You must specify --current, --next <mode>, or an explicit version.", file=sys.stderr)
        sys.exit(1)

    if current == new_version:
        print(f"No change: version is already {current}.")
        sys.exit(0)

    _write_new_pyproject_version(PYPROJECT_FILE_PATH, new_version)
    if not args.version_files_only:
        _update_tag_tokens(f"v{new_version}")
    print(f"Updated version: {current} -> {new_version}")


if __name__ == "__main__":
    main()

