#!/usr/bin/env node
/**
 * check_routes.mjs — Verifica que todas as rotas declaradas respondem 200.
 *
 * Inicia o dev server, faz requests para cada rota, reporta falhas.
 * Uso: npm run check:routes
 */

import { spawn } from "node:child_process"
import { setTimeout as wait } from "node:timers/promises"

const PORT = 3456
const BASE = `http://localhost:${PORT}`

const ROTAS_FIXAS = [
  "/",
  "/conhecimento",
  "/galeria",
  "/dashboard",
  "/claudinho",
]

const SLUGS_TEMAS = [
  "01_introducao",
  "02_projeto",
  "03_terreno",
  "04_orcamento-planejamento-controle",
  "05_servicos-preliminares",
  "06_fundacoes",
  "07_estruturas-vedacoes",
  "08_lajes",
  "09_coberturas",
  "10_acabamentos",
  "11_aberturas-esquadrias",
  "12_instalacoes-residenciais",
]

const ROTAS = [...ROTAS_FIXAS, ...SLUGS_TEMAS.map((s) => `/conhecimento/${s}`)]

async function aguardaServidor(timeoutMs = 60000) {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    try {
      const r = await fetch(BASE)
      if (r.ok) return true
    } catch {}
    await wait(500)
  }
  return false
}

async function checa(rota) {
  try {
    const r = await fetch(`${BASE}${rota}`)
    return { rota, status: r.status, ok: r.ok }
  } catch (e) {
    return { rota, status: 0, ok: false, erro: e.message }
  }
}

async function main() {
  console.log(`Iniciando dev server em :${PORT}...`)
  const server = spawn("npx", ["next", "dev", "-p", String(PORT)], {
    stdio: ["ignore", "pipe", "pipe"],
    shell: process.platform === "win32",
  })

  let serverLogs = ""
  server.stdout.on("data", (d) => (serverLogs += d.toString()))
  server.stderr.on("data", (d) => (serverLogs += d.toString()))

  const pronto = await aguardaServidor()
  if (!pronto) {
    console.error("Servidor não subiu em 60s. Logs:")
    console.error(serverLogs)
    server.kill()
    process.exit(1)
  }

  console.log(`\nChecando ${ROTAS.length} rotas...\n`)
  let falhas = 0
  for (const rota of ROTAS) {
    const r = await checa(rota)
    const ico = r.ok ? "OK " : "ERR"
    console.log(`  ${ico}  ${String(r.status).padStart(3)}  ${rota}`)
    if (!r.ok) falhas++
  }

  console.log()
  if (falhas > 0) {
    console.error(`${falhas} rota(s) falharam.`)
    server.kill()
    process.exit(1)
  } else {
    console.log(`Todas as ${ROTAS.length} rotas responderam OK.`)
    server.kill()
    process.exit(0)
  }
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
