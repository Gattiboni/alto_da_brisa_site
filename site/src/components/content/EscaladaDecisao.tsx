import type { CSSProperties } from "react"

export interface DegrauEscalada {
  numero: number
  nome: string
  condicao: string
  nota: string
  aula: number | null
}

/**
 * Parser do bloco ```escalada.
 *
 * Sintaxe (uma linha por degrau):
 *   N | nome | condição de subida | economia/nota | aula: N
 *
 * A sequência vai do mais barato (degrau 1) ao mais caro. O componente
 * mantém um <ol> semântico — screen reader lê 1→5 com as condições, sem
 * depender do visual diagonal (que é só CSS).
 */
export function parseEscalada(raw: string): DegrauEscalada[] {
  const degraus: DegrauEscalada[] = []

  for (const linhaBruta of raw.split("\n")) {
    const linha = linhaBruta.trim()
    if (!linha) continue

    const partes = linha.split("|").map((p) => p.trim())
    if (partes.length < 2) continue

    const numero = parseInt(partes[0], 10)
    if (Number.isNaN(numero)) continue

    const [, nome = "", condicao = "", nota = "", aulaCampo = ""] = partes
    const aulaMatch = aulaCampo.match(/(\d+)/)
    degraus.push({
      numero,
      nome,
      condicao,
      nota,
      aula: aulaMatch ? parseInt(aulaMatch[1], 10) : null,
    })
  }

  return degraus
}

export function EscaladaDecisao({ degraus }: { degraus: DegrauEscalada[] }) {
  if (degraus.length === 0) return null

  return (
    <ol className="my-8 list-none pl-0 space-y-0">
      {degraus.map((degrau, i) => (
        <li
          key={degrau.numero}
          style={{ "--step": i } as CSSProperties}
          className="md:ml-[calc(var(--step)*2.25rem)]"
        >
          {i > 0 && (
            <div
              className="flex items-center gap-2 py-2 md:ml-4 text-sand select-none"
              aria-hidden
            >
              <span className="text-[13px] leading-none">↑</span>
              <span className="font-ui text-[10px] uppercase tracking-[0.12em]">
                não passou? sobe um degrau
              </span>
            </div>
          )}
          <div className="border border-stone rounded-md bg-white px-4 py-4">
            <div className="flex items-baseline gap-3">
              <span className="font-serif text-[26px] md:text-[30px] text-green leading-none">
                {degrau.numero}
              </span>
              <span className="font-sans text-[15px] font-semibold text-coal leading-tight">
                {degrau.nome}
              </span>
              {degrau.numero === degraus[0].numero && (
                <span className="ml-auto font-ui text-[9px] font-semibold uppercase tracking-[0.14em] text-green">
                  comece aqui
                </span>
              )}
            </div>
            <p className="text-[14px] text-coal/85 leading-relaxed mt-2">
              {degrau.condicao}
            </p>
            <div className="flex items-center flex-wrap gap-x-3 gap-y-1 mt-2">
              {degrau.nota && degrau.nota !== "—" && (
                <span className="font-ui text-[11px] uppercase tracking-[0.08em] text-coal/60">
                  {degrau.nota}
                </span>
              )}
              {degrau.aula != null && (
                <a
                  href={`#aula-${degrau.aula}`}
                  className="font-ui text-[11px] uppercase tracking-[0.1em] text-green hover:text-coal underline underline-offset-2 decoration-green/40 hover:decoration-coal/40 transition-colors"
                >
                  Aula {degrau.aula} →
                </a>
              )}
            </div>
          </div>
        </li>
      ))}
    </ol>
  )
}
