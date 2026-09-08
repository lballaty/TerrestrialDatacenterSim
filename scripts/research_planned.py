#!/usr/bin/env python3
"""Refresh the planned-builds dataset for the AI Data Center models — runs LOCALLY, not in CI.

Calls an LLM with web search to compile planned / under-construction AI datacenters
(terrestrial) or space-based datacenters (orbital), and writes a confidence-tagged JSON
the tool loads. The API key is read from your shell environment and is NEVER committed
or shipped to the page (GitHub Pages only serves the resulting JSON).

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 scripts/research_planned.py terrestrial   # writes data/planned_terrestrial.json
    python3 scripts/research_planned.py orbital        # writes data/planned_orbital.json
    python3 scripts/research_planned.py both

Requires:  pip install anthropic     (and network access to the API)

Every field in the output is {value, confidence, source?, note?, as_of?}:
  known    = stated by the operator / an official or primary source (source URL required)
  reported = from press or analyst coverage (source URL required)
  inferred = our estimate from context (reasoning note required, no source)

The tool shows the 'generated' date prominently and treats the file as a lead list to
verify, not authoritative. Existing data files (jurisdictions, power_options, gp.json,
etc.) are untouched — this only writes data/planned_<domain>.json.
"""
import json, os, sys, datetime, pathlib

MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-4-6")
HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"

SCHEMAS = {
 "terrestrial": {
   "file": "planned_terrestrial.json", "schema": "planned-terrestrial/1.0",
   "fields": ["operator","site","region","it_mw","facility_mw","power_source","cooling",
              "compute","build_start","energization","full_buildout","investment","purpose","status"],
   "prompt": ("Compile a list of the largest PLANNED or UNDER-CONSTRUCTION terrestrial AI data centers "
              "worldwide (not yet fully operational, or ramping). For each: operator, site/campus name, "
              "region/grid, IT MW and/or facility MW, power source, cooling if known, compute (GPU counts/type), "
              "build start, energization/timeline, full buildout, investment, purpose, and status.")
 },
 "orbital": {
   "file": "planned_orbital.json", "schema": "planned-orbital/1.0",
   "fields": ["operator","program","satellites_planned","orbit","compute","interconnect",
              "first_launch","full_deployment","per_satellite_power","mass_kg","launch_vehicle","purpose","status"],
   "prompt": ("Compile a list of PLANNED or ANNOUNCED space-based (orbital) AI data centers / compute "
              "constellations. For each: operator, program/constellation name, satellites planned, orbit "
              "(altitude/inclination/type), compute (chips), inter-satellite/downlink, first launch, full "
              "deployment timeline, per-satellite power, mass, launch vehicle, purpose, and status.")
 },
}

INSTRUCTIONS = (
 "Use web search. Return ONLY a JSON array, no prose, no markdown fences. Each element is one project. "
 "Every field value must be an object: {\"value\":..., \"confidence\":\"known|reported|inferred\", "
 "\"source\":\"<url>\", \"as_of\":\"YYYY-MM\"} for known/reported (source REQUIRED), or "
 "{\"value\":..., \"confidence\":\"inferred\", \"note\":\"<why>\"} for inferred (no source). "
 "Omit a field entirely if you have nothing — never invent. Include an \"id\" (short slug) and \"operator\" "
 "(plain string) on each element. Prefer primary/official sources; mark press/analyst as reported; mark any "
 "estimate of yours as inferred with a one-line reason. Aim for 10-20 terrestrial or the known orbital projects."
)

def build(domain):
    try:
        import anthropic
    except ImportError:
        sys.exit("Install the SDK first:  pip install anthropic")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("Set ANTHROPIC_API_KEY in your environment (it is never committed).")
    spec = SCHEMAS[domain]
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model=MODEL, max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": spec["prompt"] + "\n\n" + INSTRUCTIONS}],
    )
    # collect text blocks
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip() if "```" in text else text
    try:
        records = json.loads(text)
    except json.JSONDecodeError as e:
        outp = DATA / (spec["file"] + ".raw.txt"); outp.write_text(text)
        sys.exit(f"Model did not return clean JSON ({e}). Raw saved to {outp} for inspection.")
    today = datetime.date.today().isoformat()
    bundle = {
        "schema": spec["schema"], "generated": today,
        "note": ("Planned/under-construction AI datacenters compiled from public reporting via LLM web search. "
                 "Every field carries a confidence tag. Lead list to verify, not authoritative. "
                 "Refresh with scripts/research_planned.py."),
        "confidence_legend": {"known": "operator/official/primary source",
                              "reported": "press or analyst coverage",
                              "inferred": "our estimate from context; not directly sourced"},
        "records": records,
    }
    DATA.mkdir(exist_ok=True)
    (DATA / spec["file"]).write_text(json.dumps(bundle, indent=1, ensure_ascii=False))
    print(f"wrote {DATA/spec['file']} with {len(records)} projects (generated {today})")

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    for d in (["terrestrial", "orbital"] if which == "both" else [which]):
        if d not in SCHEMAS: sys.exit(f"unknown domain {d!r}; use terrestrial | orbital | both")
        build(d)

if __name__ == "__main__":
    main()
