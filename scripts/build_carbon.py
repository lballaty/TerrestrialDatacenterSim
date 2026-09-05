#!/usr/bin/env python3
"""Fetch Ember's yearly electricity data and write a compact carbon-intensity bundle.

Output:
{ "fetched": ISO-8601, "source": "Ember Yearly Electricity Data", "licence": "CC BY 4.0",
  "rows": { "DE": {"gco2_kwh": 350, "renewable_share": 0.55, "year": 2024}, ... } }
Falls back to a previous bundle if the download fails. Stdlib only.
"""
import csv, io, json, sys, pathlib, urllib.request, datetime as dt

URL = "https://ember-energy.org/app/uploads/2022/07/yearly_full_release_long_format.csv"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/data/carbon.json")
FALLBACK = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "terrestrial-ai-dc-model/1.0 (github actions)"})
        with urllib.request.urlopen(req, timeout=300) as r:
            text = r.read().decode("utf-8", errors="replace")
        rows = {}
        for rec in csv.DictReader(io.StringIO(text)):
            iso = rec.get("ISO 3 code") or rec.get("Country code")
            if not iso or rec.get("Area type") not in (None, "Country"):
                continue
            try:
                year = int(rec["Year"])
            except (KeyError, ValueError):
                continue
            var, unit = rec.get("Variable"), rec.get("Unit")
            try:
                val = float(rec["Value"])
            except (KeyError, ValueError, TypeError):
                continue
            slot = rows.setdefault(iso, {})
            if var == "CO2 intensity" and unit == "gCO2/kWh":
                if year >= slot.get("year", 0):
                    slot["gco2_kwh"] = round(val); slot["year"] = year
            if var == "Renewables" and unit == "%" and rec.get("Category") == "Electricity generation":
                if year >= slot.get("ryear", 0):
                    slot["renewable_share"] = round(val / 100, 3); slot["ryear"] = year
        rows = {k: v for k, v in rows.items() if "gco2_kwh" in v}
        if len(rows) < 100:
            raise RuntimeError(f"suspiciously few countries: {len(rows)}")
        for v in rows.values():
            v.pop("ryear", None)
        bundle = {"fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                  "source": "Ember Yearly Electricity Data", "licence": "CC BY 4.0", "url": URL, "rows": rows}
        OUT.write_text(json.dumps(bundle, separators=(",", ":")))
        print(f"wrote {OUT} with {len(rows)} countries")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"fetch failed: {e}", file=sys.stderr)
        if FALLBACK and FALLBACK.exists():
            OUT.write_text(FALLBACK.read_text()); print(f"kept previous bundle from {FALLBACK}"); return 0
        return 1

if __name__ == "__main__":
    sys.exit(main())
