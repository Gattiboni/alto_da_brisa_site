# Alto da Brisa — Projeto Integrado

> Base de conhecimento, controle e evolução do Sítio Alto da Brisa. Para
> moradores, parceiros e colaboradores do projeto.

---

## O Projeto

O **Alto da Brisa** é um projeto de vida comunitário localizado em
**Sapucaí-Mirim, MG** (região de Gonçalves, Serra da Mantiqueira), sobre a Gleba
7 do Sítio São Miguel — 20.000 m² de área privativa, com nascente própria e APP.

O empreendimento reúne três famílias que dividem não apenas o terreno, mas uma
visão de como se quer viver: com natureza, autonomia, tecnologia e intenção.

---

## Este Repositório

Este repositório é o backbone digital do projeto. Aqui vivem:

| Diretório / Arquivo | Conteúdo                                                            |
| ------------------- | ------------------------------------------------------------------- |
| `README.md`         | Este arquivo. Visão geral e orientação.                             |
| `CHANGELOG.md`      | Registro cronológico de eventos, marcos e entregas.                 |
| `DECISION_LOG.md`   | Registro de decisões estratégicas e suas justificativas.            |
| `docs/`             | Documentação técnica, escopo, DoD, contratos, plantas, laudos.      |
| `site/`             | Código-fonte do site (Next.js).                                     |
| `automations/`      | Scripts, integrações e automações (futuro — TARS integration).      |
| `media/`            | Fotos, vídeos e registros visuais do projeto (referências locais).  |
| `knowledge/`        | Transcrições de cursos, referências técnicas, base de conhecimento. |

---

## O Site

URL atual: **https://alto-da-brisa-site.vercel.app** URL futura:
`altodabrisa.alangattiboni.site` (v2 — ver DECISION_LOG D005)

Objetivos:

- Base de conhecimento interativa com transcrições dos cursos adquiridos e IA
  assistente embutida
- Painel de controle e evolução do projeto (cronograma, decisões, status de
  obras)
- Arquivo vivo de fotos, plantas e documentos
- Portal dos moradores e parceiros (acesso autenticado)
- Ponto de integração futura com automações, sensores e o assistente TARS

### Stack

| Camada                          | Tecnologia                                    |
| ------------------------------- | --------------------------------------------- |
| Frontend / Full-stack           | Next.js 15 (App Router, TypeScript, Tailwind) |
| Hospedagem frontend             | Vercel                                        |
| Banco de dados + Auth + Storage | Supabase                                      |
| IA                              | Claude API (Anthropic)                        |
| Backend scripts / automações    | Python (Railway — v2+)                        |
| Versionamento                   | GitHub                                        |

---

## Dados do Imóvel

| Campo               | Valor                                              |
| ------------------- | -------------------------------------------------- |
| Nome                | Sítio São Miguel — Gleba 7                         |
| Município           | Sapucaí-Mirim, MG                                  |
| Comarca             | Paraisópolis, MG                                   |
| Matrícula origem    | 5.484, Livro 2                                     |
| Área total          | 20.000 m²                                          |
| Área APP (estimada) | 10.604 m² _(a confirmar após georreferenciamento)_ |
| Área livre estimada | ~9.396 m²                                          |
| Projeto urbanístico | Vila São Miguel / Alto da Brisa                    |
| Coordenadas         | 22°44'36.20"S, 45°53'48.60"O                       |
| Projeto Canva       | https://www.canva.com/folder/FAF5ijcSyrk           |

---

## Partes do Projeto

| Papel                 | Nome                                   |
| --------------------- | -------------------------------------- |
| Vendedora             | Sonia Padovan Catenne                  |
| Comprador / Tech Lead | Alan Gattiboni                         |
| Compradora / Jurídico | Ana Carolina Duarte Oliveira Queiroz   |
| Comprador             | Filipe José Brito da Silva Oliveira    |
| Comprador             | Gustavo Jorge Britos da Silva Oliveira |

---

## Status Atual

> Fase: **Pré-obra / Infraestrutura + Site v1 em desenvolvimento**

**Imóvel**

- [x] Contrato de compromisso de compra e venda assinado
- [x] Sinal pago (R$ 72.000)
- [ ] Georreferenciamento da Gleba 7 (responsabilidade da vendedora)
- [ ] Desmembramento e abertura de matrícula individualizada
- [ ] Escritura definitiva
- [ ] Projeto hídrico (captação + caixa-mãe)
- [ ] Ponto de energia CEMIG
- [ ] Instalação de mata-burros (2x, responsabilidade da vendedora)
- [ ] Construção: Casas 1, 2, 3 + Chalés

**Site**

- [x] Repositório GitHub criado
- [x] Escopo funcional e DoD v1 documentados
- [x] Stack definida
- [x] Next.js scaffolded
- [x] Vercel conectado ao GitHub — deploy automático ativo
- [x] Supabase projeto criado
- [x] Variáveis de ambiente configuradas (Vercel + .env local)
- [ ] Supabase: schema inicial (users, content)
- [ ] Autenticação funcional
- [ ] Base de conhecimento (transcrições dos cursos)
- [ ] Assistente IA integrado
- [ ] Galeria de fotos e vídeos
- [ ] Release v1

---

## Contribuindo

Repositório privado. Acesso por convite. Dúvidas operacionais: Alan Gattiboni —
projetoaltodabrisa@gmail.com
