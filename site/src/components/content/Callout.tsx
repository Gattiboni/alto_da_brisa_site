import { cn } from "@/lib/cn"

export type CalloutTipo = "atencao" | "dica" | "exemplo"

interface CalloutProps {
  tipo: CalloutTipo
  titulo?: string
  children: React.ReactNode
  className?: string
}

const EYEBROW: Record<CalloutTipo, string> = {
  atencao: "ATENÇÃO",
  dica: "DICA",
  exemplo: "EXEMPLO",
}

const BARRA: Record<CalloutTipo, string> = {
  atencao: "border-l-[3px] border-coal",
  dica: "border-l-[3px] border-green",
  exemplo: "border-l-[4px] border-sand",
}

export function Callout({ tipo, titulo, children, className }: CalloutProps) {
  const mostrarEyebrow = Boolean(titulo)

  return (
    <aside
      className={cn(
        "bg-stone rounded-r my-6 px-4 py-4 md:px-6 md:py-5",
        BARRA[tipo],
        className,
      )}
    >
      {mostrarEyebrow && (
        <div className="font-ui text-[11px] font-semibold uppercase tracking-[0.14em] text-coal mb-2">
          {EYEBROW[tipo]}
          {titulo && titulo !== EYEBROW[tipo] && (
            <span className="ml-2 normal-case tracking-normal font-normal text-coal/80">
              {titulo}
            </span>
          )}
        </div>
      )}
      <div className="text-coal text-[17px] md:text-[18px] leading-[1.65] [&_p]:mb-3 [&_p:last-child]:mb-0">
        {children}
      </div>
    </aside>
  )
}
