import { notFound } from "next/navigation"
import Link from "next/link"
import { Container } from "@/components/Container"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { SectionEyebrow } from "@/components/SectionEyebrow"
import { Tag } from "@/components/Tag"
import { Markdown } from "@/components/Markdown"
import { Toc } from "@/components/Toc"
import { ClaudinhoFloatingButton } from "@/components/ClaudinhoFloatingButton"
import { AulaAnchorOpener } from "@/components/AulaAnchorOpener"
import { lerTema, listarSlugs } from "@/lib/temas"
import { lerPacote } from "@/lib/pacotes"
import type { Metadata } from "next"

interface PageProps {
  params: Promise<{ slug: string }>
}

export async function generateStaticParams() {
  return listarSlugs().map((slug) => ({ slug }))
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params
  try {
    const tema = lerTema(slug)
    return {
      title: tema.titulo,
      description: tema.visaoGeral.slice(0, 160),
    }
  } catch {
    return { title: "Tema não encontrado" }
  }
}

// CONTRATO de âncora: cada aula é uma <section id="aula-N">. Os callouts de
// aulas ausentes (gerados em scripts/consolidar_temas.py → montar_callout_ausente)
// linkam para `#aula-N`. Os headings do corpo NÃO recebem id (react-markdown sem
// rehype-slug), então este é o único alvo estável. Se mudar aqui, mude lá também.
function aulaAnchor(numero: number): string {
  return `aula-${numero}`
}

export default async function TemaPage({ params }: PageProps) {
  const { slug } = await params

  let tema
  try {
    tema = lerTema(slug)
  } catch {
    notFound()
  }

  // Composição condicional (D019): existe pacote → renderiza a seção;
  // não existe → página intocada (os 11 módulos sem pacote não mudam).
  const pacote = lerPacote(slug)

  const numFmt = String(tema.numero).padStart(2, "0")
  const tocItems = [
    ...(pacote ? [{ id: "pacote", label: "Em 7 minutos" }] : []),
    { id: "visao-geral", label: "Visão Geral" },
    ...tema.aulas.map((aula) => ({
      id: aulaAnchor(aula.numero),
      label: `${aula.numero}. ${aula.titulo}`,
    })),
  ]

  return (
    <>
      <Header />
      <main className="py-12 md:py-16">
        <Container size="wide">
          <div className="mb-3">
            <Link
              href="/conhecimento"
              className="font-ui text-[10px] uppercase tracking-[0.15em] text-sand hover:text-green transition-colors inline-flex items-center gap-1"
            >
              <span>←</span>
              <span>Conhecimento</span>
            </Link>
          </div>

          <SectionEyebrow>Módulo {numFmt}</SectionEyebrow>
          <h1 className="font-serif text-4xl md:text-5xl text-coal mb-4">
            {tema.titulo}
          </h1>
          <div className="flex items-center gap-2 mb-10 md:mb-14">
            <Tag variant="green">
              {tema.meta.totalAulas}{" "}
              {tema.meta.totalAulas === 1 ? "aula" : "aulas"}
            </Tag>
          </div>

          <div className="grid gap-10 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-14">
            {/* TOC desktop */}
            <aside className="hidden lg:block">
              <Toc items={tocItems} />
            </aside>

            {/* Conteúdo */}
            <article className="min-w-0">
              {/* Visão Geral */}
              <section id="visao-geral" className="mb-12 md:mb-16 prose-content">
                <h2 className="font-serif text-2xl md:text-3xl text-coal mb-4">
                  Visão Geral
                </h2>
                <div className="text-coal/90">
                  <Markdown>{tema.visaoGeral}</Markdown>
                </div>
              </section>

              {/* Pacote de 7 min (D019) — camada aditiva, só quando existe.
                  Divisor visual: hr + eyebrow (identidade), conforme §2. */}
              {pacote && (
                <>
                  <hr className="border-stone mb-12 md:mb-16" />
                  <section
                    id="pacote"
                    className="mb-12 md:mb-16 scroll-mt-20"
                  >
                    <SectionEyebrow>Pacote de 7 min</SectionEyebrow>
                    <h2 className="font-serif text-2xl md:text-3xl text-coal mb-6">
                      {tema.titulo} em 7 minutos
                    </h2>
                    <div className="prose-content">
                      <Markdown>{pacote}</Markdown>
                    </div>
                    <div className="mt-8">
                      <a
                        href="#aulas"
                        className="inline-block border border-green text-green font-ui text-[10px] font-semibold uppercase tracking-[0.14em] px-7 py-3 rounded-sm hover:bg-green hover:text-white transition-colors"
                      >
                        Ler o módulo completo ↓
                      </a>
                    </div>
                  </section>
                </>
              )}

              {/* Aulas — DUAS renderizações mutuamente exclusivas.
                  Invariante §0/§8: os 11 módulos SEM pacote precisam sair
                  byte-idênticos ao estado atual. Por isso o colapso é
                  PILOTADO só onde há pacote (D019: "os 11 não sabem que o
                  piloto existe"). Sem pacote → markup original intocado. */}

              {/* Com pacote: aulas colapsáveis (§2). <details> nativo —
                  teclado e a11y de graça, zero estado JS. Abertas por
                  default; regra da âncora via AulaAnchorOpener. */}
              {pacote && tema.aulas.length > 0 && (
                <section id="aulas" className="mb-12 md:mb-16 scroll-mt-20">
                  <hr className="border-stone mb-12 md:mb-16" />
                  <h2 className="font-serif text-2xl md:text-3xl text-coal mb-6 prose-content">
                    Aulas
                  </h2>
                  <div className="space-y-12 md:space-y-16">
                    {tema.aulas.map((aula) => (
                      <details
                        key={aula.numero}
                        id={aulaAnchor(aula.numero)}
                        open
                        className="group scroll-mt-20 prose-content"
                      >
                        <summary className="list-none cursor-pointer flex items-start gap-3 [&::-webkit-details-marker]:hidden">
                          <span
                            className="flex-shrink-0 mt-1 text-green text-sm leading-none transition-transform group-open:rotate-90"
                            aria-hidden
                          >
                            ›
                          </span>
                          <span className="min-w-0">
                            <span className="block font-ui text-[10px] uppercase tracking-[0.15em] text-sand mb-2">
                              Aula {aula.numero}
                            </span>
                            <span className="block font-serif text-xl md:text-2xl text-coal">
                              {aula.titulo}
                            </span>
                          </span>
                        </summary>
                        <div className="mt-5 pl-[calc(0.75rem+1ch)]">
                          <Markdown>{aula.conteudo}</Markdown>
                        </div>
                      </details>
                    ))}
                  </div>
                </section>
              )}

              {/* Sem pacote: markup ORIGINAL, byte-idêntico ao pré-piloto.
                  NÃO ALTERAR — é a prova da composição condicional (§8). */}
              {!pacote && tema.aulas.length > 0 && (
                <section className="mb-12 md:mb-16">
                  <h2 className="font-serif text-2xl md:text-3xl text-coal mb-6 prose-content">
                    Aulas
                  </h2>
                  <div className="space-y-12 md:space-y-16">
                    {tema.aulas.map((aula) => (
                      <section
                        key={aula.numero}
                        id={aulaAnchor(aula.numero)}
                        className="scroll-mt-20"
                      >
                        <div className="prose-content">
                          <div className="font-ui text-[10px] uppercase tracking-[0.15em] text-sand mb-2">
                            Aula {aula.numero}
                          </div>
                          <h3 className="font-serif text-xl md:text-2xl text-coal mb-5">
                            {aula.titulo}
                          </h3>
                          <Markdown>{aula.conteudo}</Markdown>
                        </div>
                      </section>
                    ))}
                  </div>
                </section>
              )}

              {/* Transcrição: oculta por D013 — campo continua exposto no
                  tipo Tema mas não é renderizado. */}
            </article>
          </div>
        </Container>
      </main>
      <Footer />
      <ClaudinhoFloatingButton />
      {pacote && <AulaAnchorOpener />}
    </>
  )
}
