# Terrestrial AI Data Center Siting and Economics Model

**Modeling Tool Specification — Revision 0.7**
Companion tool: `index.html` (repository root; not yet built)
Status: **Draft** — scope and parameter map for review before implementation
Base compute unit: 135 kW / 72-GPU GB300-class rack (identical to the orbital model), now one row of a platform catalog (§4b)
Scope: inference workloads only; new-build facilities; grid-connected or with on-site generation. Training, retrofits and colocation resale pricing beyond a lease benchmark are out of scope (§22).
Sibling model: Orbital AI Data Center Economics Model, Specification Rev 0.3 — the two share the economic spine (§13) and the GB300 compute anchor; this one is standalone and does not feed the orbital tool.

---

## 1. Purpose

The model answers:

> Given a location, build size, power-sourcing strategy, cooling architecture, redundancy tier, compute platform, served model, demand environment and regulatory setting, what facility is required, when is it powered, what does it cost per installed MW and per useful inference token, and what energy, water and carbon does it consume — and how much of that answer rests on referenced data versus stated baselines?

Bottom-up, same discipline as the orbital model: what can be computed from physics or public data is computed; what cannot is a labelled baseline the user is expected to override for a real project. **Location is a first-class input** resolved from a coordinate (§5). **Time-varying quantities are trajectories, not constants** (§5.5). The tool must survive disagreement: a reader changes the disputed input, not the code.

## 2. Revision history

### 2.1 Revision 0.7

| # | Change | Rationale |
|---|---|---|
| 26 | Derived LCOE per generation option at the pinned site, delivered-cost comparison against the grid tariff, and hybrid mix templates with a firm-capacity dispatch rule (§8a.1, §8c.1) | Options were listed with cost ingredients but no levelised cost; hybrids (gas + storage, solar + gas, wind + storage + peaker) are the realistic on-site configurations and need a firmness accounting, not a sum of nameplates. |
| 27 | Modern gas rows split: aeroderivative turbine, fast-start recips, CCGT, CCGT with carbon capture, hydrogen-ready turbines (§8a) | Cost, lead time, efficiency and carbon differ enough to change the answer; "gas" as one row hid it. |
| 29 | Tool v0.4 (step 5): catalog of 21 generation options with site LCOE, resource-layer stub per site (solar/wind CF, geothermal class, gas access, contractable hydro/plant MW, nuclear policy, gas price), seven resource-aware supply-mix templates sized by firmness, merit-order dispatch per operating year producing firm-equivalent $/MWh and gCO₂/kWh that feed the spine, on-site generation capex in the stack, time-to-power from the mix as a candidate binding term; `data/power_options.json` mirrors the catalog | Implements §8a–8d and §8c.1. Unserved load is priced at 3× tariff as a visible penalty rather than silently ignored. Backup gensets moved from the MEP baseline into the mix. |
| 28 | Tool v0.3: custom sites saved in browser, export/import as jurisdiction-style JSON, curated `data/jurisdictions.json` replaces embedded presets when served, `data-test-*` tags on every interactive element and readout (shared testability convention) | Presets seed, they do not constrain; agent-testable UI from the first build. |

### 2.2 Revision 0.6

| # | Change | Rationale |
|---|---|---|
| 24 | Fleet cohorts with cascade paths and per-cohort retirement rules (§13.4) | Economic lifecycle must be configurable: a cohort may be kept beyond refresh, moved to lighter models while new hardware serves heavy ones, or run to failure. The facility's fixed MW is the constraint the cascade competes for. |
| 25 | UI: same design system as the orbital tool (CSS, panel and input-row markup, footer, self-test and spec modals lifted from its `index.html`); responsive single-column layout below ~700 px (§3.5) | Continuity across the two tools; the orbital page is not mobile-usable. |

### 2.3 Revision 0.5 — research pass before build

| # | Change | Rationale |
|---|---|---|
| 18 | Optional financing block: PropCo / ComputeCo debt share, rate, tenor, interest during construction; per-jurisdiction cost-of-capital baseline (§13.3) | Projects are financed in split structures with debt arriving early; cost of capital differs by jurisdiction and asset class. All-equity remains the default comparable case. |
| 19 | Accelerator residual-value curves (three bands, dated) and refresh strategy selector hold-to-refresh / rotate-and-resell (§13.2) | Straight-line salvage misstates the largest variable in compute TCO; secondary-market data now exist (H100 36-month mid-case 50–60%). |
| 20 | Flexible / non-firm interconnection as a power option: queue reduction, curtailment hours → availability, workload-flexibility fraction (§8a, §8e) | FERC June 2026 large-load orders and a growing share of large-load tariffs offer speed for flexibility. |
| 21 | Trade layer: import duty % by equipment class and export-control class per jurisdiction; platform export-restriction flags; duty as a trajectory (§7, §4b.1, §10.2) | Semiconductors are roughly half of build cost; duties and licensing decide both price and which platforms reach which country. |
| 22 | Air permit and fuel-supply agreement as explicit lead items for on-site gas; will-serve vs contracted capacity distinction (§8a, §14.4) | Powered land means contracted capacity by a date, or in-hand air permits and fuel access. |
| 23 | Minor: DRAM/HBM/SSD shortage rows in lead times; security opex baseline; community-benefit payment lowering opposition probability; decommissioning cost at horizon | Closing the residual gaps from the review. |

### 2.4 Revision 0.4

| # | Change | Rationale |
|---|---|---|
| 16 | Power supply catalog, location resource layer and supply mix by period (§8a–8d) | On-site generation was a single "gas" option. Power viability is technology × location × date: geothermal or hydro contracts can be immediate in Iceland or Norway; gas recips lead in Texas; SMRs and portable microreactors have earliest-availability years that gate them regardless of lead time. Time-to-power becomes the date the mix first covers the load. |
| 17 | Existing-plant proximity as a resource (§8b) | Co-location with stranded or retiring capacity is a live siting strategy. Curated per site; v1.x. |

### 2.5 Revision 0.3

| # | Change | Rationale |
|---|---|---|
| 8 | Climate grid built from ERA5 via Copernicus CDS bulk download, not the Open-Meteo API (§6.1) | Open-Meteo weights long requests as multiple calls (4 weeks ≈ 3 calls); a 10-year hourly pull for ~15,000 cells is ~7.5M weighted calls against a 300k/month free budget. Runtime exact-point refinement stays on Open-Meteo (§6.6): one pin ≈ 250 weighted calls, within limits. |
| 9 | Supply-chain and lead-time module (§14.4) | Transformers, switchgear, turbines, chillers and accelerator allocation currently set the critical path more often than permitting; the model had no representation of product availability. |
| 10 | Risk register — political, community, policy, grid, labour, climate-event (§12a) | Unknowns that are individual to a project and cannot be looked up; represented as expected-value adjustments shown separately from the deterministic result. |
| 11 | Trajectories for time-varying inputs (§5.5) | Tariff, carbon price, water price, grid intensity and design wet-bulb change over a 15-year horizon; a single constant hides the question. |
| 12 | Workload & Demand tab: global traffic, addressable share, capture, ramp → derived utilization; optional business-case block (§4c, §16.2) | Utilization was an input; sizing to demand was impossible. |
| 13 | Model regime and model catalog (§4a) | Same facility, different served model → different tokens/s/MW and market price. Third-party owners can compare open-weight models against leasing capacity to a proprietary vendor. |
| 14 | Compute platform catalog with platform × model throughput matrix; rack / server / component granularity (§4b) | The rack was a single NVIDIA anchor. Competing stacks differ in cost, power density, cooling need, availability and software maturity. |
| 15 | Component-level refresh option (§13.2) | Server-in-rack replacement is cheaper than rack-scale replacement and depends on platform granularity. |

### 2.6 Revision 0.2

| # | Change | Rationale |
|---|---|---|
| 6 | Input-type vocabulary anchor / referential / baseline / scenario / derived (§3.3) | Looked-up values are dated baselines the user overrides per project; the provenance count separates referenced from assumed. |
| 7 | Seed jurisdictions extended to Africa, South America, second Australian state (§7) | Layer A was global; Layer B was not. |

### 2.7 Revision 0.1 — scope and parameter map

| # | Decision | Rationale |
|---|---|---|
| 1 | Standalone tool, not a benchmark feed for the orbital model | Different question; a parity self-test (§17) keeps the overlap consistent. |
| 2 | Location from lat/lon with external lookups | User choice. Objection recorded: economic and regulatory facts are jurisdiction-level; mitigated by the two-layer model (§5). |
| 3 | Scale selector: hall (20–50 MW) or campus (100 MW – 1 GW) | Regimes differ in power sourcing, phasing and learning, not in the spine. |
| 4 | GB300 block and inference-only kept as the anchor | Cross-model comparability. |
| 5 | Single-file `index.html` plus build-time `data/` bundle | Same hosting pattern as the orbital repo. |

## 3. Architecture of the tool

### 3.1 Files

| Path | Role |
|---|---|
| `index.html` | The model. No build step, no framework. Leaflet from CDN for the map pin only. |
| `terrestrial_datacenter_model_specification.md` | This document, opened by the Specification button. |
| `data/climate_grid.json` | 1° land-cell grid of derived climate parameters (§6.1). Built by Actions, not committed. |
| `data/carbon.json` | Grid carbon intensity and mix by country / balancing area, with year and a default trajectory. |
| `data/ixp.json` | Internet exchange and carrier-hotel coordinates (PeeringDB). |
| `data/hazard.json` | Seismic PGA and flood class on the 1° grid. |
| `data/jurisdictions.json` | **Curated** economic, regulatory and risk baselines per jurisdiction (§7). Committed; schema-validated in CI. |
| `data/platforms.json` | **Curated** compute platform catalog (§4b). |
| `data/models.json` | **Curated** served-model catalog with market prices (§4a). |
| `data/throughput.json` | **Curated** platform × model tokens/s/MW where published; derived cells computed client-side (§4b.3). |
| `data/leadtimes.json` | **Curated** long-lead equipment baselines (§14.4). |
| `data/power_options.json` | **Curated** generation option catalog (§8a). |
| `data/resources.json` | Wind and solar capacity-factor grids, geothermal potential class, gas-pipeline proximity; existing-plant records curated per seed site (§8b). |
| `scripts/build_climate_grid.py` | CDS API → ERA5 hourly 2 m temperature, dew point, pressure → wet-bulb → per-cell statistics → grid JSON. Requires a free CDS account token in Actions secrets. |
| `scripts/build_carbon.py`, `build_ixp.py`, `build_hazard.py` | Fetch-and-compact, each with fallback to the previously published bundle. |
| `scripts/validate_curated.py` | Schema, source-URL and date checks on every curated file; CI fails on a value without a source. |
| `.github/workflows/pages.yml` | On push + monthly cron: run scripts, assemble `site/`, deploy. Climate and hazard rebuild only on script change. |

### 3.2 Tabs

Site · Power Supply · Climate & Cooling · Land & Construction · Compute Platform · Model & Workload · Network · Regulatory & Risk · Operations · Timeline & Supply · Results

### 3.3 Controls and input labels

Recalculate · Reset base scenario · Download scenario JSON (includes provenance) · Break-even solver · Run self-tests · Specification · ±20% sensitivity tornado · Site comparison (up to 4 pins) · Platform/model comparison · Business-case toggle · integrity footer.

| Label | Meaning |
|---|---|
| **anchor** | vendor or standards figure (rack TDP, tier availability) |
| **referential** | public dataset or curated record — dated, sourced |
| **baseline** | value set by the author where no reference exists, reasoning in the tooltip; expected to be overridden per project |
| **scenario** | user-set, or a referential/baseline value the user has overridden |
| **derived** | computed |

Results reports counts by label, e.g. "14 referential, 9 baseline, 3 scenario, 0 unresolved" — the honest answer to "how much of this is known".

### 3.4 Scale selector

`hall` — one building, 20–50 MW IT, grid-connected, single phase, backup generation only.
`campus` — 100 MW – 1 GW IT, N halls at a cadence, substation and on-site generation options, learning on repeated halls (§10.4), phased energisation (§14.2).

Changes defaults and enables inputs; never changes formulas.

### 3.5 Presentation

Design system reused verbatim from the orbital tool's `index.html`: colour tokens, typography, panel and card styles, input-row markup with type-label chips, warning chips, footer integrity notes, Specification and self-test modals, scenario JSON download. Differences: a CSS grid that collapses to one column below ~700 px; tab bar becomes a horizontally scrollable strip; tables scroll inside their panel; SVG charts (tornado, Gantt, mix-by-period, cohort allocation) size to container width; Leaflet map is touch-friendly. Pop-out windows are desktop-only. Self-test: no horizontal overflow at 390 px.

## 4. Compute, model and workload

### 4a. Model regime and served-model catalog

**Regime** fixes who operates and what they charge:

| Regime | Operator | Model cost line | Revenue benchmark (business case only) |
|---|---|---|---|
| Frontier lab / hyperscaler, own model | model owner | R&D allocation $/1M tokens (baseline) | frontier list price |
| Third-party open-weight inference provider (base) | independent owner | zero, or commercial-licence fee where the licence requires | open-weight market price for that model |
| Neocloud / capacity lessor | independent owner | none | $/GPU-hour or $/kW-month |
| Enterprise private inference | end user | zero or licence | avoided external spend |
| Mixed | fractions of installed racks per regime | blended | blended |

**Served-model catalog** (`models.json`), one record per model:

| Field | Type | Drives |
|---|---|---|
| total parameters, active parameters (MoE), weight precision, KV-cache bytes/token, typical context | referential (model card) | memory per replica → replicas per platform unit → throughput (§4b.3) |
| licence: open-weight permissive / open-weight restricted / proprietary not self-hostable | referential | serveability by a third party; licence fee line |
| market price $/1M tokens, blended input/output, dated | referential (provider price lists) | revenue, margin, break-even utilization |
| interactivity target tokens/s/user | baseline | batch depth → throughput derate |

Seed rows: Llama 4 Maverick and Scout, DeepSeek V3 / R1, Qwen 3 235B-A22B and a dense mid-size Qwen, Mistral Large / Mixtral, gpt-oss-120b, Kimi K2; proprietary rows (GPT, Claude, Gemini families) carry licence = proprietary and no throughput fields — they enter only through the lessor regime.

### 4b. Compute platform catalog

**4b.1 Record** (`platforms.json`):

| Field | Type | Drives |
|---|---|---|
| granularity: rack-scale system / server / component (accelerator + host) | anchor | what is swapped at refresh; fit-out cost |
| accelerators per unit; TDP and peak kW per unit | anchor | power, racks per MW, cooling architecture minimum (§9.1) |
| HBM GB per accelerator; scale-up interconnect (NVLink / UALink / Infinity Fabric / Ethernet / optical) | anchor | replicas per unit for a given model |
| unit cost $ | referential where published, else baseline | CAPEX |
| lead time months; allocation probability | baseline, dated | §14.4 supply chain |
| cooling: air-capable / DLC required / immersion | anchor | forces or forbids cooling options |
| software maturity factor 0.6–1.0 | baseline | derates derived throughput; exposed, in the tornado |
| purchasable by third party: yes / cloud-only / region-restricted | referential | shown, not silently excluded |
| export-control class (US ECCN band); countries requiring licence | referential | availability at the resolved jurisdiction |
| residual-value curve: % of unit cost at 12/24/36/48/60 months, three bands (conservative / mid / optimistic), dated | referential from secondary-market reports where they exist, else baseline | §13.2 refresh economics |

Seed rows: NVIDIA GB300 NVL72 (anchor row, $4M, 135/155 kW, 72 GPUs, DLC), NVIDIA B300 HGX 8-GPU server (server granularity, air or DLC), AMD MI355X 8-GPU server, AMD MI400 "Helios" rack, Intel Gaudi 3 server, Cerebras CS-3, Groq LPU rack, SambaNova rack, Huawei Ascend 910C server / CloudMatrix 384 (region-restricted), Google TPU Ironwood (cloud-only), AWS Trainium 3 (cloud-only).

**4b.2 Derived quantities**

$$N_{unit}=\left\lceil\frac{1000\,P_{target}}{P_{unit}}\right\rceil,\qquad N_{installed}=N_{unit}(1+S),\qquad P_{IT,installed}=\frac{N_{installed}P_{unit}(1+O_{IT})}{1000}$$

Racks per MW, white-space area and cooling minimum follow from the unit record. A warning fires when unit kW exceeds the selected cooling architecture's maximum or when the platform is cloud-only / region-restricted for the resolved jurisdiction.

**4b.3 Throughput matrix**

$TPS_{MW}[platform][model]$ is **referential** where MLPerf Inference or a vendor publishes the pair (the NVIDIA 2.8M tokens/s/MW reference is one cell). Otherwise **derived**:

$$n_{rep}=\left\lfloor\frac{N_{acc}\,M_{HBM}}{M_{weights}+M_{KV}(ctx,\,batch)}\right\rfloor,\qquad TPS_{MW}=\frac{n_{rep}\,\tau_{acc}(model)\,\mu}{P_{unit}(1+O_{IT})/1000}$$

$\tau_{acc}$ = per-accelerator decode tokens/s for the model class (baseline table by active-parameter band and precision), $\mu$ = software maturity factor. Derived cells are labelled derived and are the least-defended numbers in the tool; interconnect bandwidth is not modeled — models that do not fit one scale-up domain are flagged, not priced.

### 4c. Workload and demand

| Input | Type | Default |
|---|---|---|
| Global inference demand $D_0$, tokens/day; growth %/yr | baseline (public provider disclosures, dated) | trajectory |
| Population weights per must-reach metro | referential | — |
| Latency budget ms → addressable share $f_{addr}$ from §11 | derived | 100 ms |
| Capture share $f_{cap}$ of addressable; ramp months (S-curve) | scenario | 1%, 18 mo |
| Interactivity tokens/s/user | baseline | per model |

$$D_{served}(t)=\min\big(D(t)\,f_{addr}\,f_{cap}\,\sigma(t),\ TPS\cdot86400\big),\qquad U(t)=\frac{D_{served}(t)}{TPS\cdot86400}$$

Utilization is derived per period when the demand module is on; otherwise the 75% scenario input stands. Reverse mode: solve MW required to serve a target share of addressable demand at a target utilization. Stranded capacity (installed but unserved) is reported.

## 5. Location model

### 5.1 Two layers

**Layer A — continuous, at the coordinate:** climate design conditions and free-cooling hours, seismic and flood class, grid carbon intensity of the balancing area, water stress, distance to internet exchanges.

**Layer B — discrete, snapped to a jurisdiction:** tariff structure, interconnection queue and cost, permitting duration, land and construction indices, labour rate and availability, property tax, incentives, moratoria, regulatory obligations, and the jurisdiction's **risk baselines** (§12a).

The user sees one pin. Results prints a provenance table for every location-dependent input: layer, record ID, date, label (§3.3).

### 5.2 Resolution

1. Pin → 1° cell → climate, hazard, water stress.
2. Pin → country by point-in-polygon on Natural Earth 110m admin-0 → sub-national unit by nearest centroid where the jurisdiction file defines one (no sub-national polygons in v1).
3. Country / sub-national → balancing area → `carbon.json`.
4. Pin → k nearest IXPs and distances to must-reach metros.
5. No record → parent record → baseline defaults flagged **unresolved** in red.

### 5.3 Provenance

Every Layer B and curated-catalog value is `{value, unit, source_url, as_of, label}`. Scenario JSON export carries provenance.

### 5.4 Manual override

Any value may be overwritten; label becomes *scenario*; provenance records "user override"; Reset restores.

### 5.5 Trajectories

Inputs that change over the horizon accept either a constant or `{start, pct_per_yr}` (optionally a year-indexed array). Applied in the period sum of §13. Defaults, all baselines:

| Quantity | Default trajectory |
|---|---|
| Electricity tariff | +2%/yr |
| Carbon price | by jurisdiction scheme (EU ETS path referential; none elsewhere unless recorded) |
| Water price | +3%/yr |
| Grid carbon intensity | −3%/yr |
| Design wet-bulb | +0.03 K/yr |
| Open-weight model market price | −15%/yr (business case only) |
| Accelerator unit cost at refresh | −10%/yr per performance-equivalent unit |

## 6. Layer A — data derived at the coordinate

### 6.1 Climate

Source: ERA5 hourly reanalysis obtained in bulk from the Copernicus Climate Data Store (2 m temperature, 2 m dew point, surface pressure), 10 most recent full years, sampled to the 1° land grid; wet-bulb computed from the three. NASA POWER (0.5°, hourly) is the fallback. Open-Meteo is **not** used for the grid because of call weighting (§2.1 #8). Stored per cell:

| Field | Definition |
|---|---|
| `Tdb_99.6`, `Twb_99.6` | dry- and wet-bulb exceeded 0.4% of hours (ASHRAE 99.6%) |
| `Tdb_ann`, `Twb_ann` | annual means |
| `h_econ[T]` | hours/yr with wet-bulb below {12,15,18,21,24,27,30} °C |
| `h_dry[T]` | hours/yr with dry-bulb below {18,24,30,35} °C |
| `h_extreme` | hours/yr above Twb 30 °C (derate exposure, §12a) |
| `trend_K_per_yr` | 30-year linear trend in annual mean, seeds the wet-bulb trajectory |
| `elev` | m |

Client: bilinear interpolation between the four surrounding cells.

### 6.2 Hazard — GEM PGA (475-yr) → five classes → structural multiplier (§10.2); JRC 100-yr flood depth → three classes → site-prep multiplier and warning above class 2.

### 6.3 Grid carbon — Ember country data; ENTSO-E bidding zones (EU) and EIA balancing authorities (US) where available; `gCO2_per_kWh`, `renewable_share`, `year`, default trajectory.

### 6.4 Connectivity — PeeringDB `ix` and `fac` → point set; one-way fibre latency = distance × route factor 1.6 / (c × 0.68) to k nearest and to must-reach metros (default Frankfurt, Amsterdam, London, Ashburn, Singapore, São Paulo, Johannesburg, Sydney).

### 6.5 Water stress — WRI Aqueduct baseline stress → class → warning and default WUE ceiling (§9.3). Price is Layer B.

### 6.6 Optional live refinement — one opt-in button queries Open-Meteo's historical API for the exact coordinate (5 years hourly ≈ 250 weighted calls; free tier 10,000/day, non-commercial, CC BY 4.0 attribution shown) and recomputes §6.1 fields in the browser. On failure the grid value stands and the status line says so. README states the licence position for a public research tool.

## 7. Layer B — curated jurisdiction record

Schema (sub-national records inherit unset fields from the country):

```
{
  "id": "DE-HE", "name": "Hesse, Germany", "parent": "DE",
  "currency": "EUR", "fx_to_usd": {...},
  "power": {
    "tariff_industrial_usd_mwh": {...}, "tariff_trajectory_pct_yr": {...},
    "tariff_structure": "energy+capacity|flat|ppa_typical",
    "capacity_charge_usd_kw_month": {...}, "grid_fees_usd_mwh": {...},
    "ppa_typical_usd_mwh": {...},
    "interconnection_queue_months": {...}, "interconnection_cost_usd_mw": {...},
    "queue_requires_permits_first": bool,
    "max_single_connection_mw": {...}, "grid_reliability_saidi_min": {...},
    "curtailment_risk": {...}, "flexible_interconnection_available": bool,
    "moratorium": {"status": "none|partial|full", "note", source_url, as_of}
  },
  "land": {
    "industrial_land_usd_m2": {...}, "construction_cost_index": {...},
    "labour_usd_hr_electrical": {...}, "labour_availability_factor": {...},
    "permitting_months": {...}, "property_tax_pct_capex_yr": {...},
    "incentives": {"capex_credit_pct", "tax_abatement_years", "note", source_url, as_of}
  },
  "water": {"usd_m3": {...}, "consumption_permit_required": bool, "restriction_risk": {...}},
  "trade": {
    "import_duty_pct": {"accelerators": {...}, "servers": {...}, "electrical": {...}, "mechanical": {...}},
    "duty_trajectory": {...}, "export_control_class": "unrestricted|licence|embargo", "note"
  },
  "finance": {"cost_of_capital_premium_pct": {...}, "typical_debt_share": {...}},
  "carbon": {"price_usd_tco2": {...}, "scheme": "EU ETS|none|...", "trajectory": {...}},
  "regulatory": {
    "eu_eed_reporting": bool, "nis2_essential_entity": bool,
    "eu_ai_act_gpai_relevance": "note", "data_sovereignty_constraints": "none|sectoral|strict",
    "heat_reuse_obligation": bool, "pue_cap": null|number,
    "platform_import_restrictions": [], "notes": []
  },
  "risk_baselines": { <per §12a: probability, delay_months, cost_multiplier per risk> },
  "ops": {"staff_usd_fte_yr": {...}, "insurance_pct_capex_yr": {...}}
}
```

Every value carries source URL and date; CI rejects records without them. Fields with no public source are stored as **baseline** with reasoning in `note`.

Seed set (~34):

| Region | Records |
|---|---|
| Europe | DE (+ DE-HE), NL, IE, FR, ES, PT, SE, NO, FI, DK, PL, CZ, GB |
| North America | US-VA, US-TX, US-OR, US-AZ, CA-QC |
| South America | BR-SP, CL, CO, UY |
| Africa | ZA (Gauteng / Western Cape where data allows), KE, NG-LA, MA, EG |
| Middle East | AE, SA |
| Asia | IN-MH, SG, MY-JH, JP |
| Oceania | AU-NSW, AU-VIC |

Coverage in Africa and South America will lean on baselines; the provenance count shows that per site.

## 8. Site & power sourcing

### 8.1 Facility power — $P_{facility}=P_{IT,installed}\cdot PUE$, with $P_{IT,installed}$ from §4b.2.

### 8a. Generation option catalog (`power_options.json`)

| Field | Type | Drives |
|---|---|---|
| capex $/MW; fixed O&M $/MW-yr; variable $/MWh; fuel $/MWh_th; efficiency | referential (IEA, Lazard LCOE, NREL ATB — dated) | cost per delivered MWh by period |
| capacity factor at site; firmness (baseload / dispatchable / variable) | derived from §8b or anchor | firm MW per installed MW; storage or backup needed to cover load |
| lead time months; **earliest commercial availability year** | baseline, dated | when it can contribute; a row cannot deliver before its availability year whatever the lead time |
| permitting class and typical months (per jurisdiction) | baseline | critical path |
| carbon intensity gCO₂/kWh | referential | §15 |
| minimum and maximum economic unit MW; modularity; relocatable | anchor | fit to hall vs campus; portability |
| resource dependency | anchor | gated by §8b |

Seed rows (availability year is a baseline and will move):

| Option | Firmness | Unit MW | Lead, mo | Available from | Dependency |
|---|---|---|---|---|---|
| Grid connection | baseload | any | queue (§7) | now | interconnection capacity |
| Flexible / non-firm interconnection (curtailable) | baseload less curtailment | any | queue − reduction | now where tariff exists | `flexible_interconnection_available` |
| PPA (contract, no plant) | as underlying | any | 6 | now | market |
| Gas reciprocating engines (fast start, ~45% eff., modular) | dispatchable | 2–20 | 12 | now | gas pipeline or LNG; air permit; fuel-supply agreement |
| Gas aeroderivative turbine (fast start, ~40% eff.) | dispatchable | 30–60 | 24–36 | now | gas; air permit |
| Gas CCGT (~60% eff.) | baseload | 300–800 | 48–60 | now | gas; air permit; water |
| Gas CCGT + carbon capture (~54% eff., 90% capture) | baseload | 300–800 | 60–72 | 2029 (baseline) | gas; CO₂ transport/storage |
| Hydrogen-ready turbine (blend now, 100% H₂ later) | dispatchable | 30–500 | 36–48 | now (blend) | gas now, H₂ supply later |
| Fuel cells (SOFC) | baseload | 0.3–50 | 12 | now | gas or H₂ |
| Diesel / gas backup gensets | dispatchable | 1–3 | 12 | now | fuel storage |
| On-site solar PV + BESS | variable | any | 12–18 | now | GHI |
| On-site wind + BESS | variable | 5–200 | 24–36 | now | wind class |
| Geothermal, flash / binary | baseload | 5–100 | 36–60 | now | geothermal class ≥ moderate |
| Enhanced geothermal (EGS) | baseload | 10–100 | 36–48 | 2028 (baseline) | heat flow, drilling depth |
| Hydro — existing plant capacity contract | baseload | any | 6–12 | now | plant within range with spare capacity |
| Nuclear — existing plant contract / uprate / restart | baseload | 100–1,000 | 12–48 | now | plant within range; policy |
| SMR (light-water, 50–300 MW) | baseload | 50–300 | 60–84 | 2031 (baseline) | licence, policy |
| Portable / micro reactor (1–20 MW, transportable, factory-built) | baseload | 1–20 | 24–36 | 2028–2030 (baseline; first units in test/regulatory approval) | licence, policy, siting rules |
| Waste heat / biomass CHP | baseload | 5–50 | 24 | now | feedstock |
| Standalone BESS | shifting only | any | 9 | now | — |
| Hydrogen turbines / storage | dispatchable | 10–100 | 36 | 2030 (baseline) | H₂ supply |

Flexible interconnection carries `queue_reduction_months`, `curtailment_hours_yr` and `max_curtailment_pct`; curtailment reduces availability by hours × (1 − workload-flexibility fraction). Inference workloads are less deferrable than training; the flexibility fraction baseline is 0.2 and is a scenario input.

Grid capacity is entered as *contracted MW by date* or *will-serve only*; a will-serve letter counts as zero firm MW until a contract date is set, and the tool says so.

Micro and portable reactors are recorded because they are moving from concept to licensing; the availability year and cost rows are the least defended in the catalog and are exposed for that reason.

#### 8a.1 Levelised cost of energy at the site

For every option that can deliver at the pin, the tool computes LCOE from the record and the resource layer:

$$LCOE=\frac{C_{capex}\,CRF(r,T)+O\&M_{fixed}}{8760\,CF}+O\&M_{var}+\frac{c_{fuel}}{\eta}+c_{CO_2}\,I_{fuel}+c_{connect}$$

$CRF(r,T)=\dfrac{r(1+r)^T}{(1+r)^T-1}$ at the model discount rate (or the financing WACC when the block is on) and the option's economic life $T$; $CF$ from §8b for variable sources, from the record for dispatchable ones **at the dispatch it actually runs** (a peaker at 15% CF has a very different LCOE than at 90%); $c_{connect}$ = interconnection or on-site wiring $/MWh. Fuel and carbon prices follow their trajectories, so LCOE is reported for year 1 and as a horizon average.

Against this the tool shows the grid's **delivered cost** = tariff + capacity charge ÷ (8760·L) + grid fees + carbon, on the same $/MWh basis, so every option is comparable on one line. Referential anchors for the option records: Lazard LCOE+ (annual), IEA *Projected Costs of Generating Electricity*, NREL ATB — each dated; site-specific drivers (fuel price, resource CF, labour) come from Layers A and B.

Firmness is priced, not assumed: a variable source's LCOE is quoted on its own output, and the **firm-equivalent cost** of a mix (§8c.1) is what enters the lifecycle spine.

### 8b. Location resource layer (extends Layer A)

| Resource | Source | Gives |
|---|---|---|
| Wind | Global Wind Atlas mean speed at 100 m → CF | on-site wind CF |
| Solar | Global Solar Atlas GHI → CF | on-site PV CF |
| Geothermal potential class | global heat-flow compilations; national atlases where they exist (ÍSOR, USGS, GeoORG) | viability, drilling-cost class |
| Gas pipeline proximity | OSM Overpass, curated | gas options viability; connection cost |
| Existing power plants within R km: type, capacity, retirement date | Global Energy Monitor / WRI Global Power Plant Database, curated per seed site (v1.x) | hydro, nuclear and stranded-capacity contract options |
| Nuclear policy: allowed / restricted / banned; SMR and micro-reactor licensing status | Layer B | gates nuclear rows |

An option whose dependency is not met at the pin is shown greyed with the reason, never hidden.

### 8c. Supply mix by period

The user composes a mix: entries of (option, MW, order date). Per period the tool computes firm MW available, delivered $/MWh, carbon intensity, and a shortfall against facility load (red). Bridging behaviour (§14.2) is a mix whose entries have different ready dates. Default mixes: hall = grid + backup; campus = grid + one bridging + one renewable or PPA.

A **"first available"** helper ranks options at the pin by earliest firm-MW date and delivered cost, so the tool shows, for an Icelandic pin, geothermal or hydro contract ahead of any grid queue elsewhere; for Texas, gas recips; for Norway, hydro PPA; for a 2033 start date, SMR rows become eligible.

#### 8c.1 Hybrid templates and firm-capacity accounting

Templates prefill a mix; every entry remains editable:

| Template | Entries | Firmness logic |
|---|---|---|
| Grid + backup (hall default) | grid, gensets | grid firm; gensets only for outages |
| Gas bridge → grid | recips or aeroderivatives sized to load, grid later | gas firm until grid date, then backup or sold as capacity |
| Solar + BESS + gas peaker | PV at CF, BESS h hours, recips for residual | firm MW = PV·CF·(1−loss) + BESS dispatch; peaker covers residual at its resulting CF |
| Wind + BESS + grid (non-firm) | wind, BESS, flexible interconnection | curtailment hours from §8a; workload flexibility fraction applies |
| Geothermal / hydro contract + grid | baseload contract, grid top-up | contract firm; grid for growth |
| Nuclear contract / SMR + BESS | baseload, BESS for ramps | firm from availability year |
| CCGT + CCS behind the meter | CCGT, grid backup | firm; carbon at captured intensity |

Dispatch rule (v1, deterministic): for each period, load $P$ is met in order of ascending variable cost, subject to each entry's firm MW; storage shifts variable output within a day at its round-trip efficiency and hours; unmet load is a shortfall (red). The **firm-equivalent $/MWh** of the mix is total period cost ÷ energy served, and that is what the spine uses as $c_{energy,p}$. Hourly dispatch and weather-year sampling are later refinements (§20).

### 8d. Time-to-power from the mix

$T_{power}$ = first period in which firm MW covers facility load. It enters §14.1 as a candidate binding term ("power mix") alongside queue, permit, build and long-lead items.

### 8e. Redundancy tier

| Tier | Availability | MEP multiplier | Backup |
|---|---|---|---|
| II | 99.74% | 0.80 | N |
| III (base) | 99.98% | 1.00 | N+1 |
| IV | 99.995% | 1.35 | 2N |

$A_{eff}=A_{tier}-\max(0,\ SAIDI/525{,}600\cdot(1-f_{backup}))-A_{curtail}-A_{extreme}$ (last two from §12a).

## 9. Climate & cooling

### 9.1 Architecture

| Architecture | Max unit kW | $\kappa$ (kW cooling / kW IT at design) | Economiser | Supply temp |
|---|---|---|---|---|
| Air, hot/cold aisle | 40 | 0.35 | air-side | 24 °C |
| Rear-door heat exchanger | 80 | 0.22 | water-side | 24 °C |
| Direct liquid to chip (base) | 150 | 0.12 | dry cooler | 32 °C |
| Immersion | 200 | 0.08 | dry cooler | 40 °C |

The platform record's cooling requirement constrains the choice (§4b.1).

### 9.2 Derived PUE

$$PUE = 1+\eta_{elec}+\kappa\left[1-f_{free}\,(1-\rho_{econ})\right]+\kappa_{aux}$$

$f_{free}$ interpolated from `h_econ[T]` or `h_dry[T]` at supply temperature minus approach; $\rho_{econ}$ = 0.25; $\eta_{elec}$ = 0.06 (Tier III) / 0.08 (Tier IV); $\kappa_{aux}$ = 0.02. Design wet-bulb follows its trajectory (§5.5), so PUE drifts over the horizon. Manual PUE mode retained (parity test §17.2).

Validation bands to be checked in self-tests: Stockholm DLC dry ≈ 1.12–1.15; Frankfurt air ≈ 1.30–1.35; Phoenix air ≈ 1.40–1.50; Singapore air ≈ 1.45–1.55.

### 9.3 Water — $WUE=\lambda_{evap}(1-f_{free,dry})$ L/kWh_IT; $\lambda_{evap}$ = 1.8 (evaporative towers) or 0 (dry). Warnings on stress class ≥ 3 with WUE > 0, on consumption-permit requirement, and on recorded restriction risk (§12a).

### 9.4 Heat reuse — recoverable fraction × heat price → OPEX credit; on by default where the jurisdiction sets `heat_reuse_obligation`; district-heating capex as scenario input.

## 10. Land & construction

### 10.1 Site area — $A_{white}=N_{installed}\,a_{unit}$ (from platform record), $A_{gross}=A_{white}\,g$ (1.8 DLC, 2.2 air), $A_{site}=A_{gross}\,s$ (3.0 hall, 4.0 campus).

### 10.2 CAPEX stack

| Term | Basis | Default (US avg, Tier III, DLC) | Scaling |
|---|---|---|---|
| Land | $A_{site}$ × $/m² | referential | B |
| Site preparation | $A_{site}$ × $/m² × flood multiplier | 60 $/m² | A |
| Shell | $A_{gross}$ × $/m² × seismic × construction index | 2,200 $/m² | A + B |
| MEP | $P_{IT}$ × $M/MW × tier × construction index | 7.5 $M/MW | B |
| Cooling plant | $P_{IT}$ × $M/MW by architecture | 1.2 DLC / 1.8 air | — |
| Interconnection + substation | $P_{facility}$ × $M/MW | 1.0 $M/MW | B |
| On-site generation / BESS | §8a–8c | 0 (hall) | — |
| Fit-out | $N_{installed}$ × $k by granularity | 120 $k/rack; 25 $k/server | — |
| Fibre entry + meet-me | fixed + per km | 2 $M + 60 $k/km | A |
| Soft costs | % hard | 12% | B |
| Contingency | % hard | 10% | — |
| Compute | $N_{installed}$ × unit cost | platform record | — |
| Import duties | duty % × (compute, electrical, mechanical) by period | jurisdiction trade record | B |
| Community-benefit payments | $/MW one-off (lowers opposition probability in §12a) | 0 | scenario |
| Expediting premiums | §14.4 | 0 | — |

Parity: shell + MEP + cooling + interconnection + fit-out + soft + contingency at US-average, Tier III, air must compose to the orbital stub's 12 $M/MW (self-test §17.2).

### 10.3 Incentives — capex credit at t = 0; tax abatement for stated years; pre-tax otherwise.

### 10.4 Campus learning — halls 2…N on a Wright curve (shell, MEP, cooling, fit-out), 92% per doubling; compute not on the curve; orbital §15.1 batch-mean formula.

## 11. Network

Bandwidth from TB/day/MW; transit $/Gbit/s/month (referential where recorded). Latency to must-reach metros feeds the addressable-demand share (§4c) and TTFT. Output: fraction of population-weighted demand within 30 / 60 / 100 ms.

## 12. Regulatory

Priced where it maps to cost or time: EED reporting (staff hours), heat-reuse (§9.4), PUE cap (warning), moratorium (red banner; override with stated waiver), NIS2 essential entity (security opex uplift %, baseline), platform import restrictions (blocks catalog rows), sovereignty class (flag). All shown with source and date — the tab doubles as a siting checklist.

## 12a. Risk register

Risks that cannot be looked up and are individual to a project. Each carries a triple **(probability over the build period, delay months if realised, cost multiplier if realised)**; jurisdiction records supply baselines where recorded, else global baselines; all overridable.

| Risk | Affects | Global baseline (p, Δt, ×cost) |
|---|---|---|
| Community opposition / litigation | permitting duration, soft costs | 0.20, 9, 1.05 — probability reduced by community-benefit payment (baseline: −0.05 per $50k/MW, floor 0.05) |
| Permit appeal | permitting | 0.15, 6, 1.02 |
| Policy reversal (moratorium, incentive withdrawal, water restriction) | availability to proceed, incentives, WUE cap | 0.10, 12, 1.10 |
| Grid curtailment / emergency orders once connected | $A_{curtail}$ hours/yr | 0.30, —, 0.2% availability |
| Tariff reform | tariff trajectory ± | 0.25, —, ±15% tariff |
| Geopolitical / sovereignty event | platform availability, sovereignty class | 0.05, 6, 1.10 |
| Labour shortage | construction duration, labour rate | 0.30, 4, 1.08 labour |
| Extreme-heat / smoke / storm derate | $A_{extreme}$ from `h_extreme` × derate fraction | derived, 0.5 |
| Accelerator allocation slip | compute delivery (§14.4) | platform record |

**Representation A (v1, default):** expected-value adjustments — $E[\Delta t]=\sum p_i\Delta t_i$ added to the affected duration, $E[\times]=\prod(1+p_i(m_i-1))$ on the affected cost — with Results showing **unrisked** and **risked** side by side and the delta attributed per risk.
**Representation B (later):** Monte Carlo over the register → P10/P50/P90 on time-to-power and $/1M tokens (parallels orbital §26 item 10).

Rule: register values are baselines, counted as such in provenance, so the reader sees how much of the risked result rests on guesses.

## 13. Lifecycle cost — the shared spine

### 13.1 Present value

$$PV=C_{CAPEX,0}+\sum_{p}\frac{C_{ops,p}}{(1+r)^{t_p}}+\sum_{k:\ kT_{refresh}<Y}\left[\frac{C_{refresh,k}}{(1+r)^{kT_{refresh}}}-Salvage\right]-Salvage(C_{facility},0,T_{fac})+C_{model}$$

$$C_{ops,p}=E_p\,c_{energy,p}+P_{fac}\,c_{cap}\cdot12+C_{fac}(o_{maint}+o_{tax}+o_{ins})+N_{FTE}c_{FTE}+W_pc_{water,p}+E_pI_{CO2,p}c_{CO2,p}+C_{transit}+C_{licence}-C_{heat}$$

$$E_p=P_{IT,installed,p}\cdot PUE_p\cdot 8760\,L_p,\qquad L_p=0.5+0.5\,U_p$$

$c_{energy,p}$, $c_{water,p}$, $c_{CO2,p}$, $I_{CO2,p}$, $PUE_p$ follow their trajectories; $U_p$ is derived from demand (§4c) or the scenario input. $C_{model}$ is the R&D allocation (own-model regime) or zero. $C_{licence}$ is the open-weight commercial-licence line where a licence requires it.

$$C_{annualized}=\frac{PV}{AF(r,Y)},\qquad C_{1M\,tok}=\frac{C_{annualized}\cdot10^6}{\sum_p TPS\cdot U_p\cdot A_{eff}\cdot T_p},\qquad C_{GPUh}=\frac{C_{annualized}}{N_{prod}N_{acc}\,8760\,U\,A_{eff}}$$

Also: annualized facility cost per kW-month (excludes compute and energy) for comparison with published colocation and lessor rates.

Defaults: horizon 15 yr, discount 8%, maintenance 2% facility capex/yr, insurance 0.4%/yr, staff 0.6 FTE/MW (DLC), physical and cyber security 0.3% facility capex/yr (baseline; NIS2 uplift where flagged), decommissioning 2% facility capex at horizon. $L$ is a v1 simplification; accelerator idle power is not public.

### 13.2 Refresh by granularity

| Platform granularity | Refresh cost $C_{refresh,k}$ |
|---|---|
| Rack-scale system | installed units × unit cost (trajectory-adjusted) + rack re-fit-out |
| Server | installed servers × server cost + server fit-out; racks, PDUs and manifolds retained |
| Component | accelerator trays × cost; host retained; lowest fit-out |

**Residual value.** Compute salvage uses the platform's residual-value curve (band selectable; mid default) instead of straight-line. **Refresh strategy** selector: *hold-to-refresh* (run to refresh interval, resell at curve value) or *rotate-and-resell* (sell at a chosen month, typically 18–24, buy current generation; refresh interval shortens, CAPEX rises, residual credit rises). Results report compute depreciation as economic (curve-based), with accounting life shown only as a footnote — the tool takes no position on financial reporting.

A cross-vendor refresh (e.g. GB300 → MI400) is allowed when cooling and power density fit; the tool re-derives throughput from the matrix and flags integration cost as a baseline uplift.

### 13.4 Fleet cohorts and cascade

The installed compute is a list of **cohorts**, each with platform, unit count, install date and a **cascade path** — an ordered list of stages `{model_class, months}` (e.g. heavy 24 → mid 24 → light 36). Throughput per stage comes from the platform × model matrix (§4b.3); revenue per stage (business case) from that model class's market price and trajectory.

**Retirement rule per cohort** (selector): at refresh interval (default, reproduces §13.2); when residual value falls below a floor; when tokens/s/MW falls below a fraction of the current-generation row; or **never within horizon** — run-to-failure with annual failure rate $p_f(t)=p_0(1+\gamma)^{t}$ and maintenance cost rising at the same rate (baselines $p_0$ 3%, $\gamma$ 0.25).

**Capacity constraint.** Facility MW and cooling are fixed by the build. A retained cohort occupies MW a new cohort cannot use; new cohorts fit only into MW freed by retirement, spare capacity, or a facility expansion (campus mode). Results show MW allocation by cohort and tokens delivered by model class over the horizon.

**Demand by class.** When the demand module is on, §4c demand is split by model class (heavy / mid / light, baseline shares 30 / 40 / 30) so each cascade stage serves its own demand and stranded capacity is reported per class.

Default: one cohort, refresh at interval, cascade path of a single stage — identical to §13.2 behaviour.

### 13.3 Financing block (toggle, off by default)

| Input | Type | Default |
|---|---|---|
| PropCo debt share, rate, tenor | scenario; rate = base + jurisdiction premium | 60%, 6.5%, 15 yr |
| ComputeCo debt share, rate, tenor, advance rate vs unit cost | scenario | 50%, 9%, 4 yr, 70% |
| Interest during construction | derived from schedule | — |
| Cost of equity | scenario | 12% |

When on, the discount rate becomes the blended WACC, IDC is capitalised, and debt service appears in the period sum; when off, the all-equity 8% spine stands so results stay comparable with the orbital model. Tenant credit and lease structures (lessor regime) are not modeled beyond a contract term input.

## 14. Timeline & supply

### 14.1 Time-to-power (hall)

$$T_{TTP}=T_{permit}+\max\big(T_{power}-T_{permit}\cdot[1-q],\ T_{design}+T_{construct},\ \max_i T_{lead,i}\big)$$

$T_{power}$ from §8d replaces the bare grid queue; for a grid-only mix it equals the queue.

$q$ = `queue_requires_permits_first` (0 or 1): where the queue position needs permits, the queue is additive. Risked durations from §12a add on top. The **binding term is named in Results** (queue / build / permit / named long-lead item).

### 14.2 Phased energisation (campus) — hall $i$ at $T_{TTP,1}+(i-1)\tau$, $\tau$ = 6 mo default; bridging generation per hall until the grid date; compute bought at energisation.

### 14.3 Comparator — orbital `T_deploy` from a pasted orbital scenario JSON, else 30 months.

### 14.4 Supply chain and long-lead items

Curated `leadtimes.json`, one record per item: lead months (baseline, dated, with source where a market report exists), expediting premium % and months saved, allocation probability, substitution option.

| Item | Baseline lead, months (2026) | Notes |
|---|---|---|
| HV transformer (≥100 MVA) | 30 | market-wide shortage; expediting rarely available |
| MV switchgear | 14 | |
| Generation units | from power option record (§8a) | gas turbines 36–48 (order books into 2029–30); recips shorter |
| Gensets (backup) | 12 | |
| Chillers / CDUs | 10 | |
| UPS / BESS | 9 | |
| Accelerators | from platform record | allocation probability < 1 shifts compute delivery and token start, not facility cost |
| HBM / DRAM / SSD | 6–12 | 2026 memory shortage; affects servers and storage, not facility |
| Air permit (on-site combustion) | 9–18 | gates gas rows; jurisdiction-dependent |
| Fuel-supply agreement / gas connection | 6–24 | gates gas rows |

Each item's ready date = order date + lead; order date defaults to project start for facility items and to construction completion minus lead for compute. The critical path is recomputed with these; Results shows a Gantt-style bar list. Expediting is a user choice with its premium in CAPEX.

## 15. Carbon and water

$$tCO_2/yr=\sum_pE_pI_p,\qquad I_p=\text{grid or generation intensity by period}$$

Reported: tCO₂/yr; gCO₂, L water and MWh per 1M tokens. Scope 1 and location-based Scope 2 only; embodied carbon excluded and stated so.

## 16. Sensitivity, solver, comparison, business case

### 16.1 ±20% one-at-a-time over all numeric inputs including referential values, baselines and maturity factors; tornado. Break-even solver by bisection on tariff, PUE, unit cost, utilization, throughput, queue months, construction index or lead time to a target $/1M tokens or time-to-power.

### 16.2 Comparison modes
- **Sites:** up to four pins, identical non-location inputs, results side by side with provenance counts.
- **Platforms × models:** same site and building; rows = platform, columns = served model or "lease to vendor"; cells = $/1M tokens cost, availability date, and (business case on) margin.

### 16.3 Business-case block (toggle, off by default)
Revenue benchmark from the model catalog or lessor rate → gross margin per token, break-even utilization, MW needed for a target token demand, payback. Kept separate so the default result remains the defensible cost question comparable to the orbital model.

## 17. Self-tests (planned)

1. Annuity factor, Wright batch mean, haversine, wet-bulb from T/Td/p.
2. **Orbital parity:** manual PUE 1.3, facility composed to 12 $M/MW per §10.2, $80/MWh flat, 4% opex, 99.5%, horizon 10, discount 8%, refresh 3, GB300 row, 2.8M tokens/s/MW referential cell, demand module off, risk off, US-average → $/1M tokens = 0.247 ± 0.5%.
3. Derived PUE at four reference cities within §9.2 bands.
4. Ocean pin → all Layer B unresolved; tool computes.
5. Moratorium banner for Amsterdam / Dublin pins at data date.
6. Campus 300 MW, 6 halls: schedule and hall-6 learning multiplier $0.92^{\log_2 6}$.
7. Throughput matrix: derived cell for GB300 × Llama 4 Maverick within ±30% of the referential NVIDIA cell for the same model class.
8. Refresh granularity: server refresh cheaper than rack refresh for the same platform family.
9. Critical path: with a 30-month transformer lead and 12-month queue, binding term = transformer.
10. Risked vs unrisked delta equals the sum of per-risk attributions.
11. Power mix: Reykjavík-area pin, mix = geothermal 40 MW → $T_{power}$ < grid queue for a Frankfurt pin with identical building; micro-reactor row ineligible for a 2027 start, eligible for 2031.
12. LCOE: recips at 90% CF, $40/MWh_th gas, 45% eff., $1.2M/MW, 25-yr life at 8% → within ±5% of the closed-form value; solar+BESS+peaker template at a Phoenix-class pin returns firm-equivalent cost above the PV LCOE and below the peaker-only LCOE.
13. Residual curve: hold-to-refresh at 36 months with mid band vs rotate-and-resell at 24 months — both computed, delta reported; straight-line legacy mode reproduces the parity test.
14. Duty trajectory: 25% on accelerators applied to a US pin raises compute CAPEX by 25% × compute share and nothing else.
15. Cohorts: (a) refresh every 3 yr vs (b) keep cohort 1 for 6 yr cascading heavy→mid→light, add cohort 2 at year 3 into spare MW — both compute; CAPEX, tokens by class and $/1M tokens deltas reported; single-cohort default reproduces the parity test.
16. Layout: no horizontal overflow at 390 px viewport.
17. Base regression: hall 40 MW, DLC, Tier III, grid-only, GB300, DeepSeek V3, US-VA — value fixed once implemented.

## 18. Outputs

Financial: CAPEX/MW with and without compute, lifecycle TCO/MW, $/1M tokens, $/GPU-hour, facility $/kW-month, unrisked vs risked. Physical: white space, gross and site area, facility MW, PUE trajectory, WUE, cooling margin. Time: time-to-power, binding term, energisation schedule, long-lead Gantt, compute delivery date. Environment: tCO₂/yr; gCO₂, L, MWh per 1M tokens. Location: provenance table, unresolved count, hazard classes, latency and addressable share, regulatory flags. Workload: derived utilization, served vs stranded capacity. Comparison: site table; platform × model table. Business case (toggle): margin, break-even utilization, payback.

## 19. Empirical anchors and assumptions

Anchors: Lenovo GB300 NVL72; NVIDIA and MLPerf inference results; vendor datasheets for other platforms; ASHRAE design-condition definitions; Uptime tier availability; ERA5 (Copernicus); Ember/ENTSO-E/EIA; PeeringDB; GEM and JRC hazard; WRI Aqueduct; model cards; provider price lists; per-jurisdiction sources in `jurisdictions.json`.

Baselines (all exposed): unit costs where unpublished; maturity factors; per-accelerator throughput by model class; cooling overheads and economiser parameters; tier multipliers; construction defaults; soft cost and contingency; learning rate; staff density; maintenance and insurance; route factor; TB/day/MW; design and construction durations; bridging generation costs; heat price; every trajectory default; every risk-register triple; every lead time; demand level and growth; R&D allocation.

## 20. Known limitations

No hourly dispatch or time-of-use tariff; no hourly carbon matching; no demand-response revenue; no tax structure; financing block is a simple split-structure approximation, off by default; no retrofits; no training; no embodied carbon; no sub-national polygons; no grid-topology view within a jurisdiction; supply-mix dispatch is a deterministic daily rule on capacity factors, not hourly weather-year simulation; nuclear rows depend on licensing dates that are baselines; negotiated tariffs and PPAs as published ranges only; interconnect bandwidth not modeled (multi-domain models flagged, not priced); derived throughput cells are first-order; risk register is expected-value in v1; demand and price trajectories are baselines that will be wrong in direction as well as magnitude — the tornado exists to show how much that matters.

## 21. Primary questions the model should answer

1. Among compared sites, which minimises lifecycle $/1M tokens, and how much of the gap is energy price vs climate vs construction vs delay?
2. Which site is powered first, what is binding (queue, permit, build, a named component), and what does the delay cost in undelivered tokens?
3. For a third-party owner, same building: which open-weight model yields the lowest $/1M tokens, and does serving it beat leasing the racks to a proprietary vendor?
4. Same site, same model: GB300 vs a competing platform — cost, availability date, throughput, and how sensitive the answer is to the maturity factor?
5. At this pin, which supply mix delivers firm power first, at what $/MWh and carbon, and when does an on-site option beat waiting for the grid?
6. How much MW is needed to serve a given share of latency-addressable demand, and what utilization does that imply?
7. How far does the risked result move from the unrisked one, and which risk drives it?
8. Which referenced or baseline facts, if wrong by 20%, would change the ranking of sites, platforms or models?
9. Does accepting curtailable interconnection — earlier power, fewer hours — deliver more tokens over the horizon than waiting for firm capacity?
10. How much of compute TCO is decided by the residual-value assumption alone, and does rotate-and-resell beat hold-to-refresh at this platform's curve?

## 22. Interpretation rule

The model never produces one number for "the cost of an AI data center". It produces:

> Under these visible assumptions, these dated location and catalog records, and these stated risks, this facility at this coordinate, on this platform, serving this model, is powered in this many months, costs this much per installed MW, and delivers tokens at this cost with this energy, water and carbon footprint — and this fraction of that answer rests on referenced data rather than baselines.
