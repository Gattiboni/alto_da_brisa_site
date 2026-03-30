# DECISION_LOG — Alto da Brisa

Registro de decisões estratégicas do projeto: técnicas, jurídicas, arquitetônicas e operacionais.  
Cada entrada documenta o **contexto**, as **alternativas consideradas**, a **decisão tomada** e o **racional**.

Isso evita que a mesma discussão aconteça duas vezes.

---

## Template

```
### [DATA] ID — Título da Decisão
**Contexto:** O que motivou essa decisão.
**Alternativas consideradas:** O que mais estava na mesa.
**Decisão:** O que foi escolhido.
**Racional:** Por quê.
**Responsável:** Quem decidiu / aprovou.
**Status:** Ativa | Revisada | Superada
```

---

## Decisões Registradas

---

### [2026-03-29] D001 — Escolha do domínio e arquitetura do site

**Contexto:** Necessidade de um hub digital centralizado para o projeto. O site precisa servir como base de conhecimento, arquivo, painel de controle e futura plataforma de automação.

**Alternativas consideradas:**
- Notion ou Obsidian como base de conhecimento (sem autonomia de hospedagem, sem IA integrada customizada)
- Site em plataforma terceira (Webflow, WordPress) — limitação para automações e integração com TARS
- Site próprio hospedado em servidor controlado

**Decisão:** Site próprio em `altodabrisa.alangattiboni.site`, hospedado em servidor sob controle do projeto. Stack a definir.

**Racional:** Autonomia total. O site precisa ser servidor de automações, integrar IA (Claude via API), suportar login de moradores e parceiros, e eventualmente ser o backbone do TARS. Plataformas prontas não sustentam esse roadmap.

**Responsável:** Alan Gattiboni  
**Status:** Ativa

---

### [2026-03-29] D002 — Repositório GitHub como espinha dorsal do projeto

**Contexto:** Necessidade de controle de versão, rastreabilidade e colaboração no desenvolvimento do site e da documentação.

**Alternativas consideradas:**
- Pasta local sem versionamento (frágil, sem histórico)
- Google Drive para documentos + repositório separado para código

**Decisão:** Repositório único no GitHub (`alto_da_brisa_site`) cobrindo código, documentação, changelog e decision log.

**Racional:** Tudo em um lugar com histórico completo. Facilita colaboração futura e serve de auditoria do projeto.

**Responsável:** Alan Gattiboni  
**Status:** Ativa

---

### [A DEFINIR] D003 — Stack do site

**Contexto:** O site precisa ser estático o suficiente para ser rápido, mas dinâmico o suficiente para suportar IA embutida, autenticação e automações.

**Alternativas em análise:**
- Next.js (React) + Vercel — flexível, bom ecossistema, suporta API routes
- Astro — excelente para sites de conteúdo, SSG/SSR híbrido
- SvelteKit — leve, performático
- Backend separado (FastAPI / Node) + frontend desacoplado

**Decisão:** ⏳ Em definição.

**Racional:** Depende do volume de automações e da estratégia de integração com Claude API e TARS.

**Responsável:** Alan Gattiboni  
**Status:** Em aberto

---

### [2026-03-29] D004 — Localização oficial do imóvel: Gonçalves vs Sapucaí-Mirim

**Contexto:** O projeto é referenciado coloquialmente como "região de Gonçalves, MG" por ser a referência cultural e turística mais conhecida da Serra da Mantiqueira na área. O imóvel, no entanto, está registrado no município de **Sapucaí-Mirim, MG**, Bairro Juncal, a ~14km do centro de Gonçalves.

**Decisão:** Município oficial é **Sapucaí-Mirim, MG**. Uso de "região de Gonçalves" restrito a contexto coloquial e de comunicação/marketing.

**Racional:** Confirmado pelo proprietário. Todos os documentos legais, tributários e ambientais devem referenciar Sapucaí-Mirim.

**Responsável:** Alan Gattiboni  
**Status:** ✅ Resolvida

---

*Todo membro do projeto pode propor uma entrada. Decisões sem log são decisões que se perdem.*
