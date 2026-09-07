# Original params-proto documentation archive

Captured 2026-09-07 before the DreamLake Dockit migration. This is a documentation backup, not a Python package release. Existing upstream release tags are unchanged.

The archive preserves the original local Sphinx build (46 HTML pages), repository Git bundle, 88 tagged source snapshots, 41 additional hash-verified PyPI wheel snapshots, and Read the Docs version/build metadata. Historical remote RTD HTML downloads returned HTTP 403 and are explicitly recorded as unavailable.

Restore on macOS/Linux:

```sh
cat params-proto-original-history-2026-09-07.tar.gz.part* > params-proto-original-history-2026-09-07.tar.gz
shasum -a 256 -c SHA256SUMS
tar -tzf params-proto-original-history-2026-09-07.tar.gz
```

This archive is split into files under 50 MiB for Git storage. Retain this branch and the corresponding source history. Do not treat a regenerated build as the original rendered artifact.
