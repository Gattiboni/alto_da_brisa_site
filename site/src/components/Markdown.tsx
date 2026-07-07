import {
  Children,
  cloneElement,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { cn } from "@/lib/cn"
import { Callout, type CalloutTipo } from "@/components/content/Callout"
import { Citacao } from "@/components/content/Citacao"
import { Tabela } from "@/components/content/Tabela"
import { ProcessFlow, parseFlow } from "@/components/content/ProcessFlow"
import { MapaTipos } from "@/components/content/MapaTipos"
import {
  EscaladaDecisao,
  parseEscalada,
} from "@/components/content/EscaladaDecisao"
import {
  ComparativoCustos,
  parseCustos,
} from "@/components/content/ComparativoCustos"

/** Linguagens de fenced block roteadas para componentes (sem <pre> wrapper). */
const CUSTOM_LANGS = ["flow", "tipos", "escalada", "custos"]

interface MarkdownProps {
  children: string
}

/**
 * Retorna texto puro de uma sub-árvore React.
 * Usado para inspecionar conteúdo de células e parágrafos.
 */
function getText(node: ReactNode): string {
  if (node == null || node === false) return ""
  if (typeof node === "string" || typeof node === "number") return String(node)
  if (Array.isArray(node)) return node.map(getText).join("")
  if (isValidElement(node))
    return getText((node.props as { children?: ReactNode }).children)
  return ""
}

function isTag(
  node: ReactNode,
  tag: string,
): node is ReactElement<{ children?: ReactNode }> {
  return (
    isValidElement(node) &&
    typeof node.type === "string" &&
    node.type.toLowerCase() === tag
  )
}

function cleanChildren(children: ReactNode): ReactNode[] {
  return Children.toArray(children).filter((c) => {
    if (typeof c === "string" && c.trim() === "") return false
    return true
  })
}

interface HastNode {
  type: string
  tagName?: string
  value?: string
  children?: HastNode[]
}

/**
 * Tenta detectar `> [!atencao]` ou similar no primeiro parágrafo
 * de um blockquote. Devolve tipo, título e o restante do corpo.
 *
 * Detecção é feita via AST do mdast (prop `node` do react-markdown)
 * porque nossos custom renderers tornam os filhos React indistinguíveis
 * por tag.
 */
function extractAlertInfo(
  children: ReactNode,
  node: HastNode | undefined,
): {
  tipo: CalloutTipo
  titulo?: string
  body: ReactNode[]
} | null {
  if (!node || !node.children) return null
  const firstP = node.children.find(
    (n) => n.type === "element" && n.tagName === "p",
  )
  if (!firstP || !firstP.children) return null
  const firstText = firstP.children[0]
  if (!firstText || firstText.type !== "text" || !firstText.value) return null

  const m = firstText.value.match(
    /^\[!(atencao|dica|exemplo)\][ \t]*([^\n]*)?(\n[\s\S]*)?$/,
  )
  if (!m) return null

  const tipo = m[1] as CalloutTipo
  const titulo = m[2]?.trim() || undefined

  // Modifica os children React: remover a primeira linha (que contém o
  // marcador) do primeiro parágrafo, mantendo o resto da formatação.
  const arr = cleanChildren(children)
  if (arr.length === 0) return null
  const first = arr[0]
  if (!isValidElement(first)) return null

  const firstProps = first.props as { children?: ReactNode }
  const pChildren = Children.toArray(firstProps.children)
  const newPChildren: ReactNode[] = []
  let consumido = false

  for (const c of pChildren) {
    if (!consumido && typeof c === "string") {
      const stripped = c.replace(/^\[![^\]]+\][^\n]*/, "").replace(/^\n/, "")
      if (stripped) newPChildren.push(stripped)
      consumido = true
    } else {
      newPChildren.push(c)
    }
  }

  const body: ReactNode[] = []
  if (newPChildren.length > 0) {
    body.push(
      cloneElement(
        first,
        { ...firstProps, children: newPChildren } as Record<string, unknown>,
      ),
    )
  }
  for (let i = 1; i < arr.length; i++) body.push(arr[i])
  return { tipo, titulo, body }
}

/**
 * Detecta atribuição (linha começando com travessão) em um blockquote
 * de citação. Devolve corpo e atribuição se possível separar.
 */
function extractCitation(children: ReactNode): {
  body: ReactNode[]
  atribuicao?: string
} {
  const arr = cleanChildren(children)
  if (arr.length === 0) return { body: [] }

  const last = arr[arr.length - 1]
  if (!isTag(last, "p")) return { body: arr }

  const lastChildren = Children.toArray(last.props.children)
  // Caso A: último parágrafo é uma string só que termina com "\n— Atribuição"
  if (lastChildren.length === 1 && typeof lastChildren[0] === "string") {
    const text = lastChildren[0]
    // Tudo é atribuição (ex: "— Amanda Calastro") e existe parágrafo anterior
    const onlyDash = text.match(/^\s*(?:—|--|-\s)\s*([\s\S]+)$/)
    if (onlyDash && arr.length > 1) {
      return {
        body: arr.slice(0, -1),
        atribuicao: onlyDash[1].trim(),
      }
    }
    // Citação + atribuição inline separadas por \n
    const inline = text.match(/^([\s\S]+?)\n(?:—|--|-\s)\s*([^\n]+)\s*$/)
    if (inline) {
      const novoP = cloneElement(last, {
        ...last.props,
        children: inline[1].trim(),
      })
      return {
        body: [...arr.slice(0, -1), novoP],
        atribuicao: inline[2].trim(),
      }
    }
  }

  // Caso B: último parágrafo é mais complexo. Tentamos analisar só o texto puro
  // do último parágrafo — se for evidente que termina com `\n— Atribuição`,
  // não reconstruímos (deixaria visualmente como está), apenas devolvemos
  // o corpo intacto. Manter simples: o autor pode usar parágrafo isolado se
  // quiser garantir o estilo de atribuição.
  return { body: arr }
}

export function Markdown({ children }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="font-serif text-3xl text-coal mt-8 mb-4">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="font-serif text-2xl text-coal mt-8 mb-3">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="font-serif text-xl text-coal mt-6 mb-2">{children}</h3>
        ),
        h4: ({ children }) => (
          <h4 className="font-ui text-[11px] font-semibold uppercase tracking-[0.1em] text-coal/70 mt-5 mb-2">
            {children}
          </h4>
        ),
        p: ({ children }) => (
          <p className="text-coal/85 leading-relaxed mb-4">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-6 mb-4 space-y-1 text-coal/85 marker:text-sand">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-6 mb-4 space-y-1 text-coal/85 marker:text-sand">
            {children}
          </ol>
        ),
        li: ({ children }) => <li className="leading-relaxed">{children}</li>,

        blockquote: ({ children, node }) => {
          const alert = extractAlertInfo(children, node as HastNode | undefined)
          if (alert) {
            return (
              <Callout tipo={alert.tipo} titulo={alert.titulo}>
                {alert.body}
              </Callout>
            )
          }
          const citacao = extractCitation(children)
          return (
            <Citacao atribuicao={citacao.atribuicao}>
              {citacao.body.length > 0 ? citacao.body : children}
            </Citacao>
          )
        },

        table: ({ children }) => <Tabela>{children}</Tabela>,

        pre: ({ children, ...rest }) => {
          // Se o filho é um code com language-flow, removemos o <pre>
          // — o ProcessFlow renderiza sozinho.
          const arr = Children.toArray(children)
          const first = arr[0]
          if (isValidElement(first)) {
            const className =
              (first.props as { className?: string }).className || ""
            const lang = /language-(\w+)/.exec(className)?.[1]
            if (lang && CUSTOM_LANGS.includes(lang)) {
              return <>{children}</>
            }
          }
          return (
            <pre
              {...rest}
              className="bg-stone/40 px-4 py-3 rounded my-4 overflow-x-auto font-mono text-[13px] text-coal"
            >
              {children}
            </pre>
          )
        },

        code: ({ className, children, ...rest }) => {
          const langMatch = /language-(\w+)/.exec(className || "")
          const lang = langMatch?.[1]
          if (lang && CUSTOM_LANGS.includes(lang)) {
            const raw = String(getText(children)).replace(/\n$/, "")
            if (lang === "flow") return <ProcessFlow steps={parseFlow(raw)} />
            if (lang === "tipos") return <MapaTipos raw={raw} />
            if (lang === "escalada")
              return <EscaladaDecisao degraus={parseEscalada(raw)} />
            if (lang === "custos") {
              const dados = parseCustos(raw)
              return dados ? <ComparativoCustos dados={dados} /> : null
            }
          }
          if (className) {
            // Code block com outra linguagem
            return (
              <code
                {...rest}
                className={cn("font-mono text-[13px] text-coal", className)}
              >
                {children}
              </code>
            )
          }
          // Inline
          return (
            <code
              {...rest}
              className="font-mono text-[13px] bg-stone/40 px-1.5 py-0.5 rounded"
            >
              {children}
            </code>
          )
        },

        a: ({ href, children }) => (
          <a
            href={href}
            target={href?.startsWith("http") ? "_blank" : undefined}
            rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
            className="text-green hover:text-coal underline underline-offset-2 decoration-green/40 hover:decoration-coal/40 transition-colors"
          >
            {children}
          </a>
        ),
        strong: ({ children }) => (
          <strong className="text-coal font-semibold">{children}</strong>
        ),
        hr: () => <hr className="my-8 border-stone" />,
      }}
    >
      {children}
    </ReactMarkdown>
  )
}
