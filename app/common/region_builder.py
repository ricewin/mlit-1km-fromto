"""Region Builder

Use:
    prefecture, cities = region_builder()
"""

from typing import Any, Hashable

import pandas as pd
import streamlit as st


@st.cache_data
def _load_region() -> pd.DataFrame:
    return pd.read_csv(
        "https://raw.githubusercontent.com/ricewin/mlit-1km-fromto/refs/heads/main/"
        "assets/regioncode_master_utf8_2020.csv"
    )


@st.cache_data
def _load_city() -> pd.DataFrame:
    return pd.read_csv(
        "https://raw.githubusercontent.com/ricewin/mlit-1km-fromto/refs/heads/main/"
        "assets/prefcode_citycode_master_utf8_2020.csv"
    )


@st.cache_data
def prefcode_to_name() -> tuple[dict[Any, Any], dict[Any, Any]]:
    """
    都道府県コードと都道府県名の dict を作成
    市区町村コードと市区町村名の dict を作成

    Returns:
        tuple[dict[Any, Any], dict[Any, Any]]: dict.
    """
    df: pd.DataFrame = _load_city()
    return (
        dict(zip(df["prefcode"], df["prefname"])),
        dict(zip(df["citycode"], df["cityname"])),
    )


def region_builder() -> tuple[None, None] | tuple[dict[Any, Any], dict[Any, Any]]:
    """
        リージョンを選択して返す

    Returns:
        tuple[Any | None, None] | tuple[Any | None, list[Any]]: 都道府県、市区町村

    """
    #     ██████╗ ███████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗
    #     ██╔══██╗██╔════╝██╔════╝ ██║██╔═══██╗████╗  ██║
    #     ██████╔╝█████╗  ██║  ███╗██║██║   ██║██╔██╗ ██║
    #     ██╔══██╗██╔══╝  ██║   ██║██║██║   ██║██║╚██╗██║
    #     ██║  ██║███████╗╚██████╔╝██║╚██████╔╝██║ ╚████║
    #     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

    df = _load_region()
    regions = df["regionname"].unique()

    selected_region: str | None = st.pills("地域を選択してください", regions)

    if selected_region is None:
        return None, None

    #     ██████╗ ██████╗ ███████╗███████╗███████╗ ██████╗████████╗██╗   ██╗██████╗ ███████╗███████╗
    #     ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗██╔════╝██╔════╝
    #     ██████╔╝██████╔╝█████╗  █████╗  █████╗  ██║        ██║   ██║   ██║██████╔╝█████╗  ███████╗
    #     ██╔═══╝ ██╔══██╗██╔══╝  ██╔══╝  ██╔══╝  ██║        ██║   ██║   ██║██╔══██╗██╔══╝  ╚════██║
    #     ██║     ██║  ██║███████╗██║     ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗███████║
    #     ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝

    prefectures = df[df["regionname"] == selected_region]["prefname"].tolist()

    if len(prefectures) == 1:
        selected_prefecture = prefectures[0]
    else:
        selected_prefecture = st.pills("都道府県を選択してください", prefectures)

    pref_data = df[df["prefname"] == selected_prefecture][
        ["prefcode", "prefname"]
    ].to_dict(orient="records")

    pref_dict = {item["prefcode"]: item["prefname"] for item in pref_data}

    #      ██████╗██╗████████╗██╗███████╗███████╗
    #     ██╔════╝██║╚══██╔══╝██║██╔════╝██╔════╝
    #     ██║     ██║   ██║   ██║█████╗  ███████╗
    #     ██║     ██║   ██║   ██║██╔══╝  ╚════██║
    #     ╚██████╗██║   ██║   ██║███████╗███████║
    #      ╚═════╝╚═╝   ╚═╝   ╚═╝╚══════╝╚══════╝

    df: pd.DataFrame = _load_city()

    city_name = df[df["prefname"] == selected_prefecture]["cityname"].tolist()

    with st.expander("市区町村を選択できます", expanded=True):
        cities = st.pills(
            "市区町村",
            city_name,
            selection_mode="multi",
            default=city_name[0],
            label_visibility="collapsed",
        )

    city_data: list[dict[Hashable, Any]] = df[df["cityname"].isin(cities)][
        ["citycode", "cityname"]
    ].to_dict(orient="records")

    city_dict: dict[Any, Any] = {
        item["citycode"]: item["cityname"] for item in city_data
    }

    return (
        pref_dict,
        city_dict,
    )
