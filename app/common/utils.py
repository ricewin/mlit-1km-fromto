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
def _unzip_csv(url: str) -> pd.DataFrame:
    response: requests.Response = requests.get(url)
    f = BytesIO(response.content)

    with zipfile.ZipFile(f) as z:
        file_list: list[str] = z.namelist()

        # st.write("ZIPファイル内のファイル:", file_list)

        for filename in file_list:
            if filename.endswith(".csv"):
                with z.open(filename) as csv_file:
                    df: pd.DataFrame = pd.read_csv(csv_file)
                    # st.write(f"*CSV file: {filename}*")
                    # st.write(df.head())

    return df


def fetch_data(f: str, year: int) -> pd.DataFrame:
    ss: SessionStateProxy = st.session_state

    path = "https://ricewin.blob.core.windows.net/assets/"

    if f == "mesh1km":
        if year == 2019:
            path += "attribute/attribute_mesh1km_2019.csv.zip"

        else:
            path += "attribute/attribute_mesh1km_2020.csv.zip"

    else:
        pcode = list(ss.pref)[0]

        if ss.set == "mdp":
            path += f"{f}/{pcode:02}/{year}/{ss.month:02}/monthly_{f}_mesh1km.csv.zip"
        elif ss.set == "fromto":
            path += f"{f}/{pcode:02}/{year}/{ss.month:02}/monthly_{f}_city.csv.zip"

    path += st.secrets.azure_blob.sas_token
    return _unzip_csv(path)


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
    polygons: list[Polygon] = [
        lonlat_to_polygon(*row)
        for row in df[["lon_min", "lat_min", "lon_max", "lat_max"]].to_numpy()
    ]

    gdf = gpd.GeoDataFrame(df[[value]], geometry=polygons)  # type: ignore
    return gdf
