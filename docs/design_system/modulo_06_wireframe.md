# Wireframe — Módulo 6 (Fundações) — Piloto D015

Destino no repo: `docs/design_system/modulo_06_wireframe.md`
Etapa 2 do processo definido em `reformulacao_modulos.md`.
Representação textual/ASCII + comportamento. **Não é código React.**

---

## 0. Invariante de conteúdo

O pacote de 7 min é **camada aditiva**. Nenhuma aula é editada, resumida,
recortada ou ocultada por este wireframe. As 12 aulas do módulo continuam
renderizando completas, exatamente como saíram da Fase 3 (incluindo a Aula
32 preenchida e o callout da 39). Todo link do pacote desce para o texto
denso via contrato `#aula-N` — o mesmo generalizado e validado na Fase 3.

---

## 1. Arquitetura — onde o pacote vive

- **Arquivo:** `site/content/pacotes/06_fundacoes.md` — curado à mão,
  nunca gerado. Espelho simétrico do D016: `temas/` = gerado, nunca
  editar; `pacotes/` = curado, nunca gerar.
- **Composição:** `[slug]/page.tsx` verifica a existência de
  `site/content/pacotes/{slug}.md`. Existe → renderiza a seção Pacote
  antes da seção Aulas. Não existe → página renderiza como hoje.
  Os 11 módulos sem pacote não sabem que o piloto aconteceu.
- **Componentes no markdown:** fenced blocks roteados pelo
  `Markdown.tsx`, mesma convenção do ` ```flow ` (D014). Novos blocos
  deste piloto: ` ```tipos `, ` ```escalada `, ` ```custos `.
- **Proveniência:** cada bloco do pacote declara a(s) aula(s) de origem
  em comentário HTML na fonte (`<!-- fonte: aula 40 -->`). Não renderiza;
  serve à norma de manutenção (seção 8).

---

## 2. Estrutura da página do módulo

```
┌─────────────────────────────────────────────┐
│ (topbar / breadcrumb — inalterados)         │
├─────────────────────────────────────────────┤
│ # Fundações                                 │
│ Visão Geral (inalterada)                    │
├─────────────────────────────────────────────┤
│ ══ PACOTE · FUNDAÇÕES EM 7 MINUTOS ══       │  ← id="pacote"
│                                             │
│  Bloco 1 · A cadeia de cargas       (~30s)  │
│  Bloco 2 · O mapa dos tipos        (~2.5m)  │
│  Bloco 3 · A escalada de decisão   (~1.5m)  │
│  Bloco 4 · O caso IGO em números    (~1m)   │
│  Bloco 5 · Os inegociáveis          (~30s)  │
│                                             │
│  [ Ler o módulo completo ↓ ]                │  ← rola até #aulas
├─────────────────────────────────────────────┤
│ ## Aulas  (id="aulas")                      │
│ 29 … 40 — completas, abertas, inalteradas   │
└─────────────────────────────────────────────┘
```

- TOC sticky (desktop ≥1024px) ganha uma entrada no topo: "Pacote de
  7 min" → `#pacote`. Resto do TOC inalterado.

### Colapso de aulas (decisão do Tech Lead, 2026-07-07)

Aulas **abertas por default** (padrão de leitura atual, inalterado),
**com colapso individual disponível** por aula pra teste de UX:

- Controle no heading de cada aula; preferir `<details>/<summary>`
  nativo (teclado e a11y de graça, zero estado JS). Se o `page.tsx` já
  tem mecanismo de colapso, reusar — verificação na Etapa 0 da
  implementação, não presumir.
- **Regra da âncora:** navegar para `#aula-N` de uma aula colapsada
  **abre** a aula antes de rolar (o `<details>` nativo não faz isso
  sozinho — exige JS mínimo no hashchange/load). Sem essa regra, os
  links do pacote quebram silenciosamente pra quem colapsou.
- Estado não persiste (sem localStorage): recarregou, tudo aberto.
- Divisor visual entre pacote e aulas: mesma linguagem de `hr` + eyebrow
  da identidade (Montserrat label). Nada de card gigante envolvendo o
  pacote inteiro — o pacote é seção, não widget.

---

## 3. Pacote — bloco a bloco

### Bloco 1 — A cadeia de cargas  `<!-- fonte: aula 29 -->`

**Componente:** `ProcessFlow` (D014, reuso puro). Fluxo linear de 5 nós:

```
Laje ──► Vigas ──► Pilares ──► Fundação ──► Solo
```

Uma linha de legenda abaixo (Lato, body-small): "A fundação é o último
elo antes do solo — tudo que a casa pesa passa por ela."

Mobile: o ProcessFlow já resolve (comportamento herdado do D014).
Se o componente atual só renderiza horizontal e estourar em 320px com 5
nós, a correção é no ProcessFlow (quebra em coluna), não um componente
novo — registrar como ajuste, não invenção.

---

### Bloco 2 — O mapa dos tipos  `<!-- fonte: aulas 29–35 -->`

**Componente novo: `MapaTipos`** (contém as fichas — mapa e ficha são um
componente só; o mapa é o índice das fichas).

Desktop (≥768px) — três colunas por grupo, ficha expande no lugar:

```
  RASAS                    PROFUNDAS               MISTAS
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Bloco simples│        │ Estacas      │        │ Combinações  │
│ $ · aula 30 ▸│        │ pré-moldadas │        │ rasas +      │
├──────────────┤        │ $$$ · a34  ▸ │        │ profundas    │
│ Sapata armada│        ├──────────────┤        │ $$–$$$ · a35▸│
│ $$ · aula 31▾│        │ Escavadas    │        └──────────────┘
│ ┌──────────┐ │        │ in loco      │
│ │ O "sapato"│ │        │ $$–$$$ · a34▸│         ─ ─ ─ ─ ─ ─ ─
│ │ do pilar: │ │        ├──────────────┤        ELO DO SISTEMA
│ │ distribui │ │        │ Hélice       │        ┌──────────────┐
│ │ carga...  │ │        │ contínua     │        │ Viga baldrame│
│ │ Quando: … │ │        │ $$$$ · a34 ▸ │        │ conecta tudo │
│ │ [Aula 31 →]│ │        └──────────────┘        │ aula 32    ▸ │
│ └──────────┘ │                                 └──────────────┘
├──────────────┤
│ Radier    …  │
└──────────────┘
```

Mobile (<768px) — lista única em accordion, grupos como sub-headers:

```
RASAS ────────────────────
▸ Bloco simples          $
▾ Sapata armada         $$
  │ O "sapato" do pilar:
  │ distribui a carga…
  │ Quando usar: …
  │ [Aula 31 →]
▸ Radier                $$
PROFUNDAS ────────────────
▸ Estacas pré-moldadas $$$
…
ELO ──────────────────────
▸ Viga baldrame
```

**Conteúdo da ficha (fechado):** nome · custo relativo · nº da aula.
**Ficha aberta (+):** 1 frase do que é · "quando usar" em 1–2 linhas ·
link `[Aula N →](#aula-N)`.

**Regras de fidelidade:**
- Custo relativo em escala qualitativa `$`–`$$$$`, derivada das relações
  que o conteúdo afirma (bloco < sapata < profunda; radier depende).
  **Não inventar R$/m² onde a aula não dá** — números reais só no Bloco 4,
  onde a aula 40 os fornece.
- Viga baldrame renderiza fora dos três grupos, marcada como "elo do
  sistema" — fiel ao conteúdo (não é um tipo de fundação).

**Sintaxe do fenced block** (spec pro Codinho; parser linha a linha,
mesmo espírito do `flow`):

````
```tipos
## Rasas
- Sem ferro (bloco, pedra, ciclópico) | Três variantes da mesma ideia: casa leve + solo firme, zero aço | $ | aula: 30
- Sapata armada | O "sapato" do pilar: distribui a carga concentrada | $$ | aula: 31
- Radier | Laje-fundação: piso e fundação num elemento só | $$ | aula: 33
## Profundas
- Estacas pré-moldadas | Cravadas até o solo firme lá embaixo | $$$ | aula: 34
- Escavadas in loco | Perfura e concreta no lugar | $$-$$$ | aula: 34
- Hélice contínua | Baixa vibração, custo alto | $$$$ | aula: 34
## Mistas
- Combinações | Rasa + profunda no mesmo lote | varia | aula: 35
## Elo
- Viga baldrame | Não é fundação: é o que amarra o sistema | — | aula: 32
```

(Os ASCII acima usam rótulos abreviados por espaço; o fenced block é a
fonte canônica dos textos.)
````

Campo "quando usar" da ficha aberta: segunda linha opcional iniciada por
`  > ` sob o item (detalhe de sintaxe a critério do Codinho, desde que
continue editável como texto).

---

### Bloco 3 — A escalada de decisão  `<!-- fonte: aula 40 (+ ecos da 29 e 37) -->`

**Componente novo: `EscaladaDecisao`.** A sequência do mais barato ao
mais caro, com a pergunta que faz subir de degrau e a economia de cada um.

Desktop — escada diagonal:

```
                                            ┌──────────────────┐
                                            │ 5 · Profundas    │
                                            │ último recurso   │
                              ┌─────────────┤ [aula 34 →]      │
                              │ 4 · Sapata  └──────────────────┘
                              │ corrida     ▲ solo muito fraco
                ┌─────────────┤ [a31 →]     │ ou carga muito alta?
                │ 3 · Sapata  └─────────────┘
                │ ou Radier   ▲ isolada ficou grande demais?
  ┌─────────────┤ [a31/a33 →] │
  │ 2 · Bloco   └─────────────┘
  │ simples     ▲ não passou no cálculo estrutural?
  │ −40% ferro  │
┌─┤ [a30 →]     │
│ │ 1 · Pedra   │
│ │ argamassada ▲ casa não é leve o bastante / solo não é firme?
│ │ −50% custo  │
│ └─────────────┘
│  COMECE AQUI
```

Mobile — escada vertical, mesmo conteúdo:

```
① Pedra argamassada / ciclópico
   casa muito leve + solo muito bom · −50%
   [aula 30 →]
   ↓ não passou no cálculo?
② Bloco de concreto simples
   casa leve + solo bom · −40%
   [aula 30 →]
   ↓ não passou?
③ Sapata ou Radier  … 
④ Sapata corrida …
⑤ Fundações profundas — último recurso
```

**Regras:** os degraus, condições e percentuais vêm literais da aula 40
(seção "Sempre Tente Primeiro Sem Ferro"). Nada de degrau inventado.
A pergunta de subida ("não passou no cálculo estrutural?") é o conector
— reforça o inegociável do SPT/projeto sem virar quarto bloco.

**Sintaxe:**

````
```escalada
1 | Pedra argamassada ou concreto ciclópico | casa muito leve + solo muito bom | -50% vs sapata | aula: 30
2 | Bloco de concreto simples | casa leve + solo bom | -40% vs sapata | aula: 30
3 | Sapata ou radier | peso médio ou solo regular | acabamento integrado no radier | aula: 31
4 | Sapata corrida | quando a isolada fica grande demais | — | aula: 31
5 | Fundação profunda (estacas) | solo muito fraco ou cargas altas | último recurso | aula: 34
```
````

---

### Bloco 4 — O caso IGO em números  `<!-- fonte: aula 40 -->`

**Componente novo: `ComparativoCustos`.** Duas barras empilhadas, os
números reais da aula 40, e a punchline.

```
   "A fundação barata pode sair cara."

   OPÇÃO A · Alicerce         OPÇÃO B · Radier polido
  ┌─────────────────┐        ┌─────────────────┐
  │ Porcelanato     │        │ Polimento       │
  │ R$ 130/m²       │        │ R$ 60/m²        │
  ├─────────────────┤        ├─────────────────┤
  │ (contrapiso)    │        │                 │
  ├─────────────────┤        │ Radier          │
  │ Alicerce        │        │ (fundação+piso) │
  │ R$ 96/m²        │        │ R$ 174/m²       │
  └─────────────────┘        └─────────────────┘
   TOTAL R$ 273/m²            TOTAL R$ 234/m²
                              ▼ economia de 14%
                                (R$ 3.900 em 100 m²)

   O alicerce parece mais barato — até somar o piso.
   A conta completa é o Impacto Global na Obra (IGO). [Aula 40 →]
```

- Alturas das barras proporcionais aos valores (CSS puro, sem lib de
  chart — são 2 barras, não um gráfico).
- Mobile 320px: as duas barras lado a lado cabem (cada uma ~140px);
  se apertar, empilham verticalmente com os totais alinhados.
- Callout `[!atencao]` logo abaixo, reusado: "estimativa preliminar
  (EVF) — não substitui orçamento executivo" (a ressalva é da própria
  aula 40; omiti-la recortaria conteúdo).

**Sintaxe:**

````
```custos
titulo: A fundação barata pode sair cara
a: Alicerce de pedra
a.item: Alicerce | 96
a.item: Porcelanato + contrapiso | 130 + contrapiso
a.total: 273
b: Radier polido
b.item: Radier (fundação + piso) | 174
b.item: Polimento | 60
b.total: 234
punchline: Economia de 14% — R$ 3.900 em uma casa de 100 m²
aula: 40
```
````

(Formato exato dos campos a critério do Codinho; o requisito é: valores
como dados, não hardcoded no componente.)

---

### Bloco 5 — Os inegociáveis  `<!-- fonte: aulas 29, 32, 36 -->`

**Componente:** `Callout` (D014, reuso puro). Três, em sequência:

1. `[!atencao]` **SPT antes de tudo.** Escolher fundação sem ensaio de
   solo é prescrever sem exame. [Aula 29 →]
2. `[!atencao]` **Impermeabilize sempre.** Corrigir umidade ascendente
   depois da casa pronta é caro e raramente definitivo. [Aula 36 →]
3. `[!atencao]` **Baldrame não se elimina** onde é necessário: trincas,
   deformações e infiltração cobram a economia. [Aula 32 →]

Zero componente novo. Fecho do pacote + botão "Ler o módulo completo ↓"
(`btn-o` da identidade) rolando pra `#aulas`.

---

## 4. Componentes — reuso vs novos

| Componente          | Status | Justificativa                                          |
| ------------------- | ------ | ------------------------------------------------------ |
| `ProcessFlow`       | Reuso  | Bloco 1 é fluxo linear de 5 nós — caso de uso nativo   |
| `Callout`           | Reuso  | Bloco 5, ressalva do Bloco 4, proveniência da Aula 32  |
| `Citacao`, `Tabela` | Reuso  | Continuam servindo dentro das aulas (inalterados)      |
| **`MapaTipos`**     | Novo   | Taxonomia + fichas integradas não existe no D014; é a  |
|                     |        | espinha do catálogo — candidato nº 1 a reuso (M9, M7)  |
| **`EscaladaDecisao`**| Novo  | Sequência decisória com condição de transição não é    |
|                     |        | fluxo linear (ProcessFlow) nem tabela — semântica própria |
| **`ComparativoCustos`**| Novo| Barras proporcionais com dados do markdown; Tabela não |
|                     |        | comunica proporção visual                               |

**Resultado do teste 4.5 (ProcessFlow nos passo-a-passo):** os
passo-a-passo executivos das aulas 30/31/33 **não viram componente**.
Têm sub-passos e detalhe que um fluxograma achataria — componentizar ali
recortaria conteúdo, violando o invariante. Permanecem como listas
numeradas MD (já corretas pós-D014). ProcessFlow reusado apenas no
Bloco 1. Nenhuma variante criada.

Total de componentes novos: **3**. Local: `site/src/components/content/`,
roteados pelo `Markdown.tsx` como os fenced blocks do D014.

---

## 5. Responsividade e acessibilidade (por componente novo)

**Geral (herda D014):** 320→1280 sem quebra; nada hover-only; tipografia
e cores da identidade (`identidade_visual.md`); Lighthouse A11y ≥ 90.

**MapaTipos**
- <768px: accordion de lista única; ≥768px: colunas por grupo com
  expansão in-place. Breakpoint único.
- Cada ficha é `<button>` com `aria-expanded`; conteúdo expandido em
  região associada. Teclado: Tab entre fichas, Enter/Espaço alterna.
- Estado aberto não é obrigatório pra acessar conteúdo: o link
  `#aula-N` da ficha leva à aula completa de qualquer forma.

**EscaladaDecisao**
- <768px: escada vertical (lista ordenada estilizada — semanticamente
  um `<ol>`); ≥768px: diagonal via CSS (offsets), mantendo o `<ol>` no
  DOM. Screen reader lê a sequência 1→5 com condições, sem depender do
  visual.
- Links de degrau são âncoras normais, focáveis.

**ComparativoCustos**
- Barras em CSS puro com alturas proporcionais; rótulos e valores sempre
  em texto real no DOM (nunca só visual).
- Par de barras cabe em 320px lado a lado; fallback: empilha.
- Tabela visualmente oculta (`sr-only`) com os mesmos dados para leitores
  de tela, se as barras não forem suficientes semanticamente — decisão
  de implementação do Codinho, requisito é: dado acessível sem o visual.

---

## 6. Norma de manutenção (dessincronia pacote × aula)

O pacote duplica números por design (camada de destilação). Regras:

1. Todo bloco declara fonte em comentário (`<!-- fonte: aula N -->`).
2. **Editou aula → confere os blocos do pacote que a citam.** Vale como
   norma de processo; entra no DECISION_LOG junto com a aprovação deste
   wireframe.
3. Valores vivem no markdown (fenced blocks), nunca no componente —
   corrigir número é editar texto, não código.

---

## 7. Decisões — resolvidas e pendentes

**Resolvidas pelo Tech Lead (2026-07-07):**

1. **Aulas abertas por default + colapso individual disponível** pra
   teste de UX. Spec completa na seção 2 ("Colapso de aulas"), incluindo
   a regra da âncora.
2. **Escala `$`–`$$$$` das fichas validada** contra o conteúdo das aulas
   — derivação documentada no Anexo A. Ajustes decorrentes: ficha
   sem-ferro nomeia as três variantes (bloco, pedra, ciclópico); custo
   de Mistas vira "varia" (range implicaria precisão que o curso não dá).
3. **Nomes dos fenced blocks e rótulos do TOC** mantidos como propostos
   (`tipos`/`escalada`/`custos`; "Em 7 minutos" no TOC). Ajustes de
   rótulo podem vir depois da validação visual.

**Pendentes (não bloqueiam implementação):**

4. **Callout de proveniência da Aula 32 em `[!atencao]`** — mantido;
   tipo `nota` neutro só se o padrão reaparecer (Fase 7, regra dos 2+).
5. **Registrar D019** junto do commit desta aprovação: arquitetura de
   pacotes (`site/content/pacotes/` curado × `temas/` gerado) + norma
   de manutenção da seção 6 + decisão de colapso.

---

## 8. Critério de pronto

Herda integralmente o "Critério de Pronto por Módulo" do
`reformulacao_modulos.md`, mais os específicos deste piloto:

- Página do M6 renderiza pacote + 12 aulas completas (invariante §0)
- Módulos 01–05 e 07–12 renderizam **byte-idênticos** ao estado atual
  (prova da composição condicional)
- Links `#aula-N` do pacote testados por clique (lição da âncora morta —
  tarefa 6.6 do plano)
- Os 3 componentes novos funcionam com dados vindos do markdown (trocar
  um valor no `.md` muda o render sem tocar código)
- Colapso: colapsar uma aula manualmente e clicar no link do pacote pra
  ela → a aula abre e a página rola até o heading (regra da âncora, §2)

---

## Anexo A — Derivação da escala de custo das fichas

Base textual de cada posição, verificada contra o conteúdo consolidado
do módulo (versão do site, pós-Fase 3):

| Ficha | Escala | Base no conteúdo |
| --- | --- | --- |
| Sem ferro (bloco, pedra, ciclópico) | `$` | Aulas 30/40: economia de 40–50% vs sapata armada; "R$ 1.000+ só de ferro por fundação" |
| Sapata armada | `$$` | Referência da escalada — os percentuais do curso são medidos contra ela |
| Radier | `$$` | Aula 33: "pode ser mais econômico que sapatas ou blocos, dependendo do projeto"; aula 40: R$ 174/m² já integrando o piso |
| Estacas pré-moldadas | `$$$` | Aula 34: "custos competitivos" *dentro* das profundas; profundas "encarecem muito a obra" (Grav. 14) |
| Escavadas in loco | `$$–$$$` | Aula 34: execução manual "mais econômica em pequenas quantidades" |
| Hélice contínua | `$$$$` | Aula 34: "custo elevado", uso em "alto padrão" |
| Mistas | varia | Aula 35: "comparação de custos nem sempre é direta"; "economia depende do terreno" |

A escala é **relativa e qualitativa** — comunica ordem, não preço.
Valores absolutos (R$/m²) aparecem apenas no Bloco 4, onde a aula 40 os
fornece literalmente.

---

Responsável: Alan Gattiboni · Elaborado com Claude
Versão: 1.1 — 2026-07-07 (decisões 1–3 resolvidas; colapso especificado;
ficha sem-ferro corrigida; Anexo A com derivação da escala)
Versão: 1.0 — 2026-07-07
