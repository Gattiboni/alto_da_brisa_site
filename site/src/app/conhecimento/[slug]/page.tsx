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
import { lerTema, listarSlugs } from "@/lib/temas"
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

  const numFmt = String(tema.numero).padStart(2, "0")
  const tocItems = [
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

              {/* Aulas (sempre abertas) */}
              {tema.aulas.length > 0 && (
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
    </>
  )
}
