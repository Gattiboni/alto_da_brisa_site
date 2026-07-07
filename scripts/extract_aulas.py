"""
extract_aulas.py — Reconstrói o conteúdo das 89 aulas do curso Amanda & Fernando
a partir das transcrições de áudio polidas.

Estratégia:
- Pra cada aula, monta um prompt com:
  - Contexto do módulo e da aula
  - Lista das outras aulas do módulo (pra Claude saber onde uma para e outra começa)
  - O texto integral das gravações alocadas àquele módulo
- Pede pro Claude extrair o trecho que cobre a aula específica e formatá-lo
- Usa prompt caching pra economizar (gravações do módulo são cacheadas)
- Salva cada aula em arquivo individual primeiro (resiliência), depois consolida

Saída:
  knowledge/aulas/{modulo_id:02d}_{aula_id:03d}.md — uma por aula (fonte curada, D016)
  build/temas_v3/{XX_slug}.md                   — 12 arquivos finais consolidados
  build/transcricoes/{N:02d}.md                  — 21 gravações em formato final
  build/aulas_log.json                          — metadados (custo, tokens, status)

USO:
  ANTHROPIC_API_KEY=sk-ant-... python scripts/extract_aulas.py --help
  python scripts/extract_aulas.py --dry-run         # só mostra plano de execução
  python scripts/extract_aulas.py --pilot 28,56     # roda só 2 aulas-piloto
  python scripts/extract_aulas.py                   # roda todas as 89
  python scripts/extract_aulas.py --resume          # continua de onde parou
  python scripts/extract_aulas.py --only-module 6   # só o módulo 6
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERRO: pacote 'anthropic' não instalado.", file=sys.stderr)
    print("Instale com: pip install anthropic", file=sys.stderr)
    sys.exit(1)


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

# Espera-se que o script seja rodado da raiz do repo `alto_da_brisa_site/`
REPO_ROOT = Path(__file__).resolve().parents[1]

# Inputs
COURSE_STRUCTURE = REPO_ROOT / "knowledge" / "course_structure.json"
MAPEAMENTO = REPO_ROOT / "knowledge" / "mapeamento.json"
CURSO_LIMPO = REPO_ROOT / "knowledge" / "curso_limpo.md"
TERMOS_AULAS = REPO_ROOT / "knowledge" / "termos_aulas.json"

# Outputs
BUILD_DIR = REPO_ROOT / "build"
# Fonte de verdade curada das aulas (D016): knowledge/aulas/ versionado.
# ATENÇÃO: re-rodar este script sobrescreve a curadoria — exige reconciliação
# explícita (nunca sobrescrita cega). Ver D016.
AULAS_DIR = REPO_ROOT / "knowledge" / "aulas"
TEMAS_OUT = BUILD_DIR / "temas_v3"
TRANSCRICOES_OUT = BUILD_DIR / "transcricoes"
LOG_FILE = BUILD_DIR / "aulas_log.json"

MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 8000  # por aula, generoso pra não cortar conteúdo

# Budget de tokens pra parte cacheada do prompt (gravações).
# Sonnet 4.5 tem 200k de contexto total; deixamos margem pra system prompt,
# parte volátil, output e overhead.
BUDGET_TOKENS_CACHEADO = 150_000


# Gravações alocadas a cada módulo (extraído do mapeamento.json após análise).
# É a fonte primária de "qual gravação tem o conteúdo de qual módulo".
GRAVACOES_POR_MODULO = {
    1: [1, 2],
    2: [3],
    3: [4],
    4: [5, 6, 7, 11, 12, 13],
    5: [8],
    6: [9, 14],
    7: [10, 15, 16],
    8: [15, 16, 17],
    9: [17, 18],
    10: [19, 20],
    11: [21],
    12: [20, 21],
}

# Mapa invertido: cada gravação → lista de módulos que ela atravessa.
# Computado uma vez no carregamento; usado pra avisar o Claude quando
# uma gravação cobre múltiplos módulos.
MODULOS_POR_GRAVACAO: dict[int, list[int]] = {}
for _mid, _gravs in GRAVACOES_POR_MODULO.items():
    for _g in _gravs:
        MODULOS_POR_GRAVACAO.setdefault(_g, []).append(_mid)

# Nome legível de cada módulo (mantido aqui pra evitar reler o JSON na
# montagem do prompt).
MODULO_NOMES = {
    1: "Introdução Casa Baixo Custo Sustentável",
    2: "Projeto",
    3: "Terreno",
    4: "Orçamento, Planejamento e Controle",
    5: "Serviços Preliminares",
    6: "Fundações",
    7: "Estruturas e Vedações",
    8: "Lajes",
    9: "Coberturas",
    10: "Acabamentos",
    11: "Aberturas e Esquadrias",
    12: "Instalações Residenciais",
}


# -----------------------------------------------------------------------------
# CARREGAMENTO E INDEXAÇÃO
# -----------------------------------------------------------------------------

@dataclass
class Aula:
    id_global: int       # 1..89
    modulo_id: int       # 1..12
    modulo_nome: str
    modulo_slug: str
    posicao_no_modulo: int
    titulo: str
    aulas_irmas: list[str] = field(default_factory=list)  # outras aulas do mesmo módulo


def carregar_aulas() -> list[Aula]:
    with open(COURSE_STRUCTURE, encoding="utf-8") as f:
        cs = json.load(f)
    aulas = []
    id_global = 0
    for m in cs["modulos"]:
        for i, titulo in enumerate(m["aulas"]):
            id_global += 1
            aulas.append(Aula(
                id_global=id_global,
                modulo_id=m["id"],
                modulo_nome=m["nome"],
                modulo_slug=m["slug"],
                posicao_no_modulo=i + 1,
                titulo=titulo,
                aulas_irmas=list(m["aulas"]),
            ))
    return aulas


def carregar_gravacoes() -> dict[int, str]:
    """Lê curso_limpo.md e devolve dict {numero_gravacao: texto}."""
    with open(CURSO_LIMPO, encoding="utf-8") as f:
        curso = f.read().replace('\r\n', '\n')
    grav_pattern = re.compile(r'^## ## Gravação (\d+) —', re.MULTILINE)
    matches = list(grav_pattern.finditer(curso))
    gravacoes = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(curso)
        gravacoes[num] = curso[start:end].strip()
    return gravacoes


def carregar_termos() -> dict[int, dict]:
    """
    Lê knowledge/termos_aulas.json e devolve {aula_id: {titulo, termos}}.
    Esse JSON é usado pra ranquear quais gravações de fato cobrem cada
    aula (Python local, sem chamadas de API).

    Se o arquivo não existir, devolve dict vazio — o pipeline cai no
    comportamento legado (gravações por módulo).
    """
    if not TERMOS_AULAS.exists():
        return {}
    with open(TERMOS_AULAS, encoding="utf-8") as f:
        raw = json.load(f)
    out = {}
    for k, v in raw.items():
        if k == "_meta":
            continue
        try:
            out[int(k)] = v
        except (TypeError, ValueError):
            continue
    return out


def estimar_tokens(texto: str) -> int:
    """
    Estimativa conservadora: chars/4. Não é exato (tokenizer real da
    Anthropic difere), mas suficiente pra decidir budget.
    """
    return len(texto) // 4


def ranquear_gravacoes_por_aula(
    aula: "Aula",
    gravacoes_texto: dict[int, str],
    termos_aulas: dict[int, dict],
    budget_tokens: int = BUDGET_TOKENS_CACHEADO,
) -> tuple[list[int], list[int]]:
    """
    Ranqueia as 21 gravações pelo grau de cobertura dos termos-âncora da
    aula e seleciona as top-K que caibam em `budget_tokens`.

    Devolve (escolhidas, descartadas_por_budget).

    Se não há termos pra essa aula, devolve as gravações alocadas ao
    módulo no comportamento legado (sem ranqueamento).
    """
    info = termos_aulas.get(aula.id_global)
    if not info or not info.get("termos"):
        # Fallback: gravações mapeadas ao módulo
        legacy = list(GRAVACOES_POR_MODULO[aula.modulo_id])
        return legacy, []

    termos = info["termos"]

    # Conta hits ponderados em cada gravação
    scores: dict[int, int] = {}
    for grav_num, texto in gravacoes_texto.items():
        score = 0
        for t in termos:
            peso = 3 if " " in t else 1
            score += len(re.findall(re.escape(t), texto, re.IGNORECASE)) * peso
        if score > 0:
            scores[grav_num] = score

    # Sem hits em nenhuma gravação → fallback legado
    if not scores:
        legacy = list(GRAVACOES_POR_MODULO[aula.modulo_id])
        return legacy, []

    # Ordena por score decrescente
    ranked = sorted(scores.items(), key=lambda x: -x[1])

    escolhidas: list[int] = []
    descartadas: list[int] = []
    tokens_acumulado = 0
    for grav_num, _score in ranked:
        tokens_g = estimar_tokens(gravacoes_texto[grav_num])
        if tokens_acumulado + tokens_g > budget_tokens:
            descartadas.append(grav_num)
            continue
        escolhidas.append(grav_num)
        tokens_acumulado += tokens_g

    # Ordena escolhidas pelo número da gravação (apresentação no prompt
    # fica mais natural assim, e o cache é estável quando aulas
    # diferentes do mesmo módulo selecionam o mesmo conjunto na mesma
    # ordem).
    escolhidas.sort()
    return escolhidas, descartadas


# -----------------------------------------------------------------------------
# PROMPT
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um editor técnico que reconstrói o conteúdo de aulas de um curso a partir de transcrições de áudio.

## REGRAS INVIOLÁVEIS

1. **Não invente.** Use SOMENTE o que está na transcrição fornecida.
2. **Fidelidade ao escopo da aula.** Você extrai conteúdo de UMA aula específica. Tudo que pertence a outras aulas (do mesmo módulo OU de outros módulos) DEVE ser ignorado, mesmo que apareça na mesma transcrição. As aulas e módulos relevantes serão listados explicitamente na tarefa.
3. **Se a aula não estiver coberta**, responda EXATAMENTE: `AULA_AUSENTE`. Use isso quando o tópico aparece só de passagem, é mencionado mas não desenvolvido, ou simplesmente não está na transcrição.
4. **Aula é conteúdo completo, não resumo.** Mantenha toda a informação técnica do trecho. Não corte por brevidade. Não generalize. Não interprete além do que está dito.
5. **Reescreva fala em texto escrito legível.** Ajuste pontuação, organize em parágrafos, remova vícios de fala remanescentes. Mantenha o sentido, os exemplos e os valores exatamente como ditos.

## ESPECIAL: AULAS DE INTRODUÇÃO

Quando o título da aula contém "Introdução" ou é a primeira aula do módulo, ela cumpre papel de **panorama**:
- Apresenta o tópico do módulo em alto nível (o que é, por que importa)
- Lista os tipos/subtemas que o módulo cobrirá (sem aprofundar — isso é trabalho das aulas seguintes)
- Pode incluir conceitos fundamentais necessários pra entender o módulo

NÃO aprofunde em tipos específicos que têm aulas dedicadas adiante. Se a aula seguinte é "Laje Maciça e Treliçada", a introdução só MENCIONA esses tipos; não os explica em detalhe.

## ESTRUTURA DE SAÍDA (Markdown)

- Parágrafos curtos (3-6 linhas).
- Listas com `-` para enumerações.
- Listas numeradas para procedimentos ou etapas.
- `**Subseção:** texto` para dividir tópicos dentro da aula.
- `> Citação` (blockquote) para frases marcantes preservadas literalmente.
- Tabelas Markdown para comparações sistemáticas.
- `> [!atencao] Texto` para alertas ou erros comuns mencionados.
- `> [!exemplo] Texto` para casos práticos.
- `> [!dica] Texto` para dicas práticas.
- Mantenha valores numéricos, nomes próprios, links e referências exatamente como aparecem.

## REGRAS DE FORMA

- NÃO inclua o título da aula no output (ele já está no `.md` pai). Comece direto pelo conteúdo.
- NÃO inclua frases meta como "Nesta aula..." ou "O professor explica...". Vá direto ao tópico.
- NÃO use primeira pessoa ("vou te ensinar"). Use terceira pessoa ou impessoal.

## AUTOVERIFICAÇÃO ANTES DE RESPONDER

Antes de devolver o conteúdo, confirme silenciosamente:
1. As primeiras 3 frases deixam claro que se trata do tópico exato da aula solicitada?
2. Todo o conteúdo é sobre esse tópico específico (não sobre tópicos de outras aulas/módulos)?
3. Se o conteúdo principal acabou cobrindo outra aula que não a solicitada, a resposta correta é `AULA_AUSENTE`.

Se alguma das checagens falhou, ajuste ou responda `AULA_AUSENTE`."""


def montar_prompt_aula(
    aula: Aula,
    gravacoes_texto: dict[int, str],
    gravacoes_selecionadas: list[int] | None = None,
) -> tuple[str, str]:
    """
    Retorna (texto_cacheado, texto_volátil).
    O texto_cacheado é o contexto do módulo (gravações + lista de aulas-irmãs +
    aviso sobre gravações multi-módulo). Idêntico pra todas as aulas do módulo
    quando o ranqueamento não é usado; varia por aula quando o ranqueamento é.
    O texto_volátil é o foco específico da aula solicitada.

    Se `gravacoes_selecionadas` é fornecido, usa essa lista exata.
    Caso contrário, cai no comportamento legado de usar as gravações do módulo.
    """
    if gravacoes_selecionadas is not None:
        gravs_usadas = list(gravacoes_selecionadas)
    else:
        gravs_usadas = list(GRAVACOES_POR_MODULO[aula.modulo_id])

    # Detecta gravações que cobrem múltiplos módulos (vazamento de conteúdo).
    avisos_gravacao: list[str] = []
    for g in gravs_usadas:
        modulos_atravessados = sorted(MODULOS_POR_GRAVACAO.get(g, []))
        if len(modulos_atravessados) > 1:
            outros = [m for m in modulos_atravessados if m != aula.modulo_id]
            outros_str = ", ".join(
                f"Módulo {m} ({MODULO_NOMES[m]})" for m in outros
            )
            avisos_gravacao.append(
                f"- A Gravação {g} também contém conteúdo de: {outros_str}. "
                f"Você está extraindo SOMENTE conteúdo do Módulo {aula.modulo_id}."
            )

    # Lista as gravações com texto integral.
    bloco_gravacoes = []
    for g in gravs_usadas:
        bloco_gravacoes.append(f"=== GRAVAÇÃO {g} ===\n\n{gravacoes_texto[g]}\n")
    transcricao_completa = "\n".join(bloco_gravacoes)

    # Lista das aulas-irmãs do módulo.
    aulas_irmas_str = "\n".join(
        f"  {i+1}. {t}" for i, t in enumerate(aula.aulas_irmas)
    )

    # Bloco de aviso (só aparece quando há gravações multi-módulo).
    if avisos_gravacao:
        bloco_aviso = (
            "\n## ATENÇÃO — Gravações multi-módulo\n\n"
            "Algumas gravações desta lista atravessam mais de um módulo do curso:\n\n"
            + "\n".join(avisos_gravacao)
            + "\n\nIgnore qualquer conteúdo que pertença aos outros módulos listados acima.\n"
        )
    else:
        bloco_aviso = ""

    cacheado = f"""# CONTEXTO DO MÓDULO {aula.modulo_id} — {aula.modulo_nome}

Este módulo cobre as seguintes aulas:
{aulas_irmas_str}
{bloco_aviso}
A transcrição abaixo reúne {len(gravs_usadas)} gravação(ões) do curso "Casa de Baixo Custo Sustentável" (Amanda e Fernando), selecionadas por terem maior cobertura do tópico solicitado. Pode conter conteúdo de múltiplas aulas (e múltiplos módulos) misturado — você deve isolar o trecho relevante à aula específica solicitada.

## Transcrição

{transcricao_completa}
"""

    # Parte VOLÁTIL: a aula específica.
    eh_introducao = (
        aula.posicao_no_modulo == 1
        or "introdução" in aula.titulo.lower()
        or "introducao" in aula.titulo.lower()
    )

    nota_introducao = ""
    if eh_introducao:
        # Lista as próximas aulas do módulo pra deixar claro o que NÃO aprofundar
        proximas = aula.aulas_irmas[aula.posicao_no_modulo:aula.posicao_no_modulo + 4]
        if proximas:
            proximas_str = ", ".join(f'"{t}"' for t in proximas)
            nota_introducao = (
                f"\n**Esta é uma aula de INTRODUÇÃO ao módulo.** "
                f"Apresente panorama do tópico do módulo. "
                f"NÃO aprofunde nos tipos específicos que serão cobertos pelas "
                f"próximas aulas ({proximas_str}); apenas mencione-os.\n"
            )

    volatil = f"""## Tarefa

Extraia da transcrição acima o conteúdo que cobre especificamente a aula:

**Aula {aula.posicao_no_modulo} do Módulo {aula.modulo_id}: "{aula.titulo}"**
{nota_introducao}
Localize o trecho que aborda esse tópico, ignorando:
- O conteúdo das outras aulas-irmãs listadas no contexto (a menos que sejam mencionadas de passagem)
- Qualquer conteúdo de outros módulos (mesmo que apareça na transcrição)

Reescreva como aula completa em Markdown, seguindo todas as regras do system prompt.

Se a transcrição **não desenvolver esse tópico específico** (apenas mencionar de passagem ou não cobrir), responda: AULA_AUSENTE"""

    return cacheado, volatil


# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------

@dataclass
class ResultadoAula:
    aula_id: int
    modulo_id: int
    titulo: str
    status: str  # "ok" | "ausente" | "erro"
    conteudo: str = ""
    erro: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_cache_read: int = 0
    tokens_cache_write: int = 0
    custo_usd: float = 0.0
    duracao_s: float = 0.0


def calcular_custo(input_tokens: int, output_tokens: int, cache_read: int, cache_write: int) -> float:
    # Sonnet 4 pricing (USD per million tokens):
    # input: 3.00 / cache_write: 3.75 / cache_read: 0.30 / output: 15.00
    return (
        input_tokens * 3.00 / 1_000_000
        + cache_write * 3.75 / 1_000_000
        + cache_read * 0.30 / 1_000_000
        + output_tokens * 15.00 / 1_000_000
    )


def extrair_aula(
    client: anthropic.Anthropic,
    aula: Aula,
    gravacoes_texto: dict[int, str],
    gravacoes_selecionadas: list[int] | None = None,
    usar_cache: bool = True,
    max_retries: int = 5,
) -> ResultadoAula:
    """
    Executa uma chamada à Anthropic API e devolve o resultado.

    Retry automático:
      - 429 (rate_limit): espera `retry-after` do header (ou 70s) e re-tenta
      - 5xx / 529 (overloaded ou erro interno transiente): backoff exponencial
        2s, 4s, 8s, 16s, 32s

    Demais exceções (incluindo 400 prompt too long) não são re-tentadas
    porque indicam erro estrutural da requisição.

    Se `gravacoes_selecionadas` é fornecido, monta o prompt com essas
    gravações específicas (modo "ranqueamento por aula"). Caso contrário,
    cai no comportamento legado (gravações do módulo).
    """
    cacheado, volatil = montar_prompt_aula(aula, gravacoes_texto, gravacoes_selecionadas)

    t0 = time.time()
    attempt = 0
    last_error: Exception | None = None

    while attempt <= max_retries:
        try:
            # Constrói o bloco de conteúdo. cache_control só é setado se
            # `usar_cache=True` — quando o ranqueamento por aula está
            # ativo, geralmente cada aula tem seleção própria e o cache
            # não é reusado, então pagar cache_write é desperdício.
            content_blocks: list[dict] = [
                {"type": "text", "text": cacheado},
                {"type": "text", "text": volatil},
            ]
            if usar_cache:
                content_blocks[0]["cache_control"] = {"type": "ephemeral"}

            msg = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": content_blocks}],
            )
            dt = time.time() - t0

            # Extrai resposta
            texto = msg.content[0].text.strip()

            # Verifica se é AULA_AUSENTE
            if texto.upper().startswith("AULA_AUSENTE"):
                status = "ausente"
                conteudo = ""
            else:
                status = "ok"
                conteudo = texto

            # Tokens
            usage = msg.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0

            custo = calcular_custo(input_tokens, output_tokens, cache_read, cache_write)

            return ResultadoAula(
                aula_id=aula.id_global,
                modulo_id=aula.modulo_id,
                titulo=aula.titulo,
                status=status,
                conteudo=conteudo,
                tokens_input=input_tokens,
                tokens_output=output_tokens,
                tokens_cache_read=cache_read,
                tokens_cache_write=cache_write,
                custo_usd=custo,
                duracao_s=dt,
            )

        except anthropic.RateLimitError as e:
            last_error = e
            wait = 70
            try:
                hdr = (e.response.headers.get("retry-after") if e.response is not None else None)
                if hdr:
                    wait = int(float(hdr))
            except Exception:
                pass
            wait = max(wait, 30)

            attempt += 1
            if attempt > max_retries:
                break

            print(f"    [rate_limit] tentativa {attempt}/{max_retries} — pausa {wait}s antes de re-tentar...")
            time.sleep(wait)
            continue

        except (anthropic.InternalServerError, anthropic.APIStatusError) as e:
            # Erros 5xx / 529 (overloaded). Re-tenta com backoff exponencial.
            # Verifica se realmente é um erro transiente baseado em status code
            status_code = getattr(e, "status_code", None)
            if status_code is None or status_code < 500 and status_code != 529:
                # Não é transiente — propaga como erro definitivo
                return ResultadoAula(
                    aula_id=aula.id_global,
                    modulo_id=aula.modulo_id,
                    titulo=aula.titulo,
                    status="erro",
                    erro=str(e),
                    duracao_s=time.time() - t0,
                )

            last_error = e
            attempt += 1
            if attempt > max_retries:
                break

            wait = min(2 ** attempt, 32)
            print(f"    [server_error {status_code}] tentativa {attempt}/{max_retries} — pausa {wait}s antes de re-tentar...")
            time.sleep(wait)
            continue

        except anthropic.APIConnectionError as e:
            # Erro de conexão transiente (timeout, reset, etc) — retry curto
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break

            wait = min(2 ** attempt, 16)
            print(f"    [connection_error] tentativa {attempt}/{max_retries} — pausa {wait}s antes de re-tentar...")
            time.sleep(wait)
            continue

        except Exception as e:
            return ResultadoAula(
                aula_id=aula.id_global,
                modulo_id=aula.modulo_id,
                titulo=aula.titulo,
                status="erro",
                erro=str(e),
                duracao_s=time.time() - t0,
            )

    # Esgotou retries
    return ResultadoAula(
        aula_id=aula.id_global,
        modulo_id=aula.modulo_id,
        titulo=aula.titulo,
        status="erro",
        erro=f"esgotou {max_retries} retries: {last_error}",
        duracao_s=time.time() - t0,
    )


# -----------------------------------------------------------------------------
# PERSISTÊNCIA
# -----------------------------------------------------------------------------

def salvar_aula(resultado: ResultadoAula):
    """Salva uma aula individual em arquivo (cache de progresso)."""
    AULAS_DIR.mkdir(parents=True, exist_ok=True)
    nome = f"{resultado.modulo_id:02d}_{resultado.aula_id:03d}.md"
    path = AULAS_DIR / nome
    
    header = f"""<!-- 
aula_id: {resultado.aula_id}
modulo_id: {resultado.modulo_id}
titulo: {resultado.titulo}
status: {resultado.status}
tokens_input: {resultado.tokens_input}
tokens_output: {resultado.tokens_output}
tokens_cache_read: {resultado.tokens_cache_read}
tokens_cache_write: {resultado.tokens_cache_write}
custo_usd: {resultado.custo_usd:.6f}
-->

"""
    if resultado.status == "ok":
        path.write_text(header + resultado.conteudo + "\n", encoding="utf-8")
    elif resultado.status == "ausente":
        path.write_text(header + "*Esta aula não é desenvolvida nas gravações disponíveis.*\n", encoding="utf-8")
    else:
        path.write_text(header + f"ERRO: {resultado.erro}\n", encoding="utf-8")


def carregar_aula_salva(modulo_id: int, aula_id: int) -> dict | None:
    """Se já foi extraída, devolve metadados + conteúdo."""
    nome = f"{modulo_id:02d}_{aula_id:03d}.md"
    path = AULAS_DIR / nome
    if not path.exists():
        return None
    texto = path.read_text(encoding="utf-8")
    # Extrai metadados do header HTML comment
    meta_match = re.search(r'<!--\s*(.*?)\s*-->', texto, re.DOTALL)
    if not meta_match:
        return None
    meta = {}
    for linha in meta_match.group(1).strip().split("\n"):
        if ": " in linha:
            k, v = linha.split(": ", 1)
            meta[k.strip()] = v.strip()
    conteudo = texto[meta_match.end():].strip()
    return {"meta": meta, "conteudo": conteudo}


# -----------------------------------------------------------------------------
# CONSOLIDAÇÃO
# -----------------------------------------------------------------------------

def consolidar_temas(aulas: list[Aula]):
    """Lê todas as aulas individuais e monta os 12 arquivos finais."""
    TEMAS_OUT.mkdir(parents=True, exist_ok=True)
    
    # Agrupa por módulo
    por_modulo: dict[int, list[Aula]] = {}
    for a in aulas:
        por_modulo.setdefault(a.modulo_id, []).append(a)
    
    with open(COURSE_STRUCTURE, encoding="utf-8") as f:
        cs = json.load(f)
    modulo_info = {m["id"]: m for m in cs["modulos"]}
    
    for mid, lista_aulas in sorted(por_modulo.items()):
        m = modulo_info[mid]
        slug_base = m["slug"]
        nome_arquivo = f"{mid:02d}_{slug_base}.md"
        
        lines = []
        lines.append(f"# {m['nome']}")
        lines.append("")
        lines.append(f"> Módulo {mid} de 12 · {len(lista_aulas)} aulas")
        lines.append("> Fonte: Curso Casa de Baixo Custo Sustentável — Amanda & Fernando")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Visão Geral")
        lines.append("")
        # Visão Geral pode ser gerada num passo separado; por hora deixamos um placeholder
        lines.append(f"_Visão geral do módulo {mid}._")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Aulas")
        lines.append("")
        
        for a in lista_aulas:
            salva = carregar_aula_salva(a.modulo_id, a.id_global)
            if not salva:
                continue
            lines.append(f"### {a.posicao_no_modulo}. {a.titulo}")
            lines.append("")
            lines.append(salva["conteudo"])
            lines.append("")
        
        (TEMAS_OUT / nome_arquivo).write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    print(f"\n12 arquivos consolidados em {TEMAS_OUT}")


def gerar_transcricoes(gravacoes_texto: dict[int, str]):
    """Salva as 21 gravações em arquivos individuais (formato final)."""
    TRANSCRICOES_OUT.mkdir(parents=True, exist_ok=True)
    
    # Lê o mapeamento pra anotar qual módulo cada gravação cobre
    with open(MAPEAMENTO, encoding="utf-8") as f:
        map_data = json.load(f)
    
    info_grav = {}
    for entrada in map_data["arquivos_gerados"]:
        mid = entrada["modulo_id"]
        nome = entrada["nome"]
        for g in entrada["gravacoes"]:
            info_grav.setdefault(g, []).append((mid, nome))
    
    for num in sorted(gravacoes_texto.keys()):
        modulos = info_grav.get(num, [])
        mods_str = ", ".join(f"Módulo {mid} — {nome}" for mid, nome in modulos) if modulos else "(sem módulo mapeado)"
        
        lines = [
            f"# Gravação {num}",
            "",
            f"> Fonte: ACBS-{num}-mp3 · Curso Casa de Baixo Custo Sustentável (Amanda & Fernando)",
            f"> Cobre: {mods_str}",
            "",
            "---",
            "",
            gravacoes_texto[num],
        ]
        (TRANSCRICOES_OUT / f"{num:02d}.md").write_text("\n".join(lines), encoding="utf-8")
    
    print(f"21 transcrições salvas em {TRANSCRICOES_OUT}")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="Extrai conteúdo das 89 aulas do curso")
    p.add_argument("--dry-run", action="store_true", help="só mostra o plano, não chama API")
    p.add_argument("--pilot", type=str, default="", help="comma-separated aula_ids pra rodar como piloto (ex: '28,56')")
    p.add_argument("--resume", action="store_true", help="pula aulas que já têm arquivo salvo")
    p.add_argument("--only-module", type=int, default=0, help="processa só esse módulo")
    p.add_argument("--consolidar", action="store_true", help="só consolida arquivos existentes em temas_v3/")
    p.add_argument("--transcricoes", action="store_true", help="só gera as 21 transcrições em build/transcricoes/")
    args = p.parse_args()
    
    print(f"Repo root: {REPO_ROOT}")
    
    # Carrega tudo
    aulas = carregar_aulas()
    gravacoes = carregar_gravacoes()
    print(f"Carregadas: {len(aulas)} aulas, {len(gravacoes)} gravações")
    
    # Modos especiais
    if args.transcricoes:
        gerar_transcricoes(gravacoes)
        return 0
    
    if args.consolidar:
        consolidar_temas(aulas)
        return 0
    
    # Filtro de execução
    if args.pilot:
        ids_piloto = {int(s.strip()) for s in args.pilot.split(",") if s.strip()}
        aulas_run = [a for a in aulas if a.id_global in ids_piloto]
        print(f"\nMODO PILOTO: rodando {len(aulas_run)} aula(s): {sorted(ids_piloto)}")
    elif args.only_module:
        aulas_run = [a for a in aulas if a.modulo_id == args.only_module]
        print(f"\nMODO MÓDULO: rodando módulo {args.only_module} ({len(aulas_run)} aulas)")
    else:
        aulas_run = aulas
        print(f"\nMODO COMPLETO: rodando 89 aulas")
    
    if args.resume:
        antes = len(aulas_run)
        pendentes = []
        for a in aulas_run:
            salva = carregar_aula_salva(a.modulo_id, a.id_global)
            if salva is None:
                # Não foi processada ainda
                pendentes.append(a)
            elif salva["meta"].get("status") == "erro":
                # Processada mas deu erro — re-rodar
                pendentes.append(a)
            # OK ou AUSENTE: pula
        aulas_run = pendentes
        print(f"  --resume: {antes - len(aulas_run)} aulas já concluídas (ok/ausente), processando {len(aulas_run)} (novas + erros anteriores)")
    
    if args.dry_run:
        print("\n[dry-run] Aulas que seriam processadas:")
        for a in aulas_run:
            print(f"  Aula {a.id_global:>2} (Módulo {a.modulo_id}): {a.titulo}")
        # Estima custo
        # Pra dry-run, estima sem cache
        print(f"\nEstimativa: ~R${len(aulas_run) * 0.40:.2f} a R${len(aulas_run) * 0.60:.2f} (depende muito do tamanho do módulo)")
        return 0
    
    # API key check
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERRO: defina ANTHROPIC_API_KEY no ambiente.", file=sys.stderr)
        return 1
    
    client = anthropic.Anthropic()

    # Carrega termos-âncora pra ranqueamento.
    termos_aulas = carregar_termos()
    if termos_aulas:
        print(f"\nRanqueamento ativo: {len(termos_aulas)} aulas com termos-âncora.")
    else:
        print("\nRanqueamento INATIVO: knowledge/termos_aulas.json não encontrado, usando gravações por módulo (legado).")

    # Pré-computa a seleção de gravações pra cada aula e adiciona como atributo.
    # Isso permite ordenar o loop de forma que aulas com seleções idênticas
    # rodem em sequência (maximiza reuso de cache).
    selecoes_por_aula: dict[int, list[int]] = {}
    descartes_por_aula: dict[int, list[int]] = {}
    for a in aulas_run:
        esc, des = ranquear_gravacoes_por_aula(a, gravacoes, termos_aulas)
        selecoes_por_aula[a.id_global] = esc
        descartes_por_aula[a.id_global] = des

    # Ordena aulas pelo conjunto de gravações selecionadas (depois por
    # posição no módulo). Aulas com mesma seleção ficam adjacentes → cache
    # reusado.
    def chave_ordenacao(a: Aula) -> tuple:
        sel = tuple(selecoes_por_aula[a.id_global])
        return (a.modulo_id, sel, a.posicao_no_modulo)

    aulas_run.sort(key=chave_ordenacao)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Loop
    total_custo = 0.0
    resultados = []

    # Janela móvel de tokens consumidos nos últimos 60s (pra evitar 429).
    # Tier 1 do Sonnet 4.5 = 30k input tokens/min. Mantemos uma margem.
    TPM_LIMIT = 30_000
    TPM_MARGIN = 0.85  # usa até 85% do limite antes de pausar
    janela_tokens: list[tuple[float, int]] = []  # [(timestamp, tokens_consumidos)]

    def tokens_na_janela() -> int:
        agora = time.time()
        # remove entradas com mais de 60s
        nonlocal janela_tokens
        janela_tokens = [(t, n) for t, n in janela_tokens if agora - t < 60]
        return sum(n for _, n in janela_tokens)

    selecao_anterior: tuple[int, ...] | None = None
    for i, aula in enumerate(aulas_run, 1):
        gravs_selecionadas = selecoes_por_aula[aula.id_global]
        descartadas = descartes_por_aula[aula.id_global]
        selecao_atual = tuple(gravs_selecionadas)

        # Estima tokens da próxima chamada (input cacheado + volátil)
        chars_estimados = sum(len(gravacoes[g]) for g in gravs_selecionadas) + 2000
        tokens_estimados = chars_estimados // 4

        # Se essa aula vai estourar a janela, espera
        consumido = tokens_na_janela()
        if consumido + tokens_estimados > int(TPM_LIMIT * TPM_MARGIN):
            if janela_tokens:
                mais_antiga = janela_tokens[0][0]
                espera = max(5, int(61 - (time.time() - mais_antiga)))
                print(f"  [throttle] janela com {consumido:,} tokens, próxima aula ~{tokens_estimados:,} — pausando {espera}s...")
                time.sleep(espera)
                consumido = tokens_na_janela()

        # Decide cache: ligar só se a próxima aula vai ter a mesma seleção
        # (cache_read barato) ou se essa é a primeira aula de um grupo de >=2
        # aulas com mesma seleção (cache_write compensa).
        # Lookahead simples: tenta usar cache se a aula seguinte (se houver)
        # tem mesma seleção.
        usar_cache = False
        if i < len(aulas_run):
            proxima_sel = tuple(selecoes_por_aula[aulas_run[i].id_global])
            if proxima_sel == selecao_atual:
                usar_cache = True
        # Também usar cache se a anterior teve mesma seleção (cache já está
        # quente do prompt anterior)
        if selecao_anterior == selecao_atual:
            usar_cache = True

        print(f"\n[{i}/{len(aulas_run)}] Aula {aula.id_global} — Módulo {aula.modulo_id} — {aula.titulo}")
        if termos_aulas:
            extra = f" (descartadas por budget: {descartadas})" if descartadas else ""
            cache_info = " [cache]" if usar_cache else ""
            print(f"  Gravações selecionadas: {gravs_selecionadas}{cache_info}{extra}")

        r = extrair_aula(
            client, aula, gravacoes,
            gravacoes_selecionadas=gravs_selecionadas,
            usar_cache=usar_cache,
        )
        resultados.append(r)
        salvar_aula(r)

        tokens_chamada = r.tokens_input + r.tokens_cache_write + r.tokens_cache_read
        if tokens_chamada > 0:
            janela_tokens.append((time.time(), tokens_chamada))

        if r.status == "ok":
            print(f"  OK em {r.duracao_s:.1f}s | output {r.tokens_output} tokens | "
                  f"cache_read {r.tokens_cache_read} | cache_write {r.tokens_cache_write} | "
                  f"custo ${r.custo_usd:.4f}")
        elif r.status == "ausente":
            print(f"  AULA_AUSENTE em {r.duracao_s:.1f}s | custo ${r.custo_usd:.4f}")
        else:
            print(f"  ERRO em {r.duracao_s:.1f}s: {r.erro}")

        total_custo += r.custo_usd
        selecao_anterior = selecao_atual
    
    # Log final
    LOG_FILE.write_text(
        json.dumps([asdict(r) for r in resultados], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    ok = sum(1 for r in resultados if r.status == "ok")
    aus = sum(1 for r in resultados if r.status == "ausente")
    erro = sum(1 for r in resultados if r.status == "erro")
    print(f"  OK:       {ok}")
    print(f"  AUSENTE:  {aus}")
    print(f"  ERRO:     {erro}")
    print(f"  Custo total: ${total_custo:.4f} (~R${total_custo*5.5:.2f})")
    print(f"\nLog: {LOG_FILE}")
    print(f"Aulas individuais: {AULAS_DIR}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
