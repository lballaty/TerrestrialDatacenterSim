# UI Testability Convention — `data-test-*` tags + manifest + reconciliation

**Version:** 1.0.0 · **Status:** Draft for Review
**Applies to:** Terrestrial AI Data Center Siting and Economics Model (this repo) — the same reusable house standard first used on the Orbital model, and intended across the single-file apps (Drafting Grid, Intendit, ArionComply).
**Companions:** `TerrestrialDatacenterSim-test-cases.json` (the manifest) · `TerrestrialDatacenterSim-reconcile.js` (the drift check)

---

## 1. The idea in one paragraph

Every element a user can act on, and every value a user reads, carries a small **identifier tag inside the element itself** (`data-test-*` attributes). That makes the whole UI *self-describing*: an agent (or a person) can point at the running page and discover everything, with no external document. The heavier detail that won't fit in an attribute — validity rules, expected direction, formulas, baseline values — lives once in a **manifest** file, keyed by the same identifier. A small **reconciliation script** walks the live page, gathers all the tags, and checks them against the manifest. If anyone adds, renames, or removes an element without updating the manifest (or vice-versa), the script fails and names exactly what drifted. Three parts, one job: **the tags say what exists, the manifest says what it means, the script keeps them honest.**

In this app the tags are applied **programmatically at load** (a short pass over every `.pane`, `.actions`, modal and readout element), so a new control is tagged automatically as long as it has an `id` and a label — and the reconciler catches anything that slips through. The convention is therefore enforced by construction, not by hand-editing each element.

---

## 2. Why not just rely on the `id` attribute?

An `id` tells you *which* element, but not *what kind* it is, *which tab* it lives on, *what it shows*, or *what unit* it's in — and `id`s are also used for styling and app logic, so they can change for reasons unrelated to testing. The `data-test-*` layer is a **purpose-built, stable contract** alongside the `id`. To keep it cheap, **`data-test-id` mirrors the existing `id`** — no new identifiers, just descriptive labels next to them.

---

## 3. The attribute schema

### On every **interactive** element (input, select, action button, file, template row control)

| Attribute | Required | Meaning | Example |
|---|---|---|---|
| `data-test-id` | ✅ | Mirrors the DOM `id` | `data-test-id="tariff"` |
| `data-test-kind` | ✅ | `number · text · select · action · file` | `data-test-kind="number"` |
| `data-test-tab` | ✅ | Where it lives: `site · power · climate · build · compute · econ · time · global · modal:breakeven · modal:spec · modal:test` | `data-test-tab="power"` |
| `data-test-label` | ✅ | Short human name (matches the visible label) | `data-test-label="Electricity tariff, $/MWh"` |
| `data-test-gated-by` | optional | `id` of the select that unlocks/locks this input | `data-test-gated-by="pueMode"` |
| `data-test-dir` | optional | Expected-direction hint | `data-test-dir="util-up->tokc-down"` |
| `data-test-unit` | optional | Unit string | `data-test-unit="$/MWh"` |

### On every **readout** the user reads (KPI, derived value, table, badge, note, warning)

| Attribute | Required | Meaning | Example |
|---|---|---|---|
| `data-test-id` (or `data-test-out`) | ✅ | Mirrors the DOM `id` | `data-test-id="tok"` |
| `data-test-kind` | ✅ | Always `readout` | `data-test-kind="readout"` |
| `data-test-tab` | ✅ | Region it appears in | `data-test-tab="results"` |
| `data-test-label` | ✅ | What it shows | `data-test-label="Delivered cost / 1M tokens"` |
| `data-test-role` | optional | `kpi · derived · badge · note · table · warning` | `data-test-role="kpi"` |

**What stays out of the tags and lives only in the manifest:** defaults/min/max/step, select option lists, mode-gating rules, validity checks, expected direction, formulas, baseline (oracle) values, and which suite covers the element. Tags are the *index*; the manifest is the *reference book*.

Discover the whole UI in one line:
```js
document.querySelectorAll('[data-test-id], [data-test-out]');
```

---

## 4. App-specific vocabulary

- **Tabs / regions (`data-test-tab`):** `site`, `power`, `climate`, `build`, `compute`, `econ`, `time`, `results`, `global`, `modal:breakeven`, `modal:spec`, `modal:test`.
- **Kinds (`data-test-kind`):** `number`, `text`, `select`, `action`, `file`, `readout`.
- **Dynamic power-mix rows.** The supply-mix rows (`mixOpt{i}`, `mixMW{i}`, `mixOrd{i}`, `mixDel{i}`) are created at runtime by the template engine and tagged as they are built. Because their count varies, they are **not enumerated in the manifest**; the reconciler lists them as `dom_only` **INFO**, never failures. The stable handles the manifest does carry are the template select (`mixTemplate`) and the add button (`mixAdd`).

---

## 5. How the three parts fit together

```
   ┌─────────────────────┐        ┌──────────────────────────────┐
   │  index.html          │        │  manifest                     │
   │  data-test-* tags     │◄──────►│  test-cases.json              │
   │  (applied at load)    │ recon- │  (validity, direction,        │
   │                       │ cile   │   formulas, baselines, suites)│
   └─────────┬────────────┘        └──────────────┬───────────────┘
             └──────────► reconcile.js ◄───────────┘
                    reports: untagged / dom_only /
                    manifest_only / attr_mismatch /
                    missing_required   →   pass:true/false
```

`reconcile.js` is **not app-specific** — it reads whatever the manifest declares. `kEq()` treats the equivalent kind names (`readout`≡`output`, `number`≡`input`, `action`≡`button`) as matching, and `mix*{i}` ids are exempt from `manifest_only`.

---

## 6. The drift-free workflow

1. The load-time tagging pass in `index.html` tags every `.pane`/`.actions`/modal/readout element with the four required attributes.
2. The manifest (`test-cases.json`) carries the rich detail, keyed by the same id.
3. Run the reconciliation on the page — or headlessly (the repo does this in the in-file self-tests and in CI via jsdom):
   ```js
   const m = await fetch('./TerrestrialDatacenterSim-test-cases.json').then(r=>r.json());
   console.log(JSON.stringify(reconcile(m), null, 2));   // reconcile.js loaded first
   ```
4. Fix what it names, repeat until `pass: true`:
   - **`untagged`** — a real control/readout with no `data-test-*`. *The load pass missed it — extend the selector.*
   - **`dom_only`** — tagged but not in the manifest. *Add a manifest entry (or it's a dynamic mix row → INFO).*
   - **`manifest_only`** — in the manifest but no element found. *Removed/renamed — update the manifest.*
   - **`attr_mismatch`** — a tag's `kind` disagrees with the manifest after `kEq()` (hard). `tab`/`label` differences are soft **warnings**.
   - **`missing_required_tags`** — a tagged element missing one of the four required attributes.
5. The in-file **Run self-tests** already asserts tag completeness; wire `reconcile(MANIFEST).pass` there too for full drift protection.
6. **Regenerate the flat indexes from the page:** `buildIndexFromDom()` returns one row per tagged element, so `element-index.csv` and `display-index.csv` are *generated*, not hand-maintained. The running page is the single source of truth.

---

## 7. Adopting this on the next UI

1. Copy §3's four required attributes as a hard rule.
2. Define that UI's own `data-test-tab` vocabulary.
3. Ship a manifest in the same shape and the same `reconcile.js`.
4. Add the `reconcile(...).pass` assertion to that app's self-tests from day one.

**Review flags.** (1) `data-test-label` is a short form, not necessarily the exact visible label — reconciler treats differences as warnings. (2) The page is the source of truth; regenerate the manifest's registry and the CSVs from the DOM rather than hand-editing. (3) When a future version stabilises the mix-row ids, enumerate them in the manifest and drop the `dom_only` exemption.
