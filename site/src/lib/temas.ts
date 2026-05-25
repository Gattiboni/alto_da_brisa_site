/**
 * lib/temas.ts
 *
 * Lê e parseia os 12 arquivos de tema de /content/temas/.
 *
 * Estrutura esperada de cada .md:
 *   # Título do Tema
 *
 *   > Módulo N de 12 · X aulas
 *   > Fonte: Curso Casa de Baixo Custo Sustentável — Amanda & Fernando
 *
 *   ---
 *
 *   ## Visão Geral
 *   [conteúdo]
 *
 *   ---
 *
 *   ## Aulas
 *
 *   ### N. Nome da aula
 *   [conteúdo da aula]
 *
 *   ### N+1. Próxima aula
 *   [conteúdo]
 *
 *   ---
 *
 *   ## Transcrição
 *
 *   ### Gravação N
 *   [conteúdo da gravação]
 *
 *   ### Gravação N+1
 *   [conteúdo]
 */

import fs from "node:fs"
import path from "node:path"

const TEMAS_DIR = path.join(process.cwd(), "content", "temas")

export interface Aula {
  numero: number
  titulo: string
  conteudo: string
}

export interface Gravacao {
  numero: number
  conteudo: string
}

export interface Tema {
  slug: string // ex: "06_fundacoes"
  numero: number // ex: 6
  titulo: string // ex: "Fundações"
  meta: {
    totalAulas: number
    fonte: string
  }
  visaoGeral: string
  aulas: Aula[]
  transcricao: Gravacao[]
}

/**
 * Normaliza line endings e remove BOM.
 */
function normalize(raw: string): string {
  return raw.replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n")
}

/**
 * Lista os slugs disponíveis (sem extensão), em ordem numérica do nome.
 */
export function listarSlugs(): string[] {
  const arquivos = fs
    .readdirSync(TEMAS_DIR)
    .filter((f) => f.endsWith(".md"))
    .sort()
  return arquivos.map((f) => f.replace(/\.md$/, ""))
}

/**
 * Lê e parseia um tema pelo slug (nome do arquivo sem .md).
 * Lança erro se o arquivo não existe ou não tem a estrutura esperada.
 */
export function lerTema(slug: string): Tema {
  const filepath = path.join(TEMAS_DIR, `${slug}.md`)
  if (!fs.existsSync(filepath)) {
    throw new Error(`Tema não encontrado: ${slug}`)
  }
  const raw = normalize(fs.readFileSync(filepath, "utf-8"))

  // Número do módulo a partir do nome (01_..., 02_..., 12_...)
  const numeroMatch = slug.match(/^(\d+)_/)
  if (!numeroMatch) {
    throw new Error(`Slug com formato inválido: ${slug}`)
  }
  const numero = parseInt(numeroMatch[1], 10)

  // Título: primeira linha começando com `# `
  const tituloMatch = raw.match(/^#\s+(.+)$/m)
  if (!tituloMatch) {
    throw new Error(`Sem H1 em ${slug}`)
  }
  const titulo = tituloMatch[1].trim()

  // Meta: blockquote com "Módulo N de 12 · X aulas"
  const metaMatch = raw.match(/^>\s*Módulo\s+\d+\s+de\s+\d+\s*·\s*(\d+)\s+aulas?/m)
  const totalAulas = metaMatch ? parseInt(metaMatch[1], 10) : 0
  const fonteMatch = raw.match(/^>\s*Fonte:\s*(.+)$/m)
  const fonte = fonteMatch ? fonteMatch[1].trim() : ""

  // Seções principais (## ...)
  const visaoGeral = extrairSecao(raw, "Visão Geral")
  const aulasBloco = extrairSecao(raw, "Aulas")
  const transcricaoBloco = extrairSecao(raw, "Transcrição")

  return {
    slug,
    numero,
    titulo,
    meta: { totalAulas, fonte },
    visaoGeral,
    aulas: parsearAulas(aulasBloco),
    transcricao: parsearTranscricao(transcricaoBloco),
  }
}

/**
 * Extrai o conteúdo entre um `## Nome` e o próximo `## ` (ou fim do arquivo).
 * Remove `---` finais.
 *
 * Nota: JavaScript regex não suporta `\Z` (anchor de fim absoluto).
 * Usamos `(?![\s\S])` como equivalente — casa apenas onde não há mais nenhum caractere depois.
 */
function extrairSecao(raw: string, nome: string): string {
  const escapado = nome.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  const re = new RegExp(`^##\\s+${escapado}\\s*\\n([\\s\\S]*?)(?=^##\\s+|(?![\\s\\S]))`, "m")
  const m = raw.match(re)
  if (!m) return ""
  return m[1].replace(/\n---\s*$/, "").trim()
}

/**
 * Parseia bloco "## Aulas" em array de aulas.
 * Cada aula começa com `### N. Título`.
 */
function parsearAulas(bloco: string): Aula[] {
  if (!bloco) return []
  const aulas: Aula[] = []
  const re = /^###\s+(\d+)\.\s+(.+?)$/gm
  const matches = [...bloco.matchAll(re)]
  for (let i = 0; i < matches.length; i++) {
    const m = matches[i]
    const numero = parseInt(m[1], 10)
    const titulo = m[2].trim()
    const inicio = m.index! + m[0].length
    const fim = i + 1 < matches.length ? matches[i + 1].index! : bloco.length
    const conteudo = bloco.slice(inicio, fim).trim()
    aulas.push({ numero, titulo, conteudo })
  }
  return aulas
}

/**
 * Parseia bloco "## Transcrição" em array de gravações.
 * Cada gravação começa com `### Gravação N`.
 */
function parsearTranscricao(bloco: string): Gravacao[] {
  if (!bloco) return []
  const gravacoes: Gravacao[] = []
  const re = /^###\s+Gravação\s+(\d+)\s*$/gm
  const matches = [...bloco.matchAll(re)]
  for (let i = 0; i < matches.length; i++) {
    const m = matches[i]
    const numero = parseInt(m[1], 10)
    const inicio = m.index! + m[0].length
    const fim = i + 1 < matches.length ? matches[i + 1].index! : bloco.length
    const conteudo = bloco.slice(inicio, fim).trim()
    gravacoes.push({ numero, conteudo })
  }
  return gravacoes
}

/**
 * Lista todos os temas em ordem numérica.
 * Usar com cuidado em rotas com muitos temas (lê 12 arquivos).
 */
export function listarTemas(): Tema[] {
  return listarSlugs().map(lerTema)
}
