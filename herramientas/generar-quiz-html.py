"""Build a quiz HTML from a question bank JSON and the template.

Deterministic step of the CCAR-F pipeline: validates the bank against
plantillas/esquema-pregunta.schema.json (self-contained validation, no
external deps) and injects it as `const DATA = ...;` between the
__PREGUNTAS_JSON_START__/__PREGUNTAS_JSON_END__ markers of
plantillas/quiz.template.html.

Usage:
    python herramientas/generar-quiz-html.py <bank.json> <output.html>

Fails loudly (exit 1) on any validation error.
"""
import html as html_lib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "plantillas" / "quiz.template.html"
MARK_START = "// __PREGUNTAS_JSON_START__"
MARK_END = "// __PREGUNTAS_JSON_END__"

DIFICULTADES = {"facil", "media", "dificil"}
RE_QID = re.compile(r"^(b[0-5]|sim)-q[0-9]{2,3}$")
RE_VERSION = re.compile(r"^[0-9]+\.[0-9]+$")
RE_OPT = re.compile(r"^[A-E]$")
CFG_KEYS = {"titulo", "version", "bloque", "modo_defecto", "solo_examen",
            "duracion_examen_min", "generado_desde_referencia", "generado_desde_corpus", "fecha"}
Q_REQUIRED = ("id", "bloque", "dominio", "taskStatement", "enunciado",
              "opciones", "seleccionar", "dificultad", "refSeccion")
Q_ALL = set(Q_REQUIRED) | {"escenario", "fuentes", "etiquetas"}


def fail(errors):
    print("BANK VALIDATION FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)


def validate(bank):
    errors = []
    cfg = bank.get("config", {})
    qs = bank.get("preguntas", [])
    if not isinstance(cfg, dict) or not isinstance(qs, list) or not qs:
        return ["top level: config object and non-empty preguntas array required"]

    for k in ("titulo", "version"):
        if k not in cfg:
            errors.append(f"config.{k}: missing")
    if "version" in cfg and not RE_VERSION.match(str(cfg["version"])):
        errors.append("config.version: must match X.Y")
    extra = set(cfg) - CFG_KEYS
    if extra:
        errors.append(f"config: unexpected fields {sorted(extra)}")

    seen = set()
    for i, q in enumerate(qs):
        where = f"preguntas[{i}] ({q.get('id', '?')})"
        for k in Q_REQUIRED:
            if k not in q:
                errors.append(f"{where}.{k}: missing")
        extra = set(q) - Q_ALL
        if extra:
            errors.append(f"{where}: unexpected fields {sorted(extra)}")
        qid = q.get("id", "")
        if not RE_QID.match(qid):
            errors.append(f"{where}.id: must match bN-qNN or sim-qNN")
        if qid in seen:
            errors.append(f"{where}.id: duplicated")
        seen.add(qid)
        if q.get("dificultad") not in DIFICULTADES:
            errors.append(f"{where}.dificultad: invalid")
        if len(str(q.get("enunciado", ""))) < 20:
            errors.append(f"{where}.enunciado: shorter than 20 chars")
        opts = q.get("opciones", [])
        if not 4 <= len(opts) <= 5:
            errors.append(f"{where}.opciones: must have 4-5 items")
        oids = [o.get("id") for o in opts]
        if len(set(oids)) != len(oids) or not all(RE_OPT.match(str(o)) for o in oids):
            errors.append(f"{where}.opciones: ids must be unique A-E")
        for o in opts:
            for k in ("id", "texto", "correcta", "justificacion"):
                if k not in o:
                    errors.append(f"{where}.opciones[{o.get('id','?')}].{k}: missing")
            if len(str(o.get("justificacion", ""))) < 15:
                errors.append(f"{where}.opciones[{o.get('id','?')}].justificacion: shorter than 15 chars")
        n_ok = sum(1 for o in opts if o.get("correcta") is True)
        if q.get("seleccionar") != n_ok:
            errors.append(f"{where}.seleccionar: {q.get('seleccionar')} but {n_ok} options are correcta:true")

    return errors


def validate_anchors(bank):
    """Every refSeccion must exist in the corpus of the QUESTION'S OWN origin
    block (its `bloque` field, not the bank's), so a multi-block bank (e.g.
    the exam simulation, banco compuesto con preguntas de los 6 corpus vía
    id bN-qXX/sim-qXX) can never validate a question's anchor against a
    different block's corpus. Anchors are cached per block since a bank may
    repeat the same block many times."""
    errors = []
    anchors_by_block = {}
    for q in bank["preguntas"]:
        b = q["bloque"]
        if b not in anchors_by_block:
            matches = list((ROOT / "corpus").glob(f"bloque-{b}-*.md"))
            if not matches:
                errors.append(f"corpus file for block {b} not found under corpus/")
                anchors_by_block[b] = set()
                continue
            text = matches[0].read_text(encoding="utf-8")
            anchors_by_block[b] = set(re.findall(r"\{(#[a-z0-9-]+)\}", text))
        if q["refSeccion"] not in anchors_by_block[b]:
            errors.append(f"{q['id']}: refSeccion {q['refSeccion']} not found in corpus for block {b}")
    return errors


def compute_title(cfg):
    """<title> from the bank's own config: the exam simulation (solo_examen
    true) gets a fixed title; regular per-block banks compose it from
    config.titulo (already 'Bloque N — <título>')."""
    if cfg.get("solo_examen"):
        return "Simulacro de examen CCAR-F"
    titulo = cfg.get("titulo", "").strip()
    return f"Quiz CCAR-F · {titulo}" if titulo else "Quiz CCAR-F"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    bank_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])

    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    errors = validate(bank)
    if not errors:
        errors = validate_anchors(bank)
    if errors:
        fail(errors)

    template = TEMPLATE.read_text(encoding="utf-8")
    title = html_lib.escape(compute_title(bank["config"]), quote=False)
    template = template.replace("<title>{{TITULO}}</title>", f"<title>{title}</title>")
    # rindex: the template's instruction comment mentions the markers literally,
    # so the real block is the LAST occurrence, inside the <script> section.
    start = template.rindex(MARK_START) + len(MARK_START)
    end = template.rindex(MARK_END)
    if end < start:
        raise SystemExit("markers out of order: end found before start")
    compact = json.dumps(bank, ensure_ascii=False, separators=(",", ":"))
    html = template[: start] + "\nconst DATA = " + compact + ";\n" + template[end:]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"OK: {len(bank['preguntas'])} questions -> {out_path}")


if __name__ == "__main__":
    main()
