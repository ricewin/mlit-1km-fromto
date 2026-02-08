"""
#     ██╗   ██╗████████╗██╗██╗     ███████╗
#     ██║   ██║╚══██╔══╝██║██║     ██╔════╝
#     ██║   ██║   ██║   ██║██║     ███████╗
#     ██║   ██║   ██║   ██║██║     ╚════██║
#     ╚██████╔╝   ██║   ██║███████╗███████║
#      ╚═════╝    ╚═╝   ╚═╝╚══════╝╚══════╝
"""

import zipfile
from io import BytesIO

import geopandas as gpd
import pandas as pd
import requests
import streamlit as st
from shapely.geometry import Polygon, box
from streamlit.runtime.state.session_state_proxy import SessionStateProxy


@st.cache_data(show_spinner="unzip...")
def _unzip_csv(path: str) -> pd.DataFrame:
    """
    Fetch and unzip CSV data from blob storage.
    
    Args:
        path: Relative path to the ZIP file in blob storage
        
    Returns:
        DataFrame containing the CSV data
        
    Raises:
        requests.RequestException: If the HTTP request fails
        zipfile.BadZipFile: If the downloaded content is not a valid ZIP file
        ValueError: If no CSV file is found in the ZIP archive
    """
    base = st.secrets.blob.url.rstrip("/")
    clean_path = path.lstrip("/")
    url = f"{base}/{clean_path}?{st.secrets.blob.token.lstrip('?')}"

    # Fetch the ZIP file
    response: requests.Response = requests.get(url, timeout=10)
    response.raise_for_status()
    f = BytesIO(response.content)

    # Extract CSV from ZIP
    try:
        with zipfile.ZipFile(f) as z:
            file_list: list[str] = z.namelist()

            for filename in file_list:
                if filename.endswith(".csv"):
                    with z.open(filename) as csv_file:
                        df: pd.DataFrame = pd.read_csv(csv_file)
                        return df
            
            # No CSV found in the archive
            raise ValueError(f"No CSV file found in ZIP archive at {path}")
    except zipfile.BadZipFile as e:
        raise zipfile.BadZipFile(f"Invalid ZIP file downloaded from {path}") from e


def fetch_data(f: str, year: int) -> pd.DataFrame:
    """
    Fetch data based on the specified parameters.
    
    Args:
        f: Data type (e.g., "mesh1km", etc.)
        year: Year of the data
        
    Returns:
        DataFrame containing the fetched data
    """
    ss: SessionStateProxy = st.session_state

    if f == "mesh1km":
        if year == 2019:
            path = "attribute/attribute_mesh1km_2019.csv.zip"
        else:
            path = "attribute/attribute_mesh1km_2020.csv.zip"
    else:
        pcode = list(ss.pref)[0]

        if ss.set == "mdp":
            path = f"{f}/{pcode:02}/{year}/{ss.month:02}/monthly_{f}_mesh1km.csv.zip"
        elif ss.set == "fromto":
            path = f"{f}/{pcode:02}/{year}/{ss.month:02}/monthly_{f}_city.csv.zip"

    try:
        return _unzip_csv(path)
    except requests.RequestException:
        st.error("データの取得に失敗しました: ネットワークエラーが発生しました")
        st.stop()
    except zipfile.BadZipFile:
        st.error("データの取得に失敗しました: ファイル形式が正しくありません")
        st.stop()
    except ValueError:
        st.error("データの取得に失敗しました: ファイルに必要なデータが見つかりませんでした")
        st.stop()


def merge_df(df_left, df_right, on, how, suffixes, drop) -> pd.DataFrame:
    df: pd.DataFrame = pd.merge(
        df_left,
        df_right,
        on=on,
        how=how,
        suffixes=suffixes,
    )

    if drop:
        df.drop(columns=[col for col in df.columns if suffixes[1] in col], inplace=True)

    df = df.rename(columns={"lat_center": "lat", "lon_center": "lon"})

    return df


def lonlat_to_polygon(
    lon_min: float, lat_min: float, lon_max: float, lat_max: float
) -> Polygon:
    return box(lon_min, lat_min, lon_max, lat_max)


def make_polygons(df: pd.DataFrame, value: str) -> gpd.GeoDataFrame:
    """
    四隅の緯度・経度からポリゴンを生成する.

    Args:
        df (pd.DataFrame): メッシュコードを含むデータ.
        value (str): 生成された GeoDataFrame に保持する列の名前.

    Returns:
        gpd.GeoDataFrame: ポリゴンを含むデータ.
    """
    coords = df[["lon_min", "lat_min", "lon_max", "lat_max"]].to_numpy()
    polygons = [lonlat_to_polygon(*row) for row in coords]

    gdf = gpd.GeoDataFrame(df[[value]].copy(), geometry=polygons)
    return gdf
