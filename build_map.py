"""Builds a state-level choropleth of electricity disconnection rates
and overlays bubbles sized by data center capacity.

Inputs (CSV, required):

1) data/disconnections_state.csv
   columns: state, state_abbr, disconnections_2024, customers_2024

2) data/datacenters_state.csv
   columns: state, state_abbr, dc_count, dc_mw

Output: dc_vs_disconnections_map.html in the repo root.
"""

import pandas as pd
import folium
import pathlib
import requests

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / 'data'

# --- load your real data here ---
disc = pd.read_csv(DATA / 'disconnections_state.csv')
centers = pd.read_csv(DATA / 'datacenters_state.csv')

# compute disconnection rate per 100 customers
disc['disc_per_100'] = 100.0 * disc['disconnections_2024'] / disc['customers_2024']

# join on state_abbr
merged = disc.merge(centers, on='state_abbr', how='inner', suffixes=('_disc','_dc'))

# quick safety check
if merged.empty:
    raise SystemExit('Joined dataframe is empty – check state_abbr values in both CSVs.')

# load US states geojson (postal codes as id)
geo_url = 'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json'
geo = requests.get(geo_url, timeout=30).json()

# base map
m = folium.Map(location=[39.8, -98.6], zoom_start=4, tiles='cartodbpositron')

# choropleth for disconnection rate
folium.Choropleth(
    geo_data=geo,
    data=merged,
    columns=['state_abbr','disc_per_100'],
    key_on='feature.properties.postal',
    fill_color='YlOrRd',
    fill_opacity=0.85,
    line_opacity=0.6,
    legend_name='Electric disconnections per 100 customers (2024)',
).add_to(m)

# simple centroid lookup; extend as needed
centroids = {
    'AL': (32.8, -86.8), 'AZ': (34.2, -111.7), 'CA': (37.2, -119.5), 'CO': (39.0, -105.5),
    'CT': (41.6, -72.7), 'DC': (38.9, -77.0), 'FL': (27.5, -81.7), 'GA': (32.7, -83.3),
    'IL': (40.0, -89.0), 'IN': (40.0, -86.3), 'KY': (37.5, -85.3), 'LA': (31.1, -92.0),
    'MD': (39.0, -76.7), 'MA': (42.4, -71.8), 'MI': (44.2, -84.7), 'MN': (46.5, -94.5),
    'MO': (38.5, -92.5), 'NC': (35.5, -79.9), 'NJ': (40.1, -74.5), 'NY': (42.9, -75.0),
    'OH': (40.4, -82.8), 'OK': (35.6, -97.5), 'OR': (44.0, -120.5), 'PA': (41.0, -77.5),
    'SC': (34.0, -81.0), 'TN': (35.8, -86.4), 'TX': (31.0, -99.0), 'VA': (37.5, -78.8),
    'WA': (47.4, -120.0), 'WI': (44.5, -89.5), 'AZ': (34.2, -111.7)
}

# overlay data center bubbles
for _, row in merged.iterrows():
    abbr = row['state_abbr']
    if abbr not in centroids:
        continue
    lat, lon = centroids[abbr]
    size = max(4.0, (row['dc_mw'] or 0) ** 0.5)  # sqrt scale, guard against 0
    popup = folium.Popup(
        f"{row['state_disc']}
"
        f"Disconnections: {row['disconnections_2024']:,}
"
        f"Customers: {row['customers_2024']:,}
"
        f"Rate: {row['disc_per_100']:.2f} per 100
"
        f"Data centers: {row['dc_count']} (~{row['dc_mw']:.0f} MW)",
        max_width=260,
    )
    folium.CircleMarker(
        location=[lat, lon],
        radius=size,
        color='#2563eb',
        fill=True,
        fill_color='#3b82f6',
        fill_opacity=0.75,
        popup=popup,
    ).add_to(m)

folium.LayerControl().add_to(m)

outfile = ROOT / 'dc_vs_disconnections_map.html'
m.save(str(outfile))
print(f'Wrote {outfile}')
