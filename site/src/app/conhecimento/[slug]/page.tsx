import { notFound } from "next/navigation"
import Link from "next/link"
import { Container } from "@/components/Container"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { SectionEyebrow } from "@/components/SectionEyebrow"
import { Accordion } from "@/components/Accordion"
import { Tag } from "@/components/Tag"
import { Markdown } from "@/components/Markdown"
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

export default async function TemaPage({ params }: PageProps) {
  const { slug } = await params

  let tema
  try {
    tema = lerTema(slug)
  } catch {
    notFound()
  }

  const numFmt = String(tema.numero).padStart(2, "0")

  return (
    <>
      <Header />
      <main className="py-16">
        <Container>
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
          <h1 className="font-serif text-4xl text-coal mb-4">{tema.titulo}</h1>
          <div className="flex items-center gap-2 mb-12">
            <Tag variant="green">
              {tema.meta.totalAulas}{" "}
              {tema.meta.totalAulas === 1 ? "aula" : "aulas"}
            </Tag>
            {tema.transcricao.length > 0 && (
              <Tag>
                {tema.transcricao.length}{" "}
                {tema.transcricao.length === 1 ? "gravação" : "gravações"}
              </Tag>
            )}
          </div>

          {/* Visão Geral */}
          <section className="mb-16">
            <h2 className="font-serif text-2xl text-coal mb-4">Visão Geral</h2>
            <div className="text-coal/85">
              <Markdown>{tema.visaoGeral}</Markdown>
            </div>
          </section>

          {/* Aulas */}
          {tema.aulas.length > 0 && (
            <section className="mb-16">
              <h2 className="font-serif text-2xl text-coal mb-5">Aulas</h2>
              <div className="space-y-2">
                {tema.aulas.map((aula) => (
                  <Accordion
                    key={aula.numero}
                    title={aula.titulo}
                    meta={`Aula ${aula.numero}`}
                  >
                    <Markdown>{aula.conteudo}</Markdown>
                  </Accordion>
                ))}
              </div>
            </section>
          )}

          {/* Transcrição */}
          {tema.transcricao.length > 0 && (
            <section className="mb-16">
              <h2 className="font-serif text-2xl text-coal mb-3">Transcrição</h2>
              <p className="text-[13px] text-coal/55 italic mb-5">
                {tema.transcricao.length}{" "}
                {tema.transcricao.length === 1 ? "gravação" : "gravações"} de
                áudio do curso, transcritas e polidas.
              </p>
              <div className="space-y-2">
                {tema.transcricao.map((gravacao, idx) => (
                  <Accordion
                    key={idx}
                    title={`Gravação ${gravacao.numero}`}
                    meta={`Áudio ${idx + 1} de ${tema.transcricao.length}`}
                  >
                    <Markdown>{gravacao.conteudo}</Markdown>
                  </Accordion>
                ))}
              </div>
            </section>
          )}
        </Container>
      </main>
      <Footer />
      <ClaudinhoFloatingButton />
    </>
  )
}
