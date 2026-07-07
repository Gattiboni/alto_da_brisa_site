"use client"

import { useEffect } from "react"

/**
 * Regra da âncora (wireframe §2): navegar para `#aula-N` de uma aula
 * colapsada **abre** a aula antes de rolar. O `<details>` nativo não faz
 * isso sozinho — este componente escuta `hashchange` e o `load` inicial,
 * abre o `<details>` alvo e rola até ele.
 *
 * Sem persistência: recarregou, tudo volta ao default (aberto).
 */
export function AulaAnchorOpener() {
  useEffect(() => {
    const abrirAlvo = () => {
      const hash = decodeURIComponent(window.location.hash)
      if (!/^#aula-\d+$/.test(hash)) return
      const alvo = document.getElementById(hash.slice(1))
      if (!alvo) return
      if (alvo instanceof HTMLDetailsElement && !alvo.open) {
        alvo.open = true
      }
      // Rola após abrir — o salto nativo pode ter ocorrido antes da
      // expansão; scroll-margin-top (scroll-mt) é respeitado.
      requestAnimationFrame(() => {
        alvo.scrollIntoView({ block: "start" })
      })
    }

    abrirAlvo()
    window.addEventListener("hashchange", abrirAlvo)
    return () => window.removeEventListener("hashchange", abrirAlvo)
  }, [])

  return null
}
