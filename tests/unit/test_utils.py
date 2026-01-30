"""Unit tests for app/common/utils.py"""

import pandas as pd
import pytest
from shapely.geometry import Polygon

from app.common.utils import lonlat_to_polygon, make_polygons, merge_df


class TestLonlatToPolygon:
    """Test lonlat_to_polygon function"""

    @pytest.mark.unit
    def test_basic_polygon_creation(self):
        """Test creating a basic polygon from coordinates"""
        lon_min, lat_min = 139.0, 35.0
        lon_max, lat_max = 140.0, 36.0

        polygon = lonlat_to_polygon(lon_min, lat_min, lon_max, lat_max)

        assert isinstance(polygon, Polygon)
        bounds = polygon.bounds
        assert bounds == (lon_min, lat_min, lon_max, lat_max)

    @pytest.mark.unit
    def test_zero_area_polygon(self):
        """Test polygon with zero area (point)"""
        lon, lat = 139.5, 35.5

        polygon = lonlat_to_polygon(lon, lat, lon, lat)

        assert isinstance(polygon, Polygon)
        assert polygon.area == 0

    @pytest.mark.unit
    def test_negative_coordinates(self):
        """Test polygon with negative coordinates"""
        lon_min, lat_min = -140.0, -36.0
        lon_max, lat_max = -139.0, -35.0

        polygon = lonlat_to_polygon(lon_min, lat_min, lon_max, lat_max)

        assert isinstance(polygon, Polygon)
        bounds = polygon.bounds
        assert bounds == (lon_min, lat_min, lon_max, lat_max)


class TestMergeDf:
    """Test merge_df function"""

    @pytest.mark.unit
    def test_basic_merge(self):
        """Test basic dataframe merge"""
        df_left = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "lat_center": [35.0, 36.0, 37.0],
                "lon_center": [139.0, 140.0, 141.0],
                "value": [10, 20, 30],
            }
        )

        df_right = pd.DataFrame({"id": [1, 2, 3], "extra": ["a", "b", "c"]})

        result = merge_df(
            df_left, df_right, on="id", how="left", suffixes=("", "_right"), drop=False
        )

        assert "lat" in result.columns
        assert "lon" in result.columns
        assert "lat_center" not in result.columns
        assert "lon_center" not in result.columns
        assert len(result) == 3

    @pytest.mark.unit
    def test_merge_with_drop(self):
        """Test merge with dropping suffix columns"""
        df_left = pd.DataFrame(
            {
                "id": [1, 2],
                "lat_center": [35.0, 36.0],
                "lon_center": [139.0, 140.0],
                "value": [10, 20],
            }
        )

        df_right = pd.DataFrame({"id": [1, 2], "value": [100, 200]})

        result = merge_df(
            df_left, df_right, on="id", how="left", suffixes=("", "_right"), drop=True
        )

        assert "value" in result.columns
        assert "value_right" not in result.columns
        assert result["value"].tolist() == [10, 20]


class TestMakePolygons:
    """Test make_polygons function"""

    @pytest.mark.unit
    def test_make_polygons_basic(self):
        """Test creating polygons from DataFrame"""
        df = pd.DataFrame(
            {
                "lon_min": [139.0, 140.0],
                "lat_min": [35.0, 36.0],
                "lon_max": [139.5, 140.5],
                "lat_max": [35.5, 36.5],
                "population": [1000, 2000],
            }
        )

        gdf = make_polygons(df, "population")

        assert len(gdf) == 2
        assert "population" in gdf.columns
        assert "geometry" in gdf.columns
        assert all(isinstance(geom, Polygon) for geom in gdf.geometry)

    @pytest.mark.unit
    def test_make_polygons_preserves_values(self):
        """Test that make_polygons preserves the value column"""
        df = pd.DataFrame(
            {
                "lon_min": [139.0],
                "lat_min": [35.0],
                "lon_max": [140.0],
                "lat_max": [36.0],
                "count": [500],
            }
        )

        gdf = make_polygons(df, "count")

        assert gdf["count"].iloc[0] == 500
        assert len(gdf.columns) == 2  # count and geometry

    @pytest.mark.unit
    def test_make_polygons_multiple_rows(self):
        """Test make_polygons with multiple rows"""
        df = pd.DataFrame(
            {
                "lon_min": [139.0, 140.0, 141.0],
                "lat_min": [35.0, 36.0, 37.0],
                "lon_max": [139.5, 140.5, 141.5],
                "lat_max": [35.5, 36.5, 37.5],
                "value": [100, 200, 300],
            }
        )

        gdf = make_polygons(df, "value")

        assert len(gdf) == 3
        assert gdf["value"].tolist() == [100, 200, 300]
