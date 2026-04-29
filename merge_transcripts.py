"""
merge_transcripts.py
Unifica todos os .md de transcrição da pasta transcripts_original
em um único arquivo raw, ordenados pelo número sequencial do nome.

Uso:
    python merge_transcripts.py

Saída:
    knowledge/curso_amanda_fernando_raw.md
"""

import os
import re
from pathlib import Path

# --- Configuração ---
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "transcripts_original"
OUTPUT_DIR = BASE_DIR / "knowledge"
OUTPUT_FILE = OUTPUT_DIR / "curso_amanda_fernando_raw.md"


def extract_sequence(filename: str) -> int:
    """Extrai o número sequencial do padrão ACBS-N-mp3-..."""
    match = re.match(r"ACBS-(\d+)-", filename)
    return int(match.group(1)) if match else 9999


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    md_files = sorted(
        [f for f in INPUT_DIR.iterdir() if f.suffix == ".md"],
        key=lambda f: extract_sequence(f.name),
    )

    if not md_files:
        print(f"Nenhum .md encontrado em: {INPUT_DIR}")
        return

    print(f"Encontrados {len(md_files)} arquivos. Iniciando merge...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Curso Amanda & Fernando — Transcrição Completa\n\n")
        out.write(
            "> Arquivo unificado gerado automaticamente a partir de 21 gravações.\n"
        )
        out.write(
            "> Fonte bruta para organização temática e alimentação do Claudinho da Brisa.\n\n"
        )
        out.write("---\n\n")

        for i, filepath in enumerate(md_files, 1):
            content = filepath.read_text(encoding="utf-8", errors="replace").strip()

            out.write(f"## Gravação {i} — {filepath.name}\n\n")
            out.write(content)
            out.write("\n\n---\n\n")

            print(
                f"  [{i:02d}/{len(md_files)}] {filepath.name} ({len(content):,} chars)"
            )

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\nConcluído.")
    print(f"Arquivo gerado: {OUTPUT_FILE}")
    print(f"Tamanho: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
