#!/usr/bin/env python3
"""Convert checked-in MyST documentation (or historical README) to Dockit MDX.

Never imports historical Python packages or changes the original documentation.
"""
import argparse
import json
import posixpath
import re
from pathlib import Path


def convert(text, rel, known, version):
    text = text.replace('{VERSION}', version)
    def directive(m):
        kind, body = m.group(1), m.group(2)
        body = re.sub(r'^:[\w_-]+:.*\n?', '', body, flags=re.M).strip()
        if kind == 'toctree':
            links = []
            for line in body.splitlines():
                line = line.strip()
                if not line: continue
                pair = re.match(r'(.*?)\s*<(.+)>$', line)
                label, target = pair.groups() if pair else (line.split('/')[-1].replace('_', ' ').replace('-', ' ').title(), line)
                dest = posixpath.normpath(posixpath.join(str(rel.parent), target))
                if dest in known: links.append(f'- [{label}]({route(dest)})')
            return '\n'.join(links)
        if kind in ('note', 'warning', 'tip', 'important', 'admonition'):
            return '\n'.join('> '+line for line in (f'**{kind.title()}**\n\n'+body).splitlines())
        if kind == 'eval-rst':
            names = re.findall(r'\.\. auto(?:class|function|module)::\s*(\S+)', body)
            return '\n'.join(f'- `{name}` — see the [generated API reference](/reference).' for name in names)
        if kind == 'ansi-block':
            body = re.sub(r'(?:\\x1b|\x1b)\[[0-9;]*m', '', body)
            return f'```text\n{body}\n```'
        return f'```text\n{body}\n```'
    text = re.sub(r'^```\{([^}]+)\}[^\n]*\n(.*?)^```\s*$', directive, text, flags=re.M|re.S)
    # Escape MDX syntax only in prose; retain Python and shell examples verbatim.
    parts = re.split(r'(^[ \t]*```[^\n]*\n.*?^[ \t]*```\s*$)', text, flags=re.M|re.S)
    for i in range(0, len(parts), 2):
        s = parts[i]
        def link(m):
            label, target = m.groups()
            if '://' in target or target.startswith(('#','mailto:', '/')): return m.group()
            p, sep, anchor = target.partition('#')
            p = re.sub(r'\.(md|rst|html)$', '', p)
            resolved = posixpath.normpath(posixpath.join(str(rel.parent), p))
            aliases = {'key_concepts/configuration_basics':'key_concepts/configuration-patterns','key_concepts/types':'key_concepts/type-system','api/hyper':'key_concepts/hyperparameter_sweeps','api/utils':'reference'}
            resolved = aliases.get(resolved, resolved)
            if resolved in known or resolved == 'reference': return f'[{label}]({route(resolved)}{sep}{anchor})'
            return f'`{label}`'
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, s)
        s = re.sub(r'\{(?:doc|ref)\}`([^`]+)`', lambda m: '`'+m.group(1)+'`', s)
        inline = re.split(r'(`+[^`]*`+)', s)
        for j in range(0,len(inline),2):
            inline[j] = inline[j].replace('<br>', '<br />')
            inline[j] = re.sub(r'<(?!br\s*/>)([^>]+)>', r'&lt;\1&gt;', inline[j])
            inline[j] = inline[j].replace('{','&#123;').replace('}','&#125;')
        parts[i] = ''.join(inline)
    return ''.join(parts)


def route(slug):
    return '/' if slug == 'index' else '/' + re.sub(r'/index$', '', slug)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--version', required=True)
    args = p.parse_args()
    root = args.source
    docs = root/'docs' if (root/'docs').is_dir() else root
    files = sorted(f for f in docs.rglob('*.md') if not any(x.startswith('_') for x in f.relative_to(docs).parts))
    if not files:
        files = [f for f in (root/'README.md',root/'README.rst',root/'README') if f.is_file()][:1]
        docs = root
    known = {str(f.relative_to(docs).with_suffix('')) for f in files}
    manifest=[]
    for order,f in enumerate(files):
        rel=f.relative_to(docs)
        slug=str(rel.with_suffix(''))
        if len(files)==1 and f.name.startswith('README'): slug='index'
        text=f.read_text()
        title_match=re.search(r'^# (.+)',text,re.M)
        title=title_match.group(1).replace('`','') if title_match else f.stem.replace('_',' ').title()
        if slug=='index': title='Introduction'
        section={'key_concepts':'Key concepts','examples':'Examples','api':'API reference'}.get(rel.parts[0], 'Release history' if 'release' in slug else 'Getting started')
        out=args.output/('api' if slug=='api/index' else slug)/'+Page.mdx'; out.parent.mkdir(parents=True,exist_ok=True)
        content=convert(text,rel,known,args.version)
        front={'title':title,'section':section,'order':0 if slug=='index' else order+1,'description':f'{title} — params-proto {args.version} documentation.'}
        out.write_text('---\n'+''.join(f'{k}: {json.dumps(v)}\n' for k,v in front.items())+'---\n\n'+content)
        manifest.append({'source':str(rel),'route':route(slug)})
    print(json.dumps({'version':args.version,'pages':manifest},indent=2))
if __name__=='__main__': main()
