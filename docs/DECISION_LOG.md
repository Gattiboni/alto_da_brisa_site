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

### [2026-05-18] D010 — Polimento determinístico da base de conhecimento

**Contexto:** A base de conhecimento gerada em D008 ainda contém vícios de fala,
linhas-confirmação isoladas e artefatos de transcrição/copy-paste que prejudicam
tanto a leitura humana quanto a qualidade do RAG do Claudinho da Brisa. Material
de origem é audio + slides; estilo de fala é conversacional e cheio de muletas.

**Alternativas consideradas:**

- Claude API revisando cada chunk: custo estimado R$15–25 com Sonnet, risco de
  alterar conteúdo técnico, ironia de gastar API processando conteúdo sobre
  construção de baixo custo
- Estratificação visual (Visão Geral visível / Aulas expandível / Transcrição
  oculta) sem tocar no conteúdo: paliativo que carrega dívida técnica de
  conteúdo sujo indefinidamente
- Polimento determinístico Python puro: regex calibrados para vícios óbvios,
  zero custo, zero risco de alteração semântica, log auditável de tudo que muda

**Decisão:** Pipeline determinístico em Python puro, sem API. Limpeza
conservadora: remove apenas padrões claramente identificáveis como vício
(`, né?`, `, tá?`, `Peraí,` no início de frase, `Gente,` como muleta etc).
Detecta mas não corrige espaços colados (CamelCase) por risco alto de falso
positivo em nomes próprios e neologismos. Testes internos rodam antes de
qualquer escrita validando regex contra 28 palavras acentuadas que devem ficar
intactas.

**Racional:** Qualidade da fonte define qualidade do RAG. O polimento na fonte
pesa nada (1 segundo de processamento, custo zero) e elimina ruído que
contaminaria todas as consultas ao Claudinho da Brisa. A estratégia
determinística é também auditável: cada arquivo gera um log paralelo listando
linha-por-linha o que foi removido, permitindo verificação humana. Ambiente de
desenvolvimento (Linux + Python 3) e produção (Windows + Python 3.12) produzem
output bit-a-bit equivalente.

**Pós-decisão:** Saída em `knowledge/temas_v2/`. Originais preservados em
`knowledge/temas/` como fonte histórica intocada. Aplicações que consomem a base
(Claudinho da Brisa, páginas `/conhecimento/[slug]`) referenciam `temas_v2/`.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-05-01] D009 — Pipeline 3D para homepage interativa

**Contexto:** Homepage definida como mapa 3D interativo com ícones clicáveis
levando a subpáginas. Necessidade de gerar modelo 3D georreferenciado da área
Juncal → encosta sul do Sítio São Miguel, com estética alinhada à identidade
visual sóbria do projeto (não fotorrealista).

**Alternativas consideradas:**

- 3D-Mapper.com / maps3d.io com embed: perda de controle de câmera, cliques e
  integração com IA — incompatível com requisitos de interatividade
- Cesium ion + 3DTilesRendererJS: overkill para escala e ambição v1
- Sketchfab embed: perde controle de runtime, não integra com Next.js
- Pipeline próprio: Blender GIS + SRTM 30m + estilização Cenário A + Three.js

**Decisão:** Pipeline próprio. Terreno via Blender GIS (DEM SRTM 30m via
OpenTopography), estilização Cenário A (cor sólida derivada da paleta, sem
fotorrealismo, sem vegetação 3D), exportação `.glTF`, integração no Next.js via
react-three-fiber em fase posterior.

**Racional:** Controle total da estética, da câmera, das interações e da
integração com Claudinho da Brisa e ícones-clicáveis. Custo zero de ferramentas.
Cenário A casa com a identidade contemplativa do projeto e escala bem em mobile
com baixo peso de `.glTF`. Compatível com o princípio de zero dívida técnica e
autonomia documentado em D001. SRTM 30m é suficiente para a escala da
`area_expandida` (~1.18 km × 730 m); ALOS PALSAR 12.5m fica como upgrade
reservado caso resolução decepcione.

**Fonte de verdade espacial:** `docs/geo/alto_da_brisa_geo_v1.kmz`, com 3
polígonos (`alto_da_brisa_area_expandida`, `sitio_sao_miguel`,
`alto_da_brisa_perimetro`) e 9 pins. Catalogado em `docs/geo/features.md`.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-04-29] D008 — Estrutura da base de conhecimento: tema, não aula

**Contexto:** O curso tem 89 aulas em 21 gravações de áudio sem correspondência
1:1. Organizar por aula geraria arquivos fragmentados e inúteis para RAG. O
usuário do site nunca vai buscar "Aula 31" — vai buscar "fundações" ou "quanto
custa radier".

**Alternativas consideradas:**

- Um arquivo por aula (89 arquivos): fragmentação excessiva, gravações cobrindo
  múltiplas aulas geram duplicação
- Um arquivo único (blob): inviável para RAG, contexto gigante
- Um arquivo por módulo temático (12 arquivos): balanceia granularidade e
  riqueza

**Decisão:** 12 arquivos em `knowledge/temas/`, um por módulo. Módulo de
Orçamento (crítico) estruturado internamente por aula específica.

**Racional:** Unidade de busca do Claudinho da Brisa é o tema, não a aula.
Chunks de ~500 tokens por módulo vão para o pgvector. Usuário pergunta sobre
fundações e o RAG retorna o chunk certo do `06_fundacoes.md`.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-04-29] D007 — Claude API no pipeline offline de processamento

**Contexto:** O mapeamento de 21 gravações às 89 aulas exigia compreensão
semântica do conteúdo. Abordagem puramente por palavras-chave produzia falsos
positivos e módulos vazios.

**Alternativas consideradas:**

- Keyword matching estático: rápido, sem custo de API, mas impreciso
- Distribuição proporcional por contagem de aulas: sem semântica, erros nas
  bordas
- Claude API com amostragem em múltiplas posições: custo ~50k tokens total,
  classificação com confiança "alta" em 21/21 gravações

**Decisão:** Claude API (claude-sonnet-4) usada no pipeline offline de
organização. Não só no front com o usuário.

**Racional:** O custo de API para processamento offline é desprezível comparado
ao custo de uma base de conhecimento mal organizada que compromete a qualidade
do Claudinho da Brisa. Qualidade da fonte define qualidade do RAG.

**Responsável:** Alan Gattiboni **Status:** Ativa

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
