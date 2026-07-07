"use client"

import { useState } from "react"
import { cn } from "@/lib/cn"

export interface FichaTipo {
  nome: string
  descricao: string
  custo: string
  aula: number | null
  quando?: string
}

export interface GrupoTipos {
  nome: string
  fichas: FichaTipo[]
}

/**
 * Parser do bloco ```tipos.
 *
 * Sintaxe (parser linha a linha, mesmo espírito do ```flow):
 *   ## Nome do grupo
 *   - Nome | descrição do que é | custo | aula: N
 *     > quando: texto de "quando usar" (linha opcional sob o item)
 *
 * O grupo "Elo" é renderizado fora dos três grupos de fundação (fiel ao
 * conteúdo: viga baldrame não é um tipo de fundação, é o elo do sistema).
 */
export function parseTipos(raw: string): GrupoTipos[] {
  const grupos: GrupoTipos[] = []
  let grupoAtual: GrupoTipos | null = null

  for (const linhaBruta of raw.split("\n")) {
    const linha = linhaBruta.trim()
    if (!linha) continue

    if (linha.startsWith("## ")) {
      grupoAtual = { nome: linha.slice(3).trim(), fichas: [] }
      grupos.push(grupoAtual)
      continue
    }

    if (linha.startsWith("> ")) {
      // Linha "quando usar" — anexa à última ficha do grupo atual.
      const fichas = grupoAtual?.fichas
      if (fichas && fichas.length > 0) {
        const texto = linha.slice(2).replace(/^quando:\s*/i, "").trim()
        fichas[fichas.length - 1].quando = texto
      }
      continue
    }

    if (linha.startsWith("- ")) {
      if (!grupoAtual) continue
      const partes = linha
        .slice(2)
        .split("|")
        .map((p) => p.trim())
      const [nome = "", descricao = "", custo = "", aulaCampo = ""] = partes
      const aulaMatch = aulaCampo.match(/(\d+)/)
      grupoAtual.fichas.push({
        nome,
        descricao,
        custo,
        aula: aulaMatch ? parseInt(aulaMatch[1], 10) : null,
      })
    }
  }

  return grupos
}

function Ficha({ ficha }: { ficha: FichaTipo }) {
  const [aberta, setAberta] = useState(false)

  return (
    <div
      className={cn(
        "border border-stone rounded-md bg-white transition-colors",
        aberta && "border-sand",
      )}
    >
      <button
        type="button"
        onClick={() => setAberta((v) => !v)}
        aria-expanded={aberta}
        className="w-full flex items-start justify-between gap-3 px-4 py-3 text-left hover:bg-[var(--color-bg-soft)] transition-colors rounded-md"
      >
        <span className="font-sans text-[14px] md:text-[15px] font-semibold text-coal leading-tight">
          {ficha.nome}
        </span>
        <span className="flex-shrink-0 flex items-center gap-2">
          <span className="font-ui text-[11px] tracking-wide text-green tabular-nums">
            {ficha.custo}
          </span>
          {ficha.aula != null && (
            <span className="font-ui text-[10px] uppercase tracking-[0.1em] text-sand">
              a{ficha.aula}
            </span>
          )}
          <span
            className={cn(
              "text-green text-sm transition-transform leading-none",
              aberta && "rotate-90",
            )}
            aria-hidden
          >
            ›
          </span>
        </span>
      </button>
      {aberta && (
        <div className="px-4 pb-4 pt-1 border-t border-stone/60 mt-1">
          <p className="text-[14px] text-coal/85 leading-relaxed">
            {ficha.descricao}
          </p>
          {ficha.quando && (
            <p className="text-[13px] text-coal/70 leading-relaxed mt-2">
              <span className="font-ui text-[10px] uppercase tracking-[0.1em] text-sand mr-1">
                Quando
              </span>
              {ficha.quando}
            </p>
          )}
          {ficha.aula != null && (
            <a
              href={`#aula-${ficha.aula}`}
              className="inline-block mt-3 font-ui text-[11px] uppercase tracking-[0.1em] text-green hover:text-coal underline underline-offset-2 decoration-green/40 hover:decoration-coal/40 transition-colors"
            >
              Aula {ficha.aula} →
            </a>
          )}
        </div>
      )}
    </div>
  )
}

function GrupoColuna({ grupo }: { grupo: GrupoTipos }) {
  return (
    <div className="space-y-2">
      <div className="font-ui text-[11px] font-semibold uppercase tracking-[0.14em] text-coal/70 mb-1">
        {grupo.nome}
      </div>
      {grupo.fichas.map((ficha, i) => (
        <Ficha key={i} ficha={ficha} />
      ))}
    </div>
  )
}

export function MapaTipos({ raw }: { raw: string }) {
  // Parse feito aqui dentro (não no Markdown server component): parseTipos
  // vive num módulo "use client" e não pode ser invocado do servidor.
  const grupos = parseTipos(raw)
  if (grupos.length === 0) return null

  const principais = grupos.filter((g) => g.nome.toLowerCase() !== "elo")
  const elo = grupos.find((g) => g.nome.toLowerCase() === "elo")

  return (
    <div className="my-8">
      <div className="grid gap-5 md:grid-cols-3 md:gap-4">
        {principais.map((grupo, i) => (
          <GrupoColuna key={i} grupo={grupo} />
        ))}
      </div>

      {elo && elo.fichas.length > 0 && (
        <div className="mt-6 pt-6 border-t border-dashed border-stone">
          <div className="font-ui text-[10px] font-semibold uppercase tracking-[0.16em] text-sand mb-2">
            Elo do sistema
          </div>
          <div className="md:max-w-sm">
            {elo.fichas.map((ficha, i) => (
              <Ficha key={i} ficha={ficha} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
