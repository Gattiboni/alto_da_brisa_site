"""
corrigir_mapeamento.py

Corrige dois problemas do mapeamento gerado pelo organizar_com_claude.py:

  1. Módulos vazios (8-Lajes, 12-Instalações): re-escaneia gravações
     adjacentes em múltiplas posições para encontrar o conteúdo perdido.

  2. Falsos positivos no módulo 4 (Orçamento inflado): re-verifica
     gravações suspeitas com amostra do meio do transcript.

Regenera SOMENTE os arquivos .md afetados e atualiza mapeamento.json.

Uso:
    python corrigir_mapeamento.py
"""

import re
import json
import os
import time
from pathlib import Path
from collections import defaultdict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
except ImportError:
    print("ERRO: pip install anthropic")
    raise SystemExit(1)

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
RAW_FILE    = BASE_DIR / "knowledge" / "curso_amanda_fernando_raw.md"
DESC_FILE   = BASE_DIR / "knowledge" / "descricoes_das_aulas.md"
STRUCT_FILE = BASE_DIR / "knowledge" / "course_structure.json"
MAP_FILE    = BASE_DIR / "knowledge" / "mapeamento.json"
TEMAS_DIR   = BASE_DIR / "knowledge" / "temas"

MODEL      = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ── Limpeza ───────────────────────────────────────────────────────────────────
def limpar_bloco(texto: str) -> str:
    linhas = texto.splitlines()
    limpas = []
    for linha in linhas:
        l = linha.strip()
        if re.match(r'^\*\*Meeting Date:\*\*', l): continue
        if re.match(r'^# ACBS \d+', l):           continue
        l = re.sub(r'\*\*Speaker \d+\*\*\s*\*\[\d+:\d+\]\*\s*:', '', l)
        l = re.sub(r'\*?\[\d{1,2}:\d{2}(:\d{2})?\]\*?', '', l)
        l = re.sub(r'\*\*Speaker \d+\*\*', '', l)
        if re.match(r'^-{3,}$', l): continue
        l = l.strip()
        if l:
            limpas.append(l)
    return '\n'.join(limpas)


def extrair_gravacoes(raw: str) -> dict[int, dict]:
    partes = re.split(r'(## Gravação \d+ —.*)', raw)
    gravacoes = {}
    i = 1
    while i < len(partes) - 1:
        header = partes[i].strip()
        corpo  = partes[i + 1] if i + 1 < len(partes) else ''
        num    = re.search(r'Gravação (\d+)', header)
        if num:
            n = int(num.group(1))
            limpo = limpar_bloco(corpo)
            gravacoes[n] = {'numero': n, 'header': header, 'texto_limpo': limpo}
        i += 2
    return gravacoes


def parse_descricoes(desc_file: Path) -> dict:
    texto  = desc_file.read_text(encoding='utf-8', errors='replace')
    linhas = texto.splitlines()
    resultado = {}
    modulo_atual = ''
    aula_num = None
    aula_titulo = ''
    desc_buf = []

    def flush():
        if aula_num is not None:
            resultado[aula_num] = {
                'titulo': aula_titulo,
                'modulo': modulo_atual,
                'descricao': '\n'.join(desc_buf).strip(),
            }

    for linha in linhas:
        m_mod  = re.match(r'^## (.+)', linha)
        m_aula = re.match(r'^### (\d+)\.\s+(.+)', linha)
        if m_mod:
            flush()
            modulo_atual = m_mod.group(1).strip()
            aula_num = None
            desc_buf = []
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


# ── Amostras em múltiplas posições ────────────────────────────────────────────
def amostras_gravacao(texto: str, n_amostras: int = 4, chars_por_amostra: int = 2500) -> list[str]:
    """Retorna n_amostras trechos distribuídos ao longo do texto."""
    total = len(texto)
    if total == 0:
        return ['']
    amostras = []
    for i in range(n_amostras):
        inicio = int((total / n_amostras) * i)
        trecho = texto[inicio: inicio + chars_por_amostra]
        amostras.append(trecho)
    return amostras


# ── Claude: busca módulos em amostra ─────────────────────────────────────────
def verificar_modulos_em_amostra(
    num_grav: int,
    posicao: str,
    amostra: str,
    modulos_alvo: list[dict],   # [{'id', 'nome', 'aulas_range': (ini, fim)}]
) -> list[int]:
    """
    Pergunta ao Claude se a amostra contém conteúdo de algum dos módulos alvo.
    Retorna lista de module IDs detectados.
    """
    descricao_modulos = '\n'.join(
        f"  Módulo {m['id']}: {m['nome']} (aulas {m['aulas_range'][0]}–{m['aulas_range'][1]})"
        for m in modulos_alvo
    )

    prompt = f"""Você analisa transcrições de um curso de construção civil.

Módulos que precisamos identificar:
{descricao_modulos}

Trecho da Gravação {num_grav} ({posicao}):

{amostra}

---
Este trecho contém conteúdo de algum dos módulos listados acima?
Responda SOMENTE com JSON:
{{"modulos_encontrados": [lista de IDs de módulo encontrados, ou [] se nenhum], "raciocinio": "uma frase"}}

Seja conservador: só inclua um módulo se o conteúdo tratar CLARAMENTE daquele tema."""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = resp.content[0].text.strip()
        texto = re.sub(r'^```json\s*|```$', '', texto, flags=re.MULTILINE).strip()
        dados = json.loads(texto)
        return dados.get('modulos_encontrados', [])
    except Exception as e:
        print(f"    AVISO Claude (grav {num_grav}, {posicao}): {e}")
        return []


# ── Claude: verificar se gravação é falso positivo para módulo ───────────────
def verificar_falso_positivo(num_grav: int, texto_limpo: str, modulo_suspeito: dict) -> bool:
    """
    Verifica se uma gravação é genuinamente sobre um módulo
    ou se foi classificada por mencionar o tema de passagem.
    Amostra o MEIO da gravação, que é onde o conteúdo principal costuma estar.
    """
    meio = len(texto_limpo) // 2
    amostra = texto_limpo[meio - 1500: meio + 1500]

    prompt = f"""Gravação {num_grav} foi classificada como pertencente ao módulo "{modulo_suspeito['nome']}".

Trecho do MEIO desta gravação:

{amostra}

---
Este trecho trata PRIMARIAMENTE do tema "{modulo_suspeito['nome']}"?
Ou o tema aparece apenas de passagem, como menção rápida ou introdução?

Responda SOMENTE com JSON:
{{"primariamente": true_ou_false, "raciocinio": "uma frase"}}"""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = resp.content[0].text.strip()
        texto = re.sub(r'^```json\s*|```$', '', texto, flags=re.MULTILINE).strip()
        dados = json.loads(texto)
        return dados.get('primariamente', True)
    except Exception as e:
        print(f"    AVISO Claude (falso positivo grav {num_grav}): {e}")
        return True  # conservador: mantém classificação em caso de erro


# ── Gera arquivo .md de módulo ────────────────────────────────────────────────
def gerar_md_modulo(modulo: dict, aulas_com_desc: list[dict],
                    blocos: list[str], intro: str) -> str:
    linhas = [
        f"# {modulo['nome']}",
        "",
        f"> Módulo {modulo['id']} de 12 · {modulo['total_aulas']} aulas",
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
        desc = aula.get('descricao', '')
        if desc and desc != '[sem descrição]':
            linhas.append(desc)
        else:
            linhas.append("*Descrição não disponível para esta aula.*")
        linhas.append("")

    if blocos:
        linhas += ["---", "", "## Transcrição", ""]
        for bloco in blocos:
            linhas.append(bloco.strip())
            linhas.append("")
            linhas.append("---")
            linhas.append("")

    return '\n'.join(linhas)


def gerar_intro(modulo: dict, aulas: list[dict], amostra: str) -> str:
    nomes = '\n'.join(f"- {a['titulo']}" for a in aulas)
    prompt = f"""Escreva um parágrafo introdutório conciso (3-5 frases) para o módulo "{modulo['nome']}" de um curso de construção de baixo custo sustentável.
Aulas do módulo:
{nomes}

Trecho do conteúdo:
{amostra[:1200]}

Tom: informativo, direto. Só prosa, sem bullet points nem cabeçalhos."""
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception as e:
        return f"Este módulo aborda {modulo['nome']} com foco em construção de baixo custo sustentável."


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Carregando dados...")
    raw        = RAW_FILE.read_text(encoding='utf-8', errors='replace')
    estrutura  = json.loads(STRUCT_FILE.read_text(encoding='utf-8'))
    descricoes = parse_descricoes(DESC_FILE)
    mapeamento = json.loads(MAP_FILE.read_text(encoding='utf-8'))
    gravacoes  = extrair_gravacoes(raw)

    por_gravacao = mapeamento['por_gravacao']

    # Faixas de aulas por módulo
    aula_inicio = 1
    modulo_faixas = {}
    modulo_por_id = {}
    for modulo in estrutura['modulos']:
        fim = aula_inicio + modulo['total_aulas'] - 1
        modulo_faixas[modulo['id']] = (aula_inicio, fim)
        modulo_por_id[modulo['id']] = modulo
        aula_inicio = fim + 1

    # ── 1. CORRIGIR MÓDULOS VAZIOS ─────────────────────────────────────────────
    modulos_vazios = [8, 12]  # Lajes e Instalações
    gravacoes_candidatas = {
        8: [15, 16, 17],   # Entre Estruturas e Coberturas
        12: [20, 21],      # Final do curso
    }

    print("\n── Buscando conteúdo para módulos vazios ─────────────────────")
    modulos_alvo = [
        {
            'id': mid,
            'nome': modulo_por_id[mid]['nome'],
            'aulas_range': modulo_faixas[mid],
        }
        for mid in modulos_vazios
    ]

    modulo_grav_encontradas = defaultdict(set)  # mid → {num_grav}

    for mid in modulos_vazios:
        candidatas = gravacoes_candidatas[mid]
        modulo = modulo_por_id[mid]
        print(f"\n  Módulo {mid} ({modulo['nome']}) — verificando gravações {candidatas}")

        for num_grav in candidatas:
            if num_grav not in gravacoes:
                continue
            texto = gravacoes[num_grav]['texto_limpo']
            amostras = amostras_gravacao(texto, n_amostras=4, chars_por_amostra=2500)
            posicoes = ['início', '25%', '50%', '75%']

            encontrou = False
            for pos, amostra in zip(posicoes, amostras):
                print(f"    Gravação {num_grav} @ {pos}...", end=' ', flush=True)
                mods_enc = verificar_modulos_em_amostra(num_grav, pos, amostra, [{'id': mid, 'nome': modulo['nome'], 'aulas_range': modulo_faixas[mid]}])
                if mid in mods_enc:
                    print(f"✓ ENCONTRADO")
                    modulo_grav_encontradas[mid].add(num_grav)
                    encontrou = True
                    # Atualiza mapeamento da gravação
                    aulas_atuais = por_gravacao[str(num_grav)]['aulas']
                    ini, fim = modulo_faixas[mid]
                    # Adiciona aulas deste módulo ao mapeamento da gravação
                    for aula_num in range(ini, fim + 1):
                        if aula_num not in aulas_atuais:
                            aulas_atuais.append(aula_num)
                    aulas_atuais.sort()
                    por_gravacao[str(num_grav)]['aulas'] = aulas_atuais
                    por_gravacao[str(num_grav)]['raciocinio'] += f" | Revisado: contém módulo {mid}"
                else:
                    print(f"—")
                time.sleep(0.2)

            if not encontrou:
                print(f"    Gravação {num_grav}: conteúdo do módulo {mid} não encontrado.")

        if not modulo_grav_encontradas[mid]:
            print(f"  AVISO: módulo {mid} permanece sem gravação mapeada.")

    # ── 2. VERIFICAR FALSOS POSITIVOS NO MÓDULO 4 ─────────────────────────────
    print("\n── Verificando falsos positivos no módulo 4 (Orçamento) ──────")
    modulo_4 = modulo_por_id[4]

    # Gravações atribuídas ao módulo 4
    gravs_mod4 = [
        num for num, info in por_gravacao.items()
        if any(modulo_faixas[4][0] <= a <= modulo_faixas[4][1] for a in info['aulas'])
    ]

    removidas_mod4 = []
    for num_str in gravs_mod4:
        num = int(num_str)
        print(f"  Gravação {num}...", end=' ', flush=True)
        texto = gravacoes[num]['texto_limpo']
        e_principal = verificar_falso_positivo(num, texto, {'nome': modulo_4['nome']})
        if e_principal:
            print("✓ primariamente orçamento — mantido")
        else:
            print("✗ orçamento de passagem — REMOVIDO do módulo 4")
            removidas_mod4.append(num)
            # Remove aulas do módulo 4 da lista desta gravação
            ini, fim = modulo_faixas[4]
            aulas_novas = [a for a in por_gravacao[num_str]['aulas'] if not (ini <= a <= fim)]
            por_gravacao[num_str]['aulas'] = aulas_novas
            por_gravacao[num_str]['raciocinio'] += " | Revisado: removido do módulo 4 (menção de passagem)"
        time.sleep(0.3)

    # ── 3. RECALCULA GRAVAÇÕES POR MÓDULO ────────────────────────────────────
    print("\n── Recalculando distribuição de gravações por módulo ─────────")
    gravacoes_por_modulo = defaultdict(list)
    for num_str, info in por_gravacao.items():
        num = int(num_str)
        modulos_vistos = set()
        for aula_num in info['aulas']:
            for mid, (ini, fim) in modulo_faixas.items():
                if ini <= aula_num <= fim:
                    modulos_vistos.add(mid)
        for mid in modulos_vistos:
            gravacoes_por_modulo[mid].append(gravacoes[num])

    # ── 4. REGENERA ARQUIVOS AFETADOS ────────────────────────────────────────
    modulos_afetados = set(modulos_vazios) | {4} | set(
        mid for mid, gravs in gravacoes_por_modulo.items()
        if any(g['numero'] in removidas_mod4 for g in gravs)
    )
    # Adiciona módulos que ganharam gravações novas
    for mid in modulos_vazios:
        if modulo_grav_encontradas[mid]:
            modulos_afetados.add(mid)

    print(f"\n── Regenerando módulos afetados: {sorted(modulos_afetados)} ──")
    arquivos_atualizados = []

    for modulo in estrutura['modulos']:
        mid = modulo['id']
        if mid not in modulos_afetados:
            continue

        ini, fim = modulo_faixas[mid]
        slug  = modulo['slug']
        fname = f"{mid:02d}_{slug}.md"
        fpath = TEMAS_DIR / fname

        # Aulas com descrição
        aulas_com_desc = []
        for num in range(ini, fim + 1):
            if num in descricoes:
                aulas_com_desc.append({
                    'num': num,
                    'titulo': descricoes[num]['titulo'],
                    'descricao': descricoes[num]['descricao'],
                })
            else:
                idx = num - ini
                nome = modulo['aulas'][idx] if idx < len(modulo['aulas']) else f"Aula {num}"
                aulas_com_desc.append({'num': num, 'titulo': nome, 'descricao': ''})

        # Blocos de transcript
        gravs_do_mod = gravacoes_por_modulo.get(mid, [])
        vistos = set()
        blocos = []
        for g in sorted(gravs_do_mod, key=lambda x: x['numero']):
            if g['numero'] not in vistos:
                vistos.add(g['numero'])
                blocos.append(f"### Gravação {g['numero']}\n\n{g['texto_limpo']}")

        print(f"  [{mid:02d}] {modulo['nome']} — {len(vistos)} gravação/ões — gerando intro...", end=' ', flush=True)
        amostra = blocos[0][:1200] if blocos else ''
        intro = gerar_intro(modulo, aulas_com_desc, amostra)
        print("✓")
        time.sleep(0.3)

        conteudo = gerar_md_modulo(modulo, aulas_com_desc, blocos, intro)
        fpath.write_text(conteudo, encoding='utf-8')
        size_kb = fpath.stat().st_size / 1024
        print(f"       → {fname} ({size_kb:.0f} KB)")
        arquivos_atualizados.append(fname)

    # ── 5. ATUALIZA mapeamento.json ───────────────────────────────────────────
    # Atualiza arquivos_gerados no mapeamento
    for entry in mapeamento['arquivos_gerados']:
        mid = entry['modulo_id']
        gravs = sorted(list({g['numero'] for g in gravacoes_por_modulo.get(mid, [])}))
        entry['gravacoes'] = gravs

        fpath = TEMAS_DIR / entry['arquivo']
        if fpath.exists():
            entry['size_kb'] = round(fpath.stat().st_size / 1024, 1)

    mapeamento['por_gravacao'] = por_gravacao
    MAP_FILE.write_text(json.dumps(mapeamento, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n" + "=" * 55)
    print("CORRECÃO CONCLUÍDA")
    print(f"  Arquivos atualizados: {arquivos_atualizados}")
    print(f"  Gravações removidas do módulo 4: {removidas_mod4 or 'nenhuma'}")
    for mid in modulos_vazios:
        gravs = sorted(modulo_grav_encontradas[mid])
        print(f"  Módulo {mid} ganhou gravações: {gravs or 'nenhuma (revisar manualmente)'}")
    print(f"  mapeamento.json: atualizado")


if __name__ == "__main__":
    main()
