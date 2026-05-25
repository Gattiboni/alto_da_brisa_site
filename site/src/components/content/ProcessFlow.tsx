import { cn } from "@/lib/cn"

export interface FlowStep {
  titulo: string
  descricao?: string
}

interface ProcessFlowProps {
  steps: FlowStep[]
  className?: string
}

/**
 * Parser do bloco ```flow.
 *
 * Variante 1: linha única "Etapa1 → Etapa2 → Etapa3"
 * Variante 2: uma etapa por linha, opcionalmente "Etapa :: descrição"
 */
export function parseFlow(raw: string): FlowStep[] {
  const linhas = raw
    .trim()
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)

  if (linhas.length === 0) return []

  // Variante 1: única linha com setas
  if (linhas.length === 1 && linhas[0].includes("→")) {
    return linhas[0]
      .split("→")
      .map((s) => s.trim())
      .filter(Boolean)
      .map((titulo) => ({ titulo }))
  }

  // Variante 2: uma etapa por linha, com possível "::"
  return linhas.map((linha) => {
    const sep = linha.indexOf("::")
    if (sep === -1) return { titulo: linha.trim() }
    return {
      titulo: linha.slice(0, sep).trim(),
      descricao: linha.slice(sep + 2).trim(),
    }
  })
}

function StepCard({ index, step }: { index: number; step: FlowStep }) {
  const numero = String(index + 1).padStart(2, "0")
  return (
    <div className="border border-stone rounded-md bg-white px-4 py-4 md:px-5 md:py-5 flex-1 min-w-[160px] md:min-w-[180px]">
      <div className="font-serif text-[28px] md:text-[32px] text-green leading-none font-normal">
        {numero}
      </div>
      <div className="font-sans text-[14px] md:text-[15px] font-semibold text-coal mt-2 leading-tight">
        {step.titulo}
      </div>
      {step.descricao && (
        <div className="font-sans text-[13px] text-coal/70 mt-2 leading-snug">
          {step.descricao}
        </div>
      )}
    </div>
  )
}

export function ProcessFlow({ steps, className }: ProcessFlowProps) {
  if (steps.length === 0) return null

  return (
    <div className={cn("my-8", className)}>
      {/* Desktop: horizontal com setas */}
      <div className="hidden md:flex md:flex-wrap md:items-stretch md:gap-3">
        {steps.map((step, i) => (
          <div key={i} className="flex items-stretch gap-3">
            <StepCard index={i} step={step} />
            {i < steps.length - 1 && (
              <div
                className="flex items-center font-serif text-[24px] text-sand select-none"
                aria-hidden
              >
                →
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Mobile: vertical com conectores */}
      <div className="md:hidden flex flex-col">
        {steps.map((step, i) => (
          <div key={i} className="flex flex-col">
            <StepCard index={i} step={step} />
            {i < steps.length - 1 && (
              <div
                className="flex flex-col items-center my-1 select-none"
                aria-hidden
              >
                <div className="w-px h-4 bg-sand" />
                <div className="text-sand text-[12px] leading-none">▼</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
