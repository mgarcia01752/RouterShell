# RouterShell Support Tools

Support tools are small helpers used by release and workflow scripts.

## Version Bump

Show the current version:

```bash
./tools/support/bump_version.py --current
```

Apply the next patch version:

```bash
./tools/support/bump_version.py --next patch
```

Set an explicit version:

```bash
./tools/support/bump_version.py 0.2.0
```

Update only version files without rewriting README/doc tag placeholders:

```bash
./tools/support/bump_version.py --next patch --version-files-only
```
