
/// <reference types="vite/client" />

declare module '*.svg?react' {
  import type { FunctionComponent, SVGProps } from 'react'
  const ReactComponent: FunctionComponent<SVGProps<SVGSVGElement>>
  export default ReactComponent
}

declare module '*.css' {
  const content: Record<string, string>
  export default content
}