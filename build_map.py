"""
Data Centers vs. Electricity Disconnections — Folium Choropleth Map
Source data:
  - EIA Residential Utility Disconnections Report (April 2026 / 2024 data)
  - LBNL 2024 US Data Center Energy Usage Report
Output: dc_vs_disconnections_map.html
"""

import pandas as pd
import folium
import pathlib
import requests

# ── Paths ────────────────────────────────────────────────────────────────────
try:
    ROOT = pathlib.Path(__file__).resolve().parent
except NameError:
    ROOT = pathlib.Path.cwd()          # Colab / Jupyter fallback

DATA = ROOT / 'data'

# ── Load CSVs ─────────────────────────────────────────────────────────────────
disc = pd.read_csv(DATA / 'disconnections_state.csv')
centers = pd.read_csv(DATA / 'datacenters_state.csv')

# Clean abbreviations
disc['state_abbr'] = disc['state_abbr'].astype(str).str.strip().str.upper()
centers['state_abbr'] = centers['state_abbr'].astype(str).str.strip().str.upper()

# Disconnection rate per 100 customers
disc['disc_per_100'] = (100.0 * disc['disconnections_2024'] / disc['customers_2024']).round(2)

# ── Merge ─────────────────────────────────────────────────────────────────────
merged = disc.merge(centers, on='state_abbr', how='inner', suffixes=('_disc', '_dc'))

if merged.empty:
    raise SystemExit(
        'Joined dataframe is empty.\n'
        f'  disconnections abbrs : {disc[\"state_abbr\"].tolist()}\n'
        f'  datacenters abbrs    : {centers[\"state_abbr\"].tolist()}'
    )

print(f'Merged {len(merged)} states.')

# ── GeoJSON ───────────────────────────────────────────────────────────────────
# folium example GeoJSON: feature.id = 2-letter state abbreviation
geo_url = (
    'https://raw.githubusercontent.com/python-visualization/folium'
    '/master/examples/data/us-states.json'
)
geo = requests.get(geo_url, timeout=30).json()

# ── Base map ──────────────────────────────────────────────────────────────────
m = folium.Map(location=[39.8, -98.6], zoom_start=4, tiles='cartodbpositron')

# ── Choropleth — disconnection rate ───────────────────────────────────────────
folium.Choropleth(
    geo_data=geo,
    data=merged,
    columns=['state_abbr', 'disc_per_100'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.85,
    line_opacity=0.6,
    nan_fill_color='#e5e5e5',
    legend_name='Electric disconnections per 100 customers (2024)',
).add_to(m)

# ── State centroids ───────────────────────────────────────────────────────────
centroids = {
    'AL': (32.8, -86.8), 'AZ': (34.2, -111.7), 'AR': (34.8, -92.2),
    'CA': (37.2, -119.5), 'CO': (39.0, -105.5), 'CT': (41.6, -72.7),
    'DC': (38.9, -77.0), 'FL': (27.5, -81.7), 'GA': (32.7, -83.3),
    'IL': (40.0, -89.0), 'IN': (40.0, -86.3), 'KY': (37.5, -85.3),
    'LA': (31.1, -92.0), 'MD': (39.0, -76.7), 'MA': (42.4, -71.8),
    'MI': (44.2, -84.7), 'MN': (46.5, -94.5), 'MS': (32.7, -89.7),
    'MO': (38.5, -92.5), 'NC': (35.5, -79.9), 'NJ': (40.1, -74.5),
    'NY': (42.9, -75.0), 'OH': (40.4, -82.8), 'OK': (35.6, -97.5),
    'OR': (44.0, -120.5), 'PA': (41.0, -77.5), 'SC': (34.0, -81.0),
    'TN': (35.8, -86.4), 'TX': (31.0, -99.0), 'VA': (37.5, -78.8),
    'WA': (47.4, -120.0), 'WI': (44.5, -89.5),
}

# ── Data center bubbles ───────────────────────────────────────────────────────
for _, row in merged.iterrows():
    abbr = row['state_abbr']
    if abbr not in centroids:
        continue

    lat, lon = centroids[abbr]
    size = max(4.0, float(row['dc_mw'] or 0) ** 0.5)

    popup_html = (
        f"<b>{row['state_disc']}</b><br>"
        f"Disconnections: {int(row['disconnections_2024']):,}<br>"
        f"Customers: {int(row['customers_2024']):,}<br>"
        f"Rate: {row['disc_per_100']:.2f} per 100<br>"
        f"Data centers: {int(row['dc_count'])} (~{int(row['dc_mw'])} MW)"
    )

    folium.CircleMarker(
        location=[lat, lon],
        radius=size,
        color='#1d4ed8',
        fill=True,
        fill_color='#3b82f6',
        fill_opacity=0.75,
        tooltip=row['state_disc'],
        popup=folium.Popup(popup_html, max_width=260),
    ).add_to(m)

folium.LayerControl().add_to(m)

# ── Save ──────────────────────────────────────────────────────────────────────
outfile = ROOT / 'dc_vs_disconnections_map.html'
m.save(str(outfile))
print(f'Wrote {outfile}')
