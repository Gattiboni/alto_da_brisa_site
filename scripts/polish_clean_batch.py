"""
polish_clean_batch.py — Roda o polimento determinístico nos outros 11 módulos.

Diferente do polish_clean_modulo4.py, este script NÃO normaliza estrutura —
os outros 11 módulos já estão no formato canônico (Visão Geral / Aulas /
Transcrição). Aqui só limpamos o conteúdo dentro de cada seção, preservando
headings e separadores.

Princípios não-negociáveis (espelhando módulo 4):
  - Sem alterar nem remover conteúdo informativo.
  - Limpar vícios de fala óbvios.
  - Detectar (NÃO corrigir) espaços colados — listar para revisão manual.
  - Sem chamar API. Tudo Python puro, custo zero.

USO:
   python scripts/polish_clean_batch.py                  # processa o que falta
   python scripts/polish_clean_batch.py --force          # reprocessa tudo
   python scripts/polish_clean_batch.py --only 06,07     # só esses módulos
   python scripts/polish_clean_batch.py --dry-run        # só lista, não escreve
   python scripts/polish_clean_batch.py --test-only      # só roda os testes
"""

from __future__ import annotations

import sys
import time
import argparse
from pathlib import Path

# Import da lib comum (mesmo diretório)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from polish_common import (
    rodar_testes_internos,
    PolishLog,
    polir_arquivo_preservando_estrutura,
)


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMAS_DIR = REPO_ROOT / "knowledge" / "temas"
TEMAS_V2_DIR = REPO_ROOT / "knowledge" / "temas_v2"

# Ordem: começa pelos menores para validar rápido, deixa os grandes para o fim.
# Módulo 04 NÃO entra aqui — já foi processado pelo polish_clean_modulo4.py.
TEMAS_OUTROS_ONZE = [
    "11_aberturas-esquadrias.md",          # menor
    "03_terreno.md",
    "05_servicos-preliminares.md",
    "02_projeto.md",
    "12_instalacoes-residenciais.md",
    "01_introducao.md",
    "10_acabamentos.md",
    "09_coberturas.md",
    "06_fundacoes.md",
    "08_lajes.md",
    "07_estruturas-vedacoes.md",           # maior
]


def parse_only(s: str) -> set[str]:
    """'06,07' -> {'06', '07'}. '06_fundacoes,07_estruturas' também."""
    return {p.strip().split("_")[0] for p in s.split(",") if p.strip()}


# -----------------------------------------------------------------------------
# PROCESSAMENTO
# -----------------------------------------------------------------------------

def polir_um(source: Path, dest: Path) -> tuple[bool, dict]:
    """Polia um arquivo. Retorna (sucesso, estatísticas)."""
    if not source.exists():
        return False, {"erro": f"arquivo não existe: {source}"}

    print(f"\n  {source.name}")
    raw = source.read_text(encoding="utf-8")
    print(f"    in:  {len(raw):,} chars")

    log = PolishLog(arquivo=source.name)
    t0 = time.time()
    final = polir_arquivo_preservando_estrutura(raw, log)
    dt = time.time() - t0

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(final, encoding="utf-8")

    # Log paralelo (.log.txt)
    log_path = dest.with_name(dest.stem + "_polish_log.txt")
    log_path.write_text(log.render(), encoding="utf-8")

    delta = len(final) - len(raw)
    pct = (delta / len(raw)) * 100 if len(raw) else 0
    print(f"    out: {len(final):,} chars ({delta:+,}, {pct:+.1f}%) em {dt:.1f}s")
    print(f"    linhas removidas: {len(log.linhas_removidas)}, "
          f"vícios: {sum(log.vicios_aplicados.values())}, "
          f"parágrafos quebrados: {len(log.paragrafos_quebrados)}, "
          f"espaços colados detectados: {len(log.espacos_colados)}")

    return True, {
        "chars_in": len(raw),
        "chars_out": len(final),
        "delta_chars": delta,
        "delta_pct": pct,
        "duracao_s": dt,
        "linhas_removidas": len(log.linhas_removidas),
        "vicios_aplicados": sum(log.vicios_aplicados.values()),
        "paragrafos_quebrados": len(log.paragrafos_quebrados),
        "espacos_colados_detectados": len(log.espacos_colados),
    }


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Polish determinístico — outros 11 temas")
    parser.add_argument("--force", action="store_true", help="reprocessa mesmo se já existir")
    parser.add_argument("--only", type=str, default="", help="prefixos a processar, ex: '06,07'")
    parser.add_argument("--dry-run", action="store_true", help="só lista, não escreve")
    parser.add_argument("--test-only", action="store_true", help="só roda testes internos")
    args = parser.parse_args()

    print("Rodando testes internos do polidor...")
    ok, msgs = rodar_testes_internos()
    for m in msgs:
        print(f"  {m}")
    if not ok:
        print("\nABORTADO: testes falharam.", file=sys.stderr)
        return 1
    print("Testes OK.\n")

    if args.test_only:
        return 0

    only_filter = parse_only(args.only) if args.only else set()

    fila: list[Path] = []
    for name in TEMAS_OUTROS_ONZE:
        src = TEMAS_DIR / name
        dst = TEMAS_V2_DIR / name

        if only_filter:
            prefix = name.split("_")[0]
            if prefix not in only_filter:
                continue

        if not src.exists():
            print(f"AVISO: {src} não encontrado. Pulando.")
            continue

        if dst.exists() and not args.force:
            print(f"SKIP {name} (já existe em temas_v2/; use --force para reprocessar)")
            continue

        fila.append(src)

    if not fila:
        print("Nada a fazer.")
        return 0

    print(f"\nFila: {len(fila)} arquivo(s)")
    for p in fila:
        size_kb = p.stat().st_size / 1024
        print(f"  - {p.name} ({size_kb:,.1f} KB)")

    if args.dry_run:
        print("\n[dry-run] não vou escrever nada.")
        return 0

    print("\nProcessando...")
    t_inicio = time.time()
    relatorio: list[dict] = []

    for src in fila:
        dst = TEMAS_V2_DIR / src.name
        try:
            ok_f, stats = polir_um(src, dst)
            stats["file"] = src.name
            stats["ok"] = ok_f
            relatorio.append(stats)
        except Exception as e:
            print(f"\n  ERRO em {src.name}: {e}", file=sys.stderr)
            relatorio.append({"file": src.name, "ok": False, "erro": str(e)})

    duracao = time.time() - t_inicio

    print("\n" + "=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    for r in relatorio:
        if r.get("ok"):
            print(f"  OK     {r['file']:50s} "
                  f"in:{r['chars_in']:>8,}  out:{r['chars_out']:>8,}  "
                  f"({r['delta_pct']:+.1f}%)")
        else:
            print(f"  FALHOU {r['file']:50s} {r.get('erro', '?')}")
    print(f"\nDuração total: {duracao:.1f}s ({duracao/60:.1f} min)")
    print(f"\nArquivos salvos em: {TEMAS_V2_DIR.relative_to(REPO_ROOT)}")
    print(f"Logs em: {TEMAS_V2_DIR.relative_to(REPO_ROOT)}/*_polish_log.txt")

    return 0


if __name__ == "__main__":
    sys.exit(main())
