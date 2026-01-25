# Implementation Architecture

## Folium vs MapLibre Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current (Folium)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Python Code (comparison.py)                                     │
│       ↓                                                           │
│  folium_map_builder(df, gdf_1, gdf_2, ...)                      │
│       ↓                                                           │
│  ┌─────────────────────────────────────┐                        │
│  │  folium.plugins.DualMap             │                        │
│  │  - Auto synchronized maps            │                        │
│  │  - Python-only API                   │                        │
│  │  - [lat, lon] coordinates            │                        │
│  └─────────────────────────────────────┘                        │
│       ↓                                                           │
│  HTML Output (Folium renders)                                    │
│       ↓                                                           │
│  Streamlit Display (html component)                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    New (MapLibre)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Python Code (comparison.py)                                     │
│       ↓                                                           │
│  maplibre_map_builder(df, gdf_1, gdf_2, ...)                   │
│       ↓                                                           │
│  ┌─────────────────────────────────────┐                        │
│  │  create_single_map() x 2            │                        │
│  │  - Map(), MapOptions()              │                        │
│  │  - GeoJSONSource, Layer             │                        │
│  │  - add_tooltip(), add_control()     │                        │
│  │  - [lon, lat] coordinates           │                        │
│  └─────────────────────────────────────┘                        │
│       ↓                                                           │
│  ┌─────────────────────────────────────┐                        │
│  │  st.columns(2)                      │                        │
│  │  ├── col1: st_maplibre(map1)       │                        │
│  │  └── col2: st_maplibre(map2)       │                        │
│  └─────────────────────────────────────┘                        │
│       ↓                                                           │
│  Streamlit Display (iframe via st_maplibre)                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────────┐
│  DataFrame      │
│  (lat, lon)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  GeoDataFrame 1 │  ──┐
│  (geometry,     │    │
│   population)   │    │
└─────────────────┘    │
                       │  Process & Style
┌─────────────────┐    │  with colormaps
│  GeoDataFrame 2 │  ──┤
│  (geometry,     │    │
│   diff)         │    │
└─────────────────┘    │
         │             │
         ↓             ↓
    ┌────────────────────────┐
    │  Add color property    │
    │  Add tooltip property  │
    └────────┬───────────────┘
             │
             ↓
    ┌────────────────────────┐
    │  Convert to GeoJSON    │
    │  (via __geo_interface__)│
    └────────┬───────────────┘
             │
             ↓
    ┌────────────────────────┐
    │  Create Map objects    │
    │  with maplibre Python  │
    │  - Map(MapOptions)     │
    │  - add_source()        │
    │  - add_layer()         │
    │  - add_tooltip()       │
    │  - add_control()       │
    └────────┬───────────────┘
             │
             ↓
    ┌────────────────────────┐
    │  Render in Streamlit   │
    │  - st.columns(2)       │
    │  - st_maplibre(map1)   │
    │  - st_maplibre(map2)   │
    │  (Independent maps)    │
    └────────────────────────┘
```

## Key Components

### 1. Python Layer (maplibre_map_builder.py)

```python
def format_tooltip(value, value_name, caption):
    # Helper function for tooltip formatting
    
def create_single_map(gdf, value, colormap, map_center, zoom_start):
    # Create a single map using maplibre Python package
    # - Create Map with MapOptions
    # - Add GeoJSONSource
    # - Add fill and line Layers
    # - Add tooltip
    # - Add NavigationControl and ScaleControl
    # Returns Map object
    
def maplibre_map_builder(df, gdf_1, gdf_2, ...):
    # Main entry point
    # - Calculate map center
    # - Create two colormaps
    # - Create two columns with st.columns(2)
    # - Render each map with st_maplibre()
```

### 2. Rendering (No JavaScript Layer)

The implementation uses the maplibre Python package exclusively:
- No custom HTML generation
- No JavaScript code
- Uses `st_maplibre()` from `maplibre.streamlit` for rendering
- Each map is rendered independently in its own iframe

## Feature Mapping

| Feature | Folium | MapLibre | Notes |
|---------|--------|----------|-------|
| Map initialization | `folium.DualMap()` | `Map(MapOptions())` x2 | Two separate instances |
| Synchronization | Built-in | None | Maps are independent |
| GeoJSON | `folium.GeoJson()` | `add_source() + add_layer()` | More control |
| Styling | `style_function` | Data-driven expressions | Properties-based |
| Tooltips | `tooltip` parameter | `add_tooltip()` method | Built into Map class |
| Controls | Auto + plugins | `add_control()` method | Manual addition |
| Rendering | `m.get_root().render()` | `st_maplibre(map)` | Streamlit component |

## Performance Characteristics

```
Folium:
- Server-side rendering
- Python generates all HTML
- Larger initial payload
- Good for small datasets
- Auto-synchronized maps

MapLibre:
- Client-side rendering  
- WebGL acceleration
- Smaller payload (JSON data)
- Excellent for large datasets
- Smoother interactions
- Independent maps (no sync)
```

## Coordinate System Difference

```
Folium:     [lat, lon]  e.g., [35.681, 139.767]
            ↕
MapLibre:   [lon, lat]  e.g., [139.767, 35.681]
            ↕
            MUST CONVERT WHEN MIGRATING
```

This is clearly documented in the code with comments.

## Implementation Details

### Current Implementation Features

**Implemented:**
- ✅ Two separate single maps displayed side-by-side
- ✅ GSI tile layer (地理院タイル)
- ✅ GeoJSON rendering with color styling
- ✅ Interactive tooltips on hover
- ✅ Navigation controls (zoom, pan)
- ✅ Scale control
- ✅ Colormap integration with branca
- ✅ Caption display (via st.subheader)

**Not Implemented:**
- ❌ Map synchronization (maps are independent)
- ❌ Fullscreen control
- ❌ Visual colormap legend on maps
- ❌ MiniMap

### Code Structure

```python
# Simplified structure
import streamlit as st
from maplibre import Map, MapOptions, Layer, LayerType
from maplibre.sources import GeoJSONSource
from maplibre.controls import NavigationControl, ScaleControl
from maplibre.streamlit import st_maplibre

# Create map
m = Map(MapOptions(center=(lon, lat), zoom=12, style={...}))
m.add_source("geojson", GeoJSONSource(data=gdf.__geo_interface__))
m.add_layer(Layer(id="fill", type=LayerType.FILL, ...))
m.add_tooltip("fill", "tooltip")
m.add_control(NavigationControl())
m.add_control(ScaleControl())

# Render
st_maplibre(m, height=500)
```
