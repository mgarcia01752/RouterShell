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
