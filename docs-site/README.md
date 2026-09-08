# params-proto documentation

The site has Guides and API Reference tabs. The API overview is handwritten;
`api-pages.json` groups Python modules into five generated topic pages.
Classes, methods, and functions remain sections within those pages.

To regenerate, install the reviewed `dreamlake-autodoc-py` source revision
recorded in `autodoc-requirements.txt`, then run from the repository root:

```sh
uv run --with-requirements docs-site/autodoc-requirements.txt scripts/generate_api_docs.py
cd docs-site
pnpm install --frozen-lockfile
pnpm build
```

The generator owns only files in `pages/reference/.autodoc-py.json`; it
preserves the handwritten overview. `public/_redirects` preserves old module
URLs. `api-route-migrations.json` records the original module/symbol mapping.
The package version and generator revision are independent.

Compatibility references live under their own sidebar section. `api-pages.json` groups them by version and task; `compatibility-overview.mdx` supplies the landing page. `CompatibilityRedirect` preserves symbol bookmarks from the previous combined page. Run the generation script before building.
