"""Build a flashcards HTML from a deck JSON and the template.

Deterministic step of the CCAR-F pipeline: validates the deck against
plantillas/esquema-flashcard.schema.json (self-contained validation, no
external deps) and injects it between the __MAZO_JSON_START__/__MAZO_JSON_END__
markers of plantillas/flashcards.template.html.

Usage:
    python herramientas/generar-flashcards-html.py <deck.json> <output.html>

Fails loudly (exit 1) on any validation error: the JSON is the single source
of truth and a broken deck must never produce an HTML silently.
"""
import html as html_lib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "plantillas" / "flashcards.template.html"
MARK_START = "// __MAZO_JSON_START__"
MARK_END = "// __MAZO_JSON_END__"

DIFICULTADES = {"facil", "media", "dificil"}
RE_ID = re.compile(r"^b[0-5]-fc[0-9]{2}$")
RE_VERSION = re.compile(r"^[0-9]+\.[0-9]+$")
RE_FECHA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
RE_ANCHOR = re.compile(r"^#[a-z0-9-]+$")
RE_TAG = re.compile(r"^[a-z0-9-]+$")


def fail(errors):
    print("DECK VALIDATION FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)


def validate(deck):
    errors = []
    cfg = deck.get("config")
    cartas = deck.get("cartas")
    if not isinstance(cfg, dict):
        errors.append("config: missing or not an object")
        cfg = {}
    if not isinstance(cartas, list) or len(cartas) < 10:
        errors.append("cartas: missing, not a list, or fewer than 10 items")
        cartas = cartas if isinstance(cartas, list) else []

    for k in ("bloque", "nombre", "version", "fecha", "guiaOficialExamen", "generadoDesdeCorpus"):
        if k not in cfg:
            errors.append(f"config.{k}: missing")
    if not isinstance(cfg.get("bloque"), int) or not 0 <= cfg.get("bloque", -1) <= 5:
        errors.append("config.bloque: must be an integer 0-5")
    for k in ("version", "guiaOficialExamen"):
        if k in cfg and not RE_VERSION.match(str(cfg[k])):
            errors.append(f"config.{k}: must match X.Y")
    if "fecha" in cfg and not RE_FECHA.match(str(cfg["fecha"])):
        errors.append("config.fecha: must be YYYY-MM-DD")

    seen_ids = set()
    for i, c in enumerate(cartas):
        where = f"cartas[{i}] ({c.get('id', '?')})"
        for k in ("id", "taskStatement", "front", "back", "refSeccion", "dificultad", "etiquetas"):
            if k not in c:
                errors.append(f"{where}.{k}: missing")
        extra = set(c) - {"id", "taskStatement", "front", "back", "refSeccion", "dificultad", "etiquetas"}
        if extra:
            errors.append(f"{where}: unexpected fields {sorted(extra)}")
        cid = c.get("id", "")
        if not RE_ID.match(cid):
            errors.append(f"{where}.id: must match bN-fcNN")
        if cid in seen_ids:
            errors.append(f"{where}.id: duplicated")
        seen_ids.add(cid)
        for k in ("front", "back"):
            if len(str(c.get(k, ""))) < 10:
                errors.append(f"{where}.{k}: shorter than 10 chars")
        if not RE_ANCHOR.match(c.get("refSeccion", "")):
            errors.append(f"{where}.refSeccion: must be a #kebab-case anchor")
        if c.get("dificultad") not in DIFICULTADES:
            errors.append(f"{where}.dificultad: must be one of {sorted(DIFICULTADES)}")
        tags = c.get("etiquetas", [])
        if not isinstance(tags, list) or not 1 <= len(tags) <= 4 or not all(RE_TAG.match(str(t)) for t in tags):
            errors.append(f"{where}.etiquetas: 1-4 kebab-case strings required")

    return errors


def compute_title(cfg):
    """<title> composed from the deck's own config: 'Flashcards CCAR-F ·
    Bloque N — <nombre>'."""
    bloque = cfg.get("bloque")
    nombre = cfg.get("nombre", "").strip()
    if bloque is None or not nombre:
        return "Flashcards CCAR-F"
    return f"Flashcards CCAR-F · Bloque {bloque} — {nombre}"


def validate_anchors(deck):
    """Every refSeccion must exist as an anchor in the block's corpus file."""
    bloque = deck["config"]["bloque"]
    matches = list((ROOT / "corpus").glob(f"bloque-{bloque}-*.md"))
    if not matches:
        return [f"corpus file for block {bloque} not found under corpus/"]
    corpus_text = matches[0].read_text(encoding="utf-8")
    anchors = set(re.findall(r"\{(#[a-z0-9-]+)\}", corpus_text))
    return [
        f"{c['id']}: refSeccion {c['refSeccion']} not found in {matches[0].name}"
        for c in deck["cartas"] if c["refSeccion"] not in anchors
    ]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    deck_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])

    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    errors = validate(deck)
    if not errors:
        errors = validate_anchors(deck)
    if errors:
        fail(errors)

    template = TEMPLATE.read_text(encoding="utf-8")
    title = html_lib.escape(compute_title(deck["config"]), quote=False)
    template = template.replace("<title>{{TITULO}}</title>", f"<title>{title}</title>")
    # rindex: robust even if a comment mentions the markers literally —
    # the real block is the last occurrence.
    start = template.rindex(MARK_START) + len(MARK_START)
    end = template.rindex(MARK_END)
    if end < start:
        raise SystemExit("markers out of order: end found before start")
    compact = json.dumps(deck, ensure_ascii=False, separators=(",", ":"))
    html = template[: start] + "\n" + compact + "\n" + template[end:]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"OK: {len(deck['cartas'])} cards -> {out_path}")


if __name__ == "__main__":
    main()
