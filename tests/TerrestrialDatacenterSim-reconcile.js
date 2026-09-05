/*
 * TerrestrialDatacenterSim-reconcile.js
 * -----------------------------------------------------------------------------
 * Drift check between the app's in-page data-test-* tags and the canonical
 * manifest (TerrestrialDatacenterSim-test-cases.json).
 *
 * It gathers every tagged element from the live DOM, compares that set against
 * what the manifest declares, and reports any drift. A clean run (report.pass
 * === true) proves the tags and the manifest agree — so neither can silently
 * fall out of sync with the other.
 *
 * No dependencies. Works in three contexts:
 *   1. Browser console / agent exec, on the app's own page:
 *        const m = await fetch('./TerrestrialDatacenterSim-test-cases.json').then(r=>r.json());
 *        console.log(JSON.stringify(reconcile(m), null, 2));
 *   2. Inside the app's in-file self-tests:
 *        import (or inline) reconcile();  assert(reconcile(MANIFEST).pass);
 *   3. Headless (Playwright):
 *        const m = require('./TerrestrialDatacenterSim-test-cases.json');
 *        const report = await page.evaluate((mf) => reconcile(mf), m);   // after injecting this file
 *
 * Version: 1.0.0  (matches manifest tag_contract >= 1.0.0)
 * -----------------------------------------------------------------------------
 */
(function (root) {
  "use strict";

  function reconcile(manifest, opts) {
    function kEq(a,b){ if(a===b) return true;
      var eq={readout:'output',output:'readout',number:'input',input:'number',action:'button',button:'action'};
      return eq[a]===b; }

    opts = opts || {};
    var doc = opts.document || (typeof document !== "undefined" ? document : null);
    if (!doc) throw new Error("reconcile: no document available (run in a browser/page context).");
    if (!manifest || !manifest.control_registry) throw new Error("reconcile: manifest with control_registry required.");

    var reg = manifest.control_registry;
    var IGNORE_PREFIX = "claude-"; // agent-injected helper elements, never part of the app

    // -------- 1. DECLARED set (what the manifest says exists) -----------------
    // Map id -> { kind, tab, label, surface: 'control' | 'output' }
    var declared = new Map();
    function decl(id, kind, tab, label, surface) {
      if (id) declared.set(id, { kind: kind, tab: tab, label: label, surface: surface });
    }
    (reg.numeric_inputs || []).forEach(function (x) { decl(x.id, "input", x.tab, x.label, "control"); });
    (reg.selects || []).forEach(function (x) { decl(x.id, "select", x.tab, x.label, "control"); });
    (reg.modal_controls || []).forEach(function (x) { decl(x.id, x.kind || "action", x.tab, x.label, "control"); });
    (reg.modal_selects || []).forEach(function (x) { decl(x.id, "select", "modal:breakeven", x.label, "control"); });
    (reg.checkboxes_3d_layers || []).forEach(function (x) { decl(x.id, "checkbox", "view3d", x.label, "control"); });
    (reg.top_bar_actions || []).forEach(function (x) { decl(x.id, "button", "global", x.label, "control"); });
    (reg.three_d_controls || []).forEach(function (x) { decl(x.id, x.type || "button", "view3d", x.label, "control"); });
    (reg.shells_view_buttons || []).forEach(function (x) { decl(x.id, "button", "shells", x.label, "control"); });
    (reg.popout_buttons || []).forEach(function (x) { if (x.id) decl(x.id, "popout", "global", x.text, "control"); });
    (reg.spec_modal || []).forEach(function (x) { decl(x.id, x.type || "button", "modal:spec", x.label, "control"); });
    (reg.breakeven_modal || []).forEach(function (x) { decl(x.id, x.type || "button", "modal:breakeven", x.label || x.id, "control"); });
    (reg.selftest_modal || []).forEach(function (x) { decl(x.id, x.type || "button", "modal:test", x.label, "control"); });
    (reg.display_registry || []).forEach(function (x) { decl(x.id, "output", x.region, x.shows, "output"); });
    // --- terrestrial-specific buckets ---
    (reg.top_bar_actions || []).forEach(function (x) { decl(x.id, "action", "global", x.label, "control"); });
    (reg.buttons_contextual || []).forEach(function (x) { decl(x.id, "action", x.tab, x.label, "control"); });
    (reg.text_file_inputs || []).forEach(function (x) { decl(x.id, x.kind || "text", x.tab, x.label, "control"); });
    (reg.numeric_inputs || []).forEach(function (x) { decl(x.id, "number", x.tab, x.label, "control"); });
    (reg.selects || []).forEach(function (x) { decl(x.id, "select", x.tab, x.label, "control"); });
    (reg.modal_controls || []).forEach(function (x) { decl(x.id, x.kind || "action", x.tab, x.label, "control"); });

    // -------- 2. TAGGED set (what the DOM actually carries) -------------------
    // Map id -> { el, kind, tab, label, surface }
    var tagged = new Map();
    doc.querySelectorAll("[data-test-id],[data-test-out]").forEach(function (e) {
      var id = e.getAttribute("data-test-id") || e.getAttribute("data-test-out");
      tagged.set(id, {
        el: e,
        kind: e.dataset.testKind || "",
        tab: e.dataset.testTab || "",
        label: e.dataset.testLabel || "",
        surface: e.hasAttribute("data-test-out") ? "output" : "control"
      });
    });

    // -------- 3. CANDIDATES that SHOULD be tagged (the drift catcher) ---------
    // Any real control element, plus any id the manifest lists as a readout.
    var candidates = new Set();
    doc.querySelectorAll("input,select,button").forEach(function (e) {
      if (e.id && e.id.indexOf(IGNORE_PREFIX) !== 0) candidates.add(e.id);
    });
    (reg.display_registry || []).forEach(function (x) {
      if (doc.getElementById(x.id)) candidates.add(x.id);
    });

    // -------- 4. Reconcile ----------------------------------------------------
    var report = {
      timestamp: new Date().toISOString(),
      manifest_version: (manifest.meta && manifest.meta.catalog_version) || "unknown",
      dom_only: [],              // tagged but not declared in manifest
      manifest_only: [],         // declared but element not found in DOM
      untagged: [],              // candidate present but missing data-test-* tags
      attr_mismatch: [],         // tag kind disagrees with manifest (hard); tab/label soft-warned
      missing_required_tags: [], // tagged element missing a required data-test-* attribute
      warnings: []               // soft: tab/label wording differences
    };

    tagged.forEach(function (t, id) { if (!declared.has(id)) report.dom_only.push(id); });
    declared.forEach(function (d, id) { if (!doc.getElementById(id)) if(!/^mix(Opt|MW|Ord|Del)\d+$/.test(id)) report.manifest_only.push(id); });
    candidates.forEach(function (id) { if (!tagged.has(id)) report.untagged.push(id); });

    var REQUIRED = [
      ["testKind", "data-test-kind"],
      ["testTab", "data-test-tab"],
      ["testLabel", "data-test-label"]
    ];
    tagged.forEach(function (t, id) {
      var missing = REQUIRED.filter(function (r) { return !t.el.dataset[r[0]]; }).map(function (r) { return r[1]; });
      if (missing.length) report.missing_required_tags.push({ id: id, missing: missing });

      var d = declared.get(id);
      if (d) {
        if (t.kind && d.kind && !kEq(t.kind, d.kind)) {
          report.attr_mismatch.push({ id: id, attr: "kind", tag: t.kind, manifest: d.kind });
        }
        // tab/label wording legitimately varies -> warn, don't fail
        if (t.tab && d.tab && t.tab !== d.tab && d.surface === "control") {
          report.warnings.push({ id: id, attr: "tab", tag: t.tab, manifest: d.tab });
        }
      }
    });

    // sort for stable diffs
    ["dom_only", "manifest_only", "untagged"].forEach(function (k) { report[k].sort(); });

    report.summary = {
      declared: declared.size,
      tagged: tagged.size,
      candidates: candidates.size,
      dom_only: report.dom_only.length,
      manifest_only: report.manifest_only.length,
      untagged: report.untagged.length,
      attr_mismatch: report.attr_mismatch.length,
      missing_required: report.missing_required_tags.length,
      warnings: report.warnings.length
    };
    report.pass =
      report.dom_only.length === 0 &&
      report.manifest_only.length === 0 &&
      report.untagged.length === 0 &&
      report.attr_mismatch.length === 0 &&
      report.missing_required_tags.length === 0;

    return report;
  }

  // Optional: build the live index straight from the tags (the "generate from DOM" helper).
  // Returns one row per tagged element — handy for regenerating the flat CSV/JSON indexes.
  function buildIndexFromDom(opts) {
    opts = opts || {};
    var doc = opts.document || document;
    return Array.prototype.map.call(
      doc.querySelectorAll("[data-test-id],[data-test-out]"),
      function (e) {
        var row = { id: e.getAttribute("data-test-id") || e.getAttribute("data-test-out") };
        Object.keys(e.dataset).forEach(function (k) {
          if (k.indexOf("test") === 0) row[k.replace(/^test/, "").replace(/^[A-Z]/, function (c) { return c.toLowerCase(); })] = e.dataset[k];
        });
        return row;
      }
    );
  }

  var api = { reconcile: reconcile, buildIndexFromDom: buildIndexFromDom, version: "1.0.0" };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) { root.reconcile = reconcile; root.buildIndexFromDom = buildIndexFromDom; }
})(typeof window !== "undefined" ? window : this);
