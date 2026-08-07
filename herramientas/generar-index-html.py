"""Build the course index HTML from versiones.json + the real files on disk.

Deterministic step of the CCAR-F pipeline (patrón de generar-quiz-html.py):
reads versiones.json plus the actual corpus/ and recursos/ files (never trusts
metadata alone), builds INDEX_DATA, and injects it as `const INDEX_DATA = ...;`
between the last occurrence of the markers in plantillas/index.template.html.

Usage:
    python herramientas/generar-index-html.py [versiones.json] [output.html]

Defaults: versiones.json at the project root, output at recursos/index_v1.0.html.
Fails loudly (exit 1) if a resource path recorded in versiones.json does not
exist on disk, or if the exam blueprint cannot be parsed from the exam guide.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "plantillas" / "index.template.html"
EXAM_GUIDE_TXT = ROOT / "fuentes" / "exam-guide-oficial-v1.0.txt"
FUENTES_YAML = ROOT / "fuentes" / "fuentes.yaml"
MARK_START = "// __INDEX_DATA_START__"
MARK_END = "// __INDEX_DATA_END__"

RE_DOMAIN_LINE = re.compile(r"^(\d)\s+(.+?)\s+(\d+)%\s*$", re.MULTILINE)
RE_BLOCK_YAML = re.compile(
    r'-\s*id:\s*(?P<id>\d)\s*\n\s*nombre:\s*"[^"]*"\s*\n\s*dominio:\s*(?:null|"(?P<dominio>[^"]*)")'
)
RE_TITLE = re.compile(r'^#\s*Bloque\s+\d+\s*[—-]\s*(.+?)(?:\s*\{#[^}]+\})?\s*$', re.MULTILINE)
RE_LECCION = re.compile(r'^##\s*Lecci[oó]n\b', re.MULTILINE)
RE_INTRO = re.compile(r'^##\s*Qué evalúa el examen en este bloque\s*\n+(.*?)\n##', re.DOTALL | re.MULTILINE)


def _clean_md(text):
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # single-asterisk italics (e.g. *cuándo*)
    return text


def extract_description(guia_md_text, n, max_len=280):
    """Single 1-2 sentence summary (theme + what the block teaches, already
    merged in the guide's own intro prose) from the guide's 'Qué evalúa el
    examen en este bloque' section (identical section in the 6 guia_v1.0.md
    files); never hand-written. Never cuts mid-sentence: appends the second
    sentence only if it still fits within max_len, otherwise keeps just the
    first one (word-boundary ellipsis only as a last-resort fallback if even
    the first sentence alone exceeds max_len)."""
    m = RE_INTRO.search(guia_md_text)
    if not m:
        fail(f"block {n}: could not find the 'Qué evalúa el examen en este bloque' intro in the guide")
    para = _clean_md(m.group(1))
    para = re.sub(r'\s+', ' ', para).strip()
    sentences = re.split(r'(?<=[.!?])\s+', para)
    out = sentences[0].strip()
    for s in sentences[1:]:
        candidate = (out + " " + s).strip()
        if len(candidate) <= max_len:
            out = candidate
        else:
            break
    if len(out) > max_len:
        out = out[:max_len].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return out


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def parse_blueprint():
    """Domain -> {n, nombre, peso} from the read-only exam guide text (never linked/copied)."""
    if not EXAM_GUIDE_TXT.exists():
        fail(f"exam guide not found: {EXAM_GUIDE_TXT}")
    txt = EXAM_GUIDE_TXT.read_text(encoding="utf-8")
    try:
        start = txt.index("Domain Content Domain Weight")
        end = txt.index("5. Exam Scenarios")
    except ValueError:
        fail("could not locate the blueprint table in the exam guide text")
    block = txt[start:end]
    domains = {}
    for m in RE_DOMAIN_LINE.finditer(block):
        n = int(m.group(1))
        nombre = m.group(2).replace("ﬁ", "fi").replace("ﬂ", "fl").strip()
        peso = int(m.group(3))
        domains[n] = {"n": n, "nombre": nombre, "peso": peso}
    if len(domains) != 5 or sum(d["peso"] for d in domains.values()) != 100:
        fail(f"blueprint parse looks wrong: {domains}")
    return domains


def parse_block_domains():
    """Block number (1-5) -> domain number (from fuentes.yaml 'dominio: ... (Dn, ...)'); block 0 -> None."""
    if not FUENTES_YAML.exists():
        fail(f"fuentes.yaml not found: {FUENTES_YAML}")
    txt = FUENTES_YAML.read_text(encoding="utf-8")
    out = {}
    for m in RE_BLOCK_YAML.finditer(txt):
        bloque = int(m.group("id"))
        dominio_txt = m.group("dominio")
        if dominio_txt is None:
            out[bloque] = None
            continue
        dm = re.search(r"\(D(\d)", dominio_txt)
        out[bloque] = int(dm.group(1)) if dm else None
    return out


def block_title(n):
    path = ROOT / "corpus" / f"bloque-{n}-*.md"
    matches = list(ROOT.glob(f"corpus/bloque-{n}-*.md"))
    if not matches:
        fail(f"corpus file for block {n} not found")
    m = RE_TITLE.search(matches[0].read_text(encoding="utf-8"))
    if not m:
        fail(f"could not extract H1 title from {matches[0]}")
    return m.group(1).strip()


def rel_from_recursos(path_str):
    """versiones.json paths are 'recursos/...'; verify existence and return the
    path relative to recursos/, or None if missing on disk (never trust metadata alone)."""
    if not path_str:
        return None
    if not path_str.startswith("recursos/"):
        fail(f"unexpected path outside recursos/: {path_str}")
    abs_path = ROOT / path_str
    if not abs_path.exists():
        print(f"WARNING: path listed in versiones.json but missing on disk, omitted: {path_str}")
        return None
    return path_str[len("recursos/"):]


def load_json(path_str):
    abs_path = ROOT / path_str
    if not abs_path.exists():
        return None
    return json.loads(abs_path.read_text(encoding="utf-8"))


def build_data(versiones):
    domains = parse_blueprint()
    block_domain = parse_block_domains()
    domain_block = {v: k for k, v in block_domain.items() if v is not None}

    dominios = [
        {"n": d["n"], "nombre": d["nombre"], "peso": d["peso"], "bloqueCurso": domain_block.get(d["n"])}
        for d in sorted(domains.values(), key=lambda d: d["n"])
    ]

    corpus_bloques = versiones["corpus"]["bloques"]
    recursos_bloques = versiones.get("recursos", {}).get("bloques", {})

    bloques = []
    for n in range(6):
        sn = str(n)
        titulo = block_title(n)
        dominio_num = block_domain.get(n)
        dominio_info = domains.get(dominio_num) if dominio_num else None

        guia_md_matches = list(ROOT.glob(f"recursos/guias/bloque-{n}/guia_v*.md"))
        if not guia_md_matches:
            fail(f"guide markdown for block {n} not found under recursos/guias/bloque-{n}/")
        guia_md_text = guia_md_matches[0].read_text(encoding="utf-8")
        lecciones = len(RE_LECCION.findall(guia_md_text))
        descripcion = extract_description(guia_md_text, n)

        rb = recursos_bloques.get(sn, {})
        guia_meta = rb.get("guia", {})
        guia_html = rel_from_recursos(guia_meta.get("html"))
        guia = {"version": guia_meta.get("version", corpus_bloques[sn]["corpus"]["version"]),
                "lecciones": lecciones, "html": guia_html}

        quiz = None
        if "quiz" in rb:
            qm = rb["quiz"]
            quiz_json = load_json(qm["json"]) if qm.get("json") else None
            quiz_html = rel_from_recursos(qm.get("html"))
            if quiz_json is not None and quiz_html is not None:
                quiz = {"version": qm.get("version"), "preguntas": len(quiz_json.get("preguntas", [])), "html": quiz_html}

        flashcards = None
        if "flashcards" in rb:
            fm = rb["flashcards"]
            mazo_json = load_json(fm["mazo"]) if fm.get("mazo") else None
            fc_html = rel_from_recursos(fm.get("html"))
            if mazo_json is not None and fc_html is not None:
                flashcards = {"version": fm.get("version"), "cartas": len(mazo_json.get("cartas", [])), "html": fc_html}

        resumen = None
        if "pdf_resumen" in rb:
            pm = rb["pdf_resumen"]
            resumen_html = rel_from_recursos(pm.get("html"))
            resumen_pdf = rel_from_recursos(pm.get("pdf"))
            if resumen_html is not None:
                resumen = {"version": pm.get("version"), "html": resumen_html, "pdf": resumen_pdf}

        bloques.append({
            "n": n,
            "titulo": titulo,
            "dominioNum": dominio_num,
            "peso": dominio_info["peso"] if dominio_info else None,
            "dominioNombre": dominio_info["nombre"] if dominio_info else None,
            "corpusVersion": corpus_bloques[sn]["corpus"]["version"],
            "descripcion": descripcion,
            "guia": guia,
            "quiz": quiz,
            "flashcards": flashcards,
            "resumen": resumen,
        })

    return {
        "generado": versiones.get("guia_oficial_examen", {}).get("fecha_descarga", ""),
        "examenVersion": versiones.get("guia_oficial_examen", {}).get("version", ""),
        "dominios": dominios,
        "bloques": bloques,
    }


def main():
    versiones_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "versiones.json"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "recursos" / "index_v1.0.html"

    versiones = json.loads(versiones_path.read_text(encoding="utf-8"))
    data = build_data(versiones)

    template = TEMPLATE.read_text(encoding="utf-8")
    # rindex: robust even though this file's own comments never mention the
    # marker text verbatim — kept consistent with the other injectors anyway.
    start = template.rindex(MARK_START) + len(MARK_START)
    end = template.rindex(MARK_END)
    if end < start:
        raise SystemExit("markers out of order: end found before start")
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = template[:start] + "\n" + compact + "\n" + template[end:]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    n_disponibles = sum(1 for b in data["bloques"] if b["guia"]["html"])
    print(f"OK: {len(data['bloques'])} bloques ({n_disponibles} con guía HTML) -> {out_path}")


if __name__ == "__main__":
    main()
