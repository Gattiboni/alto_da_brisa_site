<!--
  Pacote de 7 minutos — Módulo 6 · Fundações
  Arquivo CURADO À MÃO (D019). Nunca gerado por script.
  Norma: editou uma aula citada em "fonte:" → confira o bloco.
-->

### A cadeia de cargas
<!-- fonte: aula 29 -->

```flow
Laje → Vigas → Pilares → Fundação → Solo
```

A fundação é o último elo antes do solo — tudo que a casa pesa passa
por ela.

### O mapa dos tipos
<!-- fonte: aulas 29-35 -->

```tipos
## Rasas
- Sem ferro (bloco, pedra, ciclópico) | Três variantes da mesma ideia: zero aço | $ | aula: 30
  > quando: casa térrea leve, cargas bem distribuídas e solo firme comprovado por ensaio (SPT)
- Sapata armada | O "sapato" do pilar: distribui a carga concentrada | $$ | aula: 31
  > quando: cargas concentradas em pilares (concreto, metal ou madeira); peso moderado a alto
- Radier | Laje-fundação: piso e fundação num elemento só | $$ | aula: 33
  > quando: solo fraco, cargas distribuídas (alvenaria estrutural) ou quando o piso integrado compensa
## Profundas
- Estacas pré-moldadas | Cravadas até o solo firme lá embaixo | $$$ | aula: 34
  > quando: solo superficial fraco com camada firme profunda; obra com acesso pra maquinário
- Escavadas in loco | Perfura e concreta no próprio lugar | $$-$$$ | aula: 34
  > quando: poucas estacas ou até 3–5 m de profundidade — execução manual é a mais econômica em pequena quantidade
- Hélice contínua | Baixa vibração, custo alto | $$$$ | aula: 34
  > quando: áreas sensíveis a vibração e ruído, ou água no subsolo
## Mistas
- Combinações | Rasa + profunda no mesmo lote | varia | aula: 35
  > quando: terreno inclinado ou solo heterogêneo — cada trecho recebe o que pede
## Elo
- Viga baldrame | Não é fundação: é o que amarra o sistema | — | aula: 32
  > quando: sempre que houver blocos, sapatas ou estacas a conectar — elo, não escolha
```

### A escalada de decisão
<!-- fonte: aula 40 -->

```escalada
1 | Pedra argamassada ou concreto ciclópico | casa muito leve + solo muito bom | -50% vs sapata armada | aula: 30
2 | Bloco de concreto simples | casa leve + solo bom | -40% vs sapata armada | aula: 30
3 | Sapata ou radier | peso médio ou solo regular | radier integra o piso acabado | aula: 31
4 | Sapata corrida | quando a isolada fica grande demais | — | aula: 31
5 | Fundação profunda (estacas) | solo muito fraco ou cargas muito altas | último recurso | aula: 34
```

Comece do degrau mais barato. Não passou no cálculo estrutural? Sobe um.

### O caso IGO em números
<!-- fonte: aula 40 -->
<!-- 177 = 273 − 96: a aula dá porcelanato R$ 130 e contrapiso
     "necessário" sem valor isolado; o total 273 é literal da aula -->

```custos
titulo: A fundação barata pode sair cara
a: Alicerce de pedra
a.item: Alicerce | 96
a.item: Contrapiso + porcelanato | 177
a.total: 273
b: Radier polido
b.item: Radier (fundação + piso) | 174
b.item: Polimento | 60
b.total: 234
punchline: Economia de 14% — R$ 3.900 em uma casa de 100 m²
aula: 40
```

O alicerce parece mais barato — até somar o piso. A conta completa é o
Impacto Global na Obra (IGO). [Aula 40 →](#aula-40)

> [!atencao]
> Estimativa preliminar (EVF — Estudo de Viabilidade Financeira). Não
> substitui o orçamento executivo detalhado.

### Os inegociáveis
<!-- fonte: aulas 29, 32, 36 -->

> [!atencao]
> **SPT antes de tudo.** Escolher fundação sem ensaio de solo é
> prescrever sem exame. [Aula 29 →](#aula-29)

> [!atencao]
> **Impermeabilize sempre.** Corrigir umidade ascendente com a casa
> pronta é caro e raramente definitivo. [Aula 36 →](#aula-36)

> [!atencao]
> **Baldrame não se elimina onde é necessário.** Trincas, deformações
> e infiltração cobram a economia. [Aula 32 →](#aula-32)
