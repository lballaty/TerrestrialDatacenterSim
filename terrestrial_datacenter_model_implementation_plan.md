# Terrestrial AI Data Center Model — Implementation Plan

**Plan revision 1.1 — 2026-09-05 — Status: Draft for review**
Rev 1.1 adds WP9 (graphical models) and WP10 (floating/underwater/mountain-pumped-hydro siting archetypes) to the queue, after the testing files.
Governs: `index.html` from v0.4 onward, `data/*.json`, `scripts/`, spec Rev 0.7 onward.
Companion: `terrestrial_datacenter_model_specification.md` (what the model is). This document says how it gets built, in what order, and when each step is done.

---

## 1. Ground rules

1. **One work package per delivery.** Zip named `terrestrial-vX.Y-<wp-slug>.zip`, containing only changed files in repo layout. Version bumped in `<title>`, footer integrity notes, scenario JSON `version`, and a row in the spec revision table. File names never change.
2. **Done means:** all self-tests pass headlessly (jsdom), regression anchors unchanged (§7), the sanity table (§8) re-run and pasted into the delivery note, spec and README updated in the same zip if the change touches them.
3. **Standing decisions (§5) apply without asking.** Open questions (§6) are resolved by me and recorded in the delivery note unless you pre-empt them.
4. **Labels are load-bearing.** Every new input gets a type badge (anchor / referential / baseline / scenario / derived) and, if baseline, a tooltip note with the reasoning. Every new curated value goes through `validate_curated.py`.
5. **Testability.** Every new interactive element and readout gets `data-test-*` tags (id, kind, tab, label) at load, as in v0.3; WP8 adds the manifest and reconcile script in the shared convention.
6. **No silent modeling changes.** A change that moves a regression anchor is either a bug or an intended model change; intended ones get a spec revision row and a new anchor value.
7. **Mobile and rendered layout are your check.** I test logic headlessly; I cannot see CSS layout. Each delivery asks for one phone pass.

## 2. Module map (inside `index.html`)

The file stays single and dependency-free, but its script is organised in named blocks so later WPs touch known regions:

| Block | Contents | Owner WP |
|---|---|---|
| `helpers` | `$`, `n/sv` with `OV`, `fmt/money`, `pvFactor`, `crf`, `wright`, `haversineKm`, `wetBulbStull`, `salvage` | done |
| `sites` | `SITES`, `SITE_MAP`, `LABEL_MAP`, custom sites, jurisdiction ↔ preset conversion, `loadCurated()` | done; WP3 extends loader to all catalogs |
| `location` | map pin, climate-grid lookup and interpolation, IXP nearest, hazard classes | WP3 |
| `power` | `POWER_OPTIONS`, `TEMPLATES`, `MIX`, `dispatchYear`, `firstFirmMonth`, LCOE | done; WP3 loader; WP7c trajectories |
| `compute` | `PLATFORMS`, `MODELS`, `THROUGHPUT`, derived throughput, refresh by granularity, residual curves | WP6 |
| `fleet` | cohorts, cascade, capacity allocation | WP7a |
| `demand` | demand trajectory, addressable share, capture, derived utilization | WP7b |
| `risk` | register, expected-value adjustments, risked/unrisked | WP7c |
| `spine` | `calc()` — CAPEX stack, period loop, PV, outputs | all WPs, edited in place |
| `compare` | multi-site and platform×model comparison, business case, financing | WP7d |
| `ui` | tabs, tornado, break-even, scenario JSON, self-tests, spec viewer, test tags | each WP adds |

`calc()` is the only place the period loop lives. Modules expose pure functions that `calc()` calls; no module writes to the DOM except `ui`.

## 3. Work packages

### WP3 — Location layers and catalog loaders (v0.5)

**Files:** `index.html`, `scripts/build_hazard.py` (new), `scripts/build_resources.py` (new), `data/resources.json` seed (curated stub for the 10 sites), README data-layer table.

**Adds**
- Map pin: Leaflet from CDN (fallback: lat/lon inputs only if CDN unreachable; page must still work offline). Dragging the pin sets lat/lon; on drop, resolve: nearest embedded/curated site by haversine (< 300 km → adopt its Layer B, label as that jurisdiction; else → all Layer B unresolved, red flag), climate from grid if loaded else nearest site's climate values labelled baseline.
- Climate grid wiring: fetch `./data/climate_grid.json` when served; bilinear interpolation of the four cells; derived `ffree` from `h_econ`/`h_dry` at (supply temp − approach); `twb` from `Twb_99.6`; `trend_K_per_yr` seeds the wet-bulb trajectory. Label flips referential when the grid supplies the value.
- Catalog loaders: `./data/power_options.json` overrides the embedded `POWER_OPTIONS`; `./data/resources.json` overrides site resource fields; `./data/carbon.json` overrides `ci` by country; `./data/ixp.json` supplies nearest-IXP km. All same-origin fetch → embedded fallback, status line names the source in force.
- Hazard: seismic and flood class per site (curated stub now, grid later) → shell multiplier (1.00/1.03/1.06/1.10/1.15) and site-prep multiplier (1.0/1.15/1.35) and a flood warning above class 2.
- Saved mixes: name, save in browser, export/import JSON (same pattern as custom sites).

**Inputs added:** `seismicClass` (select 0–4, baseline), `floodClass` (select 0–2, baseline), `supplyTemp` °C and `approachK` (baseline; drive `ffree` when the grid is present).
**Outputs added:** location status line (which layers resolved from what), nearest-site name and distance for a free pin.
**Self-tests added:** (a) ocean pin → 0 referential Layer B, tool computes; (b) bilinear interpolation reproduces a cell value at its centre; (c) `ffree` from a synthetic `h_econ` table matches hand calculation; (d) loader precedence: curated file overrides embedded row of the same id.
**Anchors:** unchanged (grid absent in test).

### WP6 — Compute platforms, models, throughput, refresh, residuals (v0.6)

**Files:** `index.html`, `data/platforms.json` (new, 11 rows), `data/models.json` (new, ~10 rows), `data/throughput.json` (new, referential cells only), `data/leadtimes.json` (new), spec §4a/§4b/§13.2 marked implemented.

**Adds**
- Platform selector on Compute tab; the GB300 anchor row becomes `PLATFORMS[0]`. Fields per spec §4b.1. Selecting a platform sets `rkw`, `gpus`, `rcost`, `rackm2`, granularity, cooling requirement, lead/allocation, maturity, residual curve, export flags. All remain editable (scenario relabel).
- Model selector (Model & Workload tab, new); regime selector (own-model / third-party open-weight / lessor / enterprise / mixed) with the licence line and R&D allocation line in opex.
- Throughput: `tpsmw` becomes derived from `THROUGHPUT[platform][model]` if a referential cell exists, else from §4b.3 formula with a maturity factor; badge shows which. Manual override retained.
- Refresh by granularity (§13.2): rack / server / component cost and fit-out at each refresh.
- Residual-value curves (three bands) replace straight-line salvage for compute; selector hold-to-refresh / rotate-and-resell (sell month input). Legacy straight-line mode retained for parity.
- Lead-time list: transformer, switchgear, generation units (from mix), chillers/CDUs, UPS/BESS, accelerators (from platform), HBM/DRAM, air permit, fuel agreement. Each: order month default, lead, expedite premium/months. Critical path recomputed; Gantt-style SVG bar list (container-width, mobile-safe).
- Trade layer: import duty % by class from jurisdiction record applied to compute/electrical/mechanical CAPEX; export-control check platform × jurisdiction → warning or block.

**Inputs added:** `platform`, `model`, `regime`, `maturity`, `residualBand`, `refreshStrategy`, `sellMonth`, `licenceFee`, `rdAlloc`, per-lead-item order/lead/expedite (≈9×3), `dutyAccel`, `dutyElec`, `dutyMech`.
**Outputs added:** throughput provenance badge, refresh cost table over horizon, residual credit total, critical-path Gantt with binding item, duty total.
**Self-tests added:** (e) derived cell GB300 × Llama-class within ±30% of the referential 2.8M cell; (f) server refresh < rack refresh for the same family; (g) 30-month transformer with 12-month queue → binding = transformer; (h) straight-line legacy mode reproduces parity; (i) hold vs rotate both compute, delta reported; (j) 25% accelerator duty raises compute CAPEX by exactly 25% × compute share.
**Anchors:** parity via legacy mode; composition unchanged; base US-VA regression **re-anchored** (residual curve mid band replaces straight-line) — new value recorded in the delivery note and spec §22.

### WP7a — Cohorts and cascade (v0.7)

**Adds:** cohort table (platform, units, install month, cascade stages `{model class, months}`), retirement rule selector (interval / residual floor / throughput floor / never with rising failure and maintenance), MW allocation by cohort over the horizon (stacked SVG), tokens by model class. Default: one cohort, one stage — identical to WP6 behaviour.
**Self-tests:** (k) default cohort reproduces WP6 result; (l) two-cohort cascade case computes and reports deltas; (m) capacity constraint: total cohort MW never exceeds facility MW.

### WP7b — Demand module (v0.8)

**Adds:** global demand trajectory, population weights per must-reach metro (embedded), latency budget → addressable share, capture and ramp → derived utilization per period; reverse mode (MW to serve target share); demand split by model class for the cascade. Toggle off by default.
**Self-tests:** (n) module off reproduces prior result; (o) capture 0 → utilization 0 and a warning; (p) reverse mode round-trips.

### WP7c — Risk register and trajectories UI (v0.9)

**Adds:** register table (nine risks, triples, jurisdiction baselines where recorded), Representation A expected-value adjustments, unrisked/risked side-by-side with per-risk attribution; trajectory editor for tariff, carbon, water, grid intensity, wet-bulb, model price, accelerator cost (constant or start + %/yr); community-benefit payment lowering opposition probability.
**Self-tests:** (q) risked − unrisked = Σ attributions; (r) all probabilities 0 → identical results; (s) trajectories all 0 → parity intact.

### WP7d — Comparison, business case, financing (v1.0)

**Adds:** site comparison (up to four pins, identical non-location inputs, provenance counts), platform × model table (rows platforms, columns models + lease-to-vendor), business-case toggle (market price, margin, break-even utilization, payback), financing toggle (§13.3 PropCo/ComputeCo, IDC, WACC replaces discount rate). Both toggles off by default.
**Self-tests:** (t) toggles off reproduce v0.9; (u) financing with 0% debt reproduces all-equity; (v) comparison table diagonal equals single-scenario result.

### WP8 — Test system and release (v1.0.x)

**Files:** `terrestrial-test-cases.json` (manifest: every control with kind, tab, validity rules, expected direction; readouts; suites; reasonableness rules), `terrestrial-reconcile.js` (DOM tags vs manifest, wired into self-tests), `terrestrial-test-plan.md`, indexes regenerated from the DOM. README and spec final sync. Licence chosen (your call). GitHub Pages workflow first live run; fix whatever the Ember/PeeringDB/CDS scripts break on.

### WP9 — Graphical models (visual subsystem) (v1.1)

Parity with the orbital tool's visual layer, which this app deferred. Same house style, hand-rolled canvas/SVG (no map/3D library unless a later decision adds one), mobile-safe, pop-out windows following the parent scenario via postMessage as the orbital tool does.

**Views**
1. **Location zoom.** Pin on a coarse world map (reuse the orbital tool's Natural Earth 110m coastline asset) that zooms from global → region → site, driven by the Site tab lat/lon. Overlays toggled from the resolved layers: grid-carbon shading, water-stress, seismic/flood class, nearest IXPs, and (when present) the climate cell.
2. **Above-site view (plan).** A top-down schematic of the facility footprint at the current design: white-space halls, MEP/cooling yards, substation, on-site generation and BESS blocks, water/heat-reuse plant, fibre entry, laid out to the computed `siteA`/`grossA` with a scale bar. Blocks sized from the model (units, cooling architecture, mix rows), not fixed art.
3. **Datacenter build-up (assembly).** A staged section/exploded view showing how the facility "comes together" by design choice: shell → power path (grid/mix) → cooling architecture (air/RDHx/DLC/immersion drawn differently) → racks/rows → network. Steps gated on the timeline so the drawing reflects energisation phase (campus) and the binding constraint.
4. **Scenario-specific renderings** for the WP10 siting types (below).

**Data-driven fidelity rule** (as orbital §3.5): every drawn dimension traces to a model value; a caption states scale and any clamp. The visual never feeds back into the calculation.

**Tests:** extend the manifest with a `render_surfaces` registry and view-selector/pop-out buttons; S6-style suite asserting each view renders without error and redraws on input; tag every new control. No pixel oracle (brittle) — structural assertions only.

### WP10 — Non-standard siting scenarios (v1.2)

New site *archetypes* selectable on the Site tab, each adding its own inputs, power-mix eligibility, cost and risk terms, and a WP9 rendering. All bottom-up and labelled; each is a scenario the model can price, not a claim it is sensible.

**10a. Floating / offshore (surface).** Barge or platform hull instead of land+shell. Adds: hull/platform $/MW (replaces land+site-prep+shell), station-keeping/mooring, marine construction index, corrosion/maintenance uplift, motion-tolerant cooling (seawater once-through or closed loop → very low WUE, new heat-rejection term), subsea power and fibre landing distance and cost, cyclone/wave downtime, jurisdiction = flag state / EEZ (new Layer B edge cases). Power: seawater cooling sets κ near air-free; grid via subsea cable or on-board generation.
**10b. Submerged / underwater.** Sealed vessel on the seabed (Natick-style). Adds: pressure-vessel $/MW, deployment/recovery vessel cost and cadence (no in-situ service → whole-vessel refresh, ties to §13.2 granularity), nitrogen/sealed reliability factor (lower failure), seawater heat rejection (WUE ~0), cable length to shore, recovery risk. Compute refresh = vessel swap; availability model changes (no hands-on repair).
**10c. Mountain / pumped-hydro-coupled.** Site paired with a pumped-storage loop: upper and lower reservoir, elevation head, usable volume → stored MWh; pump/turbine $/MW and round-trip efficiency; solar or wind (from the resource layer) charges by pumping uphill. Adds a storage option to the power mix that is **energy-limited by reservoir volume and head**, not just MWh nameplate: firm hours = ρghV·η / P. Terrain/civil cost for reservoirs, water rights, environmental permitting (longer, higher risk). This makes the §8 dispatch genuinely energy-constrained and is the most interesting power case.

**Model touch-points:** each archetype extends the CAPEX stack (§10.2) with its structure term replacing land/shell, adds power-mix rows and eligibility (seawater cooling, pumped hydro), adds risk-register rows (marine, recovery, dam), and sets cooling defaults (seawater → near-zero WUE and low κ). Parity mode and all anchors remain reachable by selecting the ordinary land archetype.

**Tests:** each archetype gets a smoke case (selects, computes, no NaN), a reasonableness rule (e.g. pumped-hydro firm hours = ρghVη/P within tolerance; submerged WUE ≈ 0), and its rendering asserted in the WP9 suite.

## 4. Order and estimated size

| WP | Version | New inputs | Approx. lines added | Depends on |
|---|---|---|---|---|
| 3 | 0.5 | ~6 + loaders | 350 | — |
| 6 | 0.6 | ~40 | 700 | 3 (loaders) |
| 7a | 0.7 | ~10 + table | 350 | 6 |
| 7b | 0.8 | ~8 | 250 | 7a |
| 7c | 0.9 | ~30 | 400 | — |
| 7d | 1.0 | ~15 | 500 | 6, 7b |
| 8 | 1.0.x | 0 | manifest | all |
| 9 | 1.1 | ~10 + views | 700 | 6, 7d (drawings read final model state) |
| 10 | 1.2 | ~30 | 600 | 9 (each archetype needs its rendering) |

`index.html` will reach roughly 3,500 lines at v1.0 — comparable to the orbital tool. If it becomes unwieldy the fallback is a second file for curated catalogs loaded at start; the single-file default stands unless you say otherwise.

## 5. Standing decisions (recorded; apply without asking)

1. Backup gensets are a mix row, not part of MEP. MEP baseline 6.3 $M/MW excludes them.
2. Unserved load is priced at 3× tariff and flagged red; the tool never silently ignores a shortfall.
3. Variable-source firmable share = 30% + storage MWh ÷ (variable MW × CF × 14 h), capped at 1 — a baseline standing in for hourly dispatch until a weather-year model exists.
4. Eligibility: gas rows need gas access; geothermal needs class ≥ 2 (EGS ≥ 1); hydro/plant contracts need contractable MW > 0; nuclear rows need policy = allowed. Ineligible rows are greyed with the reason, never hidden.
5. Templates auto-resize to facility load whenever the template selector is not "custom"; sizes divide by firmness so firm MW ≥ load.
6. Contract rows price relative to tariff (PPA 0.85, hydro 0.8, nuclear 1.0) until a curated price exists.
7. Loader precedence: curated same-origin file > embedded row of the same id; new ids from the file are added; the status line names the source in force.
8. Interconnection application runs in parallel with permitting unless `queue_requires_permits_first`; equipment is ordered at project start unless an order month is set.
9. Parity mode (single $/MW, single % opex, manual PUE, manual availability, straight-line salvage, grid-only mix, a = 0) is preserved in every version; the parity self-test is never removed.
10. Anything with no reference gets label *baseline* and a note; nothing is labelled referential without a URL.
11. Trajectories apply in the period loop only; year-1 tables show year-1 values.
12. Currency: all curated values stored in USD with the record's `fx_to_usd` and date; the tool displays USD only in v1.

## 6. Open questions (I resolve unless you object beforehand)

| # | Question | My default |
|---|---|---|
| 1 | Leaflet from CDN, or hand-rolled equirectangular canvas with the Natural Earth coastlines already used by the orbital tool? | Hand-rolled canvas — zero dependency, consistent with the orbital tool, works offline; Leaflet only if you want street-level zoom. |
| 2 | Which open-weight models seed `models.json`? | Llama 4 Maverick & Scout, DeepSeek V3 & R1, Qwen3-235B-A22B & Qwen3-32B, Mistral Large 3, gpt-oss-120b, Kimi K2 — nine rows plus three proprietary lease-only rows. |
| 3 | Platform rows that are cloud-only (TPU, Trainium): show with a "not purchasable" badge or omit? | Show, badge, exclude from third-party regimes. |
| 4 | Residual bands for GB300 with no history? | Hopper curve shifted 12 months later; labelled baseline. |
| 5 | Regression anchor after WP6 re-anchoring: keep straight-line as the reported default or the mid residual curve? | Mid residual curve as default; straight-line kept for parity only. |
| 6 | Licence for the repo | MIT, as the orbital README suggests. |
| 7 | Map for the location-zoom view (WP9): hand-rolled canvas on the orbital Natural Earth asset, or a tile library (Leaflet)? | Hand-rolled, zero-dependency, consistent with the orbital tool; tiles only if street-level zoom is wanted. |
| 8 | Underwater/floating jurisdiction resolution (WP10): flag state, coastal state, or nearest-landfall? | Nearest coastal state's Layer B with a marine-uplift flag, overridable; a full maritime-law model is out of scope. |

## 7. Regression anchors (must not move without a spec row)

| Anchor | Value | Since |
|---|---|---|
| Orbital parity, stub inputs | $0.2473 / 1M tokens (±0.2%) | v0.2 |
| §10.2 composition, US avg, Tier III, air, grid-only | $12.14M / MW IT (±5%) | v0.2 |
| LCOE closed form, recips 90% CF, $40 gas, 8% | $111.7 / MWh | v0.4 |
| Base US-VA, 40 MW DLC Tier III, grid template, GB300×Llama4-Maverick, mid residual | **$0.161 / 1M tokens**; TTP 42 mo; PUE 1.144; facility $12.21M/MW | re-anchored at v0.8 (WP6); was $0.234 under straight-line |

## 8. Sanity table (re-run every delivery)

Ten sites × grid template: $/1M tokens, CAPEX/MW, TTP and binding term, PUE, gCO₂/1M tokens. Plus templates: Dublin bridge, Reykjanes geo, Luleå hydro, Abu Dhabi solar hybrid, Frankfurt CCS, Virginia nuclear. Any row that moves more than 2% without an intended change is investigated before delivery.

## 9. Delivery note format

Version · files changed · what was added (inputs, outputs, tests) · anchors and sanity table · standing decisions applied · open questions resolved · review flags · request for phone check.

## 11. Queued (added 2026-09-05, build after testing files)

- **WP9 graphical models** — location zoom, above-site plan, build-up/assembly view, per-scenario renderings; parity with the orbital visual subsystem this app deferred.
- **WP10 siting archetypes** — floating/offshore, submerged/underwater, and mountain pumped-hydro-coupled sites, each with its own cost/power/risk terms and rendering. The pumped-hydro case turns the §8 dispatch into a genuinely energy-limited model (firm hours from reservoir head and volume).

## 12. Out of scope for this plan

Hourly dispatch and weather-year sampling; sub-national polygons; Monte Carlo risk (Representation B); training workloads; embodied carbon; tax structuring beyond the financing block. Each is a later plan revision if wanted.
