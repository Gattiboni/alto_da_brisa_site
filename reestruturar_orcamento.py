"""
reestruturar_orcamento.py

Problema atual do módulo 4:
  - Gravação 13 foi removida indevidamente (conteúdo genuíno de orçamento)
  - As gravações estão agrupadas num blob único sem distinção por aula
  - Módulo crítico merece organização por aula, não por gravação

O que este script faz:
  1. Reavalia gravação 13 — reincorpora se for conteúdo de orçamento
  2. Mapeia cada gravação do módulo 4 à aula específica que ela cobre
     (aula 24, 25, 26 ou 27)
  3. Gera 04_orcamento-planejamento-controle.md reorganizado por aula,
     com o transcript de cada gravação sob a aula correspondente

Uso:
    python reestruturar_orcamento.py
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
OUT_FILE    = TEMAS_DIR / "04_orcamento-planejamento-controle.md"

MODEL      = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Aulas do módulo 4 com suas descrições (hard-coded para precisão máxima)
AULAS_MOD4 = {
    24: {
        "titulo": "Orçamento: Estimativa Inicial ao Executivo",
        "desc": "Processo de orçamentação desde estimativa inicial sem projeto até orçamento executivo detalhado. Planilhas de estimativa de custos, composições de serviços, bases de dados (SINAPI), diário de obra."
    },
    25: {
        "titulo": "Estudo de Caso - Orçamento, Planejamento e Controle",
        "desc": "Aplicação prática em obra real (Casa do Lago ou similar). Planilha de custos executada, diário de obra, acompanhamento diário do que acontece na obra, controle financeiro real."
    },
    26: {
        "titulo": "Estudo de Caso - Orçamento, Planejamento e Controle 2",
        "desc": "Continuação do estudo de caso. EVF (Estudo de Viabilidade Financeira), comparação de custos entre sistemas construtivos, análise de custos imprevistos."
    },
    27: {
        "titulo": "Orçamentos Custos Indiretos, Compra de Fábrica, Quadro de Concorrência",
        "desc": "Custos indiretos da obra (não são material nem mão de obra). Como comprar diretamente de fábrica para tirar loja do meio. Quadro de concorrência para comparar fornecedores. Curva ABC aplicada a serviços."
    },
}


# ── Utilitários ───────────────────────────────────────────────────────────────
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
            gravacoes[n] = {
                'numero': n,
                'header': header,
                'texto_limpo': limpar_bloco(corpo),
            }
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
                'titulo':   aula_titulo,
                'modulo':   modulo_atual,
                'descricao': '\n'.join(desc_buf).strip(),
            }

    for linha in linhas:
        m_mod  = re.match(r'^## (.+)', linha)
        m_aula = re.match(r'^### (\d+)\.\s+(.+)', linha)
        if m_mod:
            flush(); modulo_atual = m_mod.group(1).strip(); aula_num = None; desc_buf = []
        elif m_aula:
            flush(); aula_num = int(m_aula.group(1)); aula_titulo = m_aula.group(2).strip(); desc_buf = []
        else:
            if aula_num is not None and linha.strip():
                desc_buf.append(linha.strip())

    flush()
    return resultado


# ── Claude: reavaliar gravação 13 ────────────────────────────────────────────
def reavaliar_gravacao_13(texto: str) -> bool:
    """
    Verifica em múltiplas posições se a gravação 13
    contém conteúdo genuíno de orçamento/controle de obra.
    Retorna True se deve ser reincorporada ao módulo 4.
    """
    total = len(texto)
    posicoes = [0, total // 4, total // 2, 3 * total // 4]
    votos_sim = 0

    descricao_modulo = "\n".join(
        f"Aula {num}: {info['titulo']} — {info['desc']}"
        for num, info in AULAS_MOD4.items()
    )

    for i, inicio in enumerate(posicoes):
        amostra = texto[inicio: inicio + 2500]
        pos_label = ['início', '25%', '50%', '75%'][i]

        prompt = f"""Este trecho de uma gravação contém conteúdo substantivo sobre algum destes tópicos de orçamento e controle de obra?

{descricao_modulo}

Trecho ({pos_label}):
{amostra}

Responda SOMENTE com JSON:
{{"contem_orcamento": true_ou_false, "raciocinio": "uma frase curta"}}

"Contem" = o trecho ENSINA ou EXEMPLIFICA algum desses tópicos de forma substantiva, não apenas menciona."""

        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )
            dados_str = resp.content[0].text.strip()
            dados_str = re.sub(r'^```json\s*|```$', '', dados_str, flags=re.MULTILINE).strip()
            dados = json.loads(dados_str)
            sim = dados.get('contem_orcamento', False)
            razao = dados.get('raciocinio', '')
            print(f"      [{pos_label}]: {'✓ SIM' if sim else '— não'} — {razao}")
            if sim:
                votos_sim += 1
        except Exception as e:
            print(f"      [{pos_label}]: AVISO — {e}")

        time.sleep(0.2)

    # Maioria simples: >= 2 de 4 posições com conteúdo de orçamento
    return votos_sim >= 2


# ── Claude: mapear gravação → aula específica ────────────────────────────────
def mapear_gravacao_para_aula(num: int, texto: str) -> dict:
    """
    Identifica qual(is) aula(s) do módulo 4 (24–27) a gravação cobre,
    com amostragem em 3 posições.
    Retorna dict: {aula_num: peso (0-3)}
    """
    total = len(texto)
    posicoes = [0, total // 2, max(0, total - 2500)]
    pos_labels = ['início', 'meio', 'final']

    descricao_aulas = "\n".join(
        f"Aula {num}: {info['titulo']} — {info['desc']}"
        for num, info in AULAS_MOD4.items()
    )

    votos: dict[int, int] = {24: 0, 25: 0, 26: 0, 27: 0}

    for i, inicio in enumerate(posicoes):
        amostra = texto[inicio: inicio + 2500]
        pos = pos_labels[i]

        prompt = f"""Esta amostra de gravação cobre qual(is) das aulas abaixo?

{descricao_aulas}

Amostra (Gravação {num}, {pos}):
{amostra}

Responda SOMENTE com JSON:
{{"aulas_cobertas": [lista de números de aula de 24 a 27], "raciocinio": "uma frase"}}

Inclua uma aula somente se a amostra ENSINA ou EXEMPLIFICA esse tema de forma substantiva."""

        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )
            dados_str = resp.content[0].text.strip()
            dados_str = re.sub(r'^```json\s*|```$', '', dados_str, flags=re.MULTILINE).strip()
            dados = json.loads(dados_str)
            aulas = dados.get('aulas_cobertas', [])
            razao = dados.get('raciocinio', '')
            print(f"      [{pos}] aulas={aulas} — {razao}")
            for a in aulas:
                if a in votos:
                    votos[a] += 1
        except Exception as e:
            print(f"      [{pos}] AVISO: {e}")

        time.sleep(0.2)

    # Retorna aulas com pelo menos 1 voto
    return {a: v for a, v in votos.items() if v > 0}


# ── Geração do arquivo reorganizado ──────────────────────────────────────────
def gerar_md_orcamento(
    aula_para_gravacoes: dict[int, list[dict]],
    descricoes: dict,
) -> str:
    """
    Gera o arquivo do módulo 4 organizado por aula,
    com o transcript de cada gravação sob a aula correspondente.
    """
    linhas = [
        "# Orçamento, Planejamento e Controle",
        "",
        "> Módulo 4 de 12 · 4 aulas",
        "> Fonte: Curso Casa de Baixo Custo Sustentável — Amanda & Fernando",
        "",
        "---",
        "",
        "## Visão Geral",
        "",
        "O módulo de orçamento é o núcleo estratégico de qualquer construção de baixo custo. "
        "Aqui você aprende a estimar custos desde o rascunho inicial até o orçamento executivo detalhado, "
        "acompanhar uma obra real com diário e controle financeiro, comparar sistemas construtivos por custo real, "
        "e montar quadros de concorrência para comprar materiais direto de fábrica. "
        "É o módulo que separa quem constrói gastando o que tinha planejado de quem descobre no meio da obra que o dinheiro acabou.",
        "",
        "---",
        "",
    ]

    for aula_num in sorted(AULAS_MOD4.keys()):
        info = AULAS_MOD4[aula_num]
        gravs = aula_para_gravacoes.get(aula_num, [])

        linhas.append(f"## Aula {aula_num}: {info['titulo']}")
        linhas.append("")

        # Descrição da aula (do scraper, se disponível)
        if aula_num in descricoes and descricoes[aula_num]['descricao']:
            linhas.append(descricoes[aula_num]['descricao'])
        else:
            linhas.append(info['desc'])
        linhas.append("")

        if gravs:
            linhas.append("### Transcrição")
            linhas.append("")
            for g in sorted(gravs, key=lambda x: x['numero']):
                linhas.append(f"#### Gravação {g['numero']}")
                linhas.append("")
                linhas.append(g['texto_limpo'].strip())
                linhas.append("")
        else:
            linhas.append("*Nenhuma gravação mapeada para esta aula.*")
            linhas.append("")

        linhas.append("---")
        linhas.append("")

    return '\n'.join(linhas)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Carregando dados...")
    raw        = RAW_FILE.read_text(encoding='utf-8', errors='replace')
    descricoes = parse_descricoes(DESC_FILE)
    mapeamento = json.loads(MAP_FILE.read_text(encoding='utf-8'))
    gravacoes  = extrair_gravacoes(raw)

    por_gravacao = mapeamento['por_gravacao']

    # Gravações atualmente no módulo 4 (aulas 24-27)
    gravs_mod4_atuais = [
        int(n) for n, info in por_gravacao.items()
        if any(24 <= a <= 27 for a in info['aulas'])
    ]
    print(f"Gravações atuais no módulo 4: {sorted(gravs_mod4_atuais)}")

    # ── 1. REAVALIAR GRAVAÇÃO 13 ──────────────────────────────────────────────
    print("\n── Reavaliando gravação 13 ──────────────────────────────────")
    g13_texto = gravacoes[13]['texto_limpo']
    deve_incluir_13 = reavaliar_gravacao_13(g13_texto)

    if deve_incluir_13:
        print("  → Reincorporando gravação 13 ao módulo 4")
        if 13 not in gravs_mod4_atuais:
            gravs_mod4_atuais.append(13)
        # Atualiza mapeamento
        aulas_13 = por_gravacao['13']['aulas']
        for a in [24, 25, 26, 27]:
            if a not in aulas_13:
                aulas_13.append(a)
        aulas_13.sort()
        por_gravacao['13']['aulas'] = aulas_13
        por_gravacao['13']['raciocinio'] += " | Revisado: reincorporado ao módulo 4"
    else:
        print("  → Gravação 13 confirmada fora do módulo 4")

    gravs_mod4_atuais = sorted(set(gravs_mod4_atuais))
    print(f"Gravações finais para o módulo 4: {gravs_mod4_atuais}")

    # ── 2. MAPEAR CADA GRAVAÇÃO → AULA ESPECÍFICA ────────────────────────────
    print("\n── Mapeando gravações para aulas específicas ────────────────")
    gravacao_para_aulas_especificas: dict[int, dict[int, int]] = {}

    for num in gravs_mod4_atuais:
        if num not in gravacoes:
            print(f"  Gravação {num}: não encontrada no raw — pulando")
            continue
        print(f"  Gravação {num}:")
        votos = mapear_gravacao_para_aula(num, gravacoes[num]['texto_limpo'])
        gravacao_para_aulas_especificas[num] = votos
        print(f"    → votos finais: {votos}")
        time.sleep(0.3)

    # Inverte: aula → gravações
    aula_para_gravacoes: dict[int, list[dict]] = {24: [], 25: [], 26: [], 27: []}
    vistos_por_aula: dict[int, set] = {24: set(), 25: set(), 26: set(), 27: set()}

    for num_grav, votos in gravacao_para_aulas_especificas.items():
        for aula_num, peso in votos.items():
            if peso > 0 and num_grav not in vistos_por_aula[aula_num]:
                vistos_por_aula[aula_num].add(num_grav)
                aula_para_gravacoes[aula_num].append(gravacoes[num_grav])

    # Diagnóstico
    print("\n  Resultado do mapeamento:")
    for aula_num in sorted(AULAS_MOD4.keys()):
        gravs = [g['numero'] for g in aula_para_gravacoes[aula_num]]
        status = "✓" if gravs else "⚠ sem gravação"
        print(f"    Aula {aula_num} ({AULAS_MOD4[aula_num]['titulo'][:40]}): gravações={gravs} {status}")

    # Fallback: aulas sem gravação recebem todas as gravações do módulo (conteúdo sobreposto é esperado)
    for aula_num in sorted(AULAS_MOD4.keys()):
        if not aula_para_gravacoes[aula_num]:
            print(f"  Aula {aula_num} sem mapeamento — usando todas as gravações do módulo como fallback")
            for num_grav in gravs_mod4_atuais:
                if num_grav in gravacoes:
                    aula_para_gravacoes[aula_num].append(gravacoes[num_grav])

    # ── 3. GERA ARQUIVO REORGANIZADO ─────────────────────────────────────────
    print("\n── Gerando 04_orcamento-planejamento-controle.md ────────────")
    TEMAS_DIR.mkdir(parents=True, exist_ok=True)
    conteudo = gerar_md_orcamento(aula_para_gravacoes, descricoes)
    OUT_FILE.write_text(conteudo, encoding='utf-8')
    size_kb = OUT_FILE.stat().st_size / 1024
    print(f"  → {OUT_FILE.name} ({size_kb:.0f} KB)")

    # ── 4. ATUALIZA mapeamento.json ───────────────────────────────────────────
    # Atualiza entry do módulo 4
    for entry in mapeamento['arquivos_gerados']:
        if entry['modulo_id'] == 4:
            entry['gravacoes'] = gravs_mod4_atuais
            entry['size_kb']   = round(size_kb, 1)

    mapeamento['por_gravacao'] = por_gravacao
    MAP_FILE.write_text(json.dumps(mapeamento, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n" + "=" * 55)
    print("CONCLUÍDO")
    print(f"  Gravações no módulo 4: {gravs_mod4_atuais}")
    print(f"  Arquivo: {OUT_FILE.name} ({size_kb:.0f} KB)")
    print(f"  Estrutura: organizado por aula (24→27) com transcripts sob cada aula")
    print(f"  mapeamento.json: atualizado")


if __name__ == "__main__":
    main()
