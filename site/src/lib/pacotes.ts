/**
 * lib/pacotes.ts
 *
 * Lê os "pacotes de 7 min" curados à mão de /content/pacotes/ (D019).
 *
 * Espelho simétrico do D016: `temas/` é gerado (nunca editar); `pacotes/`
 * é curado (nunca gerar). A página compõe o pacote condicionalmente —
 * existe arquivo → renderiza a seção; não existe → página intocada.
 */

import fs from "node:fs"
import path from "node:path"

const PACOTES_DIR = path.join(process.cwd(), "content", "pacotes")

function normalize(raw: string): string {
  return raw.replace(/^﻿/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n")
}

/**
 * Retorna o markdown do pacote de um slug, ou null se não houver pacote.
 * A ausência é o caso normal (11 dos 12 módulos não têm pacote no piloto).
 */
export function lerPacote(slug: string): string | null {
  const filepath = path.join(PACOTES_DIR, `${slug}.md`)
  if (!fs.existsSync(filepath)) return null
  const raw = normalize(fs.readFileSync(filepath, "utf-8"))
  // Remove comentários HTML de proveniência (<!-- fonte: aula N -->).
  // Wireframe §1: eles servem à norma de manutenção na FONTE e NÃO
  // renderizam. react-markdown (sem rehype-raw) os emitiria como texto
  // visível, então tiramos aqui — o arquivo curado mantém os comentários.
  return raw.replace(/<!--[\s\S]*?-->/g, "").trim()
}
