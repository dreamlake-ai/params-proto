# Documentation deployment

This is a docs-only migration of the existing params-proto 3.3.0 source. It does not create a Python package release or modify any upstream tags.

Production: https://params-proto.dreamlake.ai
Netlify project: `params-proto-dreamlake` (`8714f50c-d823-4eff-b674-701225f78bf7`).

Build from the repository root:

```sh
cd docs-site
pnpm install --frozen-lockfile
pnpm build
cd ..
```

Deploy the verified build to a real version branch, then promote it to production:

```sh
python3 scripts/deploy_docs.py --branch v3.3.0 --production
```

Omit `--production` to publish only the branch preview. The script uses `NETLIFY_AUTH_TOKEN` or an existing Netlify CLI login. It archives every output ZIP with a timestamp and SHA256, verifies the resulting Netlify context is `branch-deploy`, then records the deploy ID. Keep these ZIPs in the `docs/archive-builds` Git branch (or another durable artifact store) after each production update. Netlify preserves the latest successful deployment for each branch; older deploy IDs alone are not a permanent backup.

Current source is on the fork's `main`; the existing-version documentation snapshot is on branch `v3.3.0`. The matching upstream Git tag remains unchanged. Historical versions link to their existing RTD builds for this initial iteration. Full historical conversion and any new package releases are deferred until the setup stabilizes.

Original documentation and sources are preserved on [`docs/archive-originals`](https://github.com/dreamlake-ai/params-proto/tree/docs/archive-originals). Its README explains restoration and checksums. `history/` records exactly which originals were available; RTD build metadata does not imply its rendered HTML was downloaded.

Deployment is explicitly performed by the verified command above. Automatic Git builds are paused for this initial iteration: repository checkout succeeds, but the cloud build failed during prerendering without a useful final error in the available log. The production build was built and checked locally, archived, then uploaded as a retained branch deploy. Verify cloud CI separately before re-enabling automatic publication. The Netlify repository uses a read-only deploy key; the live site remains available while automatic builds are paused.
