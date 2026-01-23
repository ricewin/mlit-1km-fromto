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
from streamlit.components.v1 import html


def format_tooltip(value: float, value_name: str, caption: str) -> str:
    """Format tooltip text based on caption type."""
    if caption == "増減率":
        return f"{value_name}: {value:.2%}"
    else:
        return f"{value_name}: {value}"


def create_single_map_html(
    gdf: gpd.GeoDataFrame,
    value: str,
    colormap,
    map_center: list[float],
    zoom_start: int,
    map_id: str = "map"
) -> str:
    """Create a single map HTML using MapLibre GL JS."""
    
    import json
    
    # Convert GeoDataFrame to GeoJSON and add colors to properties
    gdf_copy = gdf.copy()
    
    # Add color properties based on colormap
    gdf_copy['color'] = gdf_copy[value].apply(lambda x: colormap(x))
    
    # Add formatted tooltip values
    gdf_copy['tooltip'] = gdf_copy[value].apply(
        lambda x: format_tooltip(x, value, colormap.caption)
    )
    
    # Convert to GeoJSON
    geojson_data = json.dumps(gdf_copy.__geo_interface__)
    
    single_map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{colormap.caption}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://unpkg.com/maplibre-gl@4.0.0/dist/maplibre-gl.js"></script>
        <link href="https://unpkg.com/maplibre-gl@4.0.0/dist/maplibre-gl.css" rel="stylesheet" />
        <style>
            body {{ margin: 0; padding: 0; }}
            #{map_id} {{
                position: absolute;
                top: 0;
                bottom: 0;
                width: 100%;
            }}
            .legend {{
                background-color: white;
                padding: 10px;
                margin: 10px;
                border-radius: 3px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                font-size: 12px;
                position: absolute;
                bottom: 30px;
                left: 10px;
                z-index: 1;
            }}
            .maplibregl-popup {{
                max-width: 200px;
            }}
            .maplibregl-popup-content {{
                padding: 8px;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div id="{map_id}"></div>
        
        <!-- Legend -->
        <div class="legend">
            <strong>{colormap.caption}</strong>
        </div>
        
        <script>
            var geojson = {geojson_data};

            var map = new maplibregl.Map({{
                container: '{map_id}',
                style: {{
                    version: 8,
                    sources: {{
                        'gsi-pale': {{
                            type: 'raster',
                            tiles: ['https://cyberjapandata.gsi.go.jp/xyz/pale/{{z}}/{{x}}/{{y}}.png'],
                            tileSize: 256,
                            attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">地理院タイル</a>'
                        }}
                    }},
                    layers: [{{
                        id: 'gsi-pale',
                        type: 'raster',
                        source: 'gsi-pale'
                    }}]
                }},
                center: {map_center},
                zoom: {zoom_start},
                minZoom: 9,
                maxZoom: 14
            }});

            // Add GeoJSON layers when map is loaded
            map.on('load', function() {{
                map.addSource('geojson', {{
                    type: 'geojson',
                    data: geojson
                }});
                
                map.addLayer({{
                    id: 'geojson-fill',
                    type: 'fill',
                    source: 'geojson',
                    paint: {{
                        'fill-color': ['get', 'color'],
                        'fill-opacity': 0.6
                    }}
                }});
                
                map.addLayer({{
                    id: 'geojson-line',
                    type: 'line',
                    source: 'geojson',
                    paint: {{
                        'line-color': ['get', 'color'],
                        'line-width': 1
                    }}
                }});
                
                // Add hover popup
                var popup = new maplibregl.Popup({{
                    closeButton: false,
                    closeOnClick: false
                }});
                
                map.on('mousemove', 'geojson-fill', function(e) {{
                    map.getCanvas().style.cursor = 'pointer';
                    var tooltip = e.features[0].properties.tooltip;
                    popup.setLngLat(e.lngLat).setHTML(tooltip).addTo(map);
                }});
                
                map.on('mouseleave', 'geojson-fill', function() {{
                    map.getCanvas().style.cursor = '';
                    popup.remove();
                }});
            }});

            // Add navigation controls
            map.addControl(new maplibregl.NavigationControl());
            map.addControl(new maplibregl.ScaleControl());
            map.addControl(new maplibregl.FullscreenControl());
        </script>
    </body>
    </html>
    """
    
    return single_map_html


def maplibre_map_builder(
    df: pd.DataFrame,
    gdf_1: gpd.GeoDataFrame,
    gdf_2: gpd.GeoDataFrame,
    value_1: str,
    value_2: str,
    zoom_start: int,
) -> None:
    """
    Create two separate single maps using MapLibre displayed side-by-side in Streamlit.

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
        map_center: list[float] = [float(df["lon"].mean()), float(df["lat"].mean())]
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
            map1_html = create_single_map_html(
                gdf_1, value_1, colormap_1, map_center, zoom_start, "map1"
            )
            html(map1_html, height=500)
        
        with col2:
            st.subheader(colormap_2.caption)
            map2_html = create_single_map_html(
                gdf_2, value_2, colormap_2, map_center, zoom_start, "map2"
            )
            html(map2_html, height=500)
