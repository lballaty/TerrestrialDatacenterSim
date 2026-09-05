#!/usr/bin/env python3
"""Validate curated data files for the terrestrial model.

Rules (spec §3.3, §7): every leaf value carrying economic or regulatory meaning is an
object {value, label, source_url, as_of} where label ∈ {referential, baseline}. A
referential value must have a non-empty source_url; a baseline must have a note or a
non-empty source_url explaining the reasoning. Dates are YYYY or YYYY-MM.
Exit 1 on any violation; prints each one. Stdlib only.
"""
import json, re, sys, pathlib

DATE = re.compile(r"^\d{4}(-\d{2})?$")
LABELS = {"referential", "baseline"}
STRUCTURAL_KEYS = {"id", "name", "parent", "currency", "note", "notes", "aliases", "tariff_structure", "scheme",
                   "data_sovereignty_constraints", "export_control_class", "status", "granularity", "firmness",
                   "cooling", "dependency", "licence", "purchasable", "interconnect", "unit", "seed_rows",
                   "schema", "generated", "as_of", "eu_ai_act_gpai_relevance", "source_url", "label"}

def leaf_ok(path, v, errors):
    if isinstance(v, bool) or v is None:
        return
    if isinstance(v, (int, float, str)):
        errors.append(f"{path}: bare value {v!r} — wrap as {{value,label,source_url,as_of}}")
        return
    if isinstance(v, list):
        for i, x in enumerate(v):
            walk(f"{path}[{i}]", x, errors)
        return
    if isinstance(v, dict) and "value" in v:
        lab = v.get("label")
        if lab not in LABELS:
            errors.append(f"{path}: label {lab!r} not in {sorted(LABELS)}")
        if lab == "referential" and not v.get("source_url"):
            errors.append(f"{path}: referential value without source_url")
        if lab == "baseline" and not (v.get("note") or v.get("source_url")):
            errors.append(f"{path}: baseline value without note or source_url")
        if not DATE.match(str(v.get("as_of", ""))):
            errors.append(f"{path}: as_of {v.get('as_of')!r} not YYYY or YYYY-MM")
        return
    walk(path, v, errors)

def walk(path, obj, errors):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in STRUCTURAL_KEYS:
                continue
            leaf_ok(f"{path}.{k}", v, errors)
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            walk(f"{path}[{i}]", x, errors)

def main(paths):
    total = 0
    for p in paths:
        f = pathlib.Path(p)
        if not f.exists():
            print(f"skip {p} (not present yet)")
            continue
        data = json.loads(f.read_text())
        errors = []
        walk(f.stem, data, errors)
        for e in errors:
            print(f"ERROR {e}")
        print(f"{p}: {len(errors)} problem(s)")
        total += len(errors)
    return 1 if total else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["data/jurisdictions.json"]))
