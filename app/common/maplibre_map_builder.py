"""
#     ███╗   ███╗ █████╗ ██████╗
#     ████╗ ████║██╔══██╗██╔══██╗
#     ██╔████╔██║███████║██████╔╝
#     ██║╚██╔╝██║██╔══██║██╔═══╝
#     ██║ ╚═╝ ██║██║  ██║██║
#     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
"""

import branca.colormap as cm
import geopandas as gpd
import pandas as pd
import streamlit as st
from maplibre.layer import Layer, LayerType
from maplibre.map import Map, MapOptions
from maplibre.controls import NavigationControl, ScaleControl
from maplibre.sources import GeoJSONSource
from maplibre.streamlit import st_maplibre


def format_tooltip(value: float, value_name: str, caption: str) -> str:
    """Format tooltip text based on caption type."""
    if caption == "増減率":
        return f"{value_name}: {value:.2%}"
    else:
        return f"{value_name}: {value}"


def create_single_map(
    gdf: gpd.GeoDataFrame,
    value: str,
    colormap,
    map_center: tuple[float, float],
    zoom_start: int,
) -> Map:
    """Create a single map using maplibre Python package."""
    
    # Convert GeoDataFrame to GeoJSON and add colors to properties
    gdf_copy = gdf.copy()
    
    # Add color properties based on colormap
    gdf_copy['color'] = gdf_copy[value].apply(lambda x: colormap(x))
    
    # Add formatted tooltip values
    gdf_copy['tooltip'] = gdf_copy[value].apply(
        lambda x: format_tooltip(x, value, colormap.caption)
    )
    
    # Create map with custom style for GSI tiles
    map_options = MapOptions(
        center=map_center,
        zoom=zoom_start,
        style={
            "version": 8,
            "sources": {
                "gsi-pale": {
                    "type": "raster",
                    "tiles": ["https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png"],
                    "tileSize": 256,
                    "attribution": '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">地理院タイル</a>'
                }
            },
            "layers": [{
                "id": "gsi-pale",
                "type": "raster",
                "source": "gsi-pale"
            }]
        },
        min_zoom=9,
        max_zoom=14,
    )
    
    m = Map(map_options)
    
    # Add GeoJSON source
    geojson_source = GeoJSONSource(data=gdf_copy.__geo_interface__)
    m.add_source("geojson", geojson_source)
    
    # Add fill layer
    fill_layer = Layer(
        id="geojson-fill",
        type=LayerType.FILL,
        source="geojson",
        paint={
            "fill-color": ["get", "color"],
            "fill-opacity": 0.6
        }
    )
    m.add_layer(fill_layer)
    
    # Add line layer for borders
    line_layer = Layer(
        id="geojson-line",
        type=LayerType.LINE,
        source="geojson",
        paint={
            "line-color": ["get", "color"],
            "line-width": 1
        }
    )
    m.add_layer(line_layer)
    
    # Add tooltip
    m.add_tooltip("geojson-fill", "tooltip")
    
    # Add controls
    m.add_control(NavigationControl())
    m.add_control(ScaleControl())
    
    return m


def maplibre_map_builder(
    df: pd.DataFrame,
    gdf_1: gpd.GeoDataFrame,
    gdf_2: gpd.GeoDataFrame,
    value_1: str,
    value_2: str,
    zoom_start: int,
) -> None:
    """
    Create two separate single maps using maplibre Python package displayed side-by-side in Streamlit.

    Args:
        df (pd.DataFrame): Include latlon.
        gdf_1 (gpd.GeoDataFrame): First map data.
        gdf_2 (gpd.GeoDataFrame): Second map data.
        value_1 (str): Value 1.
        value_2 (str): Value 2.
        zoom_start (int): Zoom start level.
    """
    
    try:
        df = df.dropna(subset=["lat", "lon"])
        # IMPORTANT: Coordinate order difference between libraries
        # - Folium uses: [lat, lon] (location parameter)
        # - MapLibre uses: [lon, lat] (center parameter)
        # This is a fundamental difference between the two libraries
        map_center: tuple[float, float] = (float(df["lon"].mean()), float(df["lat"].mean()))
    except (KeyError, TypeError):
        st.error("地図表示できません。")
        return

    with st.spinner("Creating Maps...", show_time=True):
        # Create colormaps
        colormap_1 = cm.linear.Paired_06.scale(  # type: ignore
            gdf_1[value_1].min(), gdf_1[value_1].max()
        )
        colormap_1.caption = "滞在人口"

        colormap_2 = cm.linear.Accent_06.scale(  # type: ignore
            gdf_2[value_2].min(), gdf_2[value_2].max()
        )
        colormap_2.caption = "増減率"

        # Create two columns for side-by-side display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(colormap_1.caption)
            map1 = create_single_map(gdf_1, value_1, colormap_1, map_center, zoom_start)
            st_maplibre(map1, height=500)
        
        with col2:
            st.subheader(colormap_2.caption)
            map2 = create_single_map(gdf_2, value_2, colormap_2, map_center, zoom_start)
            st_maplibre(map2, height=500)
