import { initDocs } from '@dreamlake/dockit'
initDocs({
  site: {
    brand: 'params-proto', subtitle: 'Documentation',
    repoUrl: 'https://github.com/dreamlake-ai/params-proto',
    docsRepoUrl: 'https://github.com/dreamlake-ai/params-proto',
    docsBranch: __DOCS_BRANCH__, docsPagesPath: 'docs-site/pages',
    breadcrumbRoot: 'params-proto', url: 'https://params-proto.dreamlake.ai',
    summary: 'Declarative Python configuration, command-line interfaces, and parameter sweeps.',
    versionChips: [{label: 'params-proto', version: __DOCS_VERSION__, dropdown: true}],
    themeToggle: 'segmented',
  },
  pages: import.meta.glob('./pages/**/+Page.mdx', {eager: true}),
  rawPages: import.meta.glob('./pages/**/+Page.mdx', {eager: true, query: '?raw', import: 'default'}),
  sectionOrder: ['Getting started', 'Key concepts', 'Examples', 'API reference', 'Release history'],
  tabs: [],
})
