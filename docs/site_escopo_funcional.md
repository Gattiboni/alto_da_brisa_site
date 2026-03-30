# Alto da Brisa Site — Escopo Funcional e Fronteiras

## Introdução

O site **altodabrisa.alangattiboni.site** tem como objetivo ser o **hub digital central** do projeto Alto da Brisa: base de conhecimento, arquivo vivo, painel de evolução e plataforma de integração futura com automações e o assistente TARS.

Este documento define o **escopo funcional e as fronteiras claras** do projeto, servindo como fonte única de verdade para execução, alinhamento e validação do que será — e do que não será — entregue em cada fase.

---

## Objetivo do Projeto

Entregar uma **plataforma web autenticada**, acessível por moradores e parceiros, capaz de:

- centralizar o conhecimento técnico adquirido (cursos, referências, transcrições);
- disponibilizar um assistente de IA contextualizado com esse conhecimento;
- servir de arquivo vivo de fotos, vídeos e documentos do projeto;
- registrar a evolução do Alto da Brisa de forma organizada e navegável;
- ser base para automações e integrações futuras.

---

## Conceito Central (Contrato de Escopo)

> "Um único lugar onde tudo que diz respeito ao Alto da Brisa vive, cresce e pode ser consultado por qualquer membro do projeto, a qualquer momento, de qualquer dispositivo."

Características imutáveis do conceito:

- O **conteúdo é soberano**: o site serve o projeto, não o contrário.
- A **IA é assistente, não protagonista**: ela apoia quem consulta o conteúdo.
- O **acesso é controlado**: moradores e parceiros autenticados; conteúdo público separado do privado.
- A **evolução é incremental**: cada release entrega valor real, sem esperar o sistema completo.

---

## Fases do Projeto

| Fase | Nome | Status |
|---|---|---|
| v1 | Base + Conhecimento + IA | 🎯 Escopo deste documento |
| v2 | Painel de Controle + Blog de Evolução | Roadmap |
| v3 | Automações + TARS Integration | Roadmap |

---

## MUST HAVE — v1

### 1. Página Inicial Pública

- Apresentação do projeto Alto da Brisa (identidade, localização, propósito).
- Visual alinhado ao branding existente (Logo Alto da Brisa, paleta verde/terra).
- Responsiva: desktop e mobile desde o primeiro release.

### 2. Acervo de Fotos e Vídeos

- Galeria de fotos do projeto (terreno, obras, natureza).
- Integração com canal YouTube (a criar) para vídeos do projeto.
- Organizado por categoria ou data.
- Acessível publicamente ou com nível de acesso a definir.

### 3. Base de Conhecimento — Cursos Amanda & Fernando

- Transcrições completas dos vídeos do acervo [amandaefernando.com.br](https://amandaefernando.com.br/).
- Conteúdo navegável: por módulo, por tema, com busca textual.
- Fonte primária para o assistente de IA.
- Acesso restrito a moradores e parceiros autenticados.

### 4. Assistente de IA (Claudinho do Alto da Brisa)

- Interface de chat integrada ao site.
- Contextualizado com o conteúdo das transcrições dos cursos.
- Capaz de responder perguntas sobre construção, materiais, técnicas, gestão hídrica e temas correlatos.
- Capaz de correlacionar perguntas com documentos do projeto (plantas, contrato, laudos) quando disponíveis.
- Alimentado via Claude API (Anthropic).
- Acesso restrito a usuários autenticados.

### 5. Autenticação

- Sistema de login com controle de acesso.
- Perfis mínimos: **Morador** e **Parceiro** *(definição de parceiro: a confirmar — ver nota abaixo)*.
- Sem cadastro público: acesso por convite.

### 6. Responsividade

- Layout funcional e agradável em desktop e mobile.
- Prioridade: legibilidade do conteúdo e usabilidade do chat em ambos os dispositivos.

---

## NICE TO HAVE — v1

- Busca semântica (além de textual) nas transcrições via embeddings.
- Modo escuro.
- Compartilhamento de trechos da base de conhecimento via link direto.
- Player de áudio embutido para os arquivos originais dos cursos.

---

## MUST HAVE — v2 (Roadmap)

- **Blog de evolução**: registro cronológico com fotos, decisões e marcos do projeto.
- **Painel de controle**: status de obras, checklist de infraestrutura, cronograma.
- **Gestão de documentos**: plantas, contratos, laudos — upload, versão e consulta.
- **Changelog visual**: linha do tempo navegável do projeto.

---

## MUST HAVE — v3 (Roadmap)

- **Automações**: gatilhos, alertas, integração com serviços externos.
- **TARS Integration**: o site como backbone do assistente de voz da casa.
- **Sensores / IoT**: monitoramento hídrico, energético, meteorológico.
- **Notificações**: alertas para moradores via e-mail ou push.

---

## OUT OF SCOPE — v1

- Painel de controle de obras ou cronograma interativo.
- Gestão de documentos com upload de usuário.
- Automações de qualquer natureza.
- Integração com sistemas externos (WhatsApp, CEMIG, IGAM, etc.).
- E-commerce ou pagamentos.
- Multilingue.
- TARS ou qualquer integração de voz.

---

## Notas Abertas

| ID | Ponto | Responsável | Status |
|---|---|---|---|
| N01 | Definição de "parceiros" com acesso ao site (prestadores? arquiteto? só família?) | Alan / Carol | ⏳ Aberto |
| N02 | Decisão de stack técnica | Alan | ⏳ Aguarda DoD |
| N03 | Criação do canal YouTube do Alto da Brisa | Alan | ⏳ Aberto |
| N04 | Conclusão do download dos áudios dos cursos Amanda & Fernando | Alan | 🔄 Em andamento |

---

Responsável: Alan Gattiboni  
Data: 2026-03-29  
Versão: 1.0
