# Reformulação dos Módulos — Plano de Trabalho

Documento operacional. Define como cada um dos 12 módulos do portal
Alto da Brisa será reformulado para entregar leitura ativa, com
densidade variável de consumo.

Decisão originária: D015.

---

## Princípios

1. **Densidade variável de consumo.** Cada módulo abre com um "pacote
   de 7 minutos" — recursos visuais que entregam a essência sem leitura
   corrida. Aprofundamento textual fica disponível por clique.

2. **Recursos visuais específicos por natureza de conteúdo.** Não há
   componente genérico que sirva pra tudo. Cada módulo recebe os
   recursos que sua natureza pede (timeline, matriz, fluxograma,
   calculadora, comparativo, etc).

3. **D014 como camada base, não como teto.** Os 4 componentes
   universais (Callout, Citacao, Tabela, ProcessFlow) permanecem
   válidos e continuam sendo usados onde fizer sentido. A reformulação
   adiciona componentes acima dessa base, não substitui.

4. **Padrões emergem, não são impostos.** Componentes reutilizáveis
   são extraídos após aparecerem em 2+ módulos. Inventar reuso antes
   de evidência é o erro que originou esta reformulação (D015).

5. **Mobile-first absoluto permanece.** Toda visualização proposta
   precisa funcionar entre 320px e 1280px sem hover-only. Princípio
   herdado de D014.

---

## Processo por módulo

Cada módulo é tratado como ciclo independente:

### Etapa 1 — Leitura e Diagnóstico

Tech Lead anexa o conteúdo do módulo (arquivo `.md` consolidado de
`site/content/temas/`). Claude lê o conteúdo completo do módulo:
todas as aulas, sem pular nada.

Saída: diagnóstico curto identificando:

- Natureza do módulo (conceitual / técnico-processual / decisorial /
  histórico / catálogo / outro)
- Pontos de conteúdo que pedem visualização específica
- Aulas que se beneficiam de comparativos, timelines, matrizes,
  fluxogramas, simuladores, calculadoras
- Aulas que funcionam bem só com leitura textual (não toda aula
  precisa de visualização)

### Etapa 2 — Proposta de Wireframe

Claude produz um documento em markdown com:

- Estrutura da página do módulo (pacote de 7 min no topo, depois
  aprofundamento por aula)
- Wireframe textual de cada componente proposto (não código React, só
  representação visual em texto/ASCII e descrição de comportamento)
- Lista de componentes novos a criar para este módulo
- Lista de componentes existentes (D014 ou de módulos anteriores) que
  serão reusados
- Comportamento responsivo de cada componente novo
- Decisões em aberto que precisam de aprovação do Tech Lead

Saída: arquivo `docs/design_system/modulo_NN_wireframe.md` (onde NN é
o número do módulo).

### Etapa 3 — Validação

Tech Lead revisa o wireframe. Pode:

- Aprovar como está → segue pra implementação
- Pedir ajustes → Claude revisa
- Quebrar em partes → implementação fica em ciclos menores

### Etapa 4 — Implementação

Prompt para Claude Code com:

- Wireframe aprovado
- Lista de componentes a criar / modificar
- Caminhos exatos de arquivos
- Validações por viewport
- Sem commit no final (Tech Lead decide)

### Etapa 5 — Validação Visual

Tech Lead sobe o front local, valida em viewports 320 / 375 / 768 /
1024 / 1280, navega por teclado, reporta bugs ou aprova.

### Etapa 6 — Extração de Padrões

Após cada módulo concluído, Claude identifica:

- Componentes que apareceram neste módulo e podem reusar em outros
- Padrões de layout que valem extrair para `docs/design_system/`
- Atualizações no `componentes_conteudo.md` (D014) se relevante

Atualização da seção "Padrões Emergentes" deste documento.

---

## Ordem dos módulos

Ordem proposta, sujeita a revisão pelo Tech Lead:

1. **Módulo 1 — Introdução Casa de Baixo Custo Sustentável**
   - Por que primeiro: é a porta de entrada do leitor; também é o
     menor (5 aulas). Piloto ideal pra ajustar o processo.
2. **Módulo 2 — Projeto** (12 aulas, conceitual)
3. **Módulo 6 — Fundações** (12 aulas, técnico-processual)
4. **Módulo 10 — Acabamentos** (11 aulas, decisorial, 7 tabelas)
5. **Módulo 4 — Orçamento, Planejamento e Controle** (3 aulas + 1
   ausente, denso com cálculos)
6. **Módulo 9 — Coberturas** (14 aulas, catálogo de soluções)
7. **Módulo 7 — Estruturas e Vedações** (15 aulas, comparativo de
   métodos)
8. **Módulo 8 — Lajes** (5 aulas)
9. **Módulo 3 — Terreno** (6 aulas)
10. **Módulo 5 — Serviços Preliminares** (1 aula)
11. **Módulo 11 — Outros Acabamentos** (2 aulas)
12. **Módulo 12 — Encerramento** (2 aulas)

Após o piloto (M1), o Tech Lead pode reordenar baseado em prioridade
percebida.

---

## Critério de Pronto por Módulo

Um módulo está pronto quando:

- Página abre com pacote de 7 min visualmente rico e funcional
- Todas as aulas do módulo são acessíveis com leitura completa
- Navegação intra-página funciona (TOC, anterior/próxima, voltar ao
  topo)
- Responsivo entre 320px e 1280px sem quebras
- Navegação por teclado funcional
- Lighthouse Accessibility ≥ 90
- Wireframe correspondente está documentado em
  `docs/design_system/modulo_NN_wireframe.md`
- Padrões reutilizáveis foram extraídos para reuso futuro

---

## Padrões Emergentes

Esta seção será atualizada após cada módulo. Lista de componentes ou
padrões de layout que apareceram em 2+ módulos e foram extraídos para
reuso.

(Vazia até a conclusão do segundo módulo.)

---

## Pendências paralelas (não bloqueantes)

Itens identificados durante a validação de D014 que não dependem da
reformulação módulo a módulo. Podem ser implementados a qualquer
momento:

- **Navegação intra-aula**: botões "tópico anterior", "tópico
  seguinte" e "voltar ao topo", sempre visíveis durante a leitura
- **Claudinho contextual**: ao clicar na libélula, modal/drawer abre
  já sabendo do contexto da página atual, com sugestões de perguntas
  cacheadas; depende do RAG funcional
- **Aula 25 ausente em todos os módulos** (não só M4): aplicar a
  solução de UI (callout com link) em padronização global

---

Responsável: Alan Gattiboni
Versão: 1.0 — 2026-05-25
