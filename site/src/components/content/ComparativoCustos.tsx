import { cn } from "@/lib/cn"

export interface ItemCusto {
  rotulo: string
  valor: number
}

export interface OpcaoCusto {
  label: string
  itens: ItemCusto[]
  total: number
}

export interface DadosCustos {
  titulo: string
  a: OpcaoCusto
  b: OpcaoCusto
  punchline: string
  aula: number | null
}

/**
 * Parser do bloco ```custos.
 *
 * Sintaxe (uma diretiva por linha):
 *   titulo: ...
 *   a: <label da opção A>
 *   a.item: <rótulo> | <valor>
 *   a.total: <valor>
 *   b: <label da opção B>
 *   b.item: <rótulo> | <valor>
 *   b.total: <valor>
 *   punchline: ...
 *   aula: N
 *
 * Requisito do wireframe §5: valores vêm do markdown, nunca hardcoded.
 */
export function parseCustos(raw: string): DadosCustos | null {
  const dados: DadosCustos = {
    titulo: "",
    a: { label: "", itens: [], total: 0 },
    b: { label: "", itens: [], total: 0 },
    punchline: "",
    aula: null,
  }

  const numero = (s: string): number => {
    const m = s.match(/-?\d+(?:[.,]\d+)?/)
    return m ? parseFloat(m[0].replace(",", ".")) : 0
  }

  for (const linhaBruta of raw.split("\n")) {
    const linha = linhaBruta.trim()
    if (!linha) continue
    const sep = linha.indexOf(":")
    if (sep === -1) continue
    const chave = linha.slice(0, sep).trim()
    const valor = linha.slice(sep + 1).trim()

    switch (chave) {
      case "titulo":
        dados.titulo = valor
        break
      case "a":
        dados.a.label = valor
        break
      case "b":
        dados.b.label = valor
        break
      case "a.item":
      case "b.item": {
        const [rotulo = "", val = ""] = valor.split("|").map((p) => p.trim())
        const item = { rotulo, valor: numero(val) }
        ;(chave === "a.item" ? dados.a : dados.b).itens.push(item)
        break
      }
      case "a.total":
        dados.a.total = numero(valor)
        break
      case "b.total":
        dados.b.total = numero(valor)
        break
      case "punchline":
        dados.punchline = valor
        break
      case "aula":
        dados.aula = numero(valor) || null
        break
    }
  }

  if (!dados.a.label && !dados.b.label) return null
  return dados
}

function Barra({
  opcao,
  maxTotal,
  destaque,
}: {
  opcao: OpcaoCusto
  maxTotal: number
  destaque: boolean
}) {
  return (
    <div className="flex-1 min-w-[130px]">
      <div className="font-ui text-[11px] font-semibold uppercase tracking-[0.1em] text-coal/70 mb-2">
        {opcao.label}
      </div>
      {/* Barras: alturas proporcionais são só visuais, mas rótulo e valor
          são texto REAL no DOM em ordem lógica (§5: dado acessível sem o
          visual) — por isso NÃO usamos aria-hidden nem tabela sr-only. */}
      <div className="flex flex-col-reverse gap-px h-[240px] md:h-[260px]">
        {opcao.itens.map((item, i) => (
          <div
            key={i}
            className={cn(
              "flex flex-col justify-center items-start px-2 py-1 overflow-hidden rounded-[3px]",
              i === 0 ? "bg-green text-white" : "bg-stone text-coal",
            )}
            style={{
              height: `${(item.valor / maxTotal) * 100}%`,
            }}
          >
            <span className="text-[11px] font-medium leading-tight">
              {item.rotulo}
            </span>
            <span className="text-[11px] tabular-nums opacity-90 leading-tight">
              R$ {item.valor}/m²
            </span>
          </div>
        ))}
      </div>
      <div
        className={cn(
          "mt-2 font-ui text-[11px] uppercase tracking-[0.08em]",
          destaque ? "text-green font-semibold" : "text-coal/70",
        )}
      >
        Total R$ {opcao.total}/m²
        {destaque && <span className="ml-1" aria-hidden>▼</span>}
      </div>
    </div>
  )
}

export function ComparativoCustos({ dados }: { dados: DadosCustos }) {
  const maxTotal = Math.max(dados.a.total, dados.b.total) || 1
  const menor = dados.b.total < dados.a.total ? "b" : "a"

  return (
    <figure className="my-8">
      {dados.titulo && (
        <figcaption className="font-serif text-lg md:text-xl text-coal mb-4">
          “{dados.titulo}”
        </figcaption>
      )}

      <div className="flex gap-4 items-end">
        <Barra opcao={dados.a} maxTotal={maxTotal} destaque={menor === "a"} />
        <Barra opcao={dados.b} maxTotal={maxTotal} destaque={menor === "b"} />
      </div>

      {dados.punchline && (
        <p className="text-[15px] text-coal font-medium mt-4">
          {dados.punchline}
        </p>
      )}
    </figure>
  )
}
