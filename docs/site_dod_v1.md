# Alto da Brisa Site — Definition of Done (DoD) — v1

## Introdução

Este documento define o **Definition of Done (DoD)** do release **v1** do site Alto da Brisa, derivado **diretamente e exclusivamente** do escopo funcional aprovado.

Seu objetivo é estabelecer critérios **objetivos, auditáveis e verificáveis** para que o v1 seja considerado concluído, prevenindo ambiguidades, escopo implícito ou interpretações subjetivas de "pronto".

O DoD **não descreve implementação técnica**, arquitetura interna ou escolhas de ferramenta. Ele define **o que deve estar verdadeiro** para a entrega ser aceita.

---

## Princípios de Avaliação

Para que o v1 seja considerado *Done*, **todos** os critérios abaixo devem ser atendidos simultaneamente:

- Cada critério é **verificável na prática**;
- Cada critério é **independente de interpretação subjetiva**;
- Nenhum critério pressupõe funcionalidades fora do escopo v1 aprovado;
- O resultado final é **acessível, estável e reprodutível**.

---

## 1. Página Inicial Pública

Critérios de aceite:

- A URL `altodabrisa.alangattiboni.site` resolve e carrega sem erro em desktop e mobile.
- A página apresenta nome, localização e propósito do projeto Alto da Brisa.
- O logo Alto da Brisa está presente e em alta resolução.
- A paleta visual é consistente com o branding do projeto (verde/terra).
- A página é navegável sem autenticação.

---

## 2. Acervo de Fotos e Vídeos

Critérios de aceite:

- Existe uma seção de galeria com ao menos um lote inicial de fotos do projeto.
- Vídeos do canal YouTube do Alto da Brisa estão embarcados ou linkados no site.
- O conteúdo está organizado de forma navegável (por categoria ou data).
- Galeria funciona corretamente em mobile e desktop.

---

## 3. Base de Conhecimento — Cursos Amanda & Fernando

Critérios de aceite:

- As transcrições dos cursos estão ingeridas e indexadas no sistema.
- O conteúdo é navegável: é possível browsear por módulo ou tema.
- Existe busca textual funcional dentro do conteúdo.
- O acesso à base de conhecimento requer autenticação.
- Nenhum conteúdo protegido por copyright é exposto publicamente.

---

## 4. Assistente de IA

Critérios de aceite:

- Existe uma interface de chat funcional no site.
- O assistente responde perguntas com base no conteúdo das transcrições dos cursos.
- O assistente é capaz de citar ou referenciar o módulo/trecho de origem da resposta.
- O assistente não fabrica informações fora do contexto fornecido (hallucination minimizada).
- A interface de chat funciona em mobile e desktop.
- O acesso ao assistente requer autenticação.
- A chave da API Anthropic não está exposta no frontend.

---

## 5. Autenticação

Critérios de aceite:

- Existe tela de login funcional.
- Usuários sem credenciais não acessam conteúdo restrito (base de conhecimento, chat IA).
- Existe ao menos um perfil de acesso funcional (Morador).
- O sistema não permite cadastro público (acesso por convite/configuração manual).
- Sessão expira após período razoável de inatividade.

---

## 6. Responsividade

Critérios de aceite:

- Todas as páginas do v1 são funcionais e legíveis em viewport mobile (≥ 375px).
- Todas as páginas do v1 são funcionais e legíveis em viewport desktop (≥ 1280px).
- Nenhum elemento crítico de navegação está quebrado ou oculto em mobile.
- O chat do assistente é utilizável em tela de celular.

---

## 7. Qualidade Técnica Mínima

Critérios de aceite:

- O site carrega em menos de 5 segundos em conexão móvel razoável (3G/4G).
- Não existem erros críticos de console em nenhuma página do v1.
- O código está versionado no repositório GitHub `alto_da_brisa_site`.
- O ambiente de produção está separado do ambiente de desenvolvimento.
- Existe documentação mínima de como rodar o projeto localmente (`README` atualizado).

---

## 8. Escopo Preservado

Critérios de aceite:

- Nenhuma funcionalidade fora do escopo v1 aprovado foi incluída.
- Itens classificados como *Nice to Have* não bloqueiam o release.
- Itens explicitamente *Out of Scope* (automações, TARS, painel de obras, etc.) não estão presentes direta ou indiretamente.

---

## Condição Final de Aceite

O **v1** é considerado **Done** somente quando **todos os critérios acima** forem atendidos.

A validação ocorre por:

- acesso direto à URL em dispositivos desktop e mobile;
- login com credenciais válidas e tentativa de acesso sem credenciais;
- interação real com o assistente de IA (perguntas sobre conteúdo dos cursos);
- navegação pela base de conhecimento e busca por termos;
- inspeção do repositório GitHub (código versionado, README atualizado);
- verificação de que a API key não está exposta no frontend.

---

Responsável: Alan Gattiboni  
Data: 2026-03-29  
Versão: 1.0
