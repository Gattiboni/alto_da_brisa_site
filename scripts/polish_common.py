"""
polish_common.py — Biblioteca de limpeza determinística para arquivos de tema.

Compartilhada pelo batch script (polish_clean_batch.py).

Não chama API. Não modifica estrutura. Só limpa:
- Vícios de fala
- Linhas-confirmação isoladas
- Parágrafos longos
- Whitespace ruidoso

Detecta (mas não corrige) espaços colados, para revisão manual.

Espelha exatamente o comportamento validado no polish_clean_modulo4.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from collections import Counter


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

PARAGRAFO_MAX_CHARS = 600


# Classes Unicode EXPLÍCITAS — não usar [À-Ÿ] (bug de range Unicode).
LOWER_PT = r'a-záàâãäéèêëíìîïóòôõöúùûüçñ'
UPPER_PT = r'A-ZÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ'


# Linhas-confirmação a remover quando aparecem ISOLADAS em uma linha.
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
    """Lista de (regex, substituição) para vícios inline."""
    return [
        # Confirmações pós-frase com vírgula
        (re.compile(r',\s*né\?', re.IGNORECASE), '.'),
        (re.compile(r',\s*tá\?', re.IGNORECASE), '.'),
        (re.compile(r',\s*viu\?', re.IGNORECASE), '.'),
        (re.compile(r',\s*sabe\?', re.IGNORECASE), '.'),

        # Pós-frase sem vírgula
        (re.compile(r'\s+né\?', re.IGNORECASE), '.'),
        (re.compile(r'\s+tá\?', re.IGNORECASE), '.'),

        # Inseridos no meio
        (re.compile(r',\s*né,\s*', re.IGNORECASE), ', '),
        (re.compile(r',\s*tá,\s*', re.IGNORECASE), ', '),
        (re.compile(r',\s*gente,\s*', re.IGNORECASE), ', '),

        # Início de frase
        (re.compile(r'(^|(?<=[.!?\n]))\s*Peraí,?\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Olha,\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Tipo,\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Assim,\s+'), ' '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Então,\s+gente,?\s+'), ' Então, '),
        (re.compile(r'(^|(?<=[.!?\n]))\s*Gente,\s+'), ' '),

        # Bastidores
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
# Quebra parágrafo: pontuação forte + espaço + maiúscula.
# NÃO quebra quando o ponto é parte de numeração de lista (1. 2. 10. etc).
# Lookbehind exige que o caractere antes do ponto NÃO seja um dígito.
QUEBRA_PARAGRAFO_RE = re.compile(f'(?<=[^\\d][.!?])\\s+(?=[{UPPER_PT}])')


# -----------------------------------------------------------------------------
# TESTES INTERNOS
# -----------------------------------------------------------------------------

def rodar_testes_internos() -> tuple[bool, list[str]]:
    """Valida regex contra casos conhecidos. (passou, mensagens)."""
    msgs: list[str] = []
    ok = True

    palavras_intactas = [
        "estratégico", "orçamentária", "funções", "crianças", "construção",
        "disponível", "métodos", "Métodos", "Sapucaí", "área", "edificação",
        "Próximo", "início", "será", "estará", "está", "aí",
        "depois", "três", "também", "técnico", "câmera", "Estímulo",
        "tradicional", "ímãs", "câmaras", "histórico", "instalações",
    ]
    for p in palavras_intactas:
        if list(ESPACO_COLADO_RE.finditer(p)):
            ok = False
            msgs.append(f"FALHA[espaco_colado]: {p!r} foi detectado (não deveria)")

    pares_para_detectar = [
        "MétodosCusto", "estudoPreliminar", "orçamentoExecutivo", "aulaInicial",
    ]
    for entrada in pares_para_detectar:
        if not list(ESPACO_COLADO_RE.finditer(entrada)):
            ok = False
            msgs.append(f"FALHA[espaco_colado]: {entrada!r} não foi detectado")

    pares_quebra = [
        ("Primeira. é continuação.", 1),
        ("Primeira. É continuação.", 2),
        ("Primeira. Á outra.", 2),
        ("Algo importante. Frase nova.", 2),
        ("Frase 1. áudio.", 1),
        # Numeração de lista NÃO deve causar quebra
        ("1. O que é a Fundação", 1),
        ("Capítulo 2. Sapatas isoladas", 1),
        ("Item 10. Análise final", 1),
    ]
    for texto, esperado in pares_quebra:
        partes = QUEBRA_PARAGRAFO_RE.split(texto)
        if len(partes) != esperado:
            ok = False
            msgs.append(f"FALHA[quebra]: {texto!r} -> {len(partes)} partes (esperado: {esperado})")

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

    for upper_char in "ÁÉÍÓÚÇÃÕÂÊÔ":
        if not re.match(f'[{UPPER_PT}]', upper_char):
            ok = False
            msgs.append(f"FALHA[unicode_upper]: {upper_char!r} não casa como MAIÚSCULA")

    for lower_char in "áéíóúçãõâêô":
        if re.match(f'[{UPPER_PT}]', lower_char):
            ok = False
            msgs.append(f"FALHA[unicode_lower]: {lower_char!r} casa como MAIÚSCULA (não deveria)")

    if ok:
        msgs.append(
            f"Testes OK: {len(palavras_intactas)} palavras intactas, "
            f"{len(pares_para_detectar)} detecções, {len(pares_quebra)} quebras, "
            f"{len(casos_vicio)} vícios, 22 chars Unicode."
        )
    return ok, msgs


# -----------------------------------------------------------------------------
# LOG
# -----------------------------------------------------------------------------

@dataclass
class PolishLog:
    """Log de tudo que foi modificado durante o polimento de UM arquivo."""
    arquivo: str = ""
    linhas_removidas: list[tuple[int, str]] = field(default_factory=list)
    espacos_colados: list[tuple[str, str]] = field(default_factory=list)
    vicios_aplicados: dict[str, int] = field(default_factory=dict)
    paragrafos_quebrados: list[int] = field(default_factory=list)

    def render(self) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append(f"LOG DE POLIMENTO — {self.arquivo}")
        lines.append("=" * 70)
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
        lines.append("  AVISO: o script NÃO corrige automaticamente. Detecta CamelCase suspeito")
        lines.append("  e lista aqui. Se for erro real, edite o arquivo de saída manualmente.")
        lines.append("")
        if self.espacos_colados:
            cont = Counter(self.espacos_colados)
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
        lines.append(f"  Parágrafos > {PARAGRAFO_MAX_CHARS} chars subdivididos em pontuação forte.")
        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)


# -----------------------------------------------------------------------------
# OPERAÇÕES DE LIMPEZA
# -----------------------------------------------------------------------------

def detectar_espacos_colados(texto: str, log: PolishLog) -> str:
    """Detecta espaços colados (NÃO corrige). Apenas loga para revisão."""
    for m in ESPACO_COLADO_RE.finditer(texto):
        a, b = m.group(1), m.group(2)
        log.espacos_colados.append((f"{a}{b}", f"{a} {b}"))
    return texto


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
    """Pipeline completo de limpeza em um bloco de texto."""
    texto = detectar_espacos_colados(texto, log)
    texto = aplicar_vicios(texto, log)
    texto = remover_linhas_confirmacao(texto, log)
    texto = quebrar_paragrafos_longos(texto, log)
    # Normaliza whitespace residual
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = re.sub(r'[ \t]+\n', '\n', texto)
    return texto.strip()


# -----------------------------------------------------------------------------
# PARSING + LIMPEZA POR SEÇÃO (preserva estrutura existente)
# -----------------------------------------------------------------------------

def polir_arquivo_preservando_estrutura(md: str, log: PolishLog) -> str:
    """
    Para arquivos que JÁ ESTÃO no formato canônico (Visão Geral / Aulas / Transcrição):
    aplica limpeza no conteúdo de cada seção, mas preserva headings e separadores.

    Não move conteúdo entre seções. Não renomeia headings. Só limpa o texto dentro
    de cada bloco.
    """
    # Normaliza CRLF
    md = md.replace('\r\n', '\n').replace('\r', '\n')

    # Pré-processamento: junta quebras-preguiçosas dentro de parágrafo.
    # Quando uma linha termina sem pontuação forte e a próxima começa com
    # minúscula (ou parêntese, ou →), provavelmente é quebra de copy-paste.
    # Preserva quebras antes de:
    #   - Linha vazia (parágrafo real)
    #   - Heading (# ## ### ####)
    #   - Item de lista (- * • o)
    #   - Linha começando com número (1. 2. 3.)
    #   - Linha começando com MAIÚSCULA após ponto/dois-pontos
    md = _juntar_quebras_preguicosas(md)

    # Split por linha
    lines = md.split('\n')
    out_chunks: list[str] = []
    buffer: list[str] = []

    def flush_buffer():
        if not buffer:
            return
        texto = '\n'.join(buffer).strip()
        if texto:
            limpo = limpeza_geral(texto, log)
            out_chunks.append(limpo)
        else:
            out_chunks.append('')
        buffer.clear()

    for line in lines:
        stripped = line.strip()
        is_heading = bool(re.match(r'^#{1,6}\s+', stripped))
        is_separator = stripped == '---'
        is_blockquote_meta = stripped.startswith('>')

        if is_heading or is_separator:
            flush_buffer()
            out_chunks.append(line)
        elif is_blockquote_meta:
            flush_buffer()
            out_chunks.append(line)
        else:
            buffer.append(line)

    flush_buffer()

    # Recompõe
    resultado = '\n'.join(out_chunks)
    # Garante linha em branco antes E depois de headings/separadores
    resultado = re.sub(r'\n(#{1,6} [^\n]+)\n(?!\n)', r'\n\1\n\n', resultado)
    resultado = re.sub(r'(?<!\n)\n(#{1,6} )', r'\n\n\1', resultado)
    resultado = re.sub(r'\n(---)\n(?!\n)', r'\n\1\n\n', resultado)
    resultado = re.sub(r'(?<!\n)\n(---)\n', r'\n\n\1\n', resultado)
    # Normaliza quebras múltiplas
    resultado = re.sub(r'\n{3,}', '\n\n', resultado)

    return resultado.strip() + '\n'


def _juntar_quebras_preguicosas(md: str) -> str:
    """
    Junta linhas que foram quebradas no meio de um parágrafo por copy-paste.
    
    Regra: se uma linha termina sem pontuação forte (.!?:) e a próxima começa
    com minúscula ou caractere de continuação, junta em uma linha só.
    
    NÃO junta quando a próxima linha:
    - É vazia
    - Começa com heading (#)
    - É item de lista (-, *, •, o , número.)
    - Começa com MAIÚSCULA + texto curto típico (≥ tokens novos)
    """
    lines = md.split('\n')
    out: list[str] = []
    i = 0
    while i < len(lines):
        current = lines[i]
        stripped = current.strip()

        # Linhas vazias, headings, separadores, blockquotes: preserva como está
        if (not stripped or
            re.match(r'^#{1,6}\s+', stripped) or
            stripped == '---' or
            stripped.startswith('>')):
            out.append(current)
            i += 1
            continue

        # Tenta juntar com próximas linhas se forem "preguiçosas"
        merged = current
        j = i + 1
        while j < len(lines):
            next_stripped = lines[j].strip()
            if not next_stripped:
                break  # linha vazia: parágrafo real
            if re.match(r'^#{1,6}\s+', next_stripped):
                break  # heading
            if next_stripped == '---':
                break  # separador
            if next_stripped.startswith('>'):
                break  # blockquote
            # Item de lista (preserva)
            if re.match(r'^[-*•]\s+', next_stripped) or re.match(r'^o\s+', next_stripped):
                break
            # Numeração de item de lista (1. 2.) — só se for início de item curto
            if re.match(r'^\d+\.\s+\S', next_stripped):
                break

            # Junta se a linha atual NÃO termina com pontuação forte
            # OU se a próxima começa com minúscula / continuação
            current_clean = merged.rstrip()
            ends_with_strong = bool(re.search(r'[.!?:]$', current_clean))
            next_starts_lowercase = bool(re.match(f'[{LOWER_PT}]', next_stripped))
            next_starts_continuation = next_stripped[0] in '(→,;)' if next_stripped else False

            if not ends_with_strong or next_starts_lowercase or next_starts_continuation:
                # Junta
                merged = current_clean + ' ' + next_stripped
                j += 1
            else:
                break

        out.append(merged)
        i = j if j > i + 1 else i + 1

    return '\n'.join(out)
