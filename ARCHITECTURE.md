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
│  │  create_dual_map_html()             │                        │
│  │  - Convert GeoDataFrame → GeoJSON   │                        │
│  │  - Apply colormaps to properties     │                        │
│  │  - Generate custom HTML              │                        │
│  │  - [lon, lat] coordinates            │                        │
│  └─────────────────────────────────────┘                        │
│       ↓                                                           │
│  ┌─────────────────────────────────────┐                        │
│  │  Custom HTML Template               │                        │
│  │  ├── maplibre-gl.js (v4.0.0)       │                        │
│  │  ├── maplibre-gl-compare.js        │                        │
│  │  ├── Two Map instances              │                        │
│  │  ├── GeoJSON layers                 │                        │
│  │  └── Synchronized controls          │                        │
│  └─────────────────────────────────────┘                        │
│       ↓                                                           │
│  Streamlit Display (html component)                              │
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
    └────────┬───────────────┘
             │
             ↓
    ┌────────────────────────┐
    │  Inject into HTML      │
    │  template with:        │
    │  - Map configurations  │
    │  - Layer definitions   │
    │  - Event handlers      │
    └────────┬───────────────┘
             │
             ↓
    ┌────────────────────────┐
    │  Render in Browser     │
    │  - Left map (before)   │
    │  - Right map (after)   │
    │  - Synchronized views  │
    └────────────────────────┘
```

## Key Components

### 1. Python Layer (maplibre_map_builder.py)

```python
def format_tooltip(value, value_name, caption):
    # Helper function for tooltip formatting
    
def create_dual_map_html(gdf_1, gdf_2, ...):
    # Convert GeoDataFrames to GeoJSON
    # Add color and tooltip properties
    # Generate HTML with JavaScript code
    
def maplibre_map_builder(df, gdf_1, gdf_2, ...):
    # Main entry point
    # Same interface as folium_map_builder
```

### 2. JavaScript Layer (in HTML template)

```javascript
// Two MapLibre GL JS instances
var beforeMap = new maplibregl.Map({...});
var afterMap = new maplibregl.Map({...});

// Add GeoJSON sources and layers
beforeMap.addSource('geojson1', {...});
afterMap.addSource('geojson2', {...});

// Add interactive features
beforeMap.on('mousemove', 'geojson1-fill', ...);

// Synchronize with maplibre-gl-compare
var compare = new maplibregl.Compare(beforeMap, afterMap);
```

## Feature Mapping

| Feature | Folium | MapLibre | Notes |
|---------|--------|----------|-------|
| Map initialization | `folium.DualMap()` | `maplibregl.Map()` x2 | Two separate instances |
| Synchronization | Built-in | `maplibre-gl-compare` | External library |
| GeoJSON | `folium.GeoJson()` | `addSource() + addLayer()` | More control |
| Styling | `style_function` | Data-driven expressions | Properties-based |
| Tooltips | `tooltip` parameter | Popup on events | Event-driven |
| Controls | Auto + plugins | Manual addition | More flexible |

## Performance Characteristics

```
Folium:
- Server-side rendering
- Python generates all HTML
- Larger initial payload
- Good for small datasets

MapLibre:
- Client-side rendering  
- WebGL acceleration
- Smaller payload (JSON data)
- Excellent for large datasets
- Smoother interactions
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
