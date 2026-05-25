# Componentes de Conteúdo — Especificação v1

Este documento define os 4 componentes React/Tailwind que renderizam o
conteúdo das aulas no portal Alto da Brisa. Especificação propositiva
para v1 — pode evoluir com o uso.

**Princípio mestre**: o conteúdo é para ser lido em qualquer lugar — no
celular durante uma reunião, no carro entre amigos, em uma noite sem
energia em um sítio. **Mobile-first absoluto**, com escala graciosa para
desktop.

Paleta (já estabelecida em D006):
- Verde Floresta `#6b7f67`
- Areia Quente `#b7b0a1`
- Pedra Clara `#d6d3ce`
- Branco `#ffffff`
- Carvão `#333437`

Tipografia (já estabelecida):
- Cormorant Garamond — display, citações, números grandes
- Lato — corpo de texto
- Montserrat — labels, UI, small caps

---

## Princípios de Responsividade do Conteúdo

Antes dos componentes individuais, três regras gerais que se aplicam ao
conteúdo todo:

1. **Largura de leitura máxima**: 65 caracteres por linha em desktop
   (`max-w-prose` do Tailwind = ~65ch). Em mobile, padding lateral
   confortável (16-20px) e ocupa o resto.

2. **Tamanho base de texto**: 17px em mobile, 18px em desktop. Maior do
   que o padrão da web (16px) porque o conteúdo será lido em situações
   distraídas. Line-height generoso: `1.7` no corpo de texto.

3. **Sem hover-only**: tudo que tem interação precisa funcionar via
   toque. Estados de foco devem ser visíveis (relevante para navegação
   por teclado).

---

## Componente 1: `<Callout>`

### Função

Interromper o fluxo de texto para destacar alerta, dica ou exemplo.
Aparece **292 vezes** no acervo (135 atenção, 108 dica, 49 exemplo).

### Markdown de entrada

```markdown
> [!atencao] Título opcional
> Texto do callout, pode ter
> múltiplas linhas.

> [!dica]
> Texto sem título.

> [!exemplo] Caso prático
> Texto do exemplo.
```

### Variante única (decisão: economia conceitual)

Em vez de 3 variantes visuais (uma por tipo), **uma estrutura única
com indicador tipográfico diferenciado**. Razão: callouts são
frequentes (292 deles); ter 3 estilos visuais muito distintos faria as
páginas parecerem uma sopa de boxes coloridos. O conteúdo precisa
fluir.

### Anatomia

```
┌──────────────────────────────────────┐
│ ATENÇÃO                              │  ← small caps, Montserrat 500
│                                      │     letter-spacing wide
│ Texto do callout em parágrafo único  │  ← Lato 16-17px
│ ou múltiplos parágrafos, conforme    │     line-height 1.65
│ o conteúdo pedir. Sem limite rígido. │
└──────────────────────────────────────┘
```

### Diferenciação por tipo

**Marcador lateral** + **eyebrow tipográfico**. O fundo é o mesmo nos
três tipos, só muda a cor da barra lateral e o texto do eyebrow.

| Tipo | Barra lateral | Eyebrow | Fundo |
|---|---|---|---|
| `atencao` | Carvão `#333437` 3px | "ATENÇÃO" | Pedra `#d6d3ce` |
| `dica` | Verde `#6b7f67` 3px | "DICA" | Pedra `#d6d3ce` |
| `exemplo` | Areia `#b7b0a1` 4px | "EXEMPLO" | Pedra `#d6d3ce` |

Eyebrow em Montserrat 600, 11px, uppercase, letter-spacing 0.14em.
Mesma família visual dos labels usados no resto do site.

### Comportamento responsivo

**Mobile (320-767px)**:
- Padding interno: 16px
- Largura: 100% do container
- Barra lateral: 3-4px de espessura, à esquerda

**Desktop (768px+)**:
- Padding interno: 20px 24px
- Largura: igual ao corpo de texto (max-w-prose)
- Barra lateral: idem

Margem vertical: 24px acima e abaixo, separa do parágrafo anterior e
seguinte sem isolar demais.

### Edge case: callout sem título

Quando não houver título no markdown (`> [!dica]` sem texto na linha do
marcador), **omitir o eyebrow**. Só barra lateral colorida + texto.

Isso é importante porque na maioria dos callouts gerados o título é
opcional, e forçar "DICA:" repetido cansaria a leitura.

---

## Componente 2: `<Tabela>`

### Função

Mostrar comparação sistemática entre múltiplas opções. Aparece **27
vezes** no acervo, distribuídas em 22 aulas (especialmente em M9
Coberturas e M10 Acabamentos).

### Markdown de entrada

```markdown
| Material | Preço/m² | Durabilidade |
|----------|----------|--------------|
| Telha cerâmica | R$ 35-50 | 30-50 anos |
| Fibrocimento | R$ 15-25 | 15-25 anos |
| Telhado verde | R$ 200-400 | 40+ anos |
```

### Variante única, com transformação mobile

Em **desktop** (768px+), renderiza como tabela tradicional bem feita.
Em **mobile** (320-767px), **transforma cada linha em um card**.

Esta é a decisão mais importante do componente. Tabelas com 4+ colunas
ficam ilegíveis em 375px, e scroll horizontal é uma péssima
experiência para conteúdo de leitura.

### Desktop — Anatomia

```
┌─────────────────────────────────────────────────┐
│ MATERIAL        PREÇO/M²       DURABILIDADE     │ ← header em
├─────────────────────────────────────────────────┤   Montserrat 600,
│ Telha cerâmica  R$ 35-50      30-50 anos        │   small caps, Areia
│ Fibrocimento    R$ 15-25      15-25 anos        │
│ Telhado verde   R$ 200-400    40+ anos          │
└─────────────────────────────────────────────────┘
```

Estilo: tipografia primeiro, regras horizontais finas (`#d6d3ce`),
linha do header com peso visual maior (Areia Quente `#b7b0a1` clara no
fundo, ou apenas borda inferior 2px). Padding generoso por célula:
12px vertical, 16px horizontal.

### Mobile — Anatomia (transformação em cards)

```
┌────────────────────────────┐
│ TELHA CERÂMICA             │ ← primeira coluna
│                            │   vira título do card
│ Preço/m²                   │
│ R$ 35-50                   │ ← demais colunas
│                            │   viram pares
│ Durabilidade               │   label/valor
│ 30-50 anos                 │
└────────────────────────────┘
┌────────────────────────────┐
│ FIBROCIMENTO               │
│ ...                        │
└────────────────────────────┘
```

Cards empilhados, padding 16px, separação entre cards 12px. Borda fina
em volta de cada card (Pedra Clara). Título em Cormorant Garamond
mediano (20-22px), labels das demais colunas em Montserrat 11px
uppercase.

### Implementação técnica (nota)

Vai precisar de um plugin customizado de markdown ou de um componente
React que **lê o markdown, parseia a tabela e renderiza
condicionalmente** baseado em viewport. Não é trivial, mas é
necessário. Provavelmente um wrapper sobre `react-markdown` com regra
custom para `table`.

Em desktop o componente renderiza `<table>` nativa estilizada. Em
mobile, gera uma lista de `<article>` por linha. Mesma fonte de dados.

---

## Componente 3: `<Citacao>`

### Função

Destacar uma frase memorável extraída do conteúdo. Aparece **269 vezes**
no acervo, geralmente como blockquotes simples (sem marcador `[!tipo]`).

### Markdown de entrada

```markdown
> É muito mais barato mover uma linha no papel do que mover uma parede
> construída.

> "A sapata é como um sapato para a casa não ficar de salto alto na
> grama."
> — Amanda Calastro
```

### Variante única

**Tipografia expressiva, sem caixa, sem borda visível**. A citação se
distingue do corpo de texto **pela própria forma do texto**, não por
um container visual.

### Anatomia

```
                                                  
   "É muito mais barato mover uma linha no       
    papel do que mover uma parede construída."   
                                                  
                                          — Amanda 
                                                  
```

### Detalhes tipográficos

- **Fonte**: Cormorant Garamond Italic
- **Tamanho**: 22px mobile, 26-28px desktop
- **Cor**: Carvão `#333437`
- **Line-height**: 1.45 (mais apertado que corpo, dá sensação literária)
- **Alinhamento**: centro em mobile, esquerda com recuo em desktop
- **Aspas tipográficas**: usar `"` e `"` (não `"`)
- **Atribuição (se houver)**: Montserrat 11px, small caps,
  letter-spacing 0.1em, Areia Quente `#b7b0a1`, alinhada à direita,
  precedida por travessão `—`
- **Margem vertical**: 32-40px acima e abaixo, dá respiração

### Por que sem caixa?

Citação com box ou borda compete com o callout, ambos viraram blocos
visuais. A escolha é fazer a citação **tipograficamente expressiva**
para que se diferencie pelo gesto, não pelo container. É o jeito da
revista impressa de qualidade fazer isso.

Em mobile, o tamanho 22px e a italic já carregam o destaque sem
precisar de fundo.

---

## Componente 4: `<ProcessFlow>`

### Função

Visualizar sequência de etapas — fluxo de fases, processos, decisões.
Aparece poucas vezes no acervo (~3 casos atualmente em ASCII art), mas
o tipo de conteúdo do curso indica que mais vão emergir conforme o
conteúdo for revisado e enriquecido.

### Markdown de entrada (proposto)

Nenhum padrão Markdown nativo cobre isso bem. Proposta: usar um bloco
de código com linguagem custom `flow`:

```markdown
\`\`\`flow
Levantamento de Dados → Estudo de Viabilidade → Estudo Preliminar → Anteprojeto → Projeto Legal → Projeto Executivo
\`\`\`
```

Cada etapa separada por `→` (literal). O componente parseia e
renderiza.

**Variante com descrições** (opcional):

```markdown
\`\`\`flow
Estudo Preliminar :: Primeiros desenhos, definição de ambientes
Anteprojeto :: Compatibilização inicial, orçamento básico
Projeto Executivo :: Detalhamento completo, orçamento ±5%
\`\`\`
```

Cada etapa separada por nova linha; descrição opcional após `::`.

### Variante única, dois layouts responsivos

**Desktop**: fluxo horizontal com setas tipográficas entre etapas.
**Mobile**: fluxo vertical com conectores entre etapas.

### Desktop — Anatomia

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   01     │ → │   02     │ → │   03     │ → │   04     │
│          │   │          │   │          │   │          │
│ Estudo   │   │ Antepro- │   │ Projeto  │   │ Projeto  │
│ Prelimi- │   │ jeto     │   │ Legal    │   │ Executi- │
│ nar      │   │          │   │          │   │ vo       │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

- Cada etapa em um card com borda Pedra Clara (`#d6d3ce`)
- Número em Cormorant Garamond grande (28-32px), Verde Floresta
- Título da etapa em Lato 14-15px abaixo do número
- Descrição (se houver) em Lato 13px, cor Carvão atenuada
- Seta entre cards: caractere `→` em Cormorant Garamond 24px, Areia
  Quente
- Layout flex, wrap responsivo até 4-5 etapas

### Mobile — Anatomia

```
┌──────────────────────────┐
│ 01                       │
│ Estudo Preliminar        │
│                          │
│ Primeiros desenhos, etc. │
└──────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 02                       │
│ Anteprojeto              │
│                          │
│ Compatibilização etc.    │
└──────────────────────────┘
```

- Cards empilhados, largura 100%
- Conector vertical (linha + seta `▼`) entre cards, 16px de altura
- Mesma tipografia do desktop, ajustada de tamanho

### Casos especiais

Os 3 ASCII art atuais (em 02_006.md e 02_008.md) devem ser **convertidos
manualmente** para o markdown `\`\`\`flow` durante a revisão final do
conteúdo. Cada um tem características próprias (margens de erro,
etapas paralelas, etc) que vão guiar evoluções deste componente em
futuras versões.

Para v1, suficiente cobrir o caso linear simples.

---

## Mapeamento Markdown → Componente

Resumo executivo de o que o renderer Markdown faz com cada padrão:

| Padrão no `.md` | Componente | Comportamento |
|---|---|---|
| `> [!atencao]` / `> [!dica]` / `> [!exemplo]` | `<Callout>` | Renderiza variante por tipo |
| `\| col \| col \|` (tabela MD) | `<Tabela>` | Tabela em desktop, cards em mobile |
| `> texto` (blockquote sem `[!`) | `<Citacao>` | Tipográfico, sem box |
| `\`\`\`flow ... \`\`\`` | `<ProcessFlow>` | Horizontal desktop, vertical mobile |
| Demais padrões MD | Default | Headings, listas, parágrafos, links, etc |

---

## Próximos passos sugeridos

1. Validar este documento com o Tech Lead (Alan)
2. Documentar entradas correspondentes no DECISION_LOG e CHANGELOG
3. Atualizar `docs/identidade_visual.md` com seção "Componentes de
   Conteúdo"
4. Implementar em React/Tailwind no `site/src/components/content/`
5. Aplicar nas 88 aulas via parser customizado em
   `[slug]/page.tsx`
6. Converter manualmente os 3 ASCII art para markdown `flow`

---

Responsável: Alan Gattiboni
Versão: 1.0 — 2026-05-24
