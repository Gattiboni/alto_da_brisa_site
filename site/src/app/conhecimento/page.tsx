import { Container } from "@/components/Container"
import { Footer } from "@/components/Footer"
import { Header } from "@/components/Header"
import { SectionEyebrow } from "@/components/SectionEyebrow"
import { TemaCard } from "@/components/TemaCard"
import { ClaudinhoFloatingButton } from "@/components/ClaudinhoFloatingButton"
import { listarTemas } from "@/lib/temas"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Base de Conhecimento",
  description: "Os 12 módulos do curso Amanda & Fernando organizados por tema.",
}

export default function ConhecimentoPage() {
  const temas = listarTemas()
  const totalAulas = temas.reduce((s, t) => s + t.meta.totalAulas, 0)

  return (
    <>
      <Header />
      <main className="py-16">
        <Container size="wide">
          <div className="mb-12">
            <SectionEyebrow>Amanda &amp; Fernando · Acervo organizado</SectionEyebrow>
            <h1 className="font-serif text-4xl text-coal mb-3">
              Base de Conhecimento
            </h1>
            <p className="text-coal/60 text-[15px] leading-relaxed max-w-2xl">
              {temas.length} módulos, {totalAulas} aulas. Conteúdo extraído e
              organizado do curso &ldquo;Casa de Baixo Custo Sustentável&rdquo;
              para consulta direta — e também usado como base do Claudinho da
              Brisa.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {temas.map((tema) => (
              <TemaCard key={tema.slug} tema={tema} />
            ))}
          </div>
        </Container>
      </main>
      <Footer />
      <ClaudinhoFloatingButton />
    </>
  )
}
