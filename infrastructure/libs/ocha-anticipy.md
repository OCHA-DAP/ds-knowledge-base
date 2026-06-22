---
content_type: library
name: ocha-anticipy
status: superseded
purpose: "Download and process humanitarian-risk data (CHIRPS, GloFAS, IRI, FEWS NET, USGS NDVI, COD ABs) via a unified country-config / DataSource pattern"
language: python
source_repo: ocha-dap/ocha-anticipy
source_branch: main
source_sha: c9e49cb
version: "1.1.3"
install: "pip install ocha-anticipy  # also on PyPI; pin by tag for older work"
auth_env:
  - OAP_DATA_DIR
  - IRI_AUTH
key_api:
  - create_country_config
  - create_custom_country_config
  - CountryConfig
  - GeoBoundingBox
  - ChirpsDaily
  - ChirpsMonthly
  - CodAB
  - FewsNet
  - GlofasForecast
  - GlofasReforecast
  - GlofasReanalysis
  - IriForecastProb
  - IriForecastDominant
  - UsgsNdviSmoothed
depends_on: []
used_by:
  - frameworks/bgd-flooding/2025-04-25
visibility: public
last_synced: "2026-06-22"
---

## Summary

`ocha-anticipy` (package import: `ochanticipy`) is the team's original unified data-access library for anticipatory action frameworks. It wraps six external data sources — CHIRPS rainfall, COD administrative boundaries, FEWS NET food insecurity, GloFAS river discharge, IRI seasonal forecasts, and USGS NDVI — behind a consistent `DataSource` interface: `download()` → `process()` → `load()`. A `CountryConfig` object (built from a bundled YAML or a custom file) carries per-country metadata and drives file-path layout under a local `OAP_DATA_DIR`.

**Status: superseded.** The team now uses `ocha-stratus` for all blob/DB access and `ocha-lens` for data processing. Do not use `ocha-anticipy` in new frameworks. It is still present in older framework repos (e.g. `ds-floodscan`, early `bgd-flooding` analysis) and recognising it is useful when reading or maintaining that code.

Key historical role: `ocha-anticipy` introduced the `OAP_DATA_DIR` local-filesystem convention that the team later moved away from in favour of Azure Blob storage via `ocha-stratus`.

## Install & auth

```bash
# Latest release (PyPI)
pip install ocha-anticipy

# Full extras (required for GloFAS — adds cdsapi + cfgrib)
pip install "ocha-anticipy[full]"

# Pin by tag for reproducibility in older work
pip install "ocha-anticipy==1.1.3"
```

**Environment variables required at runtime:**

| Variable | Read by | Notes |
|---|---|---|
| `OAP_DATA_DIR` | all datasources | Local directory where raw/processed files are written and read. The library reads it via `os.environ` in `config/pathconfig.py` |
| `IRI_AUTH` | `IriForecastProb`, `IriForecastDominant` | IRI Data Library auth token; read via `os.getenv("IRI_AUTH")` in the IRI datasource |

These are the only two variables the library reads from the environment itself.

**GloFAS (CDS) auth is file-based, not env.** The GloFAS datasources call `cdsapi.Client()`, which authenticates from a `~/.cdsapirc` file (`url:` + `key:` lines), per the repo's `docs/datasources/glofas.rst`. The library does not read `CDSAPI_*` env vars itself.

HDX (COD AB downloads) uses the `hdx-python-api` in read-only mode — no HDX API key is required.

## Key API

| Name | What it does |
|---|---|
| `create_country_config(iso3)` | Load a bundled per-country YAML config (COD AB layer names, GloFAS reporting points, FEWS NET region, etc.) by ISO3 code |
| `create_custom_country_config(filepath)` | Load a `CountryConfig` from a caller-supplied YAML file |
| `CountryConfig` | Pydantic model holding iso3 + optional sub-configs; validated at construction |
| `GeoBoundingBox` | Bounding-box value object passed to datasource constructors to clip spatial downloads |
| `ChirpsDaily` / `ChirpsMonthly` | Download + process CHIRPS v2.0 rainfall from IRI DL (0.05° or 0.25°, 1981–present) |
| `CodAB` | Download COD administrative boundaries from HDX; `load(admin_level=N)` returns a GeoDataFrame |
| `FewsNet` | Download FEWS NET food insecurity projections by region |
| `GlofasForecast` / `GlofasReforecast` | Download GloFAS operational forecast / reforecast from CDS; process raster → reporting-point time series |
| `GlofasReanalysis` | Download GloFAS ERA5-based reanalysis river discharge from CDS |
| `IriForecastProb` / `IriForecastDominant` | Download IRI seasonal rainfall forecast (probabilistic terciles / dominant category) |
| `UsgsNdviSmoothed` | Download and load USGS eMODIS smoothed NDVI by region |

All datasource classes follow the same three-method pattern:

```python
from ochanticipy import create_country_config, ChirpsMonthly, GeoBoundingBox

country_config = create_country_config("bgd")
bbox = GeoBoundingBox(lat_max=26.6, lat_min=20.7, lon_max=92.7, lon_min=88.0)
chirps = ChirpsMonthly(country_config=country_config, geo_bounding_box=bbox)
chirps.download()   # fetch raw NetCDF to OAP_DATA_DIR/…/raw/
chirps.process()    # clip + standardise → OAP_DATA_DIR/…/processed/
ds = chirps.load()  # returns xarray.Dataset
```

## Used by

- `frameworks/bgd-flooding/2025-04-25` — older analysis uses GloFAS via `ochanticipy`; noted as `[stale]` (framework now operates on GloFAS v4, not through this library)

Other older framework repos (pre-2023) imported `ochanticipy` directly but have not been ingested into the KB. The `OAP_DATA_DIR` pattern in any repo is a reliable signal.

## Gotchas & conventions

- **`OAP_DATA_DIR` vs `AA_DATA_DIR`.** The library writes files under `OAP_DATA_DIR`. Repos from 2023 onward shifted to `AA_DATA_DIR` for local work and then to full Azure blob storage via `ocha-stratus`. If you see both in one repo, the older analysis files likely used `ocha-anticipy`.
- **pydantic < 2.0 hard dependency.** `setup.cfg` pins `pydantic<2.0`; installing into an environment that already has pydantic v2 will break or downgrade it.
- **GloFAS requires `[full]` extras.** The base install omits `cdsapi` and `cfgrib`. Install with `pip install ocha-anticipy[full]` or add them separately.
- **CDS credential file.** GloFAS datasources rely on `cdsapi`, which authenticates from a `~/.cdsapirc` file (`url:`/`key:`). Not set by default in CI; older workflows that ran GloFAS downloads needed a secrets-injected `.cdsapirc`.
- **COD AB: HDX read-only.** No HDX key needed; `hdx-python-api` is configured in read-only mode at import time (module-level side-effect in `utils/hdx_api.py`).
- **Max 500 CDS requests per GloFAS call.** The library enforces this hard limit; split large date ranges into batches.
- **Not maintained.** Last commit August 2023 (tag 1.1.3). Bugs will not be fixed upstream; use `ocha-stratus` + `ocha-lens` for new work.

## Source

- Repo: <https://github.com/OCHA-DAP/ocha-anticipy>
- PyPI: <https://pypi.org/project/ocha-anticipy/>
- Docs: <https://ocha-anticipy.readthedocs.io/en/latest/>
- Changelog: `CHANGELOG.rst` in repo root
