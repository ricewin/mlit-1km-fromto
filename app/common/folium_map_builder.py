"""
#     ███╗   ███╗ █████╗ ██████╗
#     ████╗ ████║██╔══██╗██╔══██╗
#     ██╔████╔██║███████║██████╔╝
#     ██║╚██╔╝██║██╔══██║██╔═══╝
#     ██║ ╚═╝ ██║██║  ██║██║
#     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
"""

import branca.colormap as cm
import folium
import folium.plugins
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import MiniMap
from streamlit_folium import st_folium


def add_geojson_layer(map_object, gdf, value, colormap) -> None:
    for _, row in gdf.iterrows():
        if colormap.caption == "増減率":
            tooltip: str = f"{value}: {row[value]:.2%}"
        else:
            tooltip = f"{value}: {row[value]}"

        folium.GeoJson(
            data=row["geometry"],
            style_function=lambda _, pop=row[value]: {
                "fillColor": colormap(pop),
                "color": colormap(pop),
                "weight": 1,
                "fillOpacity": 0.6,
            },
            tooltip=tooltip,
        ).add_to(map_object)


def folium_map_builder(
    df: pd.DataFrame,
    gdf_1: gpd.GeoDataFrame,
    gdf_2: gpd.GeoDataFrame,
    value_1: str,
    value_2: str,
    zoom_start: int,
) -> None:
    """
    Create map.

    Args:
        df (pd.DataFrame): Include latlon.
        gdf_1 (gpd.GeoDataFrame): Left map.
        gdf_2 (gpd.GeoDataFrame): Right map.
        value_1 (str): Value 1.
        value_2 (str): Value 2.
        zoom_start (int): Zoom start level.
    """
    # 地理院タイル
    map_tile = "https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png"
    attr = """<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">地理院タイル</a>"""

    try:
        df = df.dropna(subset=["lat", "lon"])
        map_center: list[float] = [df["lat"].mean(), df["lon"].mean()]
    except (KeyError, TypeError):
        st.error("地図表示できません。")
        return

    with st.spinner("Creating Map...", show_time=True):
        m = folium.plugins.DualMap(
            location=map_center,
            tiles=map_tile,
            attr=attr,
            zoom_start=zoom_start,
            min_zoom=9,
            max_zoom=14,
            control_scale=True,
        )

        colormap_1 = cm.linear.Paired_06.scale(  # type: ignore
            gdf_1[value_1].min(), gdf_1[value_1].max()
        )
        colormap_1.caption = "滞在人口"
        # FIXME: カラーマップを左右に表示させたいのになぜか片寄ってしまう
        # 本当は左に表示させたいが、左に偏るよりは右のほうがマシなので妥協
        m.m2.add_child(colormap_1)

        add_geojson_layer(m.m1, gdf_1, value_1, colormap_1)

        colormap_2 = cm.linear.Accent_06.scale(  # type: ignore
            gdf_2[value_2].min(), gdf_2[value_2].max()
        )
        colormap_2.caption = "増減率"
        m.m2.add_child(colormap_2)

        add_geojson_layer(m.m2, gdf_2, value_2, colormap_2)

        folium.plugins.Fullscreen().add_to(m)  # type: ignore
        MiniMap(toggle_display=True, minimized=True).add_to(m.m2)

        st_folium(m, use_container_width=True, returned_objects=[])
