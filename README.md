# Terrestrial AI Data Center Siting and Economics Model

A single-file, zero-dependency browser tool that asks a narrow question: **given a location, build size, power-sourcing strategy, cooling architecture, redundancy tier, compute platform, served model and demand environment, what facility is required, when is it powered, what does it cost per installed MW and per delivered inference token — and how much of that answer rests on referenced data rather than assumptions?**

It is the terrestrial sibling of the [Orbital AI Data Center Economics Model](https://lballaty.github.io/OrbitalDatacenterSim/). The two share the same compute anchor (a 135 kW GB300-class rack), the same lifecycle cost spine and the same design, so a reader can price the same rack on the ground and in orbit with the same method. This one is standalone: the orbital tool keeps its own simplified terrestrial benchmark, and a self-test here reproduces that benchmark exactly.

Bottom-up, same discipline: what can be computed from physics or public data is computed; what cannot is a labelled baseline you are expected to override for a real project. Every input carries one of five labels — **anchor** (vendor/standards figure), **referential** (public dataset or curated jurisdiction record, dated and sourced), **baseline** (author's starting point where no reference exists), **scenario** (yours) or **derived** — and the results panel counts them, so nobody mistakes a baseline for a measurement.

**Live tool:** `https://<owner>.github.io/<repo>/`
**Specification:** [`terrestrial_datacenter_model_specification.md`](terrestrial_datacenter_model_specification.md) — scope, every formula, default, data layer, source and known limitation, with a revision table.

---

## What it models

| Area | What is derived | What you set |
|---|---|---|
| Site | jurisdiction record from the pin, provenance table, unresolved-field count | location preset (later: any lat/lon), scale regime, target MW, tier |
| Power | facility MW, energy and capacity charges by period, carbon, availability from tier and grid reliability; later: supply mix by period and time-to-power from the mix | tariff and trajectory, queue, interconnection cost, grid intensity; later: generation options incl. geothermal, hydro/nuclear contracts, SMR, micro-reactors, flexible interconnection |
| Climate & cooling | PUE from free-cooling hours, economiser and electrical losses; water use | cooling architecture, supply temperature, design wet-bulb, evaporative or dry |
| Land & construction | site and gross area, composed CAPEX stack (land, shell, MEP, cooling, interconnection, fit-out, fibre, soft, contingency), incentives | $/m², $M/MW, construction index, ratios; or a single $/MW for parity |
| Compute | installed units, IT MW, throughput, refresh; later: platform × model matrix, cohorts and cascade, residual-value curves | anchor row (GB300), spares, utilization, refresh interval; later: catalog choices |
| Lifecycle | present value with trajectories, annualized cost, $/1M tokens, $/GPU-hour, facility $/kW-month | horizon, discount, itemised opex; later: financing block |
| Timeline | time-to-power with the binding term named (queue, permit, build, long-lead item) | permitting, design, construction, longest equipment lead; later: full lead-time list and risk register |
| Environment | tCO₂/yr, gCO₂ and litres per 1M tokens | grid intensity trajectory, carbon price |

Plus a ±20% sensitivity tornado that includes the looked-up location values, a break-even solver (to a target $/1M tokens or months to power), scenario JSON with provenance, in-file self-tests, and the specification in a modal or its own window.

## Quick start

1. Open `index.html` in any modern browser — desktop or phone. No install, no network required.
2. Pick a location preset on the **Site** tab. The default is a 40 MW direct-liquid-cooled Tier III hall in Northern Virginia on grid power.
3. Read **Model cautions** first — it names the binding constraint and anything the design violates.
4. Edit any looked-up value; it turns *scenario* in the provenance table and the badge count changes. **Reset base scenario** restores the preset.
5. **Run self-tests** (button, or `?test` in the URL): arithmetic anchors, orbital parity ($0.247 / 1M tokens on the orbital stub inputs), CAPEX-stack composition, layout overflow.
6. **Specification** in the top bar opens the spec (loads automatically on GitHub Pages; from disk, pick the `.md` when prompted).

## Data layers

The page runs from its embedded presets with no network. On GitHub Pages the workflow publishes `data/` bundles beside the HTML, and the tool uses them when present:

| File | Built by | Source | Refresh |
|---|---|---|---|
| `data/jurisdictions.json` | hand-curated, committed | per-record source URLs | as changed; CI validates every value has a label, date and source |
| `data/carbon.json` | `scripts/build_carbon.py` | Ember yearly electricity data (CC BY 4.0) | monthly |
| `data/ixp.json` | `scripts/build_ixp.py` | PeeringDB | monthly |
| `data/climate_grid.json` | `scripts/build_climate_grid.py` | ERA5 via Copernicus CDS (needs a free `CDS_TOKEN` secret) | when the script changes |
| `data/power_options.json`, `platforms.json`, `models.json`, `leadtimes.json` | hand-curated, committed | per-record source URLs | as changed |

Open-Meteo is used only for the optional exact-point refinement button, never for the grid: its call weighting makes a global hourly pull impractical on the free tier (spec §2.1 #8).

If a fetch fails the workflow keeps the previously published bundle, so the site never regresses to no data; if nothing has ever been published the page degrades to its embedded presets and says so.

## Hosting your own copy

1. Fork or push this repo. In **Settings → Pages**, set *Source* to **GitHub Actions**.
2. Optionally add a `CDS_TOKEN` repository secret (free Copernicus account) to build the climate grid; without it the step is skipped and presets remain in force.
3. Push to `main` or run the workflow manually. `.github/workflows/pages.yml` validates the curated files, builds the bundles, assembles `site/` and deploys it.

Nothing about the tool itself needs GitHub: the HTML runs from any static host or from disk.

## Reading the results honestly

- At current accelerator prices compute is most of lifecycle cost, so location moves $/1M tokens far less than it moves **time-to-power**. Compare sites on both.
- Interconnection queues in the seed set are published medians and vary by substation; treat them as a starting point. Where the queue is long, the supply-mix options (step 5) are the realistic path, not the queue.
- Referential values are dated snapshots. The provenance table tells you how many of a site's inputs are referenced, baseline or yours.
- Derived PUE depends on a free-cooling fraction that is a baseline per preset until the ERA5 grid is published.
- The tool takes no position on financial reporting: compute depreciation is economic (later, from residual-value curves), and accounting life is a footnote.

## Repository layout

```
index.html                                        the tool (single file)
terrestrial_datacenter_model_specification.md     scope, formulas, defaults, data layers, sources, limitations, revisions
data/jurisdictions.json                           curated jurisdiction records (schema in spec §7)
scripts/validate_curated.py                       CI check: label, date, source on every curated value
scripts/build_carbon.py                           Ember → carbon.json
scripts/build_ixp.py                              PeeringDB → ixp.json
scripts/build_climate_grid.py                     ERA5 via CDS → climate_grid.json
.github/workflows/pages.yml                       validate, build bundles, deploy to Pages
```

## Versioning

The tool's version is in its `<title>` and in the *Model integrity notes* footer; the specification carries a matching revision table. File names never change between versions so links and re-uploads stay stable.

## Sources

Lenovo GB300 NVL72 · NVIDIA and MLPerf inference results · ASHRAE design conditions · Uptime Institute tier definitions · ERA5 (Copernicus) · Ember · ENTSO-E / EIA · PeeringDB · GEM and JRC hazard layers · WRI Aqueduct · Turner & Townsend data centre cost index · per-jurisdiction sources in `data/jurisdictions.json`. Full list with URLs in the specification.

## Licence

Choose one before publishing (MIT is the usual fit). ERA5 is under the Copernicus licence, Ember under CC BY 4.0, PeeringDB under its terms; all require attribution, which the tool shows.
