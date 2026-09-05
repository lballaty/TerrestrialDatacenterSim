# Test Plan — Terrestrial AI Data Center Siting and Economics Model

**Target:** `https://<owner>.github.io/TerrestrialDatacenterSim/` (app v0.4 at authoring)
**Plan version:** 1.0.0 · **Authored:** 2026-09-05 · **Status:** Draft for Review
**Machine-readable companion:** `TerrestrialDatacenterSim-test-cases.json` (the executable catalog this document wraps)
**Flat reference indexes:** `TerrestrialDatacenterSim-element-index.csv` (111 interactive elements) · `TerrestrialDatacenterSim-display-index.csv` (23 read-only readouts)
**Owner:** Libor Ballaty · Arion Networks s.r.o.

> Same intent and coverage model as the Orbital model's test system, adapted to this app's controls. The Markdown here is the *methodology, protocol and acceptance criteria*; the JSON companion is the *executable spec* (control registry + parametric test cases + reasonableness oracle). Run them together. Written for an **LLM browser agent** to execute autonomously and for a human to audit.

---

## 1. Scope and objectives

The app is a **single-file, client-side HTML scenario model**. No backend; every result is computed in-browser. On a served origin it additionally fetches `data/*.json` to override embedded presets, and that data path is itself tested (S10).

Two orthogonal goals, tested on every surface:

| Axis | Question | How it is tested |
|---|---|---|
| **Functional ("does it work")** | Does every button, dropdown, input, template, modal and readout respond without error? | Suites S1–S8, S10–S13 |
| **Validity ("is the result usable")** | Are the numbers physically and economically reasonable, and is the text meaningful (no `NaN`, no empty derived fields, correct direction)? | Suite S9 + the 25 `reasonableness_rules` |

**Coverage target: 100%** of interactive controls and displayed readouts. The JSON catalog enumerates the exact inventory so coverage is measurable:

- **72** numeric inputs across 7 tabs
- **19** dropdowns in the main tabs (+ 3 modal selects)
- **16** action buttons (10 global, 6 contextual) + dynamic power-mix row buttons
- **7** supply-mix templates driving a merit-order dispatch
- **3** modals (Specification, Break-even solver, Self-tests)
- **1** custom-site subsystem (save / export / import) and **1** scenario JSON download
- **23** read-only readouts the user *reads* — the 8 headline KPIs, the CAPEX and opex tables, the LCOE and dispatch tables, the provenance table, the dynamic **Model cautions** box and the footer integrity line (indexed in `display_registry` / `display-index.csv`, tested by suite **S12**)

### Out of scope
The GitHub Actions data build (`scripts/*.py`, `.github/workflows/pages.yml`), the upstream sources' uptime (Ember, PeeringDB, Copernicus), and browser-vendor rendering bugs. Perf is out of scope except the smoke-level "recalc returns promptly." Rendered CSS layout on a real phone is a human check, not agent-testable here.

### Assumptions
- Control **DOM `id`s are stable** and equal `data-test-id`. The runner self-heals and reports drift if they change (§4).
- The **power-mix rows are dynamic**: ids `mixOpt{i}`/`mixMW{i}`/`mixOrd{i}`/`mixDel{i}` are created by the template engine and carry tags but are not enumerated in the manifest; the reconciler lists them as `dom_only` INFO, never failures.
- The **oracle baseline** (§6) is the v0.4 default scenario (US-VA, 40 MW hall, grid template). Numeric drift as the model evolves is expected — the plan distinguishes *drift* (INFO/flag) from *defect* (FAIL) by tolerance and by sign/structure.
- The **parity self-test ($0.247) is authoritative** over the oracle if the two ever disagree.

### Review flags (confirm manually)
- Any **self-test FAIL** — the app's own regression anchors outrank everything else (parity $0.2473, composition $12.14M, LCOE $111.7/MWh).
- Any KPI **drift beyond ±2%** from the oracle.
- **Download / Export** side-effects (S8) — permissioned actions.
- **Served-origin data load** (S10) — only runs where the page is served, not from `file://`.

---

## 2. Test environment

| Item | Value |
|---|---|
| URL under test | `https://<owner>.github.io/TerrestrialDatacenterSim/` (or a local `http://` server for S10) |
| App type | Static single-file HTML + inline JS/SVG |
| Agent capabilities | DOM read/enumerate, set input + dispatch events, click, read `<output>`/KPIs, read a Blob/download |
| Network | Only S10 (curated data load) needs a served origin; no third-party egress in v0.4 |
| State | `localStorage` holds custom sites and saved mixes — clear between runs if testing a clean load |
| Determinism | Always click **Recalculate** (`#calc`) before reading KPIs; **Reset** (`#reset`) between destructive suites |

---

## 3. How an agent reads and drives the app (I/O primitives)

The app auto-recalculates on change, but **always force `#calc`** before reading.

```js
const setNum = (id, v) => { const el=document.getElementById(id); el.value=String(v);
  el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); };
const setSel = (id, v) => { const el=document.getElementById(id); el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
const recalc = () => document.getElementById('calc').click();
const kpi = (id) => document.getElementById(id).textContent.trim();
const editable = (id) => { const el=document.getElementById(id); return !(el.disabled||el.readOnly||el.offsetParent===null); };
```

Headline KPIs to read after recalc (full list in JSON `runner_protocol.result_kpi_ids`): `tok` (delivered $/1M tokens), `capexMW`, `kwmo`, `ttp`, `pueMW`, `gpuh`, `env`, `avail`.

Selecting a **site**: `setSel('sitePreset', 'IE')`. Selecting a **mix template**: `setSel('mixTemplate','bridge')` — this rebuilds the dynamic rows. Editing a mix row: `setNum('mixMW0', 60)`.

---

## 4. Agent runner protocol

1. **Load & smoke (S1).** Open URL, assert title, assert baseline KPIs render, capture console errors.
2. **Establish baseline.** `#reset` → `#calc` → snapshot the KPI vector; compare to oracle (§6).
3. **Navigate (S2).** Visit each of the 7 tabs; assert its registered controls become visible.
4. **Functional sweep.**
   - **S3 numerics** — for each of the 72 inputs: nominal, low (min), high (×10), invalid-negative, invalid-text, restore. *Mode-gated inputs* (`tFac`,`tOpex`,`tAvail`,`pueManual`): enable the governing mode first; a correctly-locked field is a PASS for gating.
   - **S4 dropdowns** — select **every option** of all 19 selects; confirm the documented effect and any field unlock/lock.
   - **S5 cooling & PUE** — each cooling architecture sets its cap and overhead; toggle derived/manual PUE.
   - **S6 power mix** — build each of the 7 templates; confirm an eligible mix, editable rows, add/delete, and that the LCOE and dispatch tables render with no NaN; confirm the firm-power month and binding-term logic.
   - **S7 modals** — Specification (+ own-window + file fallback), Break-even (**every `beTarget` × `beGoal`**), Self-tests (**all must pass**).
   - **S8 actions** — Recalculate, Reset (returns to baseline), Download JSON (round-trip), custom-site save/export/import.
5. **Validity sweep (S9).** Run all 25 `reasonableness_rules` on baseline and on their stated perturbations.
6. **Data layers (S10).** On a served origin, confirm `data/jurisdictions.json` and `data/power_options.json` override embedded rows and the status line names the source; on `file://` confirm graceful fallback to presets.
7. **Cross-field (S11).** Walk every `mode_gated_inputs` entry; verify the mode select locks/unlocks the field.
8. **Display (S12) and reconciliation (S13).** Read all 23 readouts for meaning and consistency; run `reconcile(MANIFEST)` and assert `pass === true`.
9. **Report.** Emit per `report_schema`; reset to baseline between destructive suites.

### Self-healing & drift
- **Missing id:** re-enumerate `[...document.querySelectorAll('input,select,button')].map(e=>e.id)`. If the control resurfaced under a new id, log `DRIFT` (old→new). If gone, log `MISSING` + block that case.
- **Dynamic mix rows:** never treat a `mix*{i}` id as MISSING; they exist only after a template builds them.
- **New controls not in the registry:** log `INFO: uncatalogued control <id>` so the catalog stays honest.

---

## 5. Test suites (summary — full steps in the JSON)

| Suite | Name | What it proves | Type |
|---|---|---|---|
| **S1** | Smoke / load | App loads, no console errors, KPIs render | Functional |
| **S2** | Tab navigation | All 7 tabs reveal their controls | Functional |
| **S3** | Numeric inputs | All 72 inputs accept/clamp/reject; never emit NaN | Functional + Validity |
| **S4** | Dropdowns | Every option of all 19 selects applies its effect | Functional |
| **S5** | Cooling & PUE | Architecture caps + derived/manual PUE (R9–R11) | Functional + Validity |
| **S6** | Power mix & templates | 7 templates build eligible mixes; LCOE + dispatch tables; time-to-power (R12–R16) | Functional + Validity |
| **S7** | Modals | Spec, Break-even (all option pairs), Self-tests | Functional + Validity |
| **S8** | Global actions | Recalculate, Reset→baseline, Download round-trip, custom-site round-trip (R22, R23) | Functional + Validity |
| **S9** | Reasonableness | 25 physics/economics/text sanity rules | **Validity** |
| **S10** | Data layers | Curated files override presets on a served origin; graceful fallback on file:// | Functional (origin-gated) |
| **S11** | Cross-field & mode gating | Mode selects lock/unlock the right fields | Functional + Validity |
| **S12** | Display / output completeness | All 23 readouts render meaningful, consistent values | **Validity** |
| **S13** | Tag reconciliation | `reconcile(MANIFEST).pass === true`; no undocumented drift | **Validity** |

---

## 6. Oracle — the reasonableness baseline

Reset defaults (v0.4: US-VA, 40 MW hall, Tier III, DLC, grid+backup template, derived PUE, straight-line salvage, horizon 15 yr, discount 8%) must reproduce, within **±2%** (sign and structure exact):

| KPI | Expected |
|---|---|
| Delivered $/1M tokens (`tok`) | **$0.234** |
| Initial CAPEX / MW IT incl. compute (`capexMW`) | **$39.14M** |
| Time to power (`ttp`) | **42 months**, binding = power mix |
| PUE · facility MW (`pueMW`) | **1.14 · ~53 MW** |
| Effective availability (`avail`) | **99.98%** |
| Carbon / 1M tokens (`env`) | **~37 gCO₂ · 0 L** |

**Authoritative anchors (self-tests — outrank the oracle):**

| Anchor | Value |
|---|---|
| Orbital parity, stub inputs | **$0.2473 / 1M tokens** (±0.2%) |
| §10.2 composition, US-avg, Tier III, air, grid-only | **$12.14M / MW IT** (±5%) |
| LCOE closed form, recips 90% CF, $40 gas, 8% | **$111.7 / MWh** |

**Drift vs defect:** a value 1–2% off after a legitimate model tweak is `INFO`/flag. A **sign flip**, a **≥10× jump**, a **blank/NaN**, or a **broken derivation** (e.g. installed units no longer `ceil(mw·1000/rkw)·(1+spare)`) is a `FAIL`.

### The 25 reasonableness rules (validity core)

Full text in JSON `reasonableness_rules`; highlights:

- **R1/R21 — Integrity:** no `NaN`, `Infinity`, `undefined`, `[object Object]`, or empty derived readouts anywhere.
- **R2 — Non-negative economics:** `tok, capexMW, kwmo, gpuh ≥ 0`.
- **R3 — Baseline anchor:** the table above. **R4/R5/R14 — self-test anchors** (parity, composition, LCOE) are authoritative.
- **R6 — Unit derivation:** installed units and IT MW derive correctly and move monotonically with `mw`, `rkw`.
- **R7/R8 — Monotone drivers:** ↑`util`, ↑`tpsmw` lower `tok`; ↑`tariff`, ↑`rcost`, ↑`disc` raise it.
- **R9/R10/R11 — Cooling:** derived PUE bounded, consistent with facility MW, and a warning fires when unit TDP exceeds the architecture cap.
- **R12/R13 — Timeline & power:** `ttp` = max of the three candidate terms with the correct binding term named; a mix that cannot cover load reports "never" with a red caution.
- **R15/R16 — Dispatch:** merit-order used cheapest-first; on-site plant adds its CAPEX row.
- **R17 — Availability bounds.** **R18 — Provenance counting.** **R19 — Tornado ordering.**
- **R20 — Parity invariance:** in full parity mode, bypassed catalogs/templates must not move the parity figure.
- **R22/R23 — Round-trips:** scenario JSON and custom-site export/import.
- **R24 — Layout no overflow.** **R25 — Tag reconciliation passes.**

---

## 7. Pass / fail criteria

- **Case PASS:** control responds as specified **and** its reasonableness rule(s), if any, hold.
- **Case FAIL:** crash/console error, NaN/blank/`undefined` in any output, wrong directional behavior, a warning that fires when it shouldn't (or is silent when it should), a self-test FAIL, or oracle drift beyond tolerance with sign/structure break.
- **BLOCKED:** cannot run (e.g. S10 from `file://`) — not counted against quality.
- **DRIFT:** id/label changed but behavior intact — fix the catalog, not the app.
- **INFO:** benign numeric drift within tolerance, an uncatalogued new control, or a dynamic mix-row id.

**Suite gate:** the run is a release blocker if any `severity: critical` rule (R1, R2, R4, R21) fails, if a self-test fails, or if any global action (Recalculate/Reset/Download) fails.

---

## 8. Reporting

Emit one JSON report per run following `report_schema`: a `run` header, a `summary` (passed/failed/blocked/drift/info + `coverage_pct`), a `coverage_manifest`, a `findings` array (one entry per case), and `review_flags`. Rank findings most-severe first. Coverage is reported as a fraction of the registry:

```
numeric_inputs_tested: 72/72   selects_tested: 19/19   buttons: 16/16
templates: 7/7   modals: 3/3   display_readouts: 23/23
rules_run: 25/25   reconcile_pass: true   coverage_pct: 100.0
```

---

## 9. Completeness checklist

- [ ] All 7 tabs navigated (S2)
- [ ] All 72 numeric inputs: nominal + boundary + invalid (S3)
- [ ] All 19 dropdowns: every option exercised (S4)
- [ ] Each cooling architecture + PUE mode (S5)
- [ ] All 7 mix templates build eligible mixes; rows add/edit/delete; LCOE + dispatch tables render (S6)
- [ ] Spec modal: render + own-window + file fallback (S7)
- [ ] Break-even: **every `beTarget` × `beGoal`** pair (S7)
- [ ] Self-tests run; all pass; any FAIL captured verbatim (S7)
- [ ] Recalculate / Reset→baseline / Download round-trip / custom-site round-trip (S8)
- [ ] Curated data override on a served origin; fallback on file:// (S10, or BLOCKED w/ reason)
- [ ] All `mode_gated_inputs` lock/unlock verified (S11)
- [ ] All 23 display readouts render + respond + stay consistent (S12)
- [ ] Model cautions box fires/clears correctly (S12 / R11–R13)
- [ ] All 25 reasonableness rules run (S9)
- [ ] `reconcile(MANIFEST).pass === true` (S13)
- [ ] Oracle baseline compared (§6)
- [ ] Report emitted with coverage manifest (§8)

---

## 10. Gap review (author's notes before sign-off)

Confirmed by direct DOM inspection of the running v0.4 page — every id, option and readout in the catalog was read from the live DOM via `buildIndexFromDom`, not inferred. The in-file self-tests already assert tag completeness (`reconcile`-equivalent) and all numeric anchors, so a headless run reproduces this plan's core without a browser. Open items for a reviewer:

1. **Dynamic mix rows.** Ids depend on the number of rows a template creates; the manifest lists the template select and add button only, and the reconciler ignores `mix*{i}` ids. If a future version fixes row ids, enumerate them. *(Review flag.)*
2. **Served-origin S10.** From `file://` the curated-data load is correctly skipped; validate the offline path (embedded presets + status line) instead. A local `http://` server or the Pages site is needed for the override path.
3. **Derived-field editability.** `pueOut`, `unitsOut`, `mixCostOut`, `tPowerOut` are read-only outputs, not inputs; the plan tests them as readouts (S12), not free inputs.
4. **Numeric tolerance (±2%).** Chosen to absorb legitimate model iteration; the self-tests carry tighter anchors and are authoritative if the two disagree.
5. **Label vs visible text.** `data-test-label` is a short form; the reconciler treats label/tab wording differences as warnings, not failures.

---

*Filenames are intentionally version-free so re-uploads overwrite cleanly; version is tracked inside each file's header. Companion files: `TerrestrialDatacenterSim-test-cases.json`, `TerrestrialDatacenterSim-reconcile.js`, `TerrestrialDatacenterSim-tagging-convention.md`, `TerrestrialDatacenterSim-element-index.csv`, `TerrestrialDatacenterSim-display-index.csv`.*
