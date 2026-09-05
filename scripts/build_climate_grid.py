#!/usr/bin/env python3
"""Build the 1° climate grid from ERA5 (Copernicus Climate Data Store), spec §6.1.

Per land cell: Tdb_99.6, Twb_99.6, Tdb_ann, Twb_ann, h_econ[T] for T in {12,15,18,21,24,27,30} °C (wet-bulb),
h_dry[T] for T in {18,24,30,35} °C (dry-bulb), h_extreme (Twb > 30), trend_K_per_yr, elev.
Wet-bulb from 2 m temperature, 2 m dew point and surface pressure (Stull 2011 via RH; exact psychrometric
iteration is a later refinement). Ten most recent full years.

Requirements: `cdsapi` and `netCDF4`/`xarray` in the runner, and CDS_TOKEN in the environment
(https://cds.climate.copernicus.eu — free account). Without them, or if the request fails, the previously
published bundle is kept so the site never regresses. Open-Meteo is deliberately NOT used here: its
call-weighting makes a global 10-year hourly pull ~7.5M weighted calls (spec §2.1 #8).

Output: { "built", "source": "ERA5 (C3S/ECMWF) via CDS", "licence": "CC BY 4.0 (Copernicus licence)",
          "years": [y0, y1], "res_deg": 1, "cells": { "lat,lon": {...}, ... } }
"""
import json, os, sys, pathlib, datetime as dt

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/data/climate_grid.json")
FALLBACK = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
WB_T = [12, 15, 18, 21, 24, 27, 30]
DB_T = [18, 24, 30, 35]

def keep_previous(reason):
    print(f"climate grid not rebuilt: {reason}", file=sys.stderr)
    if FALLBACK and FALLBACK.exists():
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(FALLBACK.read_text()); print(f"kept previous bundle from {FALLBACK}"); return 0
    print("no previous bundle; the tool will use its embedded site presets", file=sys.stderr)
    return 0  # not fatal: the page degrades to presets

def main():
    if not os.environ.get("CDS_TOKEN"):
        return keep_previous("CDS_TOKEN not set")
    try:
        import cdsapi, numpy as np, xarray as xr  # noqa: F401
    except ImportError as e:
        return keep_previous(f"missing dependency: {e}")
    try:
        import math
        y1 = dt.date.today().year - 1; y0 = y1 - 9
        c = cdsapi.Client(url="https://cds.climate.copernicus.eu/api", key=os.environ["CDS_TOKEN"])
        target = "era5_hourly.nc"
        c.retrieve("reanalysis-era5-single-levels", {
            "product_type": "reanalysis", "format": "netcdf", "grid": [1.0, 1.0],
            "variable": ["2m_temperature", "2m_dewpoint_temperature", "surface_pressure", "land_sea_mask", "geopotential"],
            "year": [str(y) for y in range(y0, y1 + 1)], "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)], "time": [f"{h:02d}:00" for h in range(24)],
        }, target)
        ds = xr.open_dataset(target)
        t = ds["t2m"] - 273.15; td = ds["d2m"] - 273.15
        rh = 100 * np.exp(17.625 * td / (243.04 + td)) / np.exp(17.625 * t / (243.04 + t))
        twb = (t * np.arctan(0.151977 * np.sqrt(rh + 8.313659)) + np.arctan(t + rh) - np.arctan(rh - 1.676331)
               + 0.00391838 * rh ** 1.5 * np.arctan(0.023101 * rh) - 4.686035)
        lsm = ds["lsm"].isel(time=0) if "time" in ds["lsm"].dims else ds["lsm"]
        elev = (ds["z"].isel(time=0) if "time" in ds["z"].dims else ds["z"]) / 9.80665
        hours = t.sizes["time"]; years = hours / 8766
        cells = {}
        for la in ds.latitude.values:
            for lo in ds.longitude.values:
                if float(lsm.sel(latitude=la, longitude=lo)) < 0.5:
                    continue
                tt = t.sel(latitude=la, longitude=lo).values; ww = twb.sel(latitude=la, longitude=lo).values
                ann_t = tt.reshape(-1, 8766)[:, :] if False else tt
                cells[f"{float(la):.0f},{float(lo):.0f}"] = {
                    "Tdb_99.6": round(float(np.percentile(tt, 99.6)), 1), "Twb_99.6": round(float(np.percentile(ww, 99.6)), 1),
                    "Tdb_ann": round(float(tt.mean()), 1), "Twb_ann": round(float(ww.mean()), 1),
                    "h_econ": {str(T): int((ww < T).sum() / years) for T in WB_T},
                    "h_dry": {str(T): int((tt < T).sum() / years) for T in DB_T},
                    "h_extreme": int((ww > 30).sum() / years),
                    "trend_K_per_yr": round(float(np.polyfit(np.arange(len(tt)) / 8766, tt, 1)[0]), 3),
                    "elev": int(float(elev.sel(latitude=la, longitude=lo))),
                }
        bundle = {"built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "source": "ERA5 (C3S/ECMWF) via CDS",
                  "licence": "Copernicus licence, attribution required", "years": [y0, y1], "res_deg": 1, "cells": cells}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(bundle, separators=(",", ":")))
        print(f"wrote {OUT} with {len(cells)} land cells ({OUT.stat().st_size/1e6:.1f} MB)")
        return 0
    except Exception as e:  # noqa: BLE001
        return keep_previous(str(e))

if __name__ == "__main__":
    sys.exit(main())
