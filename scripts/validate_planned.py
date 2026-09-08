#!/usr/bin/env python3
"""Validate planned_<domain>.json: every field is confidence-tagged; known/reported need a source."""
import json, re, sys, pathlib
DATE=re.compile(r"^\d{4}(-\d{2})?$"); CONF={"known","reported","inferred"}
STRUCT={"id","operator","schema","generated","note","confidence_legend","records"}
def check(path):
    d=json.loads(pathlib.Path(path).read_text()); errs=[]
    for i,rec in enumerate(d.get("records",[])):
        tag=rec.get("id",f"#{i}")
        if not rec.get("operator"): errs.append(f"{tag}: missing operator")
        for k,v in rec.items():
            if k in STRUCT: continue
            if not isinstance(v,dict) or "value" not in v:
                errs.append(f"{tag}.{k}: not a {{value,confidence,...}} object"); continue
            c=v.get("confidence")
            if c not in CONF: errs.append(f"{tag}.{k}: confidence {c!r} not in {sorted(CONF)}")
            if c in ("known","reported") and not v.get("source"): errs.append(f"{tag}.{k}: {c} without source")
            if c=="inferred" and not v.get("note"): errs.append(f"{tag}.{k}: inferred without note")
            if v.get("as_of") and not DATE.match(str(v["as_of"])): errs.append(f"{tag}.{k}: as_of not YYYY[-MM]")
    for e in errs: print("ERROR",e)
    print(f"{path}: {len(errs)} problem(s)")
    return 1 if errs else 0
if __name__=="__main__":
    rc=0
    for p in (sys.argv[1:] or ["data/planned_terrestrial.json","data/planned_orbital.json"]):
        if pathlib.Path(p).exists(): rc|=check(p)
        else: print(f"skip {p} (absent)")
    sys.exit(rc)
