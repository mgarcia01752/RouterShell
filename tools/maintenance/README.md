<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell Maintenance Tools

## Cleanup

`clean.sh` removes generated local artifacts from a RouterShell workspace.
Run targeted cleanup when possible, and use `--all` only when intentionally
resetting local generated state.

```bash
tools/maintenance/clean.sh --python
tools/maintenance/clean.sh --build
tools/maintenance/clean.sh --runtime
```

Full cleanup:

```bash
tools/maintenance/clean.sh --all
```

Full cleanup preserves `tools/agent-review/*.review.md`. To also remove agent
review bundles, use:

```bash
tools/maintenance/clean.sh --all-force
```

`--all` also clears RouterShell-created Multipass VMs by delegating to:

```bash
tools/vm/multipass-cleanup.sh --all --purge
```

The cleanup script does not remove the project `.venv` during Python cache
cleanup.
