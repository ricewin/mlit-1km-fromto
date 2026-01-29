"""Pytest configuration and fixtures"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add app directory to Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


@pytest.fixture
def sample_dataframe():
    """Fixture providing a sample DataFrame for testing"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'lon_min': [139.0, 140.0, 141.0, 139.5, 140.5],
        'lat_min': [35.0, 36.0, 37.0, 35.5, 36.5],
        'lon_max': [139.5, 140.5, 141.5, 140.0, 141.0],
        'lat_max': [35.5, 36.5, 37.5, 36.0, 37.0],
        'lat_center': [35.25, 36.25, 37.25, 35.75, 36.75],
        'lon_center': [139.25, 140.25, 141.25, 139.75, 140.75],
        'value': [100, 200, 300, 400, 500]
    })


@pytest.fixture
def sample_geodataframe():
    """Fixture providing a sample GeoDataFrame for testing"""
    import geopandas as gpd
    from shapely.geometry import box
    
    data = {
        'value': [100, 200, 300],
        'geometry': [
            box(139.0, 35.0, 139.5, 35.5),
            box(140.0, 36.0, 140.5, 36.5),
            box(141.0, 37.0, 141.5, 37.5)
        ]
    }
    return gpd.GeoDataFrame(data)


@pytest.fixture
def sample_coordinates():
    """Fixture providing sample coordinate tuples"""
    return [
        (139.0, 35.0, 140.0, 36.0),  # (lon_min, lat_min, lon_max, lat_max)
        (140.0, 36.0, 141.0, 37.0),
        (141.0, 37.0, 142.0, 38.0)
    ]
