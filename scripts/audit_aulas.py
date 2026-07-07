"""
audit_aulas.py — Inventário e auditoria local das 89 aulas geradas.

Não chama API, não custa nada. Lê os .md em build/aulas/ e produz um
relatório estruturado em build/audit_report.md com:

  - Distribuição de marcadores de callout (atencao/dica/exemplo/etc)
  - Marcadores FORA DO CONJUNTO VÁLIDO (que vão ser normalizados)
  - Inventário de elementos estruturais: tabelas, code blocks, blockquotes
    longos, listas longas, ASCII art / pseudo-diagramas
  - Histograma de tamanho de aula
  - Lista de aulas potencialmente curtas ou suspeitas

O relatório é a base pra Fase 5 (prompt Perplexity buscando refs visuais
2026 pra cada tipo de elemento encontrado).

USO:
  python scripts/audit_aulas.py                # gera relatório
  python scripts/audit_aulas.py --normalizar   # também aplica fix nos
                                                # marcadores fora do padrão
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
# Fonte de verdade curada das aulas (D016): knowledge/aulas/ versionado.
AULAS_DIR = REPO_ROOT / "knowledge" / "aulas"
REPORT_FILE = REPO_ROOT / "build" / "audit_report.md"
INVENTARIO_JSON = REPO_ROOT / "build" / "audit_inventario.json"

# Marcadores válidos (definidos no system prompt da extração)
CALLOUTS_VALIDOS = {"atencao", "exemplo", "dica"}

# Padrões pra normalização — chave: marcador "errado" detectado (lowercase),
# valor: marcador válido alvo. A detecção compara em lowercase, então variantes
# de capitalização (Atenção, ATENÇÃO) também batem.
NORMALIZAR_CALLOUTS = {
    # Variantes acentuadas e em outras línguas/grafias do "atencao"
    "atenção": "atencao",
    "atencão": "atencao",
    "atenção:": "atencao",
    "importante": "atencao",
    "importante!": "atencao",
    "aviso": "atencao",
    "alerta": "atencao",
    "warning": "atencao",
    "cuidado": "atencao",
    # Variantes do "dica"
    "info": "dica",
    "informação": "dica",
    "tip": "dica",
    "note": "dica",
    "nota": "dica",
    "observação": "dica",
    # Variantes do "exemplo"
    "exemplo prático": "exemplo",
    "exemplo prático:": "exemplo",
    "case": "exemplo",
    "caso": "exemplo",
}


@dataclass
class AulaInventario:
    arquivo: str
    aula_id: int
    modulo_id: int
    titulo: str
    status: str  # ok | ausente | erro
    chars_conteudo: int = 0  # sem o header HTML
    palavras: int = 0
    callouts_validos: Counter = field(default_factory=Counter)
    callouts_invalidos: list[tuple[str, str]] = field(default_factory=list)  # (marcador_encontrado, contexto)
    tabelas: int = 0
    code_blocks: int = 0
    blockquotes: int = 0
    listas_simples: int = 0
    listas_numeradas: int = 0
    ascii_art: int = 0  # code blocks que parecem diagrama ASCII
    headings_h2: int = 0
    headings_h3: int = 0
    headings_h4: int = 0
    subsecoes_inline: int = 0  # **Texto:** no início de parágrafo
    suspeitas: list[str] = field(default_factory=list)


def parse_header(texto: str) -> dict:
    """Extrai metadados do header HTML comment no topo do .md."""
    m = re.search(r'<!--\s*(.*?)\s*-->', texto, re.DOTALL)
    if not m:
        return {}
    meta = {}
    for linha in m.group(1).strip().split("\n"):
        if ": " in linha:
            k, v = linha.split(": ", 1)
            meta[k.strip()] = v.strip()
    return meta, m.end()


def detectar_callouts(conteudo: str) -> tuple[Counter, list[tuple[str, str]]]:
    """
    Detecta callouts no formato:
        > [!marcador] Título opcional
        > Texto da callout

    Retorna (válidos, inválidos).
    """
    validos = Counter()
    invalidos: list[tuple[str, str]] = []

    pattern = re.compile(r'^>\s*\[!([^\]]+)\]', re.MULTILINE)
    for m in pattern.finditer(conteudo):
        marcador_raw = m.group(1).strip().lower()
        # Pega o contexto (até 80 chars depois)
        contexto = conteudo[m.end():m.end() + 80].split("\n")[0].strip()

        if marcador_raw in CALLOUTS_VALIDOS:
            validos[marcador_raw] += 1
        else:
            invalidos.append((marcador_raw, contexto))

    return validos, invalidos


def detectar_estruturas(conteudo: str) -> dict:
    """Conta tabelas, code blocks, blockquotes, listas, headings."""
    out = {}

    # Tabelas Markdown: 3+ linhas começando com | e linha de separação ---|---
    tabelas = 0
    linhas = conteudo.split("\n")
    i = 0
    while i < len(linhas) - 2:
        if (linhas[i].strip().startswith("|")
                and re.match(r'^\|[\s\-:|]+\|\s*$', linhas[i + 1].strip())
                and linhas[i + 2].strip().startswith("|")):
            tabelas += 1
            # avança até sair da tabela
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                i += 1
        else:
            i += 1
    out["tabelas"] = tabelas

    # Code blocks (fenced ``` ou indented)
    code_blocks = len(re.findall(r'^```', conteudo, re.MULTILINE)) // 2
    out["code_blocks"] = code_blocks

    # ASCII art: code block que contém setas Unicode ou caracteres de desenho
    ascii_art = 0
    for m in re.finditer(r'```(\w*)\n(.*?)```', conteudo, re.DOTALL):
        bloco = m.group(2)
        # Heurística: tem setas, conectores, ou muitos espaços formatando colunas
        if (re.search(r'[→←↑↓│┌┐└┘├┤┬┴┼─━║╔╗╚╝]', bloco)
                or bloco.count("  ") > 5):
            ascii_art += 1
    out["ascii_art"] = ascii_art

    # Blockquotes (excluindo callouts já contados)
    # Blockquote = linha começando com > que NÃO é [!callout]
    blockquotes = 0
    em_bq = False
    for linha in linhas:
        if linha.strip().startswith(">") and not re.match(r'^>\s*\[!', linha.strip()):
            if not em_bq:
                blockquotes += 1
                em_bq = True
        else:
            em_bq = False
    out["blockquotes"] = blockquotes

    # Listas (linhas começando com - ou *)
    out["listas_simples"] = len([l for l in linhas if re.match(r'^[\-\*]\s+', l)])
    out["listas_numeradas"] = len([l for l in linhas if re.match(r'^\d+\.\s+', l)])

    # Headings
    out["headings_h2"] = len(re.findall(r'^##\s+', conteudo, re.MULTILINE))
    out["headings_h3"] = len(re.findall(r'^###\s+', conteudo, re.MULTILINE))
    out["headings_h4"] = len(re.findall(r'^####\s+', conteudo, re.MULTILINE))

    # Subseções inline: **Texto:** no início de parágrafo
    out["subsecoes_inline"] = len(re.findall(
        r'^\*\*[^*]+:\*\*', conteudo, re.MULTILINE
    ))

    return out


def detectar_suspeitas(inv: AulaInventario) -> list[str]:
    """Sinalizadores que merecem atenção humana."""
    s = []
    if inv.chars_conteudo < 500:
        s.append(f"Conteúdo muito curto ({inv.chars_conteudo} chars)")
    if inv.chars_conteudo > 12000:
        s.append(f"Conteúdo muito longo ({inv.chars_conteudo} chars)")
    if inv.headings_h2 == 0 and inv.chars_conteudo > 1500:
        s.append("Sem seções (H2) apesar de conteúdo longo")
    if inv.callouts_invalidos:
        s.append(f"{len(inv.callouts_invalidos)} callouts com marcadores fora do padrão")
    if inv.ascii_art > 0:
        s.append(f"{inv.ascii_art} possível(is) ASCII art / diagrama em texto")
    return s


def auditar_arquivo(path: Path) -> AulaInventario:
    raw = path.read_text(encoding="utf-8")
    parsed = parse_header(raw)
    if isinstance(parsed, tuple):
        meta, header_end = parsed
        conteudo = raw[header_end:].strip()
    else:
        meta = parsed
        conteudo = raw

    # Extrai metadados
    aula_id = int(meta.get("aula_id", 0))
    modulo_id = int(meta.get("modulo_id", 0))
    titulo = meta.get("titulo", "?")
    status = meta.get("status", "?")

    # Classificação de ausência: header `status: ausente` OU corpo contendo o
    # marcador `AULA_AUSENTE`. A detecção de corpo é a rede de segurança contra
    # regressão do extract (que já classificou errado por olhar só o header —
    # ver D017): se uma futura re-extração devolver `# AULA_AUSENTE` com header
    # status: ok, o audit ainda pega.
    if status == "ok" and re.search(r"\bAULA_AUSENTE\b", conteudo):
        status = "ausente"

    inv = AulaInventario(
        arquivo=path.name,
        aula_id=aula_id,
        modulo_id=modulo_id,
        titulo=titulo,
        status=status,
        chars_conteudo=len(conteudo),
        palavras=len(conteudo.split()),
    )

    if status != "ok":
        # Aulas ausentes/erro não têm conteúdo significativo pra auditar
        inv.suspeitas.append(f"Status: {status}")
        return inv

    # Callouts
    validos, invalidos = detectar_callouts(conteudo)
    inv.callouts_validos = validos
    inv.callouts_invalidos = invalidos

    # Outras estruturas
    estruturas = detectar_estruturas(conteudo)
    inv.tabelas = estruturas["tabelas"]
    inv.code_blocks = estruturas["code_blocks"]
    inv.blockquotes = estruturas["blockquotes"]
    inv.listas_simples = estruturas["listas_simples"]
    inv.listas_numeradas = estruturas["listas_numeradas"]
    inv.ascii_art = estruturas["ascii_art"]
    inv.headings_h2 = estruturas["headings_h2"]
    inv.headings_h3 = estruturas["headings_h3"]
    inv.headings_h4 = estruturas["headings_h4"]
    inv.subsecoes_inline = estruturas["subsecoes_inline"]

    inv.suspeitas = detectar_suspeitas(inv)
    return inv


def normalizar_arquivo(path: Path, mapa: dict) -> int:
    """
    Reescreve callouts fora do padrão pelo equivalente válido.
    Devolve número de substituições.
    """
    raw = path.read_text(encoding="utf-8")
    total = 0

    def repl(m: re.Match) -> str:
        nonlocal total
        marcador = m.group(1).strip().lower()
        if marcador in mapa:
            total += 1
            return f"> [!{mapa[marcador]}]"
        return m.group(0)

    novo = re.sub(r'>\s*\[!([^\]]+)\]', repl, raw)
    if total > 0:
        path.write_text(novo, encoding="utf-8")
    return total


def gerar_relatorio(inventarios: list[AulaInventario]) -> str:
    """Monta o relatório em Markdown."""
    lines = []
    lines.append("# Auditoria das 89 aulas\n")
    lines.append(f"Total de arquivos auditados: **{len(inventarios)}**\n")

    # Status overview
    por_status = Counter(i.status for i in inventarios)
    lines.append("## Status\n")
    for status, n in por_status.most_common():
        lines.append(f"- **{status}**: {n}")
    lines.append("")

    # Apenas OK pra estatísticas estruturais
    oks = [i for i in inventarios if i.status == "ok"]

    # Tamanho
    if oks:
        chars = sorted(i.chars_conteudo for i in oks)
        lines.append("## Tamanho do conteúdo (apenas aulas OK)\n")
        lines.append(f"- Menor: {chars[0]:,} chars ({chars[0] // 5} palavras aprox.)")
        lines.append(f"- Maior: {chars[-1]:,} chars ({chars[-1] // 5} palavras aprox.)")
        lines.append(f"- Mediana: {chars[len(chars) // 2]:,} chars")
        media = sum(chars) // len(chars)
        lines.append(f"- Média: {media:,} chars")
        lines.append("")

    # Callouts válidos
    total_callouts = Counter()
    for i in oks:
        total_callouts.update(i.callouts_validos)
    lines.append("## Callouts válidos no acervo\n")
    if total_callouts:
        for marcador, n in total_callouts.most_common():
            lines.append(f"- `> [!{marcador}]`: **{n}** ocorrências")
    else:
        lines.append("Nenhum callout válido encontrado.")
    lines.append("")

    # Callouts inválidos (detalhado)
    todos_invalidos = Counter()
    detalhes_invalidos: list[tuple[str, str, str, str]] = []  # (marcador, arquivo, titulo, contexto)
    for i in oks:
        for marcador, ctx in i.callouts_invalidos:
            todos_invalidos[marcador] += 1
            detalhes_invalidos.append((marcador, i.arquivo, i.titulo, ctx))

    lines.append("## Callouts com marcadores FORA do padrão\n")
    lines.append("Marcadores válidos do projeto: `atencao`, `exemplo`, `dica`.")
    lines.append("Marcadores diferentes desses serão normalizados.\n")
    if todos_invalidos:
        lines.append("### Distribuição\n")
        for marcador, n in todos_invalidos.most_common():
            alvo = NORMALIZAR_CALLOUTS.get(marcador, "❓ SEM REGRA DE NORMALIZAÇÃO")
            lines.append(f"- `> [!{marcador}]`: **{n}** ocorrências → normalizar para `{alvo}`")
        lines.append("")

        lines.append("### Ocorrências detalhadas\n")
        for marcador, arquivo, titulo, ctx in detalhes_invalidos:
            lines.append(f"- **{arquivo}** ({titulo}) — `[!{marcador}]`: _{ctx[:70]}_")
        lines.append("")
    else:
        lines.append("Nenhum marcador fora do padrão encontrado. ✅\n")

    # Estruturas
    lines.append("## Inventário de elementos estruturais (apenas aulas OK)\n")
    if oks:
        total_tabelas = sum(i.tabelas for i in oks)
        total_code = sum(i.code_blocks for i in oks)
        total_ascii = sum(i.ascii_art for i in oks)
        total_bq = sum(i.blockquotes for i in oks)
        total_ls = sum(i.listas_simples for i in oks)
        total_ln = sum(i.listas_numeradas for i in oks)
        total_si = sum(i.subsecoes_inline for i in oks)
        total_h2 = sum(i.headings_h2 for i in oks)
        total_h3 = sum(i.headings_h3 for i in oks)
        total_h4 = sum(i.headings_h4 for i in oks)
        lines.append(f"- **Tabelas Markdown**: {total_tabelas}")
        lines.append(f"- **Code blocks** (totais): {total_code}")
        lines.append(f"  - dos quais parecem **ASCII art / diagrama**: {total_ascii}")
        lines.append(f"- **Blockquotes** (não-callout): {total_bq}")
        lines.append(f"- **Listas simples** (linhas): {total_ls}")
        lines.append(f"- **Listas numeradas** (linhas): {total_ln}")
        lines.append(f"- **Subseções inline** (`**Texto:**`): {total_si}")
        lines.append(f"- **Headings H2**: {total_h2}")
        lines.append(f"- **Headings H3**: {total_h3}")
        lines.append(f"- **Headings H4**: {total_h4}")
        lines.append("")

    # Tabelas — listar onde estão
    lines.append("## Localização das tabelas\n")
    com_tabelas = [(i.arquivo, i.titulo, i.tabelas) for i in oks if i.tabelas > 0]
    if com_tabelas:
        for arq, tit, n in sorted(com_tabelas, key=lambda x: -x[2]):
            lines.append(f"- **{arq}** ({tit}): {n} tabela(s)")
    else:
        lines.append("Nenhuma tabela encontrada.")
    lines.append("")

    # ASCII art — onde aparecem (alvo de conversão em componente)
    lines.append("## Localização de ASCII art / pseudo-diagramas\n")
    lines.append("Esses code blocks devem virar componentes visuais responsivos na Fase 5.\n")
    com_ascii = [(i.arquivo, i.titulo, i.ascii_art) for i in oks if i.ascii_art > 0]
    if com_ascii:
        for arq, tit, n in com_ascii:
            lines.append(f"- **{arq}** ({tit}): {n} bloco(s)")
    else:
        lines.append("Nenhum bloco ASCII encontrado.")
    lines.append("")

    # Aulas suspeitas
    suspeitas = [i for i in inventarios if i.suspeitas]
    lines.append("## Aulas com sinalizadores\n")
    if suspeitas:
        for i in sorted(suspeitas, key=lambda x: x.aula_id):
            lines.append(f"### A{i.aula_id} — {i.titulo} (`{i.arquivo}`)")
            for s in i.suspeitas:
                lines.append(f"- {s}")
            lines.append("")
    else:
        lines.append("Nenhuma aula suspeita. ✅\n")

    # Por módulo — visão sumária
    lines.append("## Visão por módulo\n")
    lines.append("| Módulo | Aulas | OK | Ausente | Erro | Avg chars | Callouts | Tabelas |")
    lines.append("|--------|-------|----|---------|------|-----------|----------|---------|")
    por_modulo: dict[int, list[AulaInventario]] = defaultdict(list)
    for i in inventarios:
        por_modulo[i.modulo_id].append(i)
    for mid in sorted(por_modulo.keys()):
        ms = por_modulo[mid]
        ms_ok = [m for m in ms if m.status == "ok"]
        avg = (sum(m.chars_conteudo for m in ms_ok) // len(ms_ok)) if ms_ok else 0
        n_calls = sum(sum(m.callouts_validos.values()) for m in ms_ok)
        n_tab = sum(m.tabelas for m in ms_ok)
        n_aus = sum(1 for m in ms if m.status == "ausente")
        n_err = sum(1 for m in ms if m.status == "erro")
        lines.append(
            f"| M{mid} | {len(ms)} | {len(ms_ok)} | {n_aus} | {n_err} | "
            f"{avg:,} | {n_calls} | {n_tab} |"
        )
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--normalizar", action="store_true",
                   help="Após auditar, aplica fix nos marcadores fora do padrão "
                        "diretamente nos arquivos.")
    args = p.parse_args()

    if not AULAS_DIR.exists():
        print(f"ERRO: {AULAS_DIR} não existe.", file=sys.stderr)
        return 1

    arquivos = sorted(AULAS_DIR.glob("*.md"))
    if not arquivos:
        print(f"ERRO: nenhum .md em {AULAS_DIR}.", file=sys.stderr)
        return 1

    print(f"Auditando {len(arquivos)} arquivos em {AULAS_DIR}...\n")
    inventarios = [auditar_arquivo(p) for p in arquivos]

    # Salva inventário JSON
    import json
    INVENTARIO_JSON.write_text(
        json.dumps([{
            "arquivo": i.arquivo,
            "aula_id": i.aula_id,
            "modulo_id": i.modulo_id,
            "titulo": i.titulo,
            "status": i.status,
            "chars_conteudo": i.chars_conteudo,
            "palavras": i.palavras,
            "callouts_validos": dict(i.callouts_validos),
            "callouts_invalidos": i.callouts_invalidos,
            "tabelas": i.tabelas,
            "code_blocks": i.code_blocks,
            "ascii_art": i.ascii_art,
            "blockquotes": i.blockquotes,
            "listas_simples": i.listas_simples,
            "listas_numeradas": i.listas_numeradas,
            "headings_h2": i.headings_h2,
            "headings_h3": i.headings_h3,
            "headings_h4": i.headings_h4,
            "subsecoes_inline": i.subsecoes_inline,
            "suspeitas": i.suspeitas,
        } for i in inventarios], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Gera relatório
    rel = gerar_relatorio(inventarios)
    REPORT_FILE.write_text(rel, encoding="utf-8")
    print(f"✓ Relatório: {REPORT_FILE}")
    print(f"✓ Inventário JSON: {INVENTARIO_JSON}")

    # Normalização opcional
    if args.normalizar:
        print("\n--normalizar ativado: aplicando substituições nos arquivos...\n")
        total = 0
        for path in arquivos:
            n = normalizar_arquivo(path, NORMALIZAR_CALLOUTS)
            if n > 0:
                print(f"  {path.name}: {n} substituição(ões)")
                total += n
        print(f"\nTotal: {total} substituições aplicadas.")
        if total > 0:
            print("Re-rode `python scripts/audit_aulas.py` (sem --normalizar) pra confirmar.")

    # Sumário rápido pro console
    print()
    n_ok = sum(1 for i in inventarios if i.status == "ok")
    n_aus = sum(1 for i in inventarios if i.status == "ausente")
    n_err = sum(1 for i in inventarios if i.status == "erro")
    print(f"  OK: {n_ok} | AUSENTE: {n_aus} | ERRO: {n_err}")

    n_invalidos = sum(len(i.callouts_invalidos) for i in inventarios if i.status == "ok")
    if n_invalidos > 0:
        print(f"  ⚠️  {n_invalidos} callouts fora do padrão (rode --normalizar pra corrigir)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
