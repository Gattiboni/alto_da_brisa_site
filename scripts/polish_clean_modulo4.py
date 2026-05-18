"""
polish_clean_modulo4.py — Polimento determinístico do módulo 04.

Faz duas coisas no mesmo passe, sem chamar API:

1. NORMALIZA a estrutura para o padrão dos outros 11 módulos:
   - ## Visão Geral
   - ## Aulas (com ### N. Nome da aula contendo metadata)
   - ## Transcrição (com ### Gravação N agregadas no final)

2. LIMPA determinísticamente:
   - Espaços colados ("MétodosCusto" -> "Métodos Custo")
   - Vícios de fala inline (" né?", " tá?", "Peraí, ", "Olha, ", etc)
   - Linhas-confirmação isoladas
   - Parágrafos > 600 chars quebrados em pontuação forte
   - Artefatos de copy-paste

Antes de processar, roda uma bateria de TESTES INTERNOS contra regex
para garantir que palavras com acentos não vão ser deformadas.
Se algum teste falhar, o script aborta sem tocar no arquivo.

Saída:
   - knowledge/temas_v2/04_orcamento-planejamento-controle.md
   - knowledge/temas_v2/04_orcamento_polish_log.txt

USO:
   python scripts/polish_clean_modulo4.py
   python scripts/polish_clean_modulo4.py --dry-run    # só estatísticas
   python scripts/polish_clean_modulo4.py --test-only  # só roda os testes
"""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from collections import Counter


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "knowledge" / "temas" / "04_orcamento-planejamento-controle.md"
DEST = REPO_ROOT / "knowledge" / "temas_v2" / "04_orcamento-planejamento-controle.md"
LOG_PATH = REPO_ROOT / "knowledge" / "temas_v2" / "04_orcamento_polish_log.txt"

PARAGRAFO_MAX_CHARS = 600


# Classes de caracteres EXPLÍCITAS para português.
# Não usar [À-Ÿ] porque esse range Unicode inclui letras minúsculas.
LOWER_PT = r'a-záàâãäéèêëíìîïóòôõöúùûüçñ'
UPPER_PT = r'A-ZÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ'


# Linhas-confirmação a remover quando aparecem ISOLADAS em uma linha.
# Conservador: não inclui palavras-isoladas-que-podem-ser-conteúdo.
LINHAS_CONFIRMACAO_REMOVER = {
    "Exato.",
    "Exatamente.",
    "Sim.",
    "Pronto.",
    "Beleza.",
    "Tá.",
    "Né.",
    "Próximo.",
    "Próximo aí.",
    "Aí.",
    "Aí, ó.",
    "Olha aí.",
    "Pronto, beleza.",
    "Vamos lá.",
    "Exato, sim.",
    "Sim, sim.",
    "Isso.",
    "Isso, isso.",
    "Não.",
    "Não, não.",
    "É.",
    "Ah.",
    "Ah, sim.",
    "Sim, claro.",
    "Claro.",
    "Tá bom.",
    "Ok.",
    "Tá certo.",
    "Verdade.",
    "É verdade.",
    "Bota no Google.",
}


def _build_vicios() -> list[tuple[re.Pattern, str]]:
    """Constrói lista de (regex, substituição) para vícios inline."""
    return [
        # Confirmações pós-frase
        (re.compile(r',\s*né\?', re.IGNORECASE), '.'),
        (re.compile(r',\s*tá\?', re.IGNORECASE), '.'),
        (re.compile(r',\s*viu\?', re.IGNORECASE), '.'),
        (re.compile(r',\s*sabe\?', re.IGNORECASE), '.'),

        # Pós-frase sem vírgula
        (re.compile(r'\s+né\?', re.IGNORECASE), '.'),
        (re.compile(r'\s+tá\?', re.IGNORECASE), '.'),

        # No meio de frase
        (re.compile(r',\s*né,\s*', re.IGNORECASE), ', '),
        (re.compile(r',\s*tá,\s*', re.IGNORECASE), ', '),
        (re.compile(r',\s*gente,\s*', re.IGNORECASE), ', '),

        # Início de frase — usa lookbehind para garantir contexto
        (re.compile(r'(^|(?<=[.!?\n]))\s*Peraí,?\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Olha,\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Tipo,\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Assim,\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Então,\s+gente,?\s+'), ' Então, '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Gente,\s+'), ' '),

        # Frases de bastidores
        (re.compile(r'\s*Deixa eu ver se tá aparecendo[^.!?]*[.!?]\s*', re.IGNORECASE), ' '),
        (re.compile(r'\s*Tá aparecendo\?\s*', re.IGNORECASE), ' '),

        # Pontuação
        (re.compile(r'\.{2,}'), '.'),
        (re.compile(r'\s+([.,;:!?])'), r'\1'),
        (re.compile(r'[ \t]{2,}'), ' '),
        (re.compile(r'\n +'), '\n'),
    ]


VICIOS_INLINE = _build_vicios()

ESPACO_COLADO_RE = re.compile(f'([{LOWER_PT}]{{3,}})([{UPPER_PT}][{LOWER_PT}]{{2,}})')
QUEBRA_PARAGRAFO_RE = re.compile(f'(?<=[.!?])\\s+(?=[{UPPER_PT}])')


# -----------------------------------------------------------------------------
# TESTES INTERNOS
# -----------------------------------------------------------------------------

def rodar_testes_internos() -> tuple[bool, list[str]]:
    """Valida regex contra casos conhecidos. (passou, mensagens)."""
    msgs: list[str] = []
    ok = True

    # TESTE 1: palavras com acento NÃO devem ser flaggeadas pelo ESPACO_COLADO_RE
    palavras_intactas = [
        "estratégico", "orçamentária", "funções", "crianças", "construção",
        "disponível", "métodos", "Métodos", "Sapucaí", "área", "edificação",
        "Próximo", "início", "será", "estará", "está", "aí",
        "depois", "três", "também", "técnico", "câmera", "Estímulo",
        "tradicional", "ímãs", "câmaras", "histórico", "instalações",
    ]
    for p in palavras_intactas:
        matches = list(ESPACO_COLADO_RE.finditer(p))
        if matches:
            ok = False
            msgs.append(f"FALHA[espaco_colado]: {p!r} foi detectado (não deveria)")

    # TESTE 2: pares colados DEVEM ser detectados (mas não corrigidos)
    pares_para_detectar = [
        "MétodosCusto", "estudoPreliminar", "orçamentoExecutivo", "aulaInicial",
    ]
    for entrada in pares_para_detectar:
        matches = list(ESPACO_COLADO_RE.finditer(entrada))
        if not matches:
            ok = False
            msgs.append(f"FALHA[espaco_colado]: {entrada!r} não foi detectado (deveria)")

    # TESTE 3: quebra de parágrafo não em minúscula acentuada
    pares_quebra = [
        ("Primeira. é continuação.", 1),
        ("Primeira. É continuação.", 2),
        ("Primeira. Á outra.", 2),
        ("Frase 1. Frase 2.", 2),
        ("Frase 1. áudio.", 1),
    ]
    for texto, esperado_partes in pares_quebra:
        partes = QUEBRA_PARAGRAFO_RE.split(texto)
        if len(partes) != esperado_partes:
            ok = False
            msgs.append(
                f"FALHA[quebra]: {texto!r} -> {len(partes)} partes (esperado: {esperado_partes})"
            )

    # TESTE 4: vícios não destroem palavras
    casos_vicio = [
        ("Isso é importante, né? Vamos lá.", "Isso é importante. Vamos lá."),
        ("Tá certo, tá?", "Tá certo."),
        ("Bom, gente, agora", "Bom, agora"),
    ]
    for entrada, esperado in casos_vicio:
        texto = entrada
        for padrao, sub in VICIOS_INLINE:
            texto = padrao.sub(sub, texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        esperado_norm = re.sub(r'\s+', ' ', esperado).strip()
        if texto != esperado_norm:
            ok = False
            msgs.append(f"FALHA[vicio]: {entrada!r} -> {texto!r} (esperado: {esperado_norm!r})")

    # TESTE 5: UPPER_PT pega Á É Í etc
    for upper_char in "ÁÉÍÓÚÇÃÕÂÊÔ":
        if not re.match(f'[{UPPER_PT}]', upper_char):
            ok = False
            msgs.append(f"FALHA[unicode_upper]: {upper_char!r} não casa como MAIÚSCULA")

    # TESTE 6: UPPER_PT NÃO pega á é í etc
    for lower_char in "áéíóúçãõâêô":
        if re.match(f'[{UPPER_PT}]', lower_char):
            ok = False
            msgs.append(f"FALHA[unicode_lower]: {lower_char!r} casa como MAIÚSCULA (não deveria)")

    if ok:
        msgs.append(
            f"Todos os testes passaram: {len(palavras_intactas)} palavras intactas, "
            f"{len(pares_para_detectar)} detecções, {len(pares_quebra)} quebras, "
            f"{len(casos_vicio)} vícios, 22 chars Unicode."
        )
    return ok, msgs


# -----------------------------------------------------------------------------
# LOG
# -----------------------------------------------------------------------------

@dataclass
class PolishLog:
    linhas_removidas: list[tuple[int, str]] = field(default_factory=list)
    espacos_colados: list[tuple[str, str]] = field(default_factory=list)
    vicios_aplicados: dict[str, int] = field(default_factory=dict)
    paragrafos_quebrados: list[int] = field(default_factory=list)
    estrutura_normalizada: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append("LOG DE POLIMENTO — MÓDULO 04")
        lines.append("=" * 70)
        lines.append("")

        lines.append(f"## NORMALIZAÇÃO DE ESTRUTURA ({len(self.estrutura_normalizada)} operações)")
        lines.append("")
        for op in self.estrutura_normalizada:
            lines.append(f"  - {op}")
        lines.append("")

        lines.append(f"## LINHAS-CONFIRMAÇÃO REMOVIDAS ({len(self.linhas_removidas)})")
        lines.append("")
        if self.linhas_removidas:
            for num, conteudo in self.linhas_removidas:
                lines.append(f"  L{num:>5}: {conteudo!r}")
        else:
            lines.append("  (nenhuma)")
        lines.append("")

        lines.append(f"## ESPAÇOS COLADOS DETECTADOS — REVISAR MANUALMENTE ({len(self.espacos_colados)})")
        lines.append("")
        lines.append("  AVISO: o script NÃO corrige automaticamente espaços colados.")
        lines.append("  Detecta padrão CamelCase suspeito e lista aqui. Se for erro real,")
        lines.append("  edite o arquivo de saída manualmente. Casos como 'ConstruTinder'")
        lines.append("  (neologismo intencional) ou nomes próprios devem ficar como estão.")
        lines.append("")
        if self.espacos_colados:
            cont = Counter([(a, b) for a, b in self.espacos_colados])
            for (a, b), c in cont.most_common(200):
                lines.append(f"  {c:>4}x  {a!r} -> {b!r}")
            if len(cont) > 200:
                lines.append(f"  ... e mais {len(cont) - 200} pares únicos")
        else:
            lines.append("  (nenhum)")
        lines.append("")

        lines.append(f"## VÍCIOS DE FALA APLICADOS")
        lines.append("")
        if self.vicios_aplicados:
            for padrao, count in sorted(self.vicios_aplicados.items(), key=lambda x: -x[1]):
                lines.append(f"  {count:>5}x  {padrao}")
        else:
            lines.append("  (nenhum)")
        lines.append("")

        lines.append(f"## PARÁGRAFOS QUEBRADOS ({len(self.paragrafos_quebrados)})")
        lines.append("")
        lines.append(f"  Parágrafos > {PARAGRAFO_MAX_CHARS} chars que foram subdivididos.")
        for n in self.paragrafos_quebrados[:50]:
            lines.append(f"  - posição aproximada {n}")
        if len(self.paragrafos_quebrados) > 50:
            lines.append(f"  ... e mais {len(self.paragrafos_quebrados) - 50}")
        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)


# -----------------------------------------------------------------------------
# PARSING
# -----------------------------------------------------------------------------

@dataclass
class Aula:
    numero: int
    titulo: str
    metadata: str
    gravacoes: list[tuple[int, str]]


@dataclass
class DocumentoOriginal:
    header: str
    visao_geral: str
    aulas: list[Aula]


def _strip_trailing_separator(texto: str) -> str:
    """Remove `---` no final do bloco de texto."""
    return re.sub(r'\n---\s*$', '', texto).rstrip()


def parsear_documento(md: str) -> DocumentoOriginal:
    md = md.replace('\r\n', '\n').replace('\r', '\n')

    primeira_h2 = re.search(r'^## ', md, re.MULTILINE)
    if not primeira_h2:
        raise ValueError("Não encontrei nenhum `## ` no arquivo.")

    header = _strip_trailing_separator(md[:primeira_h2.start()].rstrip())

    visao_match = re.search(
        r'^## Visão Geral\s*\n(.*?)(?=^## |\Z)',
        md, re.MULTILINE | re.DOTALL
    )
    if not visao_match:
        raise ValueError("Não encontrei `## Visão Geral`.")
    visao_geral = _strip_trailing_separator(visao_match.group(1).strip())

    aula_pattern = re.compile(r'^## Aula (\d+):\s*(.*?)$', re.MULTILINE)
    aula_matches = list(aula_pattern.finditer(md))

    aulas: list[Aula] = []
    for i, m in enumerate(aula_matches):
        numero = int(m.group(1))
        titulo = m.group(2).strip()
        bloco_inicio = m.end()
        bloco_fim = aula_matches[i + 1].start() if i + 1 < len(aula_matches) else len(md)
        corpo = md[bloco_inicio:bloco_fim]

        trans_match = re.search(r'^### Transcrição\s*$', corpo, re.MULTILINE)
        if trans_match:
            metadata = _strip_trailing_separator(corpo[:trans_match.start()].strip())
            corpo_transcricao = corpo[trans_match.end():]
        else:
            metadata = _strip_trailing_separator(corpo.strip())
            corpo_transcricao = ""

        gravacoes: list[tuple[int, str]] = []
        if corpo_transcricao:
            grav_pattern = re.compile(r'^#### Gravação (\d+)\s*$', re.MULTILINE)
            grav_matches = list(grav_pattern.finditer(corpo_transcricao))
            for j, gm in enumerate(grav_matches):
                num_g = int(gm.group(1))
                start = gm.end()
                end = grav_matches[j + 1].start() if j + 1 < len(grav_matches) else len(corpo_transcricao)
                conteudo = _strip_trailing_separator(corpo_transcricao[start:end].strip())
                gravacoes.append((num_g, conteudo))

        aulas.append(Aula(numero=numero, titulo=titulo, metadata=metadata, gravacoes=gravacoes))

    return DocumentoOriginal(header=header, visao_geral=visao_geral, aulas=aulas)


# -----------------------------------------------------------------------------
# LIMPEZA
# -----------------------------------------------------------------------------

def detectar_espacos_colados(texto: str, log: PolishLog) -> str:
    """
    DETECTA palavras CamelCase suspeitas mas NÃO altera o texto.
    
    Por que não corrigir automaticamente: o regex pega falsos positivos
    como neologismos intencionais ("ConstruTinder"), nomes próprios
    ("InfoDev"), siglas misturadas. Reportar para revisão manual é mais
    seguro do que mutilar conteúdo.
    
    Se você ver no log algo que de fato deveria ser separado, edite
    manualmente o arquivo de saída.
    """
    for m in ESPACO_COLADO_RE.finditer(texto):
        a, b = m.group(1), m.group(2)
        log.espacos_colados.append((f"{a}{b}", f"{a} {b}"))
    return texto  # texto NÃO é modificado


def aplicar_vicios(texto: str, log: PolishLog) -> str:
    for padrao, sub in VICIOS_INLINE:
        novo, count = padrao.subn(sub, texto)
        if count > 0:
            label = padrao.pattern[:60]
            log.vicios_aplicados[label] = log.vicios_aplicados.get(label, 0) + count
        texto = novo
    return texto


def remover_linhas_confirmacao(texto: str, log: PolishLog) -> str:
    linhas_out: list[str] = []
    for i, linha in enumerate(texto.split('\n'), start=1):
        if linha.strip() in LINHAS_CONFIRMACAO_REMOVER:
            log.linhas_removidas.append((i, linha.strip()))
            continue
        linhas_out.append(linha)
    return '\n'.join(linhas_out)


def quebrar_paragrafos_longos(texto: str, log: PolishLog) -> str:
    paragrafos = texto.split('\n\n')
    out = []
    pos = 0
    for p in paragrafos:
        p_strip = p.strip()
        if len(p_strip) > PARAGRAFO_MAX_CHARS:
            partes = QUEBRA_PARAGRAFO_RE.split(p_strip)
            if len(partes) > 1:
                log.paragrafos_quebrados.append(pos)
                acumulado = ""
                novos: list[str] = []
                for parte in partes:
                    if len(acumulado) + len(parte) + 1 > PARAGRAFO_MAX_CHARS and acumulado:
                        novos.append(acumulado.strip())
                        acumulado = parte
                    else:
                        acumulado = (acumulado + " " + parte).strip()
                if acumulado:
                    novos.append(acumulado.strip())
                out.append('\n\n'.join(novos))
            else:
                out.append(p)
        else:
            out.append(p)
        pos += len(p) + 2
    return '\n\n'.join(out)


def limpeza_geral(texto: str, log: PolishLog) -> str:
    texto = detectar_espacos_colados(texto, log)
    texto = aplicar_vicios(texto, log)
    texto = remover_linhas_confirmacao(texto, log)
    texto = quebrar_paragrafos_longos(texto, log)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = re.sub(r'[ \t]+\n', '\n', texto)
    return texto.strip()


# -----------------------------------------------------------------------------
# MONTAGEM
# -----------------------------------------------------------------------------

def montar_documento_normalizado(doc: DocumentoOriginal, log: PolishLog) -> str:
    blocos: list[str] = []

    blocos.append(doc.header.rstrip())
    blocos.append("---")

    visao_limpa = limpeza_geral(doc.visao_geral, log)
    blocos.append("## Visão Geral\n\n" + visao_limpa)
    log.estrutura_normalizada.append("Visão Geral preservada e limpa")
    blocos.append("---")

    aulas_partes = ["## Aulas"]
    for aula in doc.aulas:
        metadata_limpa = limpeza_geral(aula.metadata, log) if aula.metadata else ""
        if metadata_limpa:
            aulas_partes.append(f"### {aula.numero}. {aula.titulo}\n\n{metadata_limpa}")
        else:
            aulas_partes.append(
                f"### {aula.numero}. {aula.titulo}\n\n*Sem material adicional registrado para esta aula.*"
            )
        log.estrutura_normalizada.append(
            f"Aula {aula.numero} convertida de `## Aula N:` para `### N.` dentro de `## Aulas`"
        )
    blocos.append('\n\n'.join(aulas_partes))
    blocos.append("---")

    todas_gravacoes: list[tuple[int, str]] = []
    for aula in doc.aulas:
        todas_gravacoes.extend(aula.gravacoes)
    todas_gravacoes.sort(key=lambda x: x[0])

    if todas_gravacoes:
        trans_partes = ["## Transcrição"]
        for num, conteudo in todas_gravacoes:
            conteudo_limpo = limpeza_geral(conteudo, log)
            trans_partes.append(f"### Gravação {num}\n\n{conteudo_limpo}")
            log.estrutura_normalizada.append(
                f"Gravação {num} movida para `## Transcrição` (era `#### Gravação` dentro de aula)"
            )
        blocos.append('\n\n'.join(trans_partes))

    return '\n\n'.join(blocos) + '\n'


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Polish determinístico do módulo 04")
    parser.add_argument("--dry-run", action="store_true", help="só lê e mostra estatísticas")
    parser.add_argument("--test-only", action="store_true", help="só roda os testes internos")
    args = parser.parse_args()

    print("Rodando testes internos do polidor...")
    ok, msgs = rodar_testes_internos()
    for m in msgs:
        print(f"  {m}")
    if not ok:
        print("\nABORTADO: testes falharam. Não vou tocar no arquivo.", file=sys.stderr)
        return 1
    print("Testes OK.\n")

    if args.test_only:
        return 0

    if not SOURCE.exists():
        print(f"ERRO: {SOURCE} não existe.", file=sys.stderr)
        return 1

    print(f"Lendo {SOURCE.relative_to(REPO_ROOT)}...")
    raw = SOURCE.read_text(encoding="utf-8")
    print(f"  {len(raw):,} chars, {raw.count(chr(10)):,} linhas")

    print("\nParseando estrutura...")
    try:
        doc = parsear_documento(raw)
    except ValueError as e:
        print(f"ERRO de parsing: {e}", file=sys.stderr)
        return 1

    print(f"  - Header: {len(doc.header):,} chars")
    print(f"  - Visão Geral: {len(doc.visao_geral):,} chars")
    print(f"  - Aulas: {len(doc.aulas)}")
    for a in doc.aulas:
        total_grav = sum(len(g[1]) for g in a.gravacoes)
        print(f"    - Aula {a.numero}: {a.titulo[:60]}")
        print(f"      metadata={len(a.metadata):,} chars, gravações={len(a.gravacoes)} ({total_grav:,} chars)")

    if args.dry_run:
        print("\n[dry-run] não vou gerar arquivo.")
        return 0

    print("\nAplicando limpeza e normalização...")
    log = PolishLog()
    final = montar_documento_normalizado(doc, log)

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(final, encoding="utf-8")
    print(f"\nArquivo salvo: {DEST.relative_to(REPO_ROOT)}")
    print(f"  - antes: {len(raw):,} chars")
    print(f"  - depois: {len(final):,} chars (delta: {len(final)-len(raw):+,})")

    LOG_PATH.write_text(log.render(), encoding="utf-8")
    print(f"Log salvo: {LOG_PATH.relative_to(REPO_ROOT)}")

    print("\n--- RESUMO ---")
    print(f"  Linhas-confirmação removidas: {len(log.linhas_removidas)}")
    print(f"  Espaços colados DETECTADOS (não corrigidos): {len(log.espacos_colados)}")
    print(f"  Parágrafos quebrados: {len(log.paragrafos_quebrados)}")
    total_vicios = sum(log.vicios_aplicados.values())
    print(f"  Vícios de fala aplicados: {total_vicios}")
    print(f"  Operações de normalização estrutural: {len(log.estrutura_normalizada)}")

    print("\nPRÓXIMO PASSO: abra o arquivo gerado, compare com o original.")
    print("Se aprovar, me avise pra eu te entregar o batch dos outros 11.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
