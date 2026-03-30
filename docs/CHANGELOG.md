# CHANGELOG — Alto da Brisa

Registro cronológico de marcos, eventos e entregas do projeto. Formato:
`[DATA] Categoria — Descrição`

Categorias: `LEGAL` | `OBRA` | `INFRA` | `SITE` | `DOC` | `FINANCEIRO` |
`DECISÃO`

Ordem: mais recente no topo.

---

## 2026

### [2026-03-30] DOC — Identidade visual documentada

Arquivo `docs/identidade_visual.md` criado com paleta, escala tipográfica, grid,
regras de logo, estilo fotográfico, tom de voz e snippets prontos para Tailwind
e Next.js.

---

### [2026-03-30] DOC — Brand guide criado no Canva

Design "Alto da Brisa Brand Identity Guide" criado em
https://www.canva.com/d/o318p1DnkYFeXgS. Pasta do projeto:
https://www.canva.com/folder/FAF5ijcSyrk.

---

### [2026-03-30] SITE — Primeiro deploy bem-sucedido na Vercel

Site acessível em https://alto-da-brisa-site.vercel.app. Deploy automático via
GitHub (branch main) ativo.

---

### [2026-03-30] SITE — Supabase configurado

Projeto `alto_da_brisa_site` criado. Banco PostgreSQL provisionado em us-west-2
(Oregon). Variáveis de ambiente configuradas localmente e na Vercel.

### [2026-03-30] SITE — Next.js scaffolded

App criado com `create-next-app@16.2.1`. Flags: TypeScript, ESLint, Tailwind,
App Router, src-dir. Root directory: `site/`.

### [2026-03-30] SITE — Stack definida

Next.js + Vercel + Supabase + Claude API. Python/Railway reservado para backend
e automações futuras. Ver DECISION_LOG D003 e D005.

### [2026-03-30] DOC — Escopo funcional e DoD v1 criados

Arquivos `docs/site_escopo_funcional.md` e `docs/site_dod_v1.md` adicionados ao
repositório. Modelo baseado no framework de projetos do Tech Lead.

### [2026-03-30] SITE — Contas Google e YouTube criadas

Gmail: projetoaltodabrisa@gmail.com. Canal YouTube Alto da Brisa criado para
arquivo de vídeos do projeto.

### [2026-03-29] SITE — Repositório GitHub criado

Repositório `Gattiboni/alto_da_brisa_site` iniciado. Commit inaugural com
README, CHANGELOG, DECISION_LOG e .gitignore.

---

## 2025

### [2025-12-30] LEGAL — Versão final do contrato elaborada

Documento `LOTE_7___30122025.pdf` gerado como versão de referência com cláusulas
de APP, infraestrutura e prazos.

### [2025-12] LEGAL — Contrato de compromisso de venda e compra assinado

Partes: Sonia Padovan Catenne (vendedora) e Ana Carolina Queiroz, Filipe
Oliveira e Gustavo Oliveira (compradores). Gleba 7, 20.000 m², R$ 360.000,00.

### [2025-12] FINANCEIRO — Sinal pago: R$ 72.000,00 (20%)

Pagamento via Banco XP 348, Ag. 0001, CC 3810240.

---

## Próximos marcos esperados

**Site**

- Schema inicial do Supabase (users, content)
- Autenticação funcional
- Ingestão das transcrições dos cursos
- Assistente IA integrado
- Galeria de fotos e vídeos
- Release v1

**Imóvel**

- Cronograma de infraestrutura pela vendedora (prazo: 30 dias após escritura)
- Georreferenciamento da Gleba 7
- Abertura de matrícula individualizada
- Outorga da escritura definitiva
- Entrega do ponto de água (limite do lote)
- Entrega do ponto de energia CEMIG

---

_Atualizar este arquivo a cada evento relevante, por menor que pareça. O log é
memória do projeto._
