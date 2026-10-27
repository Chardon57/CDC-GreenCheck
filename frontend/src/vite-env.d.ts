
/// <reference types="vite/client" />

// Variables définies dans frontend/.env (toujours des textes ; le préfixe VITE_ est obligatoire)
interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_USE_MOCK?: string
}

declare module '*.svg?react' {
  import type { FunctionComponent, SVGProps } from 'react'
  const ReactComponent: FunctionComponent<SVGProps<SVGSVGElement>>
  export default ReactComponent
}

declare module '*.css' {
  const content: Record<string, string>
  export default content
}