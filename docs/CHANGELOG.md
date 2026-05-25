# CHANGELOG — Alto da Brisa

Registro cronológico de marcos, eventos e entregas do projeto. Formato:
`[DATA] Categoria — Descrição`

Categorias: `LEGAL` | `OBRA` | `INFRA` | `SITE` | `DOC` | `FINANCEIRO` |
`DECISÃO`

Ordem: mais recente no topo.

---

## 2026

# Inserts para CHANGELOG.md

### [2026-05-25] DOC — Plano de Reformulação dos Módulos criado (D015)

Documento `docs/design_system/reformulacao_modulos.md` criado. Estabelece
processo de trabalho módulo a módulo para entregar leitura ativa no portal:
pacote de 7 minutos no topo com recursos visuais específicos por natureza de
conteúdo, aprofundamento textual por clique.

Ordem proposta dos 12 módulos, com Módulo 1 como piloto para ajuste do processo.
Critério de pronto definido por módulo: visualização rica funcional + leitura
completa acessível + navegação intra-página + responsivo 320-1280px + Lighthouse
Accessibility ≥ 90.

D014 permanece válido como camada base. D015 adiciona camada específica por
módulo acima dela.

---

### [2026-05-25] DECISÃO — Conteúdo do portal: leitura ativa por módulo (D015)

Validação visual de D014 implementado mostrou que o resultado, embora
estruturalmente correto, entrega leitura passiva. Decisão D015 abre ciclo de
reformulação módulo a módulo, com recursos visuais específicos por natureza de
conteúdo, para atender a intenção original do portal (densidade variável de
consumo).

---

### [2026-05-25] SITE — Componentes D014 implementados e integrados às 88 aulas

Implementação completa dos componentes de conteúdo especificados em D014:

- `<Callout>` (atencao / dica / exemplo) com barra lateral colorida e eyebrow
  tipográfico em small caps
- `<Citacao>` em Cormorant Garamond italic, sem caixa, com atribuição em small
  caps quando presente
- `<Tabela>` com transformação responsiva em CSS puro: tabela tradicional em
  desktop, cards empilhados em mobile (sem scroll horizontal)
- `<ProcessFlow>` com parser do bloco markdown customizado `flow`: horizontal
  com setas tipográficas em desktop, vertical com conectores em mobile

Componentes localizados em `site/src/components/content/`. Roteamento em
`site/src/components/Markdown.tsx` via componentes custom do react-markdown:
detecta GFM-alert (`> [!tipo]`) na AST hast e roteia para `<Callout>`,
blockquotes sem `[!` viram `<Citacao>`, code blocks com linguagem `flow` viram
`<ProcessFlow>`, tabelas markdown viram `<Tabela>`.

Tipografia global atualizada em `site/src/app/globals.css`: corpo 17px mobile /
18px desktop, line-height 1.7, largura máxima de leitura ~65 caracteres
(`prose-content` = 65ch).

Ingestão concluída via `scripts/consolidar_temas.py`: 88 aulas reais

- Aula 25 ausente com callout direcionando para Aula 26, distribuídas em 12
  arquivos por módulo em `site/content/temas/`. Headings das aulas rebaixados 2
  níveis para manter hierarquia sob `### N. Título`. Conversão dos 3 ASCII art
  (módulo 2) para blocos `flow` aplicada. Transcrições não renderizadas no
  front, conforme D013.

Página `[slug]/page.tsx` ajustada: aulas abertas por default (sem accordion),
TOC sticky em desktop (≥1024px) com âncoras, seção `## Transcrição` oculta no
render.

Componente legado `Callout.tsx` (v0) removido após confirmar ausência de
importadores.

Build limpo, 12 rotas SSG geradas, validação visual no browser completada pelo
Tech Lead.

---

### [2026-05-24] DOC — Componentes de Conteúdo especificados (D014)

Especificação dos quatro componentes que renderizam o conteúdo das aulas no
portal: `<Callout>` (com variantes atenção/dica/exemplo, total 292 ocorrências
no acervo), `<Tabela>` (27 ocorrências, com transformação tabela→cards em
mobile), `<Citacao>` (269 ocorrências, tipografia expressiva sem caixa),
`<ProcessFlow>` (sequências de etapas, alimentado por bloco markdown customizado
`flow`).

Princípios mandatórios definidos: mobile-first absoluto entre 320px e 1280px,
sem hover-only, largura de leitura ~65 caracteres, texto base 17px mobile / 18px
desktop, line-height 1.7. Documentado em
`docs/design_system/componentes_conteudo.md`.

Auditoria estrutural (`scripts/audit_aulas.py`) executada antes da
especificação, gerando `build/audit_report.md` e `build/audit_inventario.json`
com inventário completo: 1.104 headings, 774 subseções inline, 3.549 itens de
lista, 27 tabelas, 3 ASCII art a converter para `<ProcessFlow>`.

---

### [2026-05-24] SITE — Auditoria estrutural e normalização de marcadores

Script `scripts/audit_aulas.py` (Python puro, sem API, custo zero) varreu as 89
aulas em `build/aulas/`, detectou e normalizou 5 callouts com marcadores fora do
padrão (`[!atenção]` → `[!atencao]`, `[!importante]` → `[!atencao]`, etc), e
gerou relatório completo de inventário estrutural. Mapa de normalização cobre
variantes acentuadas, em maiúsculas e equivalentes em outras grafias.

Estado final do acervo: 88 OK, 1 AUSENTE legítima (Aula 25), 0 erros, 0
marcadores fora do padrão. Pronto para ingestão em `site/content/`.

---

### [2026-05-23] SITE — Re-extração das 88 aulas concluída (D012)

Pipeline `scripts/extract_aulas.py` com ranqueamento por termos-âncora em
`knowledge/termos_aulas.json` concluído após 3 rodadas (batch + 2 resumes para
corrigir erros transientes). Resultado final:

- 88 aulas com conteúdo curado de qualidade editorial em
  `build/aulas/{modulo}_{aula}.md`
- 1 aula ausente legítima (Aula 25, "Estudo de Caso 1" — conteúdo fundido na
  Aula 26)
- 0 erros
- Custo total acumulado: ~$11 (~R$60) ao longo de 3 rodadas
- Modelo: `claude-sonnet-4-5-20250929`
- Budget final: 150k tokens cacheados por aula (reduzido de 180k após estouro
  causado por tokenização PT-BR ~15% maior que estimativa chars/4)

Inventário estrutural do acervo: 292 callouts (135 atenção, 108 dica, 49
exemplo), 27 tabelas comparativas, 269 blockquotes não-callout, 774 subseções
inline, 1.104 headings. Volume e diversidade justificam componentes próprios
documentados em D014.

---

### [2026-05-23] SITE — Pipeline de extração com retry, throttle e prompt caching

Hardening do `scripts/extract_aulas.py` para suportar batch das 89 aulas em
conta Tier 1 da Anthropic (30k input tokens/min). Adicionado:

- Retry com `retry-after` da Anthropic para 429 (rate limit)
- Retry com backoff exponencial (2s, 4s, 8s, 16s, 32s) para 500/529 (server
  errors transientes)
- Retry curto para `APIConnectionError`
- Throttle preventivo: janela móvel de 60s rastreando tokens consumidos, pausa
  antes de estourar 85% do TPM
- Prompt caching com `cache_control: ephemeral` ativado automaticamente quando
  aulas adjacentes têm seleção de gravações idêntica; desligado quando seleção é
  única (evita pagar cache_write sem reuso)
- Ordenação inteligente do loop (aulas com mesma seleção agrupadas) para
  maximizar reuso de cache

Saída persiste em arquivos individuais com header HTML de metadados (tokens,
custo, status), permitindo `--resume` ao re-rodar.

---

### [2026-05-22] DOC — Termos-âncora curados para ranqueamento por aula

Arquivo `knowledge/termos_aulas.json` criado com termos-âncora para cada uma das
89 aulas do curso. Curadoria manual, considerando:

- Termos do título (e variações)
- Jargão dos professores observado nas transcrições polidas ("pedra arrumada" =
  alicerce, "concreto ciclópico" = concreto simples, "estribado" = forte, etc)
- Negative anchors para distinguir aulas vizinhas dentro do mesmo módulo

O arquivo alimenta o ranqueamento por aula em `extract_aulas.py`: para cada
aula, busca em todas as 21 gravações, pondera termos compostos (peso 3) vs
simples (peso 1), e seleciona as gravações mais relevantes que caibam no budget
de contexto.

---

### [2026-05-22] SITE — Descoberta: conteúdo das aulas v2 era lixo do scraper Kiwify

Auditoria do conteúdo em `knowledge/temas_v2/` (gerado em D008 e polido em D010)
revelou que de 89 aulas previstas no curso, 67 estavam efetivamente vazias na
seção `## Aulas`. As "aulas" eram apenas resíduos do scraper Kiwify ("[sem
descrição]", "A senha para abrir o arquivo é seu e-mail", links de Google Drive)
— não conteúdo de aula. O conteúdo real do curso existia, mas estava só nas
seções `## Transcrição` (21 gravações concatenadas como blocos não segmentados
por aula).

Descoberta motivou a re-extração completa documentada em D012.

---

### [2026-05-22] SITE — Foundation Entrega 1 construída (D011)

Composição visual do portal estabelecida em Next.js 16 + Tailwind v4

- next/font + React Compiler:

* Tokens da paleta Alto da Brisa via `@theme` em `globals.css`
* Fontes Cormorant Garamond, Lato e Montserrat via `next/font/google`
* 12 componentes-base em `site/src/components/` (Container, Header, Footer,
  SectionEyebrow, Tag, Callout v0, HighlightBox, Accordion, TemaCard, Toc,
  EmConstrucao, Markdown, ClaudinhoFloatingButton)
* Parser de markdown customizado em `site/src/lib/temas.ts`
* Páginas-âncora montadas: homepage, `/conhecimento`, `/conhecimento/[slug]`
  (com SSG via `generateStaticParams`), `/galeria`, `/dashboard`, `/claudinho`,
  `/login`, `/solicitar-acesso`
* Validador de rotas em `site/scripts/check_routes.mjs` confirmando 17/17 rotas
  respondendo 200

Bug corrigido durante construção: regex JavaScript não suporta `\Z` como anchor
de fim de string (interpreta como caractere literal Z), substituído por
`(?![\s\S])` no parser. Sem o fix, módulo 4 perdia a aula 27 por parsing
terminar prematuramente no Z de uma URL Google Sheets.

Não commitado imediatamente — aguarda re-extração das aulas (D012) e
implementação dos componentes de conteúdo (D014) para commit unificado.

---

### [2026-05-21] DOC — Avatar do Claudinho da Brisa salvo no projeto

Libélula estilizada (referência pessoal — tatuagem no pescoço do Tech Lead)
finalizada como avatar oficial do assistente. Salva em `site/public/claudinho/`
em três variações: SVG (fonte), PNG 256×256 (avatar) e PNG 512×512 (hero). Sem
variação claro/escuro por hora. Padding interno de ~20% no canvas para render
correto em círculo (`border-radius: 50%`).

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
