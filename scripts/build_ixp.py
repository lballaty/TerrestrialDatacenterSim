#!/usr/bin/env python3
"""Fetch PeeringDB internet exchanges (with facility coordinates) and write a point set.

Output: { "fetched", "source": "PeeringDB", "count", "recs": [[name, city, country, lat, lon, participants], ...] }
PeeringDB's public API is rate-limited for anonymous use; set PEERINGDB_API_KEY in the environment
to raise the limit. Falls back to a previous bundle on failure. Stdlib only.
"""
import json, os, sys, pathlib, urllib.request, datetime as dt

IX_URL = "https://www.peeringdb.com/api/ix?status=ok"
FAC_URL = "https://www.peeringdb.com/api/fac?status=ok"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/data/ixp.json")
FALLBACK = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None

def get(url):
    h = {"User-Agent": "terrestrial-ai-dc-model/1.0 (github actions)", "Accept": "application/json"}
    key = os.environ.get("PEERINGDB_API_KEY")
    if key:
        h["Authorization"] = f"Api-Key {key}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=300) as r:
        return json.load(r)["data"]

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        facs = {f["id"]: f for f in get(FAC_URL) if f.get("latitude") and f.get("longitude")}
        # facility → city centroid fallback for IXes with no located facility
        recs = []
        for ix in get(IX_URL):
            lat = lon = None
            for fid in ix.get("fac_set", []) or []:
                f = facs.get(fid if isinstance(fid, int) else fid.get("id"))
                if f:
                    lat, lon = f["latitude"], f["longitude"]; break
            if lat is None:
                continue
            recs.append([ix.get("name", ""), ix.get("city", ""), ix.get("country", ""), round(lat, 3), round(lon, 3), ix.get("net_count", 0)])
        if len(recs) < 200:
            raise RuntimeError(f"suspiciously few IXPs located: {len(recs)}")
        bundle = {"fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "source": "PeeringDB", "count": len(recs), "recs": recs}
        OUT.write_text(json.dumps(bundle, separators=(",", ":")))
        print(f"wrote {OUT} with {len(recs)} IXPs")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"fetch failed: {e}", file=sys.stderr)
        if FALLBACK and FALLBACK.exists():
            OUT.write_text(FALLBACK.read_text()); print(f"kept previous bundle from {FALLBACK}"); return 0
        return 1

if __name__ == "__main__":
    sys.exit(main())
