#!/usr/bin/env python3
"""
consolidar_temas.py

Consolida as 88 aulas extraídas em `knowledge/aulas/{MM}_{AAA}.md`
em 12 arquivos `site/content/temas/{slug}.md`, um por módulo, preservando
título e Visão Geral já existentes em cada tema.

Para cada arquivo de aula:
  - Remove o header HTML de metadados (<!-- ... -->).
  - Converte o `# Título` em `### N. Título` (heading nível 3).
  - Concatena na seção "## Aulas" do tema correspondente.

A seção `## Transcrição` é mantida vazia (transcrições serão geradas
em uma rodada separada com flag `--transcricoes` no extract_aulas.py).

Casos especiais:
  - Módulo 4: a Aula 25 não foi extraída. Inserida como placeholder
    apontando para a Aula 26.

Uso:
    python scripts/consolidar_temas.py
"""

from __future__ import annotations

import re
from pathlib import Path

# Diretórios base (relativos à raiz do repo).
REPO_ROOT = Path(__file__).resolve().parent.parent
# Fonte de verdade curada das aulas (D016): knowledge/aulas/ versionado.
AULAS_DIR = REPO_ROOT / "knowledge" / "aulas"
TEMAS_DIR = REPO_ROOT / "site" / "content" / "temas"

# Slugs canônicos (já estabelecidos em site/content/temas/).
SLUGS: dict[int, str] = {
    1: "01_introducao",
    2: "02_projeto",
    3: "03_terreno",
    4: "04_orcamento-planejamento-controle",
    5: "05_servicos-preliminares",
    6: "06_fundacoes",
    7: "07_estruturas-vedacoes",
    8: "08_lajes",
    9: "09_coberturas",
    10: "10_acabamentos",
    11: "11_aberturas-esquadrias",
    12: "12_instalacoes-residenciais",
}

# Quando a aula tem status: ausente, substituímos o corpo por um callout
# que aponta para a aula vizinha (apresentada conjuntamente).
SUBSTITUICOES_AUSENTES: dict[int, str] = {
    25: (
        "> [!atencao]\n"
        "> Este estudo de caso é tratado em conjunto com o seguinte. "
        "Vá direto para a [Aula 26](#26-estudo-de-caso---orcamento-planejamento-e-controle-2)."
    ),
}


HEADER_HTML_RE = re.compile(r"^<!--[\s\S]*?-->\s*\n", re.MULTILINE)
TITULO_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
STATUS_AUSENTE_RE = re.compile(r"^\s*status:\s*ausente\s*$", re.MULTILINE)
TITULO_HEADER_RE = re.compile(r"^\s*titulo:\s*(.+)$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{1,5})\s+", re.MULTILINE)


def rebaixar_headings(corpo: str, niveis: int = 2) -> str:
    """
    Acrescenta `niveis` # a cada heading do corpo. Usado para manter a
    hierarquia quando o corpo da aula (originalmente com `##`) é
    embutido como filho de um `###`.
    """

    def repl(m: re.Match[str]) -> str:
        atual = m.group(1)
        novo = "#" * min(len(atual) + niveis, 6)
        return f"{novo} "

    return HEADING_RE.sub(repl, corpo)


def normalizar(raw: str) -> str:
    """Normaliza line-endings e remove BOM."""
    return raw.replace("﻿", "").replace("\r\n", "\n").replace("\r", "\n")


def ler_tema_existente(slug: str) -> tuple[str, str]:
    """
    Lê tema existente e devolve (titulo, visao_geral).
    Se não existir, devolve ("", "").
    """
    arquivo = TEMAS_DIR / f"{slug}.md"
    if not arquivo.exists():
        return "", ""
    raw = normalizar(arquivo.read_text(encoding="utf-8"))

    titulo_match = TITULO_H1_RE.search(raw)
    titulo = titulo_match.group(1).strip() if titulo_match else ""

    visao = ""
    re_visao = re.compile(
        r"^##\s+Visão Geral\s*\n([\s\S]*?)(?=^##\s+|(?![\s\S]))",
        re.MULTILINE,
    )
    m = re_visao.search(raw)
    if m:
        visao = m.group(1).strip().rstrip("-").strip()
    return titulo, visao


def parsear_aula(path: Path) -> tuple[int, int, str, str]:
    """
    Lê arquivo build/aulas/MM_AAA.md e devolve:
      (modulo, aula, titulo, conteudo_sem_h1_nem_header).
    """
    nome = path.stem  # ex: "02_006"
    parts = nome.split("_")
    if len(parts) != 2:
        raise ValueError(f"Nome inesperado: {nome}")
    modulo = int(parts[0])
    aula = int(parts[1])

    raw = normalizar(path.read_text(encoding="utf-8"))

    # Detecta status: ausente no header HTML.
    ausente = bool(STATUS_AUSENTE_RE.search(raw))
    titulo_header_match = TITULO_HEADER_RE.search(raw)
    titulo_header = (
        titulo_header_match.group(1).strip() if titulo_header_match else ""
    )

    # Remove o header HTML (apenas se for o primeiro bloco).
    raw_sem_header = HEADER_HTML_RE.sub("", raw, count=1).lstrip()

    # Captura o título (primeiro # no início) e separa o resto.
    titulo_match = TITULO_H1_RE.match(raw_sem_header)
    if titulo_match:
        titulo = titulo_match.group(1).strip()
        corpo = raw_sem_header[titulo_match.end() :].lstrip("\n")
    elif titulo_header:
        titulo = titulo_header
        corpo = raw_sem_header
    else:
        titulo = nome
        corpo = raw_sem_header

    if ausente and aula in SUBSTITUICOES_AUSENTES:
        corpo = SUBSTITUICOES_AUSENTES[aula]
    else:
        # Rebaixa headings: o `##` da aula vira `####`, ficando sob o `### N.`.
        corpo = rebaixar_headings(corpo, niveis=2)

    return modulo, aula, titulo, corpo


def montar_secao_aulas(aulas: list[tuple[int, str, str]]) -> str:
    """Monta a seção '## Aulas' a partir da lista [(numero, titulo, corpo)]."""
    linhas: list[str] = ["## Aulas", ""]
    for numero, titulo, corpo in aulas:
        linhas.append(f"### {numero}. {titulo}")
        linhas.append("")
        if corpo.strip():
            linhas.append(corpo.rstrip())
            linhas.append("")
    return "\n".join(linhas).rstrip() + "\n"


def montar_tema(
    slug: str,
    numero: int,
    titulo: str,
    visao_geral: str,
    aulas: list[tuple[int, str, str]],
) -> str:
    """Constrói o conteúdo final do arquivo de tema."""
    total = len(aulas)
    cab = (
        f"# {titulo}\n"
        f"\n"
        f"> Módulo {numero} de 12 · {total} aulas\n"
        f"> Fonte: Curso Casa de Baixo Custo Sustentável — Amanda & Fernando\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Visão Geral\n"
        f"\n"
        f"{visao_geral.strip() or '_(em redação)_'}\n"
        f"\n"
        f"---\n"
        f"\n"
    )
    secao_aulas = montar_secao_aulas(aulas)
    rodape = (
        f"\n"
        f"---\n"
        f"\n"
        f"## Transcrição\n"
    )
    return cab + secao_aulas + rodape


def main() -> None:
    if not AULAS_DIR.exists():
        raise SystemExit(f"Diretório não encontrado: {AULAS_DIR}")
    if not TEMAS_DIR.exists():
        raise SystemExit(f"Diretório não encontrado: {TEMAS_DIR}")

    # Agrupa todas as aulas por módulo.
    por_modulo: dict[int, list[tuple[int, str, str]]] = {n: [] for n in SLUGS}

    for arq in sorted(AULAS_DIR.glob("*.md")):
        modulo, aula, titulo, corpo = parsear_aula(arq)
        if modulo not in por_modulo:
            continue
        por_modulo[modulo].append((aula, titulo, corpo))

    # Ordena cada módulo por número da aula.
    for modulo in por_modulo:
        por_modulo[modulo].sort(key=lambda x: x[0])

    # Escreve um arquivo por módulo.
    for numero, slug in SLUGS.items():
        titulo, visao = ler_tema_existente(slug)
        if not titulo:
            print(f"[aviso] Tema {slug} sem título existente — usando slug.")
            titulo = slug
        aulas = por_modulo.get(numero, [])
        conteudo = montar_tema(slug, numero, titulo, visao, aulas)
        destino = TEMAS_DIR / f"{slug}.md"
        destino.write_text(conteudo, encoding="utf-8")
        print(f"[ok] {slug}.md — {len(aulas)} aulas")


if __name__ == "__main__":
    main()
