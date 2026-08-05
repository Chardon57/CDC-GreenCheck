import { useEffect } from 'react'

function TitrePage({ titre }: { titre: string }) {
  useEffect(() => {
    document.title = titre ? `GreenCheck - ${titre}` : 'GreenCheck'
  }, [titre])

  return null   // ne rend rien dans le DOM
}

export default TitrePage