# Features Georreferenciadas — Alto da Brisa

Fonte de verdade espacial do projeto. Todas as coordenadas vêm de
`docs/geo/alto_da_brisa_geo_v1.kmz`, gerado no Google Earth Pro.

Sistema de coordenadas: WGS84 (EPSG:4326), em decimal degrees.
Formato: `latitude, longitude` (sul e oeste como negativos).

---

## Polígonos

| Nome                            | Função no projeto                                                                       |
| ------------------------------- | --------------------------------------------------------------------------------------- |
| `alto_da_brisa_area_expandida`  | Bounding box para geração do terreno 3D no Blender GIS. ~1.18 km × 730 m.               |
| `sitio_sao_miguel`              | Perímetro do sítio inteiro (~17 ha). Overlay visual sobre o terreno 3D.                 |
| `alto_da_brisa_perimetro`       | Perímetro da Gleba 7 (~20.000 m²). Overlay de destaque do lote.                         |

Coordenadas dos polígonos estão no KMZ. Não duplicadas aqui para evitar
divergência entre fontes.

---

## Pins

Coordenadas em formato `latitude, longitude`.

| Nome                            | Latitude        | Longitude       | Descrição                                 |
| ------------------------------- | --------------- | --------------- | ----------------------------------------- |
| `alto_da_brisa`                 | -22.74338888889 | -45.89683333333 | Centro de referência da Gleba 7.          |
| `alto_da_brisa_casa_1`          | -22.74316673895 | -45.89678539624 | Local previsto para Casa 1.               |
| `alto_da_brisa_casa_2`          | -22.74349923345 | -45.89696949298 | Local previsto para Casa 2.               |
| `alto_da_brisa_casa_3`          | -22.74385796115 | -45.89663418133 | Local previsto para Casa 3.               |
| `alto_da_brisa_area_social`     | -22.74374344191 | -45.89743902805 | Área social comum da Gleba 7.             |
| `alto_da_brisa_airbnb_1`        | -22.74344478633 | -45.89820898714 | Chalé/airbnb planejado.                   |
| `alto_da_brisa_porteira`        | -22.74316038546 | -45.89795522355 | Porteira de entrada do lote.              |
| `entrada_sao_miguel`            | -22.73793269454 | -45.89836857538 | Entrada do Sítio São Miguel.              |
| `estrada_do_juncal`             | -22.73718083814 | -45.89833161538 | Ponto de referência na estrada do Juncal. |

---

## Papel de cada feature no pipeline 3D

- **`alto_da_brisa_area_expandida`** → vai ao Blender GIS para gerar o
  terreno via SRTM 30m. Define o bounding box do modelo 3D.
- **Polígonos `sitio_sao_miguel` e `alto_da_brisa_perimetro`** → não vão ao
  terreno. Servem como overlays visuais (linhas/áreas destacadas) renderizados
  por cima do terreno na fase Three.js.
- **Pins** → futuros pontos de interação na cena 3D. Cada pin pode virar um
  ícone clicável que leva a uma subpágina ou dispara estado da aplicação.

---

## Centróide do Sítio São Miguel (referência cruzada)

Do CAR (Cadastro Ambiental Rural):
- Latitude: 22°44'28,99" S → -22.7414
- Longitude: 45°53'53,51" O → -45.8982

Bate com o esperado pelo polígono `sitio_sao_miguel`.

---

Versão: v1
Data: 2026-05-01
Responsável: Alan Gattiboni
