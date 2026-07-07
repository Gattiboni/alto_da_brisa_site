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

### [2026-07-07] D019 — Arquitetura dos pacotes de 7 min: conteúdo curado em site/content/pacotes/, composição condicional

**Contexto:** O D015 exige um "pacote de 7 min" no topo de cada módulo
reformulado. O `consolidar_temas.py` sobrescreve `site/content/temas/`
preservando apenas Título e Visão Geral (D016) — o pacote precisa de um lar que
sobreviva à re-consolidação.

**Alternativas consideradas:**

- Seção nova preservada pelo consolidar: mais estado especial num script que
  deveria ser burro; mistura conteúdo gerado e curado no mesmo arquivo
- Arquivo em `knowledge/pacotes/`: pacote não tem etapa de geração (fonte =
  forma consumida) e a página lê fora do root de deploy (`site/`) — fragilidade
  gratuita
- Arquivo próprio em `site/content/pacotes/{slug}.md`, composto pela página

**Decisão:** Arquivo próprio em `site/content/pacotes/`. Regras: (i) `pacotes/`
é curado à mão, **nunca** gerado — espelho simétrico do D016 (`temas/` é gerado,
nunca editado); (ii) composição condicional: a página renderiza a seção do
pacote apenas se o arquivo existir — módulos sem pacote renderizam como antes,
intocados; (iii) componentes visuais entram como fenced blocks roteados pelo
`Markdown.tsx` (convenção do D014); dados vivem no markdown, nunca no
componente; (iv) norma de manutenção: o pacote duplica números por design
(camada de destilação); cada bloco declara a(s) aula(s) de origem em comentário,
e **editou aula → confere os blocos que a citam**; (v) aulas permanecem abertas
por default, com colapso individual disponível e regra da âncora (navegar pra
`#aula-N` colapsada abre a aula) — spec em
`docs/design_system/modulo_06_wireframe.md`.

**Racional:** Incrementalidade (11 módulos não sabem que o piloto existe),
modularidade (pluga/despluga por existência de arquivo, sem flag), zero dívida
(script de consolidação continua burro; nenhuma lógica de preservação nova).
Wireframe completo do piloto: `docs/design_system/modulo_06_wireframe.md`.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-07-07] D016 — Fonte de verdade do conteúdo: knowledge/aulas/ versionado; site/content/temas/ é saída gerada

**Contexto:** A retomada revelou que `build/aulas/` (89 arquivos, fonte curada
real das aulas) estava fora do git — `build/` está no `.gitignore` — e que o
`consolidar_temas.py` sobrescreve `site/content/temas/` integralmente,
preservando apenas Título e Visão Geral. Edição manual no site não é durável;
perda do disco local tornaria o acervo curado irrecuperável (`extract_aulas.py`
custa API e não é determinístico — regeneraria texto diferente).

**Alternativas consideradas:**

- Negação no `.gitignore` (`build/*` + `!build/aulas/`): zero mudança de script,
  mas perpetua fonte editável dentro de diretório cuja convenção declarada é
  "descartável"
- Congelar o pipeline e editar `site/content/temas/` à mão: mata o pipeline e
  cria fork de conteúdo
- Mover `build/aulas/` → `knowledge/aulas/` e ajustar paths nos scripts

**Decisão:** Mover. Política de conteúdo a partir de agora: (i) fonte de verdade
= `knowledge/aulas/` (versionada); (ii) `site/content/temas/` é saída gerada —
nunca editar à mão; (iii) edição de conteúdo = editar a fonte + re-rodar
`consolidar_temas.py`; (iv) `extract_aulas.py` é geração inicial — re-rodar
sobre aula curada exige reconciliação explícita, nunca sobrescrita cega.

**Racional:** `build/` significa "regenerável e descartável" por convenção — é
exatamente por isso que estava no gitignore. Conteúdo curado editável à mão é
fonte, não artefato de build. O conteúdo estava no lugar semanticamente errado;
mover corrige de uma vez ("bem feito UMA vez").

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-07-07] D017 — Tratamento das 9 aulas ausentes; Aula 32 preenchida com conteúdo de slides

**Contexto:** O censo real do acervo é **80 aulas com conteúdo / 9 ausentes** —
não "88 + 1" como registrado no audit, CHANGELOG e memory. Oito aulas
renderizavam o heading cru `AULA_AUSENTE` para o usuário (02: 9, 13 · 03: 18,
20, 21 · 06: 32, 39 · 12: 89); apenas a Aula 25 tinha callout de
redirecionamento. Causa raiz: o classificador do `audit_aulas.py` só olhava o
header `status:`, e as 8 aulas onde o LLM devolveu `AULA_AUSENTE` no corpo
passaram como OK. A Aula 32 (Viga Baldrame) é elo estrutural do Módulo 6 —
referenciada nas aulas 31, 35 e 36 — e possui conteúdo completo na geração
legada baseada em slides (`knowledge/temas/`).

**Alternativas consideradas (Aula 32):** manter ausente por pureza de fonte (só
transcrições) vs preencher com o conteúdo dos slides.

**Decisão:** Aula 32 preenchida a partir dos slides, convertida ao padrão das
demais aulas, com nota de proveniência visível. As outras 8 ausências unificadas
na convenção `status: ausente` (mecanismo do callout da Aula 25), preservando as
justificativas existentes. Classificador do `audit_aulas.py` corrigido para
detectar também corpo `AULA_AUSENTE`.

**Racional:** Buraco no elo estrutural do módulo em nome de pureza de fonte é
dívida disfarçada de rigor. E ferramenta de auditoria que classifica errado
mente de novo na próxima rodada — conserta-se a causa, não o sintoma.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-07-07] D018 — Calculadora de sapata fora do piloto M6

**Contexto:** A Aula 31 traz fórmula e exemplo numérico prontos (área = carga ÷
tensão admissível do solo), candidato natural a componente interativo.

**Decisão:** Fora do escopo do piloto. Reavaliar após o piloto concluído.

**Racional:** Único candidato interativo do módulo; incluí-lo adiciona escopo e
risco sem provar a hipótese central do D015 (densidade variável de consumo).

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-05-25] D015 — Conteúdo do portal: leitura ativa por módulo, não leitura linear

**Contexto:** Os componentes D014 foram implementados e integrados às 88 aulas.
Validação visual no browser revelou que o resultado, embora estruturalmente
correto e tipograficamente refinado, é fundamentalmente **leitura passiva**:
parágrafos sequenciais com poucos pontos de entrada visuais. O leitor entra na
página, rola, lê tudo — ou abandona.

A intenção original do portal sempre foi outra: oferecer **densidade variável de
consumo**. Pacote de 7 minutos no topo (cards, infográficos, linhas de tempo,
comparativos visuais), com aprofundamento textual disponível por clique.
Referência mental: experiências como NotebookLM, onde o usuário escolhe o nível
de imersão.

D014 entregou a fundação tipográfica e os 4 componentes universais (Callout,
Citacao, Tabela, ProcessFlow) que permanecem válidos como elementos básicos. Mas
o portal precisa de uma camada superior: **recursos visuais variados,
específicos por natureza de conteúdo**, que sirvam como pontos de entrada antes
da leitura corrida.

**Alternativas consideradas:**

- Implementar a camada visual avançada como sistema único de componentes "para
  todos os módulos": cria componentes genéricos demais, casa mal com módulos de
  naturezas distintas (M2 conceitual, M6 técnico-processual, M10 decisorial)
- Refazer toda a base visual de uma vez: caro, arriscado, perde a Foundation que
  já funciona
- Reformulação módulo a módulo, com pesquisa de padrões específicos por módulo,
  prototipagem visual em wireframe markdown antes da implementação, validação
  iterativa

**Decisão:** Reformulação módulo a módulo, documentada em
`docs/design_system/reformulacao_modulos.md`. Cada módulo é abordado como
projeto próprio:

1. Leitura completa do conteúdo do módulo
2. Identificação de pontos de conteúdo que pedem visualização (timeline,
   comparativo, matriz de decisão, processo, etc)
3. Proposta de wireframe em markdown (componentes específicos do módulo + reuso
   dos D014 onde fizer sentido)
4. Aprovação do Tech Lead
5. Implementação
6. Validação visual
7. Padrões emergentes são extraídos para reuso em módulos seguintes

**Racional:** Cada módulo tem natureza editorial diferente. Generalizar
prematuramente produziria a mesma "leitura passiva" que D014 está entregando
hoje. Iteração módulo a módulo permite aprender o que cada tipo de conteúdo
pede, e extrair padrões reusáveis a posteriori, não a priori.

D014 permanece válido como **camada base tipográfica e dos 4 componentes
universais**. D015 não revoga D014 — adiciona uma camada acima dela, específica
por módulo.

**Pós-decisão:** Próximo ciclo começa pelo **Módulo 6 (Fundações)** como piloto.
Resultado do piloto informa a abordagem dos demais 11. Pendências de navegação
intra-aula (botões "tópico anterior" / "próximo" / "voltar ao topo") e Claudinho
contextual entram como itens paralelos, não bloqueantes da reformulação.

**Revisão [2026-07-06]:** O piloto foi trocado de Módulo 1 para **Módulo 6
(Fundações)**. O critério de escolha do piloto passou de "menor risco de
processo" (M1 é o menor, 5 aulas, porta de entrada) para "prova de conceito
visual honesta". Razão: o M1 (Introdução) é texto-pesado por natureza e daria
pouco material pra exercitar timelines, matrizes e fluxogramas — um piloto morno
que não provaria a hipótese. Um módulo denso e técnico-processual como Fundações
força os componentes ricos a aparecerem: se funciona no difícil, funciona em
qualquer um. O M1 volta pra ordem mais à frente, quando já houver padrões
visuais maduros pra herdar em vez de inventar. Ordem completa em
`reformulacao_modulos.md` v1.1, seção "Critério do piloto".

**Responsável:** Alan Gattiboni **Status:** Ativa (revisada 2026-07-06)

---

### [2026-05-24] D014 — Componentes de Conteúdo do portal: paleta enxuta com transformação responsiva

**Contexto:** Após a re-extração das 88 aulas (D012), o inventário estrutural
revelou volumes que justificam componentes próprios: 292 callouts
(atenção/dica/exemplo), 27 tabelas comparativas, 269 blockquotes não-callout,
~1.100 headings e ~3.500 itens de lista. O conteúdo precisa ser legível em todos
os contextos de leitura do projeto — celular em reunião, no carro, em sítio com
pouca luz — o que torna mobile-first uma obrigação não-negociável (não uma
preferência).

**Alternativas consideradas:**

- Adotar biblioteca pronta (shadcn/ui, Radix, Mantine): qualidade visual
  baixa-média para conteúdo editorial, identidade "SaaS app" contamina a
  identidade contemplativa do projeto, custo de customização alto
- Pesquisar referências via Perplexity AI: tentado, resultados genéricos demais;
  Claude tem contexto direto do projeto e produz proposta mais aderente
- Especificar componentes próprios alinhados à identidade visual já definida em
  D006

**Decisão:** Quatro componentes próprios, especificados em
`docs/design_system/componentes_conteudo.md`:

1. `<Callout>` — uma estrutura única, diferenciada por barra lateral colorida
   (atenção: carvão, dica: verde, exemplo: areia) e eyebrow em small caps. Sem
   variações visuais drásticas: callouts são frequentes (292), variar muito
   polui a página.
2. `<Tabela>` — tabela tradicional em desktop, transformação automática em cards
   empilhados em mobile. Resolve o problema de tabelas com 4+ colunas em 375px
   sem recorrer a scroll horizontal.
3. `<Citacao>` — tipografia expressiva sem caixa nem borda. Cormorant Garamond
   italic grande, atribuição em small caps. Diferencia-se do callout pelo gesto
   tipográfico, não pelo container.
4. `<ProcessFlow>` — fluxo horizontal em desktop, vertical em mobile, alimentado
   por bloco de código markdown customizado com linguagem `flow`.

**Princípios mandatórios para qualquer componente de conteúdo:**

- Funcionalidade total entre 320px e 1280px sem hover-only
- Largura de leitura ~65 caracteres em desktop
- Texto base 17px mobile / 18px desktop (acima do padrão da web)
- Line-height 1.7 no corpo
- Zero dependência de hover para acessar informação
- Estados de foco visíveis para navegação por teclado

**Racional:** Componentes próprios alinhados à identidade contemplativa do
projeto produzem leitura melhor que biblioteca pronta genérica. Especificação
simples (uma variante por componente em vez de três ou quatro) reduz superfície
de manutenção sem sacrificar capacidade — diferenciação por tipo de callout, por
exemplo, vem de barra lateral + eyebrow, não de fundos distintos que criariam
visual ruído nas 292 ocorrências do acervo. A transformação tabela→cards em
mobile é a decisão tecnicamente mais complexa (parser customizado de markdown),
mas é a única forma de tabelas com muitas colunas serem legíveis em phone.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-05-23] D013 — Transcrições como fonte RAG, não conteúdo de front

**Contexto:** As 21 gravações de áudio polidas em `curso_limpo.md` totalizam
~2.5MB de transcrição falada. Renderizar isso no front por módulo, como estava
acontecendo nas páginas de `/conhecimento/[slug]`, gerava arquivos de 2MB por
módulo (módulo 4) e poluía a experiência de leitura: o usuário via blocos
enormes de fala não-segmentada mistos com o conteúdo curado das aulas.

**Alternativas consideradas:**

- Manter transcrições no front, esconder com accordion fechado por padrão: ainda
  carrega 2MB no cliente, ainda confunde a estrutura do conteúdo
- Remover transcrições completamente: perde-se a fonte de verdade que o
  Claudinho da Brisa pode consultar para responder perguntas específicas que
  extrapolem o conteúdo curado das aulas
- Separar transcrições em arquivos próprios, fora do conteúdo renderizado,
  disponíveis apenas para RAG

**Decisão:** Transcrições saem do front. As 21 gravações ficam em
`build/transcricoes/01.md` a `21.md` (e depois em `site/content/transcricoes/`),
com header indicando os módulos que cobrem. O front renderiza apenas o conteúdo
curado em `site/content/temas/`. O Claudinho da Brisa, em fase posterior, indexa
transcrições no pgvector com peso menor, como fallback quando o conteúdo curado
não responde a pergunta específica do usuário.

**Racional:** A unidade de leitura humana é a aula curada. A unidade de pesquisa
do RAG pode ser mais granular e incluir as transcrições brutas como contexto
secundário. Separar reduz peso do front em ordem de magnitude (cada módulo cai
de 2MB para ~100KB), simplifica a experiência de leitura, e ainda preserva a
fonte de verdade para consultas profundas via Claudinho.

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-05-23] D012 — Re-extração das 88 aulas via Claude API com ranqueamento por termos-âncora

**Contexto:** A base gerada em D008 (mapeamento gravação→módulo via Claude API)
produziu 12 arquivos `.md` por módulo, mas a seção de aulas individuais dentro
de cada módulo continha apenas resíduos do scraper Kiwify ("[sem descrição]", "A
senha para abrir o arquivo é seu e-mail", links de Google Drive). De 89 aulas
previstas no curso, 67 estavam efetivamente vazias no front, apesar do conteúdo
existir nas 21 gravações de áudio. O conteúdo dos professores estava lá; só não
havia sido segmentado por aula.

**Alternativas consideradas:**

- Aceitar o estado atual e renderizar as aulas vazias como "em processamento":
  frustra o leitor, contradiz a vocação do projeto
- Tentar segmentar manualmente as 21 gravações em 89 aulas: trabalho humano de
  dias, com qualidade duvidosa
- Pipeline Claude API com prompt curado por aula, usando o mapeamento original
  (`mapeamento.json`): segmenta corretamente as aulas que o mapeamento conhece,
  mas falha nas que o mapeamento errou ou subestimou
- Pipeline Claude API com ranqueamento automático de gravações por aula: para
  cada uma das 89 aulas, ranquear todas as 21 gravações por hits de
  termos-âncora específicos da aula e enviar as top-N que caibam em ~150k tokens

**Decisão:** Pipeline Claude API (Sonnet 4.5) com ranqueamento por
termos-âncora. Termos curados manualmente em `knowledge/termos_aulas.json` (89
entradas). Para cada aula, `extract_aulas.py` busca os termos em todas as 21
gravações, pondera termos compostos (3x peso) vs simples (1x), seleciona top-N
gravações até cair em 150k tokens, e chama Claude API com prompt calibrado para
extrair somente o conteúdo da aula específica e ignorar tudo que pertença a
aulas vizinhas ou outros módulos. Se a aula não estiver coberta, devolve
`AULA_AUSENTE` (preferir omissão à fabricação).

Custo total acumulado: ~$11 (~R$60) ao longo de 3 rodadas (batch + 2 resumes
para corrigir erros). Resultado: 88 OK, 1 ausente legítima (Aula 25, "Estudo de
Caso 1" — conteúdo fundido na Aula 26), 0 erros.

**Tecnicalidades resolvidas durante o processo:**

- Erro 400 (prompt too long): budget de 180k tokens estourava por ~7-15k devido
  a tokenização real PT-BR ser ~15% maior que estimativa chars/4. Ajustado para
  150k.
- Erro 500/529 transientes: retry com backoff exponencial (2s, 4s, 8s, 16s,
  32s), até 5 tentativas.
- Rate limit 429 (Tier 1 = 30k input tokens/min): throttle preventivo + retry
  com `retry-after` do header da Anthropic.
- Cache prompt: ativado quando aulas adjacentes têm seleção de gravações
  idêntica, desligado quando seleção é única (evita pagar cache_write sem
  reuso).
- Marcadores de callout fora do padrão: detectados e normalizados
  automaticamente por `audit_aulas.py` (`atenção` → `atencao`, `importante` →
  `atencao`, etc).

**Pós-decisão:** As 88 aulas ficam em `build/aulas/{modulo}_{aula}.md` com
header HTML de metadados (tokens, custo, status). Consolidação em 12 arquivos
finais (`build/temas_v3/`) e ingestão em `site/content/temas/` ficam para o
ciclo de release. As 21 transcrições viram fonte RAG separada (ver D013).

**Responsável:** Alan Gattiboni **Status:** Ativa

---

### [2026-05-22] D011 — Foundation Entrega 1: composição visual e parser de markdown

**Contexto:** A Foundation visual do portal precisa estar resolvida antes de
implementar componentes complexos: tipografia carregada, paleta como tokens
reutilizáveis, componentes-base estabelecidos (Container, Header, Footer, Toc,
Tag, Markdown), parser de markdown funcional e rotas das páginas-âncora montadas
(homepage, `/conhecimento`, `/conhecimento/[slug]`, `/galeria`, `/dashboard`,
`/claudinho`, `/login`, `/solicitar-acesso`). Sem isso, qualquer componente novo
nasce sem casa.

**Alternativas consideradas:**

- Adotar template ou starter pronto (Vercel templates, shadcn starter):
  contradiz a identidade visual já definida em D006, importa convenções de SaaS
  que não casam com o projeto
- Construir do zero direto em Next.js 16 + Tailwind v4 + next/font: controle
  total, alinhado à identidade, sem dívida importada

**Decisão:** Foundation construída do zero. Tailwind v4 com tokens da paleta via
`@theme` em `globals.css`. Fontes Cormorant Garamond, Lato e Montserrat via
`next/font/google` no `layout.tsx`. 12 componentes base em
`site/src/components/`: Container, Header, Footer, SectionEyebrow, Tag, Callout
(versão inicial, posteriormente substituída pela especificação D014),
HighlightBox, Accordion, TemaCard, Toc, EmConstrucao, Markdown,
ClaudinhoFloatingButton. Parser de markdown customizado em
`site/src/lib/temas.ts` lendo de `site/content/temas/`. Validador de rotas em
`site/scripts/check_routes.mjs` confirmando 17/17 rotas respondendo 200.

**Bugs resolvidos durante a construção:**

- Regex JavaScript: `\Z` interpretado como caractere literal "Z", não como
  anchor de fim de string. Substituído por `(?![\s\S])` no parser de aulas,
  corrigindo perda do módulo 4 (parsing parava no Z de uma URL Google Sheets).
- Tailwind v4 sem `tailwind.config.ts`: paleta vai direto em `globals.css` com
  `@theme`. Estabelecida a sintaxe correta.

**Racional:** Foundation própria mantém a identidade contemplativa do projeto
(D006), evita importar convenções estranhas, e estabelece a base sobre a qual
D014 (componentes de conteúdo) pode ser implementado sem conflito visual.
Validação por sandbox confirmou build OK, 17/17 rotas 200, antes de instalar
localmente no ambiente do Tech Lead.

**Pós-decisão:** Não commitado imediatamente porque a re-extração das aulas
(D012) precisava acontecer antes — sem conteúdo bom, a Foundation entraria no ar
mostrando aulas vazias. Commit unificado de Foundation + 88 aulas + componentes
D014 + decisions D011-D014 acontece no ciclo de release.

**Responsável:** Alan Gattiboni **Status:** Ativa

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
