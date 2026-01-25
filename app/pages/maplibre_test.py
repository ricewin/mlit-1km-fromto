"""Test page for maplibre dual map implementation."""

import traceback

import geopandas as gpd
import pandas as pd
import streamlit as st
from common.maplibre_map_builder import maplibre_map_builder
from shapely.geometry import Point

st.title("MapLibre Single Maps Test")
st.write("Testing two separate MapLibre maps displayed side-by-side")

# Create simple test data
test_data = {
    "lat": [35.681236, 35.691236, 35.701236],
    "lon": [139.767125, 139.777125, 139.787125],
}
df_test = pd.DataFrame(test_data)

# Create simple GeoDataFrames with polygon data
# Create test geometries (simple buffers around points)
gdf_1_data = []
gdf_2_data = []

for row in df_test.itertuples():
    point = Point(float(row.lon), float(row.lat))  # pyright: ignore[reportArgumentType]
    buffer = point.buffer(0.01)  # roughly 1km buffer
    index_val: int = int(float(row.Index))  # pyright: ignore[reportArgumentType]

    gdf_1_data.append(
        {
            "geometry": buffer,
            "population": 100 + index_val * 50,
        }
    )

    gdf_2_data.append(
        {
            "geometry": buffer,
            "diff": 0.1 + index_val * 0.05,
        }
    )

gdf_1 = gpd.GeoDataFrame(gdf_1_data, crs="EPSG:4326")
gdf_2 = gpd.GeoDataFrame(gdf_2_data, crs="EPSG:4326")

st.write("Test GeoDataFrame 1 (滞在人口):", gdf_1)
st.write("Test GeoDataFrame 2 (増減率):", gdf_2)

# Test the maplibre map builder
try:
    maplibre_map_builder(df_test, gdf_1, gdf_2, "population", "diff", zoom_start=12)
    st.success("MapLibre single maps rendered successfully!")
except Exception as e:
    st.error(f"Error rendering map: {e}")
    st.code(traceback.format_exc())
