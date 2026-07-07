# Plano de Retomada — Piloto Módulo 6 (D015)
Versão 1 — Checklist Cronológico
Alto da Brisa · Retomada pós-gap (última sessão logada: 2026-05-25)

Legenda de responsável: **[A]** Alan · **[C]** Claude (chat/planning) · **[K]** Codinho (execução na máquina)

---

# 0. Sanity-Check de Retomada
(Confirmar que o repo está saudável antes de qualquer trabalho)

**Contexto:**
Gap de ~6 semanas entre o último log e a retomada. Princípio: não presumir estado, verificar.

## ✔️ Tarefas
- [X] 0.1 Build passa (`npm run build`) — exit 0, 20 páginas, 12 rotas SSG **[K]**
- [X] 0.2 Typecheck + lint limpos **[K]**
- [X] 0.3 Graph em dia (HEAD = `04bf4bec`, sem divergência) **[K]**
- [X] 0.4 Smoke test de rotas — `/`, `/conhecimento`, `/conhecimento/06_fundacoes` = 200 **[K]**
- [X] 0.5 Identificar pendências de git — 2 docs modificados não commitados (DECISION_LOG + reformulacao_modulos v1.1) **[K]**

---

# 1. Investigação Pendente
(Fechar as lacunas de conhecimento antes de decidir e commitar)

**Contexto:**
Três perguntas abertas surgiram na retomada. Nenhum commit ou edição de conteúdo acontece antes de respondê-las. "Palma palma, não priemos cânico."

## ✔️ Tarefas
- [X] 1.1 **Pipeline**: mapeado. Só `consolidar_temas.py` escreve em `site/content/temas/` — e é destrutivo (preserva apenas Título + Visão Geral). Fonte de verdade das aulas: `build/aulas/*.md` **[K]**
- [X] 1.2 **Censo de AULA_AUSENTE**: real é **80 OK / 9 ausentes** (não 88+1). 8 com heading cru `AULA_AUSENTE` (02: 9, 13 · 03: 18, 20, 21 · 06: 32, 39 · 12: 89) + Aula 25 com callout. Causa raiz: classificador do `audit_aulas.py` só olha header `status:` **[K]**
- [X] 1.3 **Diff dos docs pendentes**: exclusivamente D015 v1.1 — seguro commitar **[K]**
- [X] 1.4 Consolidação do report e replanejamento (Fases 2–4 reescritas) **[C]**
- [X] 1.5 **`build/` está no `.gitignore`** → a fonte curada do acervo (89 arquivos) NÃO está versionada. Vira prioridade estrutural da Fase 3 **[A]**

---

# 2. Decisões e Registro
(Transformar o que foi decidido em log, e commitar o que está pendente)

**Contexto:**
Decisões já tomadas na retomada precisam virar registro formal — decisão sem log é decisão que se perde. Commits da rodada: docs (fim desta fase), fonte de conteúdo (Fase 3) e fechamento (Fase 7).

## ✔️ Tarefas
- [X] 2.1 Registrar no DECISION_LOG: **Aula 32 (Viga Baldrame) será preenchida** com o conteúdo de slides do `knowledge/temas/`, com nota de proveniência (fonte: slides, não transcrição). Demais 8 ausências ficam tratadas com callout padrão **[C→A]**
- [X] 2.2 Registrar no DECISION_LOG: **calculadora de sapata fora do piloto** (candidato interativo adiado; reavaliar pós-piloto) **[C→A]**
- [X] 2.3 Registrar no DECISION_LOG a **política de pipeline e conteúdo**: (i) fonte de verdade = diretório de aulas versionado (destino definido na 3.1); (ii) `site/content/temas/` é saída gerada — nunca editar à mão; (iii) edição de conteúdo = editar fonte + re-rodar `consolidar_temas.py`; (iv) `extract_aulas.py` é geração inicial — re-rodar sobre aula curada exige reconciliação explícita **[C→A]**
- [X] 2.4 CHANGELOG: entry retroativo do build do graph (2026-06-17) **[A]**
- [X] 2.5 CHANGELOG: entry da retomada + sanity-check + report da Fase 1 **[A]**
- [X] 2.6 Corrigir contagens erradas nos docs: CHANGELOG ("88 OK, 1 ausente" → 80/9), `reformulacao_modulos.md` (M4 "3 aulas + 1 ausente" → 4 headings, Aula 25 tratada com callout). Memory atualiza na próxima geração **[A]**
- [X] 2.7 Commit dos docs pendentes (D015 v1.1) + novos registros — mensagem única de retomada **[A]**

---

# 3. Fonte de Conteúdo — Resgate, Correções e Aula 32
(Versionar a fonte, corrigir a dívida estrutural e completar o M6 antes do desenho)

**Contexto:**
A fonte curada do acervo está fora do git — resgatá-la vem antes de qualquer edição. Depois: preencher a Aula 32 (elo estrutural do M6, referenciada nas aulas 31, 35 e 36), unificar as 8 ausências na convenção de callout e consertar o auditor que mentia.

## ✔️ Tarefas
- [ ] 3.1 Mover `build/aulas/` → `knowledge/aulas/` (89 arquivos); ajustar paths no `consolidar_temas.py` (input) e `extract_aulas.py` (output); avaliar marcar `knowledge/temas/` como legado (README curto) **[K]**
- [ ] 3.2 Commit imediato da fonte versionada — proteção contra perda vem antes de estética **[A]**
- [ ] 3.3 Preencher a Aula 32: converter o conteúdo de Viga Baldrame do `knowledge/temas/06` para o padrão das aulas (H4/H5, listas MD reais, callouts D014 onde couber) + nota de proveniência → `knowledge/aulas/06_032.md` **[C planeja / K executa]**
- [ ] 3.4 Unificar as 8 ausências restantes na convenção `status: ausente` (mecanismo da Aula 25), preservando as justificativas existentes; verificar se o `consolidar_temas.py` generaliza o callout/link ou precisa de ajuste pequeno **[K]**
- [ ] 3.5 Consertar o classificador do `audit_aulas.py` (detectar corpo `AULA_AUSENTE`, não só header `status:`) e re-rodar o audit — esperado pós-3.3/3.4: 81 com conteúdo / 8 ausentes tratadas **[K]**
- [ ] 3.6 Rodar `consolidar_temas.py` e validar o diff de `site/content/temas/` — nada além do esperado mudou **[K]**
- [ ] 3.7 Build + render local das aulas alteradas (32, 39 e as 6 dos outros módulos) **[K]**
- [ ] 3.8 Commit da rodada de conteúdo **[A]**

---

# 4. Wireframe do Módulo 6 — Etapa 2 do D015
(Do diagnóstico ao documento de design aprovável)

**Contexto:**
Diagnóstico (Etapa 1) está feito: módulo é catálogo técnico-processual com espinha decisorial; fio condutor é a escalada de custo; aula 40 concentra a matéria-prima do pacote de 7 min. Agora vira wireframe textual — representação ASCII + comportamento, **não** código React.

## ✔️ Tarefas
- [X] 4.1 Etapa 1 — Leitura completa e diagnóstico da natureza do módulo **[C]**
- [ ] 4.2 Propor estrutura do pacote de 7 min (candidatos: escalada de decisão da aula 40, taxonomia de tipos, cadeia de cargas, comparativo mestre) **[C]**
- [ ] 4.3 **Definir onde o pacote de 7 min vive** de modo que sobreviva à re-consolidação: seção nova preservada pelo `consolidar_temas.py` OU arquivo próprio (`knowledge/pacotes/06.md`?) composto pela página — decisão de arquitetura do wireframe **[C→A]**
- [ ] 4.4 Wireframe textual de cada componente novo: ficha de tipo, comparativo lado a lado, diagrama de camadas, escalada de decisão — com comportamento responsivo 320→1280 de cada um **[C]**
- [ ] 4.5 Testar se o `ProcessFlow` (D014) atende os passo-a-passo das aulas 30/31/33 antes de propor variante — reuso antes de invenção **[C]**
- [ ] 4.6 Listar componentes D014 reusados vs componentes novos, com justificativa de cada novo **[C]**
- [ ] 4.7 Listar decisões em aberto que precisam do Tech Lead **[C]**
- [ ] 4.8 Entregar `docs/design_system/modulo_06_wireframe.md` **[C]**
- [ ] 4.9 Revisão do wireframe: aprovar / ajustar / quebrar em partes **[A]**

# 5. Implementação
(Prompt fechado pro Codinho, executar o wireframe aprovado)

**Contexto:**
Planning e execução compartimentados. O prompt leva wireframe aprovado, caminhos exatos, validações por viewport. Sem commit ao final — Tech Lead decide.

## ✔️ Tarefas
- [ ] 5.1 Redigir prompt fechado de implementação (wireframe + componentes + caminhos + validações) **[C]**
- [ ] 5.2 Executar implementação **[K]**
- [ ] 5.3 Build + typecheck + lint limpos pós-implementação **[K]**

---

# 6. Validação Visual
(O critério de pronto do módulo, na prática)

**Contexto:**
Critérios do `reformulacao_modulos.md`: responsivo sem quebras, teclado funcional, acessibilidade auditada.

## ✔️ Tarefas
- [ ] 6.1 Validar viewports 320 / 375 / 768 / 1024 / 1280 **[A]**
- [ ] 6.2 Navegação por teclado em todos os componentes novos **[A]**
- [ ] 6.3 Lighthouse Accessibility ≥ 90 **[A]**
- [ ] 6.4 Pacote de 7 min funcional + todas as aulas acessíveis com leitura completa **[A]**
- [ ] 6.5 Reportar bugs → ciclo de ajuste com Codinho até aprovar **[A→K]**
- [ ] 6.6 Verificar links internos das páginas alteradas (callouts de ausência, TOC) — clicar, não só olhar **[A]**

---

# 7. Extração de Padrões e Fechamento da Rodada
(O que o piloto ensina pros próximos 11 módulos)

**Contexto:**
Etapa 6 do processo D015. O piloto só termina quando o aprendizado está registrado e o repo está limpo.

## ✔️ Tarefas
- [ ] 7.1 Identificar componentes do M6 candidatos a reuso (ficha de tipo e comparativo são apostas fortes) **[C]**
- [ ] 7.2 Atualizar seção "Padrões Emergentes" do `reformulacao_modulos.md` **[C→A]**
- [ ] 7.3 Atualizar `componentes_conteudo.md` (D014) se algum componente novo virar universal **[C→A]**
- [ ] 7.4 CHANGELOG + DECISION_LOG da rodada (incluindo: calculadora adiada, decisões de wireframe) **[A]**
- [ ] 7.5 Avaliar se a ordem dos módulos 2–12 muda com o aprendizado do piloto **[A]**
- [ ] 7.6 Commit de fechamento com mensagem de sessão **[A]**

---

Fim da versão 1.
Responsável: Alan Gattiboni · Elaborado com Claude · 2026-07-07
