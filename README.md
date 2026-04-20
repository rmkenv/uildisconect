# Data Centers vs. Power Disconnections Map

This repo builds a state-level choropleth of **residential electricity disconnection rates**
using EIA Form EIA-112 (2024 Residential Utility Disconnections) and overlays bubble markers
sized by **data center capacity** (MW) from the latest LBNL / DOE U.S. data center report.

The goal is to visualize where AI/data center growth overlaps most sharply with residential
shutoffs.

## Project Structure

- `build_map.py` – main script that joins the two CSVs and emits `dc_vs_disconnections_map.html`.
- `data/disconnections_state.csv` – template for state-level disconnection data.
- `data/datacenters_state.csv` – template for state-level data center capacity.
- `requirements.txt` – minimal Python dependencies.

## Data Requirements

### 1. Disconnections (EIA-112)

Create `data/disconnections_state.csv` with one row per state and these columns:

```text
state,state_abbr,disconnections_2024,customers_2024
Florida,FL,1500000,10123456
Virginia,VA,230000,3456789
...
```

- `disconnections_2024`: total residential electricity disconnections in calendar year 2024.
- `customers_2024`: total residential customers served by that utility/state.

Both can be derived from the April 2026 EIA Residential Utility Disconnections report
and underlying Form EIA-112 data.

### 2. Data centers (LBNL / DOE)

Create `data/datacenters_state.csv` with one row per state and these columns:

```text
state,state_abbr,dc_count,dc_mw
Virginia,VA,120,6500
Georgia,GA,45,2100
...
```

- `dc_count`: count of large data centers.
- `dc_mw`: estimated IT + facility load in MW for those sites in 2024 or latest year.

You can approximate this from the latest LBNL / DOE data center energy usage report
and public siting datasets.

## How It Works

1. `build_map.py` reads both CSVs, computes a **disconnection rate per 100 customers** for
   each state, and performs an inner join on `state_abbr`.
2. It downloads a US states GeoJSON and builds a Folium choropleth of `disc_per_100`.
3. It overlays circle markers at state centroids sized by `sqrt(dc_mw)` so that very large
   data center clusters stand out.
4. The result is written to `dc_vs_disconnections_map.html` in the repo root.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Fill in the two CSVs under data/
python build_map.py

# Open the output in a browser
open dc_vs_disconnections_map.html  # macOS
# or
start dc_vs_disconnections_map.html  # Windows
```

Once you have the HTML map, you can:

- Screen-record a short flyover for Twitter/X, LinkedIn, or Reddit.
- Export static PNGs of key states for a newsletter.
- Extend the script to support a time slider once you assemble monthly panel data.

## Extending the Repo

- Swap the basemap tiles to a dark theme for better contrast in presentations.
- Add a second layer for **natural gas disconnections**.
- Add a small Flask / FastAPI wrapper so visitors can toggle between years or
  policies and see how the map changes.
