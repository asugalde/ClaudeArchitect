"""Compose the CCAR-F full exam simulation bank from the 6 block question banks.

Deterministic step of `/generar-recursos simulacro`. Reads the 6 approved
per-block banks (recursos/quiz/bloque-N/preguntas_v1.0.json, N=0..5) and
writes recursos/simulacro/preguntas_v1.0.json with 60 questions selected
VERBATIM (byte-identical, original id kept) from those banks.

This script only READS the block banks and plantillas/esquema-pregunta.schema.json
(for documentation purposes) and WRITES the composed simulacro bank. It never
touches recursos/quiz/bloque-N/*, versiones.json, ESTADO.md or the index.

Quota design (documented rationale)
------------------------------------
The blueprint's domain weights map 1:1 to blocks (each block = one domain,
except block 0 which is transversal):

    Domain (task statements)                    weight   block
    D1 Agentic Architecture & Orchestration       27%    bloque 4
    D2 Tool Design & MCP Integration               18%    bloque 3
    D3 Claude Code Configuration & Workflows       20%    bloque 2
    D4 Prompt Engineering & Structured Output      20%    bloque 1
    D5 Context Management & Reliability            15%    bloque 5
    (transversal, no domain)                        -     bloque 0

Naive 60 * weight rounding would leave no room for block 0. Per the
contract, block 0 contributes a FEW questions (3) taken out of the other
blocks' shares, then the remainder is redistributed keeping the domains'
relative order. This yields the fixed quota table used below (60 total):

    bloque 4 (D1, 27%): 16
    bloque 2 (D3, 20%): 12
    bloque 1 (D4, 20%): 11   (one less than bloque 2 despite equal weight,
                              to make room for bloque 0 without breaking the
                              27/20/20/18/15 ordering)
    bloque 3 (D2, 18%): 10
    bloque 5 (D5, 15%):  8
    bloque 0 (transversal): 3
    -----------------------------
    TOTAL: 60

Selection algorithm (per block, deterministic)
------------------------------------------------
A single `random.Random(SEED)` instance is threaded through the whole
composition, blocks processed in fixed numeric order 0..5, so the result is
100% reproducible for a given SEED.

For each block, with its quota Q:
  1. Difficulty targets for Q are computed with the largest-remainder method,
     using THAT block's own bank-wide facil/media/dificil ratio (every block
     bank happens to be ~22/56/22 already, so this naturally keeps the
     composed 60-question simulacro close to the same global split).
  2. Task-statement coverage pass: task statements are shuffled (seeded) to
     pick an unbiased priority order, then one question is taken from each
     task statement in turn -- preferring, within that task statement, a
     question whose difficulty still has remaining target quota -- until
     either every task statement got one question or the block's quota Q is
     exhausted (whichever first). This guarantees "at least 1 per TS while
     the quota allows it", exactly as required.
  3. Fill pass: any remaining slots up to Q are filled from the rest of the
     block's questions (shuffled once, seeded), again preferring a
     difficulty that still has remaining target quota.

Finally all six blocks' selections are concatenated (block order 0..5) and
the resulting 60-question list is shuffled once more (same RNG, so it's the
next draw in the reproducible sequence) to produce the final exam order.

SEED = 20260807 (documented, fixed; matches the contract's suggestion).

Usage:
    python herramientas/componer-simulacro.py
"""
import json
import random
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUIZ_DIR = ROOT / "recursos" / "quiz"
OUT_PATH = ROOT / "recursos" / "simulacro" / "preguntas_v1.0.json"

SEED = 20260807
BLOCK_ORDER = [0, 1, 2, 3, 4, 5]
QUOTAS = {4: 16, 2: 12, 1: 11, 3: 10, 5: 8, 0: 3}
DIFFICULTIES = ("facil", "media", "dificil")
GLOBAL_TARGET_RATIO = (0.22, 0.56, 0.22)  # facil, media, dificil


def load_bank(n):
    path = QUIZ_DIR / f"bloque-{n}" / "preguntas_v1.0.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def largest_remainder(raw, quota):
    """Round a dict of {key: float} to integers summing exactly to quota."""
    floors = {k: int(v) for k, v in raw.items()}
    remainder = quota - sum(floors.values())
    order = sorted(raw.keys(), key=lambda k: raw[k] - floors[k], reverse=True)
    for i in range(max(remainder, 0)):
        order[i % len(order)]
        floors[order[i]] += 1
    # if remainder negative (shouldn't happen with our inputs), trim from smallest fracs
    if remainder < 0:
        order_asc = sorted(raw.keys(), key=lambda k: raw[k] - floors[k])
        for i in range(-remainder):
            floors[order_asc[i % len(order_asc)]] -= 1
    return floors


def pick_one(pool, targets, rng):
    """Pick (and return, without removing) a question from pool, preferring
    a difficulty that still has remaining target quota; falls back to any."""
    needed = [q for q in pool if targets.get(q["dificultad"], 0) > 0]
    candidates = needed if needed else pool
    return rng.choice(candidates)


def select_block(block_n, rng):
    bank = load_bank(block_n)
    questions = bank["preguntas"]
    quota = QUOTAS[block_n]

    # group by task statement, preserving first-seen order
    ts_groups = OrderedDict()
    for q in questions:
        ts_groups.setdefault(q["taskStatement"], []).append(q)
    remaining_by_ts = {ts: list(qs) for ts, qs in ts_groups.items()}
    for pool in remaining_by_ts.values():
        rng.shuffle(pool)

    ts_order = list(ts_groups.keys())
    rng.shuffle(ts_order)

    diff_counts = Counter(q["dificultad"] for q in questions)
    total = len(questions)
    raw = {d: quota * diff_counts.get(d, 0) / total for d in DIFFICULTIES}
    targets = largest_remainder(raw, quota)

    selected = []
    covered_ts = []

    # Phase 1: task-statement coverage, while quota allows
    for ts in ts_order:
        if len(selected) >= quota:
            break
        pool = remaining_by_ts[ts]
        if not pool:
            continue
        pick = pick_one(pool, targets, rng)
        pool.remove(pick)
        selected.append(pick)
        covered_ts.append(ts)
        if targets.get(pick["dificultad"], 0) > 0:
            targets[pick["dificultad"]] -= 1

    # Phase 2: fill remaining slots from whatever's left in the block
    leftover = [q for ts in ts_order for q in remaining_by_ts[ts]]
    rng.shuffle(leftover)
    while len(selected) < quota and leftover:
        pick = pick_one(leftover, targets, rng)
        leftover.remove(pick)
        selected.append(pick)
        if targets.get(pick["dificultad"], 0) > 0:
            targets[pick["dificultad"]] -= 1

    return selected, ts_groups, covered_ts, targets


def build_config():
    return {
        "titulo": "Simulacro de examen CCAR-F",
        "version": "1.0",
        "bloque": "simulacro",
        "modo_defecto": "examen",
        "solo_examen": True,
        "duracion_examen_min": 120,
        "generado_desde_corpus": (
            "bloque-{0..5}-*.md v1.0 (simulacro agregado desde "
            "recursos/quiz/bloque-{0..5}/preguntas_v1.0.json)"
        ),
        "fecha": "2026-08-07",
    }


def validate_output(bank, per_block_selected):
    errors = []
    qs = bank["preguntas"]
    if len(qs) != 60:
        errors.append(f"expected 60 questions, got {len(qs)}")
    ids = [q["id"] for q in qs]
    if len(set(ids)) != len(ids):
        dupes = [i for i in ids if ids.count(i) > 1]
        errors.append(f"duplicate ids: {sorted(set(dupes))}")

    counts_by_block = Counter(q["bloque"] for q in qs)
    for b, quota in QUOTAS.items():
        got = counts_by_block.get(b, 0)
        if got != quota:
            errors.append(f"bloque {b}: expected quota {quota}, got {got}")

    # byte-identical check: every selected question must be found, unchanged,
    # in its source bank (compare canonical JSON of the exact same object).
    for b in BLOCK_ORDER:
        bank_b = load_bank(b)
        by_id = {q["id"]: q for q in bank_b["preguntas"]}
        for q in per_block_selected[b]:
            orig = by_id.get(q["id"])
            if orig is None:
                errors.append(f"{q['id']}: not found in source bloque-{b} bank")
            elif json.dumps(orig, sort_keys=True) != json.dumps(q, sort_keys=True):
                errors.append(f"{q['id']}: differs from source bank (not verbatim)")

    return errors


def main():
    rng = random.Random(SEED)

    per_block_selected = {}
    per_block_ts_info = {}
    for b in BLOCK_ORDER:
        selected, ts_groups, covered_ts, remaining_targets = select_block(b, rng)
        per_block_selected[b] = selected
        per_block_ts_info[b] = (ts_groups, covered_ts, remaining_targets)

    master = [q for b in BLOCK_ORDER for q in per_block_selected[b]]
    rng.shuffle(master)  # final deterministic exam order

    out_bank = {"config": build_config(), "preguntas": master}

    errors = validate_output(out_bank, per_block_selected)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(out_bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # ---- report ----
    print(f"OK: wrote {OUT_PATH} with {len(master)} questions (SEED={SEED})")
    print()
    print("Quota per block:")
    for b in BLOCK_ORDER:
        n_ts = len(per_block_ts_info[b][0])
        covered = len(set(per_block_ts_info[b][1]))
        print(f"  bloque {b}: {len(per_block_selected[b])}/{QUOTAS[b]}  "
              f"(task statements covered: {covered}/{n_ts})")
    print(f"  TOTAL: {sum(len(v) for v in per_block_selected.values())}")

    print()
    print("Task statement coverage per block:")
    for b in BLOCK_ORDER:
        ts_groups, covered_ts, _ = per_block_ts_info[b]
        counts = Counter(q["taskStatement"] for q in per_block_selected[b])
        missing = [ts for ts in ts_groups if ts not in counts]
        detail = ", ".join(f"{ts}:{counts.get(ts, 0)}" for ts in ts_groups)
        print(f"  bloque {b}: {detail}" + (f"  (uncovered: {missing})" if missing else ""))

    print()
    diff_counts = Counter(q["dificultad"] for q in master)
    print("Difficulty distribution (global target 22/56/22):")
    for d in DIFFICULTIES:
        n = diff_counts.get(d, 0)
        print(f"  {d}: {n} ({n / len(master):.1%})")

    print()
    print("All checks passed: 60 unique ids, quotas match, every question "
          "verbatim (byte-identical) vs its source bank.")


if __name__ == "__main__":
    main()
