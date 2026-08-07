#!/usr/bin/env python3
"""Assemble dist/ (the ONLY distributable) from recursos/.

- Copies the whole recursos/ tree to dist/ (site root).
- The course index (recursos/index_v1.0.html) becomes dist/index.html so the
  published site opens directly on it (no redirect page). Relative links keep
  working because the index already lives at the recursos/ root.
- Hard guarantees before declaring success:
    * no forbidden content ships (fuentes/, corpus/, plantillas/, herramientas/,
      .claude/, ESTADO/CLAUDE/versiones) — dist contains recursos content only;
    * the expected resource set exists (index + 6 guias + 6 quizzes + simulacro);
    * every local href/src referenced by dist/index.html resolves inside dist/.

Usage: python herramientas/construir-dist.py
Publication (documented in ESTADO.md): the dist/ content is committed to the
site branch (master) and pushed; GitHub Pages serves that branch's root.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECURSOS = ROOT / "recursos"
DIST = ROOT / "dist"
INDEX_SRC = "index_v1.0.html"

FORBIDDEN_NAMES = {"fuentes", "corpus", "plantillas", "herramientas", ".claude",
                   "ESTADO.md", "CLAUDE.md", "versiones.json", "exam-guide-oficial-v1.0.pdf"}

EXPECTED = ["index.html", "simulacro/simulacro_v1.0.html"] + \
    [f"guias/bloque-{n}/guia_v1.0.html" for n in range(6)] + \
    [f"quiz/bloque-{n}/quiz_v1.0.html" for n in range(6)]


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def main():
    if not RECURSOS.is_dir():
        fail(f"recursos/ not found at {RECURSOS}")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(RECURSOS, DIST)

    index = DIST / INDEX_SRC
    if not index.exists():
        fail(f"{INDEX_SRC} not found in recursos/")
    index.rename(DIST / "index.html")

    for name in FORBIDDEN_NAMES:
        hits = list(DIST.rglob(name))
        if hits:
            fail(f"forbidden content in dist/: {hits[0]}")

    for rel in EXPECTED:
        if not (DIST / rel).exists():
            fail(f"expected resource missing in dist/: {rel}")

    html = (DIST / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"<script>.*?</script>", "", html, flags=re.DOTALL)  # JS builds links at runtime
    refs = re.findall(r'(?:href|src)="([^"#][^"]*)"', html)
    local = [r for r in refs if not re.match(r"^(https?:|data:|mailto:)", r)]
    missing = [r for r in local if not (DIST / r.split("?")[0].split("#")[0]).exists()]
    if missing:
        fail(f"index.html references missing local paths: {missing}")

    n_files = sum(1 for p in DIST.rglob("*") if p.is_file())
    print(f"OK: dist/ assembled ({n_files} files; {len(local)} local index refs verified)")


if __name__ == "__main__":
    main()
