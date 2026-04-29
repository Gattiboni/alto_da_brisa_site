"""
organizar_com_claude.py

Usa Claude API para mapear as 21 gravações às 89 aulas e gerar
knowledge/temas/01_introducao.md ... 12_instalacoes_residenciais.md

Inputs esperados (relativos à raiz do projeto):
  knowledge/curso_amanda_fernando_raw.md   ← transcrições brutas
  knowledge/descricoes_das_aulas.md        ← output do scraper
  knowledge/course_structure.json          ← estrutura do curso

Outputs:
  knowledge/temas/*.md                     ← um arquivo por módulo
  knowledge/mapeamento.json                ← diagnóstico do mapeamento
  knowledge/curso_limpo.md                 ← transcrições sem ruído

Uso:
  python organizar_com_claude.py

Custo estimado: ~21 chamadas de mapeamento (~50k tokens) + 12 intros de módulo.
"""

import re
import json
import os
import time
import unicodedata
from pathlib import Path
from collections import defaultdict

# ── Dependências ─────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env carregado manualmente ou via shell

try:
    import anthropic
except ImportError:
    print("ERRO: instale o SDK do Anthropic:")
    print("  pip install anthropic")
    raise SystemExit(1)

# ── Configuração ──────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
RAW_FILE    = BASE_DIR / "knowledge" / "curso_amanda_fernando_raw.md"
DESC_FILE   = BASE_DIR / "knowledge" / "descricoes_das_aulas.md"
STRUCT_FILE = BASE_DIR / "knowledge" / "course_structure.json"
TEMAS_DIR   = BASE_DIR / "knowledge" / "temas"
MAP_FILE    = BASE_DIR / "knowledge" / "mapeamento.json"
CLEAN_FILE  = BASE_DIR / "knowledge" / "curso_limpo.md"

MODEL       = "claude-sonnet-4-20250514"
MAX_TOKENS  = 1024

# Chars do início de cada gravação enviados para mapeamento.
# ~3000 chars ≈ ~750 tokens — suficiente para o Claude identificar o tema.
SAMPLE_CHARS = 3000

# ── Cliente Anthropic ─────────────────────────────────────────────────────────
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERRO: ANTHROPIC_API_KEY não encontrada no ambiente.")
    raise SystemExit(1)

client = anthropic.Anthropic(api_key=api_key)


# ── Limpeza de transcrição ────────────────────────────────────────────────────
def limpar_bloco(texto: str) -> str:
    linhas = texto.splitlines()
    limpas = []
    for linha in linhas:
        l = linha.strip()
        if re.match(r'^\*\*Meeting Date:\*\*', l):      continue
        if re.match(r'^# ACBS \d+', l):                 continue
        l = re.sub(r'\*\*Speaker \d+\*\*\s*\*\[\d+:\d+\]\*\s*:', '', l)
        l = re.sub(r'\*?\[\d{1,2}:\d{2}(:\d{2})?\]\*?', '', l)
        l = re.sub(r'\*\*Speaker \d+\*\*', '', l)
        if re.match(r'^-{3,}$', l): continue
        l = l.strip()
        if l:
            limpas.append(l)
    return '\n'.join(limpas)


# ── Parse do raw em gravações ─────────────────────────────────────────────────
def extrair_gravacoes(raw: str) -> list[dict]:
    partes = re.split(r'(## Gravação \d+ —.*)', raw)
    gravacoes = []
    i = 1
    while i < len(partes) - 1:
        header = partes[i].strip()
        corpo  = partes[i + 1] if i + 1 < len(partes) else ''
        num    = re.search(r'Gravação (\d+)', header)
        limpo  = limpar_bloco(corpo)
        gravacoes.append({
            'numero':      int(num.group(1)) if num else 0,
            'header':      header,
            'texto_limpo': limpo,
        })
        i += 2
    return gravacoes


# ── Parse das descrições das aulas ────────────────────────────────────────────
def parse_descricoes(desc_file: Path) -> dict:
    """
    Retorna:
      {
        aula_num: {
          'titulo':   str,
          'modulo':   str,
          'descricao': str,
        }
      }
    """
    texto  = desc_file.read_text(encoding='utf-8', errors='replace')
    linhas = texto.splitlines()

    resultado   = {}
    modulo_atual = ''
    aula_num     = None
    aula_titulo  = ''
    desc_buf     = []

    def flush():
        if aula_num is not None:
            resultado[aula_num] = {
                'titulo':   aula_titulo,
                'modulo':   modulo_atual,
                'descricao': '\n'.join(desc_buf).strip(),
            }

    for linha in linhas:
        m_mod  = re.match(r'^## (.+)', linha)
        m_aula = re.match(r'^### (\d+)\.\s+(.+)', linha)

        if m_mod:
            flush()
            modulo_atual = m_mod.group(1).strip()
            aula_num     = None
            desc_buf     = []

        elif m_aula:
            flush()
            aula_num    = int(m_aula.group(1))
            aula_titulo = m_aula.group(2).strip()
            desc_buf    = []

        else:
            if aula_num is not None and linha.strip():
                desc_buf.append(linha.strip())

    flush()
    return resultado


# ── Mapear gravação → aulas via Claude ───────────────────────────────────────
def montar_lista_aulas(descricoes: dict) -> str:
    """Texto compacto com número, título e descrição curta de cada aula."""
    linhas = []
    modulo_atual = ''
    for num in sorted(descricoes.keys()):
        d = descricoes[num]
        if d['modulo'] != modulo_atual:
            modulo_atual = d['modulo']
            linhas.append(f"\n[{modulo_atual}]")
        desc_curta = d['descricao'][:200].replace('\n', ' ') if d['descricao'] else '[sem descrição]'
        linhas.append(f"  Aula {num}: {d['titulo']} — {desc_curta}")
    return '\n'.join(linhas)


def mapear_gravacao(gravacao: dict, lista_aulas: str) -> list[int]:
    """
    Chama Claude API com amostra da gravação + lista de aulas.
    Retorna lista de números de aulas identificadas.
    """
    amostra = gravacao['texto_limpo'][:SAMPLE_CHARS]

    prompt = f"""Você é um assistente que classifica trechos de transcrições de áudio de um curso de construção civil.

Abaixo está a lista de aulas do curso, organizadas por módulo:

{lista_aulas}

---

Abaixo está o início de uma gravação de áudio (Gravação {gravacao['numero']}):

{amostra}

---

Com base no conteúdo da gravação, quais aulas da lista acima ela provavelmente cobre?
Responda SOMENTE com um objeto JSON no formato:
{{"aulas": [lista de números de aula], "confianca": "alta|media|baixa", "raciocinio": "uma frase"}}

Exemplos válidos:
{{"aulas": [1, 2], "confianca": "alta", "raciocinio": "A gravação trata de objetivos e etapas introdutórias"}}
{{"aulas": [29, 30, 31], "confianca": "media", "raciocinio": "Fala sobre fundações e tipos de blocos"}}

Não inclua nada fora do JSON."""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = resp.content[0].text.strip()
        # Remove eventual markdown fence
        texto = re.sub(r'^```json\s*|```$', '', texto, flags=re.MULTILINE).strip()
        dados = json.loads(texto)
        return dados.get('aulas', []), dados.get('confianca', '?'), dados.get('raciocinio', '')
    except Exception as e:
        print(f"    AVISO: Claude retornou erro para Gravação {gravacao['numero']}: {e}")
        return [], 'erro', str(e)


# ── Gerar intro de módulo via Claude ─────────────────────────────────────────
def gerar_intro_modulo(nome_modulo: str, aulas_do_modulo: list[dict], amostra_transcript: str) -> str:
    """
    Gera um parágrafo de introdução ao módulo baseado nas aulas e no transcript.
    """
    nomes_aulas = '\n'.join(f"- {a['titulo']}" for a in aulas_do_modulo)

    prompt = f"""Você é o Claudinho da Brisa, assistente de conhecimento do Sítio Alto da Brisa.
Escreva um parágrafo introdutório conciso (3-5 frases) para o módulo "{nome_modulo}" de um curso de construção de baixo custo sustentável.
As aulas deste módulo são:
{nomes_aulas}

Trecho do conteúdo transcrito:
{amostra_transcript[:1500]}

Tom: informativo, direto, sem jargões desnecessários. Não use bullet points, só prosa.
Não inclua cabeçalhos, só o parágrafo."""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception as e:
        print(f"    AVISO: erro ao gerar intro para {nome_modulo}: {e}")
        return f"Este módulo aborda {nome_modulo} com foco em construção de baixo custo sustentável."


# ── Gerar arquivo markdown do módulo ─────────────────────────────────────────
def gerar_md_modulo(modulo_info: dict, aulas_com_desc: list[dict],
                    transcript_blocos: list[str], intro: str) -> str:
    linhas = [
        f"# {modulo_info['nome']}",
        "",
        f"> Módulo {modulo_info['id']} de 12 · {modulo_info['total_aulas']} aulas",
        f"> Fonte: Curso Casa de Baixo Custo Sustentável — Amanda & Fernando",
        "",
        "---",
        "",
        "## Visão Geral",
        "",
        intro,
        "",
        "---",
        "",
        "## Aulas",
        "",
    ]

    for aula in aulas_com_desc:
        linhas.append(f"### {aula['num']}. {aula['titulo']}")
        linhas.append("")
        if aula['descricao'] and aula['descricao'] != '[sem descrição]':
            linhas.append(aula['descricao'])
        else:
            linhas.append("*Descrição não disponível para esta aula.*")
        linhas.append("")

    if transcript_blocos:
        linhas += [
            "---",
            "",
            "## Transcrição",
            "",
        ]
        for bloco in transcript_blocos:
            linhas.append(bloco.strip())
            linhas.append("")
            linhas.append("---")
            linhas.append("")

    return '\n'.join(linhas)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Valida arquivos de entrada
    for f in [RAW_FILE, DESC_FILE, STRUCT_FILE]:
        if not f.exists():
            print(f"ERRO: arquivo não encontrado: {f}")
            raise SystemExit(1)

    print("Carregando dados...")
    raw        = RAW_FILE.read_text(encoding='utf-8', errors='replace')
    estrutura  = json.loads(STRUCT_FILE.read_text(encoding='utf-8'))
    descricoes = parse_descricoes(DESC_FILE)

    print(f"  {len(descricoes)} aulas com descrição parseadas")
    gravacoes = extrair_gravacoes(raw)
    print(f"  {len(gravacoes)} gravações extraídas")

    # Gera curso_limpo.md
    print("\nGerando curso_limpo.md...")
    linhas_limpo = ["# Curso Amanda & Fernando — Transcrição Limpa\n\n---\n"]
    for g in gravacoes:
        linhas_limpo.append(f"## {g['header']}\n\n{g['texto_limpo']}\n\n---\n")
    CLEAN_FILE.write_text('\n'.join(linhas_limpo), encoding='utf-8')
    print(f"  → {CLEAN_FILE.stat().st_size / 1024:.0f} KB")

    # Lista de aulas para o prompt de mapeamento
    lista_aulas = montar_lista_aulas(descricoes)

    # Mapeamento: gravação → aulas
    print("\nMapeando gravações → aulas via Claude API...")
    gravacao_para_aulas = {}
    aula_para_gravacoes = defaultdict(list)

    for g in gravacoes:
        print(f"  [{g['numero']:02d}/21] Gravação {g['numero']}...", end=' ', flush=True)
        aulas, confianca, razao = mapear_gravacao(g, lista_aulas)
        print(f"aulas={aulas} ({confianca})")
        gravacao_para_aulas[g['numero']] = {
            'aulas': aulas,
            'confianca': confianca,
            'raciocinio': razao,
        }
        for aula_num in aulas:
            aula_para_gravacoes[aula_num].append(g)
        time.sleep(0.3)  # rate limiting suave

    # Agrupa aulas por módulo
    modulo_para_aulas = {}
    for modulo in estrutura['modulos']:
        modulo_para_aulas[modulo['id']] = modulo

    # Descobre qual módulo cada aula pertence
    aula_para_modulo = {}
    for aula_num, info in descricoes.items():
        for modulo in estrutura['modulos']:
            if any(
                aula_num <= sum(m['total_aulas'] for m in estrutura['modulos'][:i+1])
                for i, m in enumerate(estrutura['modulos'])
                if m['id'] == modulo['id']
            ):
                aula_para_modulo[aula_num] = modulo['id']
                break

    # Monta faixas de aulas por módulo a partir da estrutura
    aula_inicio = 1
    modulo_faixas = {}
    for modulo in estrutura['modulos']:
        fim = aula_inicio + modulo['total_aulas'] - 1
        modulo_faixas[modulo['id']] = (aula_inicio, fim)
        aula_inicio = fim + 1

    # Gravações por módulo: baseado nas aulas mapeadas
    gravacoes_por_modulo = defaultdict(list)
    for g in gravacoes:
        aulas_da_grav = gravacao_para_aulas[g['numero']]['aulas']
        modulos_vistos = set()
        for aula_num in aulas_da_grav:
            for mid, (ini, fim) in modulo_faixas.items():
                if ini <= aula_num <= fim:
                    modulos_vistos.add(mid)
        for mid in modulos_vistos:
            gravacoes_por_modulo[mid].append(g)

    # Fallback: gravações sem mapeamento vão para módulo 1
    sem_mapa = [g for g in gravacoes if not gravacao_para_aulas[g['numero']]['aulas']]
    for g in sem_mapa:
        gravacoes_por_modulo[1].append(g)

    # Gera arquivos por módulo
    print("\nGerando arquivos de módulo...")
    TEMAS_DIR.mkdir(parents=True, exist_ok=True)
    arquivos_gerados = []

    for modulo in estrutura['modulos']:
        mid  = modulo['id']
        ini, fim = modulo_faixas[mid]
        slug = modulo['slug']
        fname = f"{mid:02d}_{slug}.md"
        fpath = TEMAS_DIR / fname

        # Aulas deste módulo com descrição
        aulas_com_desc = []
        for num in range(ini, fim + 1):
            if num in descricoes:
                aulas_com_desc.append({
                    'num': num,
                    'titulo': descricoes[num]['titulo'],
                    'descricao': descricoes[num]['descricao'],
                })
            else:
                nome_da_lista = modulo['aulas'][num - ini] if (num - ini) < len(modulo['aulas']) else f"Aula {num}"
                aulas_com_desc.append({
                    'num': num,
                    'titulo': nome_da_lista,
                    'descricao': '',
                })

        # Transcript blocos das gravações deste módulo (deduplica)
        gravs_do_mod = gravacoes_por_modulo.get(mid, [])
        vistos = set()
        blocos = []
        for g in gravs_do_mod:
            if g['numero'] not in vistos:
                vistos.add(g['numero'])
                blocos.append(f"### Gravação {g['numero']}\n\n{g['texto_limpo']}")

        # Intro gerado por Claude
        amostra = blocos[0][:1500] if blocos else ''
        print(f"  [{mid:02d}] {modulo['nome']} — gerando intro...", end=' ', flush=True)
        intro = gerar_intro_modulo(modulo['nome'], aulas_com_desc, amostra)
        print("✓")
        time.sleep(0.3)

        conteudo = gerar_md_modulo(modulo, aulas_com_desc, blocos, intro)
        fpath.write_text(conteudo, encoding='utf-8')
        size_kb = fpath.stat().st_size / 1024
        print(f"       → {fname} ({size_kb:.0f} KB, {len(vistos)} gravação/ões)")
        arquivos_gerados.append({
            'modulo_id': mid,
            'nome': modulo['nome'],
            'arquivo': fname,
            'aulas': list(range(ini, fim + 1)),
            'gravacoes': sorted(list(vistos)),
            'size_kb': round(size_kb, 1),
        })

    # Salva mapeamento
    MAP_FILE.write_text(
        json.dumps({
            'por_gravacao': gravacao_para_aulas,
            'arquivos_gerados': arquivos_gerados,
        }, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print("\n" + "=" * 55)
    print("CONCLUÍDO")
    print(f"  Módulos gerados:  {len(arquivos_gerados)} arquivos em {TEMAS_DIR}/")
    print(f"  curso_limpo.md:   {CLEAN_FILE.stat().st_size / 1024:.0f} KB")
    print(f"  mapeamento.json:  salvo")
    print()
    print("Próximo passo: revise mapeamento.json e ajuste")
    print("gravações mal classificadas antes de subir para o Supabase.")


if __name__ == "__main__":
    main()
