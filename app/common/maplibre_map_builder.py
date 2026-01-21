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


def create_dual_map_html(
    gdf_1: gpd.GeoDataFrame,
    gdf_2: gpd.GeoDataFrame,
    value_1: str,
    value_2: str,
    colormap_1,
    colormap_2,
    map_center: list[float],
    zoom_start: int
) -> str:
    """Create synchronized dual map HTML using maplibre-gl-compare."""
    
    import json
    
    # Convert GeoDataFrames to GeoJSON and add colors to properties
    gdf_1_copy = gdf_1.copy()
    gdf_2_copy = gdf_2.copy()
    
    # Add color properties based on colormap
    gdf_1_copy['color'] = gdf_1_copy[value_1].apply(lambda x: colormap_1(x))
    gdf_2_copy['color'] = gdf_2_copy[value_2].apply(lambda x: colormap_2(x))
    
    # Add formatted tooltip values
    gdf_1_copy['tooltip'] = gdf_1_copy[value_1].apply(
        lambda x: format_tooltip(x, value_1, colormap_1.caption)
    )
    gdf_2_copy['tooltip'] = gdf_2_copy[value_2].apply(
        lambda x: format_tooltip(x, value_2, colormap_2.caption)
    )
    
    # Convert to GeoJSON
    geojson_1 = json.dumps(gdf_1_copy.__geo_interface__)
    geojson_2 = json.dumps(gdf_2_copy.__geo_interface__)
    
    dual_map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dual Map Comparison</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://unpkg.com/maplibre-gl@4.0.0/dist/maplibre-gl.js"></script>
        <link href="https://unpkg.com/maplibre-gl@4.0.0/dist/maplibre-gl.css" rel="stylesheet" />
        <script src="https://unpkg.com/maplibre-gl-compare@1.0.0/dist/maplibre-gl-compare.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/maplibre-gl-compare@1.0.0/dist/maplibre-gl-compare.css" type="text/css" />
        <style>
            body {{ margin: 0; padding: 0; }}
            #comparison-container {{
                position: absolute;
                top: 0;
                bottom: 0;
                width: 100%;
            }}
            .map {{
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
                z-index: 1;
            }}
            .legend-left {{
                left: 10px;
            }}
            .legend-right {{
                right: 10px;
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
        <div id="comparison-container">
            <div id="before" class="map"></div>
            <div id="after" class="map"></div>
        </div>
        
        <!-- Legends -->
        <div class="legend legend-left">
            <strong>{colormap_1.caption}</strong>
        </div>
        <div class="legend legend-right">
            <strong>{colormap_2.caption}</strong>
        </div>
        
        <script>
            var geojson1 = {geojson_1};
            var geojson2 = {geojson_2};

            var beforeMap = new maplibregl.Map({{
                container: 'before',
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

            var afterMap = new maplibregl.Map({{
                container: 'after',
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

            // Add GeoJSON layers when maps are loaded
            beforeMap.on('load', function() {{
                beforeMap.addSource('geojson1', {{
                    type: 'geojson',
                    data: geojson1
                }});
                
                beforeMap.addLayer({{
                    id: 'geojson1-fill',
                    type: 'fill',
                    source: 'geojson1',
                    paint: {{
                        'fill-color': ['get', 'color'],
                        'fill-opacity': 0.6
                    }}
                }});
                
                beforeMap.addLayer({{
                    id: 'geojson1-line',
                    type: 'line',
                    source: 'geojson1',
                    paint: {{
                        'line-color': ['get', 'color'],
                        'line-width': 1
                    }}
                }});
                
                // Add hover popup
                var popup1 = new maplibregl.Popup({{
                    closeButton: false,
                    closeOnClick: false
                }});
                
                beforeMap.on('mousemove', 'geojson1-fill', function(e) {{
                    beforeMap.getCanvas().style.cursor = 'pointer';
                    var tooltip = e.features[0].properties.tooltip;
                    popup1.setLngLat(e.lngLat).setHTML(tooltip).addTo(beforeMap);
                }});
                
                beforeMap.on('mouseleave', 'geojson1-fill', function() {{
                    beforeMap.getCanvas().style.cursor = '';
                    popup1.remove();
                }});
            }});

            afterMap.on('load', function() {{
                afterMap.addSource('geojson2', {{
                    type: 'geojson',
                    data: geojson2
                }});
                
                afterMap.addLayer({{
                    id: 'geojson2-fill',
                    type: 'fill',
                    source: 'geojson2',
                    paint: {{
                        'fill-color': ['get', 'color'],
                        'fill-opacity': 0.6
                    }}
                }});
                
                afterMap.addLayer({{
                    id: 'geojson2-line',
                    type: 'line',
                    source: 'geojson2',
                    paint: {{
                        'line-color': ['get', 'color'],
                        'line-width': 1
                    }}
                }});
                
                // Add hover popup
                var popup2 = new maplibregl.Popup({{
                    closeButton: false,
                    closeOnClick: false
                }});
                
                afterMap.on('mousemove', 'geojson2-fill', function(e) {{
                    afterMap.getCanvas().style.cursor = 'pointer';
                    var tooltip = e.features[0].properties.tooltip;
                    popup2.setLngLat(e.lngLat).setHTML(tooltip).addTo(afterMap);
                }});
                
                afterMap.on('mouseleave', 'geojson2-fill', function() {{
                    afterMap.getCanvas().style.cursor = '';
                    popup2.remove();
                }});
            }});

            // Add navigation controls
            beforeMap.addControl(new maplibregl.NavigationControl());
            afterMap.addControl(new maplibregl.NavigationControl());
            afterMap.addControl(new maplibregl.ScaleControl());
            
            // Add fullscreen control
            beforeMap.addControl(new maplibregl.FullscreenControl());

            // Create comparison
            var compare = new maplibregl.Compare(beforeMap, afterMap, '#comparison-container');
        </script>
    </body>
    </html>
    """
    
    return dual_map_html


def maplibre_map_builder(
    df: pd.DataFrame,
    gdf_1: gpd.GeoDataFrame,
    gdf_2: gpd.GeoDataFrame,
    value_1: str,
    value_2: str,
    zoom_start: int,
) -> None:
    """
    Create dual map using maplibre.

    Args:
        df (pd.DataFrame): Include latlon.
        gdf_1 (gpd.GeoDataFrame): Left map.
        gdf_2 (gpd.GeoDataFrame): Right map.
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

    with st.spinner("Creating Map...", show_time=True):
        # Create colormaps
        colormap_1 = cm.linear.Paired_06.scale(  # type: ignore
            gdf_1[value_1].min(), gdf_1[value_1].max()
        )
        colormap_1.caption = "滞在人口"

        colormap_2 = cm.linear.Accent_06.scale(  # type: ignore
            gdf_2[value_2].min(), gdf_2[value_2].max()
        )
        colormap_2.caption = "増減率"

        # Create dual map HTML
        dual_html = create_dual_map_html(
            gdf_1, gdf_2,
            value_1, value_2,
            colormap_1, colormap_2,
            map_center,
            zoom_start
        )
        
        html(dual_html, height=600)
