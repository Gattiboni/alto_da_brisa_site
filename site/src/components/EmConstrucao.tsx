import Link from "next/link"
import { Container } from "./Container"
import { SectionEyebrow } from "./SectionEyebrow"

interface EmConstrucaoProps {
  titulo: string
  descricao?: string
}

export function EmConstrucao({ titulo, descricao }: EmConstrucaoProps) {
  return (
    <Container size="narrow" className="py-32">
      <div className="text-center">
        <SectionEyebrow>Em construção</SectionEyebrow>
        <h1 className="font-serif text-4xl text-coal mb-4">{titulo}</h1>
        {descricao && (
          <p className="text-coal/60 text-[15px] leading-relaxed">{descricao}</p>
        )}
        <div className="mt-10 inline-flex items-center gap-2 font-ui text-[10px] uppercase tracking-[0.15em] text-sand">
          <span>Voltar para</span>
          <Link
            href="/"
            className="text-green hover:text-coal transition-colors border-b border-green/40 pb-px"
          >
            Início
          </Link>
        </div>
      </div>
    </Container>
  )
}
