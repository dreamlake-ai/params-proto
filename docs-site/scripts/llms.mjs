import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises'
import path from 'node:path'
const links = [], bodies = []
async function walk(dir) {
  for (const item of await readdir(dir, {withFileTypes:true})) {
    const file = path.join(dir, item.name)
    if (item.isDirectory()) await walk(file)
    else if (item.name === '+Page.mdx') {
      const text = await readFile(file, 'utf8')
      const title = JSON.parse(text.match(/^title: (.+)$/m)[1])
      const slug = path.relative('pages', dir).replace(/^index$/, '')
      const target = `dist/client/${slug || 'index'}.md`
      await mkdir(path.dirname(target), {recursive:true})
      const body = text.replace(/^---\n[\s\S]*?\n---\n/, '')
      await writeFile(target, body)
      links.push(`- [${title}](https://params-proto.dreamlake.ai/${slug || 'index'}.md)`)
      bodies.push(body)
    }
  }
}
await walk('pages')
await writeFile('dist/client/llms.txt', '# params-proto\n\n> Declarative Python configuration, CLI programs, and sweeps.\n\n' + links.join('\n')+'\n')
await writeFile('dist/client/llms-full.txt', bodies.join('\n\n---\n\n'))
