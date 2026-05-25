import {
  Children,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from "react"

interface TabelaProps {
  children: ReactNode
}

function isTag(node: ReactNode, tag: string): node is ReactElement<{ children?: ReactNode }> {
  return (
    isValidElement(node) &&
    typeof node.type === "string" &&
    node.type.toLowerCase() === tag
  )
}

function findFirstTag(
  children: ReactNode,
  tag: string,
): ReactElement<{ children?: ReactNode }> | null {
  let found: ReactElement<{ children?: ReactNode }> | null = null
  Children.forEach(children, (child) => {
    if (found) return
    if (isTag(child, tag)) {
      found = child
    }
  })
  return found
}

function extractRows(parent: ReactElement<{ children?: ReactNode }> | null): ReactNode[][] {
  if (!parent) return []
  const rows: ReactNode[][] = []
  Children.forEach(parent.props.children, (tr) => {
    if (!isTag(tr, "tr")) return
    const cells: ReactNode[] = []
    Children.forEach(tr.props.children, (cell) => {
      if (isTag(cell, "th") || isTag(cell, "td")) {
        cells.push(cell.props.children)
      }
    })
    rows.push(cells)
  })
  return rows
}

/**
 * Render uma tabela do markdown como:
 * - Tabela tradicional em desktop (>=768px)
 * - Cards empilhados em mobile (<768px)
 *
 * Ambos layouts vão no HTML; CSS esconde um deles via media query.
 */
export function Tabela({ children }: TabelaProps) {
  const thead = findFirstTag(children, "thead")
  const tbody = findFirstTag(children, "tbody")

  const headerRows = extractRows(thead)
  const headers = headerRows[0] ?? []
  const rows = extractRows(tbody)

  if (headers.length === 0 || rows.length === 0) {
    return (
      <div className="my-6 overflow-x-auto">
        <table className="w-full text-[15px]">{children}</table>
      </div>
    )
  }

  return (
    <div className="my-6">
      {/* Desktop: tabela tradicional */}
      <div className="hidden md:block">
        <table className="w-full border-collapse text-[15px]">
          <thead>
            <tr>
              {headers.map((h, i) => (
                <th
                  key={i}
                  className="font-ui text-[12px] font-semibold uppercase tracking-[0.08em] text-coal text-left px-4 py-3 border-b-2 border-sand"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td
                    key={j}
                    className="text-coal/90 px-4 py-3 border-b border-stone align-top"
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile: cards empilhados */}
      <div className="md:hidden flex flex-col gap-3">
        {rows.map((row, i) => (
          <article
            key={i}
            className="border border-stone rounded-md p-4 bg-white"
          >
            <h3 className="font-serif text-[22px] text-coal font-normal mb-3 leading-tight">
              {row[0]}
            </h3>
            <dl className="grid gap-2">
              {headers.slice(1).map((h, j) => {
                const valor = row[j + 1]
                if (valor === undefined || valor === null) return null
                return (
                  <div key={j}>
                    <dt className="font-ui text-[11px] font-semibold uppercase tracking-[0.08em] text-sand">
                      {h}
                    </dt>
                    <dd className="font-sans text-[15px] text-coal m-0 mt-0.5">
                      {valor}
                    </dd>
                  </div>
                )
              })}
            </dl>
          </article>
        ))}
      </div>
    </div>
  )
}
