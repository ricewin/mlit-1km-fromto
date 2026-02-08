"""Unit tests for app/common/utils.py"""

import zipfile
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
import requests
from shapely.geometry import Polygon


# Need to patch st.cache_data before importing utils
with patch('streamlit.cache_data', lambda **kwargs: lambda func: func):
    from app.common.utils import _unzip_csv, lonlat_to_polygon, make_polygons, merge_df


class TestUnzipCsv:
    """Test _unzip_csv function"""

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_successful_fetch_and_unzip(self, mock_get, mock_secrets):
        """Test successful fetching and unzipping of CSV data"""
        # Setup mock secrets
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        # Create a mock CSV file in a ZIP
        csv_data = "id,value\n1,100\n2,200\n"
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", csv_data)
        zip_buffer.seek(0)

        # Setup mock response
        mock_response = Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Call the function
        result = _unzip_csv("path/to/data.zip")

        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "id" in result.columns
        assert "value" in result.columns
        assert result["id"].tolist() == [1, 2]
        assert result["value"].tolist() == [100, 200]

        # Verify URL construction
        mock_get.assert_called_once_with(
            "https://example.com/data/path/to/data.zip?token=abc123", timeout=10
        )

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_url_construction_with_leading_slash(self, mock_get, mock_secrets):
        """Test URL construction when path has leading slash"""
        mock_secrets.blob.url = "https://example.com/data/"
        mock_secrets.blob.token = "?token=xyz"

        # Create a mock CSV file in a ZIP
        csv_data = "id,value\n1,100\n"
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", csv_data)
        zip_buffer.seek(0)

        mock_response = Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        _unzip_csv("/path/to/data.zip")

        # Verify URL is properly constructed without double slashes
        mock_get.assert_called_once_with(
            "https://example.com/data/path/to/data.zip?token=xyz", timeout=10
        )

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_http_request_failure(self, mock_get, mock_secrets):
        """Test handling of HTTP request failures"""
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        # Setup mock to raise exception
        mock_get.side_effect = requests.RequestException("Connection error")

        # Should raise the exception (not cache the failure)
        with pytest.raises(requests.RequestException, match="Connection error"):
            _unzip_csv("path/to/data.zip")

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_http_status_error(self, mock_get, mock_secrets):
        """Test handling of HTTP status errors"""
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        # Setup mock response with error status
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        # Should raise HTTPError (not cache the failure)
        with pytest.raises(requests.HTTPError, match="404 Not Found"):
            _unzip_csv("path/to/data.zip")

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_invalid_zip_file(self, mock_get, mock_secrets):
        """Test handling of invalid ZIP file content"""
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        # Setup mock response with invalid ZIP content
        mock_response = Mock()
        mock_response.content = b"This is not a valid ZIP file"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Should raise BadZipFile exception
        with pytest.raises(zipfile.BadZipFile):
            _unzip_csv("path/to/data.zip")

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_no_csv_in_zip(self, mock_get, mock_secrets):
        """Test handling of ZIP file with no CSV files"""
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        # Create a ZIP with non-CSV files
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("readme.txt", "This is a text file")
            zf.writestr("data.json", '{"key": "value"}')
        zip_buffer.seek(0)

        mock_response = Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Should raise ValueError
        with pytest.raises(ValueError, match="No CSV file found in ZIP archive"):
            _unzip_csv("path/to/data.zip")

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_timeout_parameter(self, mock_get, mock_secrets):
        """Test that timeout parameter is passed correctly"""
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        csv_data = "id,value\n1,100\n"
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.csv", csv_data)
        zip_buffer.seek(0)

        mock_response = Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        _unzip_csv("path/to/data.zip")

        # Verify timeout is set to 10 seconds
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 10

    @pytest.mark.unit
    @patch("app.common.utils.st.secrets")
    @patch("app.common.utils.requests.get")
    def test_multiple_csv_files_returns_first(self, mock_get, mock_secrets):
        """Test that when ZIP contains multiple CSV files, the first one is returned"""
        mock_secrets.blob.url = "https://example.com/data"
        mock_secrets.blob.token = "?token=abc123"

        # Create a ZIP with multiple CSV files
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("first.csv", "id,value\n1,100\n")
            zf.writestr("second.csv", "id,value\n2,200\n")
        zip_buffer.seek(0)

        mock_response = Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = _unzip_csv("path/to/data.zip")

        # Should return the first CSV file
        assert len(result) == 1
        assert result["id"].iloc[0] == 1
        assert result["value"].iloc[0] == 100


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
