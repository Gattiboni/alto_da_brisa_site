# DECISION_LOG — Alto da Brisa

Registro de decisões estratégicas do projeto: técnicas, jurídicas,
arquitetônicas e operacionais. Cada entrada documenta o contexto, as
alternativas consideradas, a decisão tomada e o racional.

Isso evita que a mesma discussão aconteça duas vezes.

Ordem: mais recente no topo.

---

## Template

```
### [DATA] ID — Título da Decisão
**Contexto:** O que motivou essa decisão.
**Alternativas consideradas:** O que mais estava na mesa.
**Decisão:** O que foi escolhido.
**Racional:** Por quê.
**Responsável:** Quem decidiu / aprovou.
**Status:** Ativa | Revisada | Superada | Resolvida
```

---

## Decisões Registradas

---

### [2026-03-30] D006 — Identidade visual definida

**Contexto:** Necessidade de padronizar cores, tipografia, espaçamento e regras
de uso do logo antes de iniciar o desenvolvimento do site.

**Decisão:** Paleta de 5 cores (#6b7f67, #b7b0a1, #d6d3ce, #ffffff, #333437).
Tipografia: Cormorant Garamond (títulos), Lato (body), Montserrat
(labels/accents). Grid base 8px. Documentado em `docs/identidade_visual.md` e no
Canva.

**Racional:** Definir identidade antes de codar evita retrabalho de estilo e
garante consistência em todas as mídias do projeto.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-03-30] D005 — URL do site para MVP: Vercel vs subdomínio customizado

**Contexto:** O domínio `alangattiboni.site` está no Hostinger. Configurar
`altodabrisa.alangattiboni.site` como subdomínio customizado na Vercel exige
plano pago na Vercel e configuração manual de DNS no Hostinger — overhead
desnecessário para MVP.

**Alternativas consideradas:**

- Configurar subdomínio agora: custo adicional, complexidade de DNS, sem valor
  de produto para v1
- Usar URL gerada pelo Vercel para MVP, migrar para subdomínio customizado no v2

**Decisão:** MVP opera em `https://alto-da-brisa-site.vercel.app`. Subdomínio
customizado postergado para v2.

**Racional:** Zero dívida técnica, zero custo adicional, zero tempo perdido com
infra que não entrega valor de produto. A URL do Vercel é funcional e acessível.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-03-30] D003 — Stack do site

**Contexto:** O site precisa suportar IA embutida (Claude API), autenticação,
base de conhecimento com busca, conteúdo rico e ser base para automações
futuras. Necessidade de proteger a API key do Claude no servidor.

**Alternativas consideradas:**

- React puro — não resolve API routes para proteger chaves de servidor
- Astro — ótimo para conteúdo estático, mas limitado para interatividade e API
  routes
- SvelteKit — leve e performático, ecossistema menor
- Next.js + Vercel — API routes nativas, ecossistema React completo, SSR/SSG
  híbrido, suporte oficial Supabase

**Decisão:** Next.js 15 (App Router, TypeScript, Tailwind) + Vercel para
frontend. Supabase para banco, auth e storage. Claude API via API routes (chave
nunca exposta no cliente). Python + Railway reservado para backend de
processamento e automações (v2+).

**Racional:** Next.js resolve de uma vez: proteção de chaves via API routes,
interatividade React, performance SSR/SSG, deploy contínuo no Vercel via GitHub.
Supabase elimina infraestrutura de banco, auth e storage. Ecossistema coeso, sem
over-engineering para v1.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-03-29] D004 — Localização oficial do imóvel: Gonçalves vs Sapucaí-Mirim

**Contexto:** O projeto é referenciado coloquialmente como "região de Gonçalves,
MG" por ser a referência cultural e turística mais conhecida da Serra da
Mantiqueira na área. O imóvel está registrado no município de Sapucaí-Mirim, MG,
Bairro Juncal, a ~14km do centro de Gonçalves.

**Decisão:** Município oficial é Sapucaí-Mirim, MG. Uso de "região de Gonçalves"
restrito a contexto coloquial e de comunicação/marketing.

**Racional:** Confirmado pelo proprietário. Todos os documentos legais,
tributários e ambientais devem referenciar Sapucaí-Mirim.

**Responsável:** Alan Gattiboni **Status:** Resolvida

---

### [2026-03-29] D002 — Repositório GitHub como espinha dorsal do projeto

**Contexto:** Necessidade de controle de versão, rastreabilidade e colaboração
no desenvolvimento do site e da documentação do projeto.

**Alternativas consideradas:**

- Pasta local sem versionamento: frágil, sem histórico, sem colaboração
- Google Drive para documentos + repositório separado para código: fragmentação
  desnecessária

**Decisão:** Repositório único no GitHub (`Gattiboni/alto_da_brisa_site`)
cobrindo código, documentação, changelog e decision log.

**Racional:** Tudo em um lugar com histórico completo. Facilita colaboração
futura e serve de auditoria do projeto.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-03-29] D001 — Arquitetura do hub digital do projeto

**Contexto:** Necessidade de um hub digital centralizado para o projeto. O site
precisa servir como base de conhecimento, arquivo, painel de controle e futura
plataforma de automação e integração com TARS.

**Alternativas consideradas:**

- Notion ou Obsidian: sem autonomia de hospedagem, sem IA integrada customizada,
  sem capacidade de automação
- Plataforma terceira (Webflow, WordPress): limitação para automações e
  integração com TARS
- Site próprio com stack controlada

**Decisão:** Site próprio com stack controlada, hospedado em infraestrutura sob
controle do projeto (Vercel + Supabase). Ver D003 para stack e D005 para URL.

**Racional:** Autonomia total. O site precisa ser servidor de automações,
integrar IA via API, suportar login de moradores e parceiros, e eventualmente
ser o backbone do TARS. Plataformas prontas não sustentam esse roadmap.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

_Todo membro do projeto pode propor uma entrada. Decisões sem log são decisões
que se perdem._
