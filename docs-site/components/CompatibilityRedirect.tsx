import { useEffect } from 'react'

// URL fragments never reach Netlify. Resolve bookmarks from the former
// combined page in the browser, keeping the exact symbol anchor.
const destinations: Record<string, string> = {
  "params_proto.v1": "v1-configuration",
  "params_proto.v1.params_proto": "v1-configuration",
  "params_proto.v1.hyper": "v1-sweeps",
  "params_proto.v2": "v2-configuration",
  "params_proto.v2.proto": "v2-configuration",
  "params_proto.v2.hyper": "v2-sweeps",
  "params_proto.v2.partial": "v2-helpers",
  "params_proto.v2.utils": "v2-helpers"
}

export function CompatibilityRedirect() {
  useEffect(() => {
    function followBookmark() {
      let fragment: string
      try { fragment = decodeURIComponent(window.location.hash.slice(1)) }
      catch { return }
      const module = fragment.split('--')[0]
      const page = destinations[module]
      if (page) window.location.replace(`/reference/compatibility/${page}#${encodeURIComponent(fragment)}`)
    }
    followBookmark()
    window.addEventListener('hashchange', followBookmark)
    return () => window.removeEventListener('hashchange', followBookmark)
  }, [])
  return null
}
