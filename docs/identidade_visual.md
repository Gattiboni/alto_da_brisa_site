# Identidade e Guia Visual — Alto da Brisa

Fonte única de verdade para uso visual do projeto em qualquer mídia: site,
documentos, apresentações, comunicações.

---

## 1. Paleta de Cores

| Nome           | Hex       | Uso                                                                      |
| -------------- | --------- | ------------------------------------------------------------------------ |
| Verde Floresta | `#6b7f67` | Cor primária. Títulos, botões principais, destaques, elementos de marca. |
| Areia Quente   | `#b7b0a1` | Secundária. Fundos alternativos, bordas, ícones secundários.             |
| Pedra Clara    | `#d6d3ce` | Terciária. Fundos de seções, separadores, tags.                          |
| Branco         | `#ffffff` | Fundo principal. Texto sobre fundos escuros.                             |
| Carvão         | `#333437` | Texto corrido. Nunca usar preto puro (`#000`) no corpo de texto.         |

### Regras de uso

- O Verde Floresta nunca aparece em blocos de texto longo — apenas em títulos,
  labels e elementos visuais.
- Fundo principal do site: Branco ou Pedra Clara. Nunca Areia Quente como fundo
  de página inteira.
- Contraste mínimo para acessibilidade (WCAG AA): Carvão sobre Branco, Carvão
  sobre Pedra Clara, Branco sobre Verde Floresta.
- Combinações a evitar: Verde Floresta sobre Areia Quente (contraste
  insuficiente).

### Tailwind — configuração customizada

```js
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      brisa: {
        green:  '#6b7f67',
        sand:   '#b7b0a1',
        stone:  '#d6d3ce',
        white:  '#ffffff',
        coal:   '#333437',
      },
    },
  },
},
```

---

## 2. Tipografia

### Famílias

| Família            | Uso                                               | Estilo                          |
| ------------------ | ------------------------------------------------- | ------------------------------- |
| Cormorant Garamond | Títulos principais, lettering, hero text          | Elegante, serifado, identitário |
| Lato               | Body text, parágrafos, UI geral                   | Limpo, legível, neutro          |
| Montserrat         | Labels, captions, destaques em itálico, navegação | Geométrico, versátil            |

### Importação (Google Fonts / Next.js)

```ts
// app/layout.tsx
import { Cormorant_Garamond, Lato, Montserrat } from "next/font/google";

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["300", "400", "600"],
  style: ["normal", "italic"],
  variable: "--font-cormorant",
});

const lato = Lato({
  subsets: ["latin"],
  weight: ["300", "400", "700"],
  variable: "--font-lato",
});

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-montserrat",
});
```

### Escala tipográfica

| Nível      | Fonte              | Peso       | Tamanho        | Uso                     |
| ---------- | ------------------ | ---------- | -------------- | ----------------------- |
| Display    | Cormorant Garamond | 300 italic | 56–72px        | Hero, nome do projeto   |
| H1         | Cormorant Garamond | 400        | 40px           | Título de página        |
| H2         | Cormorant Garamond | 400        | 32px           | Seções principais       |
| H3         | Lato               | 700        | 20px           | Subseções               |
| H4         | Montserrat         | 600        | 16px           | Labels, títulos de card |
| Body       | Lato               | 400        | 16px           | Texto corrido           |
| Body small | Lato               | 300        | 14px           | Descrições, secundário  |
| Caption    | Montserrat         | 400 italic | 12px           | Legendas, metadados     |
| Label      | Montserrat         | 600        | 11px uppercase | Tags, status, botões    |

---

## 3. Espaçamento e Grid

Base: **8px**. Todos os espaçamentos são múltiplos de 8.

| Token | Valor | Uso                                   |
| ----- | ----- | ------------------------------------- |
| xs    | 4px   | Espaçamento interno mínimo            |
| sm    | 8px   | Gap entre elementos inline            |
| md    | 16px  | Padding de cards, espaço entre blocos |
| lg    | 32px  | Separação de seções                   |
| xl    | 64px  | Margens de página, hero padding       |
| 2xl   | 128px | Seções grandes, espaço de respiro     |

Grid do site: 12 colunas, max-width 1280px, gutter 24px.

---

## 4. Logo

Arquivo: `docs/Logo_Alto_da_Brisa.png`

### Variações

| Variação                          | Uso                                              |
| --------------------------------- | ------------------------------------------------ |
| Completa (ícone + nome)           | Uso padrão em headers, documentos, apresentações |
| Ícone isolado                     | Favicon, avatar, contextos reduzidos             |
| Versão clara (sobre fundo escuro) | Header escuro, banners sobre foto                |
| Versão escura (sobre fundo claro) | Documentos, fundos brancos/pedra                 |

### Área de respiro

Manter ao redor do logo um espaço livre equivalente à altura da letra "A" do
logotipo em todas as direções.

### Tamanho mínimo

- Digital: 120px de largura
- Impresso: 30mm de largura

### Não fazer

- Não distorcer as proporções
- Não aplicar filtros, sombras ou efeitos
- Não usar sobre fundos com pouco contraste
- Não recolorir fora das variações aprovadas

---

## 5. Estilo Fotográfico

O Alto da Brisa é um lugar de natureza densa, luz filtrada e silêncio. As
imagens devem transmitir isso.

**Características desejadas:**

- Luz natural, preferencialmente golden hour (manhã cedo ou fim de tarde)
- Paleta terrosa: verdes, ocres, marrons, cinzas suaves
- Composições com profundidade — primeiro plano, meio, fundo
- Presença humana discreta quando existir — parte da natureza, não protagonista
- Alta resolução, sem filtros excessivos

**Evitar:**

- Fotos com saturação artificial ou filtros de Instagram
- Composições muito "turísticas" ou posadas em excesso
- Céus queimados ou exposição estourada
- Ângulos que não mostrem a natureza densa do terreno

---

## 6. Tom de Voz

O Alto da Brisa fala como quem construiu algo com intenção e quer compartilhar.

| Atributo                  | Descrição                                                        |
| ------------------------- | ---------------------------------------------------------------- |
| Direto                    | Sem rodeios. Diz o que é.                                        |
| Íntimo                    | Fala para os moradores e parceiros, não para o público em geral. |
| Contemplativo             | Deixa espaço para a natureza falar. Não precisa preencher tudo.  |
| Técnico quando necessário | Sem medo de termos precisos — o público entende.                 |
| Sem corporativês          | Nada de "soluções", "ecossistema", "jornada".                    |

---

## 7. Componentes UI (referência para o site)

### Botão primário

- Background: `#6b7f67`
- Texto: `#ffffff`, Montserrat 600, 11px uppercase, letter-spacing 0.1em
- Border-radius: 2px (quase reto — evitar o "arredondado demais" que banaliza)
- Hover: `#5a6d57` (verde 10% mais escuro)

### Botão secundário

- Background: transparente
- Borda: 1px solid `#6b7f67`
- Texto: `#6b7f67`
- Hover: background `#6b7f67`, texto `#ffffff`

### Cards

- Background: `#ffffff` ou `#d6d3ce`
- Borda: nenhuma ou 1px solid `#d6d3ce`
- Border-radius: 4px
- Shadow: `0 1px 4px rgba(51,52,55,0.08)`

### Links

- Cor: `#6b7f67`
- Sem underline por padrão
- Hover: underline + leve escurecimento

---

## 8. Referências e Arquivos

| Item              | Local                                    |
| ----------------- | ---------------------------------------- |
| Logo PNG          | `docs/Logo_Alto_da_Brisa.png`            |
| Guia visual Canva | https://www.canva.com/folder/FAF5ijcSyrk |
| Tailwind config   | `site/tailwind.config.ts`                |
| Google Fonts      | Cormorant Garamond, Lato, Montserrat     |

---

Responsável: Alan Gattiboni Versão: 1.0 — 2026-03-30
