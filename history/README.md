# Historical documentation inventory

Captured 2026-09-07 from the original Git repository, PyPI JSON API, and Read the Docs public API. `versions.json` records 129 distinct releases: 88 version tags plus 41 additional PyPI versions. `latest` and `stable` are aliases and are not releases.

- Tagged releases retain their exact original commit and a Git source archive.
- Untagged PyPI releases retain their published pure-Python wheel, verified against PyPI SHA256. These are distribution snapshots, not invented Git commits. All 41 are wheel-only releases; no source distribution is published.
- 52 early version tags have no `docs/` directory. Future migration should use the version's own README and Python source. It must not backfill current documentation and present it as historical content.
- Intended branch names are `v<version>` (for example `v3.0.0-rc8`). No historical branches or new package releases were published in this initial iteration.

`readthedocs-versions.json` lists 92 RTD version entries. Sixteen report existing builds (14 version tags plus latest/stable). `readthedocs-builds.json` preserves the 76 build metadata records exposed by the API. `original-builds.json` records original documentation links, download attempts, and preservation status. The API reports these versions as built, but rendered pages and HTML ZIP downloads returned HTTP 403 during capture. These original rendered bytes are **not preserved**. Keep the existing RTD project intact until an authorized export becomes available. Links may remain useful in a normal browser but were not verified accessible here.

`local-builds.json` records any local Sphinx `_build` archives; an empty array means no local built output was found.

Reproduce the inventory and source snapshots with:

```sh
python3 scripts/archive_doc_history.py --output history --artifacts /tmp/params-proto-history-artifacts
```

The artifacts directory also contains `original-repository.bundle` (all locally available refs at capture), and `SHA256SUMS`. Upload the aggregate archive as a durable GitHub release asset; this preserves sources and build metadata, while the manifest explicitly distinguishes unavailable original rendered builds. Each future generated documentation build should be saved separately with its source commit/distribution SHA256 and generated archive SHA256 before replacing a live alias.
