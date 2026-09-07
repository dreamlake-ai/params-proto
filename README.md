# params-proto documentation builds

Immutable output archives for the DreamLake Dockit site. These are documentation builds, not Python package releases.

Each ZIP includes the complete prerendered site, browser assets, search index, Markdown exports, and version menu. The SHA256 sidecar verifies its bytes; deploy JSON records the matching Netlify deploy and source commit. Restore by extracting the ZIP and deploying it as a static site.

Initial production URL: https://params-proto.dreamlake.ai
Existing-version branch URL: https://v3-3-0--params-proto-dreamlake.netlify.app

Keep old archives when appending new builds. Original Sphinx and historical sources are separately saved in the docs/archive-originals branch.
