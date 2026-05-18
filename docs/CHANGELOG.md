# CHANGELOG — Alto da Brisa

Registro cronológico de marcos, eventos e entregas do projeto. Formato:
`[DATA] Categoria — Descrição`

Categorias: `LEGAL` | `OBRA` | `INFRA` | `SITE` | `DOC` | `FINANCEIRO` |
`DECISÃO`

Ordem: mais recente no topo.

---

## 2026

### [2026-05-18] SITE — Polimento determinístico dos 12 módulos de conhecimento

Pipeline determinístico Python (sem API, custo zero) executado sobre os 12
arquivos `.md` em `knowledge/temas/`, com saída em `knowledge/temas_v2/`. Módulo
4 (Orçamento) processado primeiro com normalização estrutural completa
(`## Aula N:` → `### N.` dentro de `## Aulas`, gravações consolidadas em
`## Transcrição` no final). Outros 11 processados em batch, preservando
estrutura existente (Visão Geral / Aulas / Transcrição) e aplicando limpeza.

Operações: remoção de vícios de fala inline (`, né?`, `, tá?`, `Peraí,`,
`Gente,` etc), remoção de linhas-confirmação isoladas (`Exato.`, `Isso.`,
`Beleza.`), juncão de quebras-preguiçosas de copy-paste, normalização de
parágrafos > 600 chars, detecção (não correção) de CamelCase suspeito para
revisão manual.

Resultados:

- Módulo 4: 2.015.079 → 2.003.001 chars (-12.078, -0.6%)
- Outros 11: reduções entre -0.3% e -0.9% cada
- Zero perda de palavras-chave técnicas (CUB, EVF, NPR, R$, valores numéricos,
  nomes próprios)
- Zero deformações de palavras acentuadas (bug Unicode de regex corrigido com
  classes explícitas)
- Espaços colados detectados: majoritariamente neologismos legítimos
  (ConstruTinder, WhatsApp, WoodFrame, PowerPoint, LightShield, InfoDev) +
  poucos erros isolados de copy-paste mantidos como estão por irrelevância

Scripts: `scripts/polish_clean_modulo4.py`, `scripts/polish_clean_batch.py`,
`scripts/polish_common.py`.

Logs em `knowledge/temas_v2/*_polish_log.txt`.

---

### [2026-05-18] DOC — Avatar do Claudinho da Brisa criado

Ilustração 3D estilizada de uma libélula (referência pessoal — tatuagem no
pescoço do Tech Lead) finalizada como avatar oficial do Claudinho da Brisa.
Posicionamento e specs finais (tamanho, variações, contextos de uso) a definir
em revisão de aplicação.

---

### [2026-05-01] DOC — Mapeamento georreferenciado do projeto criado

Arquivo `docs/geo/alto_da_brisa_geo_v1.kmz` adicionado como fonte de verdade
espacial do projeto. Contém: 3 polígonos (`alto_da_brisa_area_expandida` para o
bounding box do terreno 3D, `sitio_sao_miguel` para o sítio inteiro,
`alto_da_brisa_perimetro` para a Gleba 7) e 9 pins (casas planejadas, área
social, airbnb, porteira, entrada do sítio, referência na estrada do Juncal).
Coordenadas em WGS84 catalogadas em `docs/geo/features.md`.

---

### [2026-05-01] DECISÃO — Pipeline 3D definido para homepage

Decisão D009 registrada: homepage será mapa 3D interativo com terreno gerado via
Blender GIS (SRTM 30m via OpenTopography), estilização Cenário A (cor sólida
derivada da paleta, sem fotorrealismo), integração Next.js via
react-three-fiber. Rejeitadas alternativas baseadas em embed (3D-Mapper,
maps3d.io, Sketchfab) por perda de controle sobre câmera, cliques e integração
com Claudinho da Brisa.

---

### [2026-04-29] SITE — Base de conhecimento gerada: 12 módulos organizados por tema

Pipeline completa de knowledge base executada. 21 gravações de áudio mapeadas às
89 aulas do curso "Casa de Baixo Custo Sustentável" (Amanda & Fernando) via
Claude API. Gerados 12 arquivos `.md` em `knowledge/temas/`, organizados por
módulo temático. Módulo 4 (Orçamento) estruturado por aula específica (24–27).
Scripts: `organizar_com_claude.py`, `corrigir_mapeamento.py`,
`reestruturar_orcamento.py`.

---

### [2026-04-29] SITE — Descrições das 89 aulas capturadas via scraper JS

Script `acbcs_scraper_v2.js` executado no DevTools do curso Kiwify. Capturou
título, módulo e descrição de cada aula navegando via Vue Router (sem reload).
Output salvo em `knowledge/descricoes_das_aulas.md`. Usado como âncora semântica
para o mapeamento gravação→aula.

---

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
