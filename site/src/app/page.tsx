import Link from "next/link"
import { Container } from "@/components/Container"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { SectionEyebrow } from "@/components/SectionEyebrow"
import { ClaudinhoFloatingButton } from "@/components/ClaudinhoFloatingButton"

export default function HomePage() {
  return (
    <>
      <Header />
      <main>
        <section className="py-32">
          <Container size="narrow">
            <SectionEyebrow>
              Sapucaí-Mirim · Serra da Mantiqueira
            </SectionEyebrow>
            <h1 className="font-serif text-5xl md:text-6xl text-coal mb-6 leading-tight tracking-tight">
              Sítio<br />
              <span className="text-green">Alto da Brisa</span>
            </h1>
            <p className="text-coal/65 text-[16px] leading-relaxed max-w-lg">
              Um projeto de vida comunitário entre natureza, autonomia e
              intenção. Este portal acompanha a evolução do projeto e organiza
              o conhecimento que orienta sua construção.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link
                href="/conhecimento"
                className="inline-block bg-green text-white font-ui text-[10px] font-semibold uppercase tracking-[0.14em] px-7 py-3 rounded-sm hover:bg-coal transition-colors"
              >
                Base de Conhecimento
              </Link>
              <Link
                href="/galeria"
                className="inline-block border border-green text-green font-ui text-[10px] font-semibold uppercase tracking-[0.14em] px-7 py-3 rounded-sm hover:bg-green hover:text-white transition-colors"
              >
                Galeria
              </Link>
            </div>
          </Container>
        </section>

        <section className="py-20 bg-[var(--color-bg-soft)]">
          <Container size="wide">
            <SectionEyebrow>Em desenvolvimento</SectionEyebrow>
            <h2 className="font-serif text-3xl text-coal mb-3">
              Acompanhe a evolução
            </h2>
            <p className="text-coal/60 text-[15px] leading-relaxed max-w-xl">
              A homepage definitiva trará um mapa 3D interativo do terreno com
              os ícones das casas, da área comum, do airbnb e dos caminhos.
              Por enquanto, o conteúdo do projeto vive na Base de Conhecimento.
            </p>
          </Container>
        </section>
      </main>
      <Footer />
      <ClaudinhoFloatingButton />
    </>
  )
}
