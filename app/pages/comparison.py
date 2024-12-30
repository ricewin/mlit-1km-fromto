# app.py
from datetime import datetime
from typing import Any

import geopandas as gpd
import pandas as pd
import streamlit as st
from common.const import Const
from common.folium_map_builder import folium_map_builder
from common.region_builder import prefcode_to_name, region_builder
from common.step_by_step import StepByStep
from common.utils import fetch_data, make_polygons, merge_df
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

CONST = Const()
dayflag: dict[int, str] = CONST.dayflag
timezone: dict[int, str] = CONST.timezone
dataset: dict[str, str] = CONST.dataset

ss: SessionStateProxy = st.session_state


def step_1() -> None:
    ss.pref, ss.city = region_builder()
    # st.write(ss.pref, ss.city)
    # st.write(ss.prefcode, ss.citycode)


def step_2() -> None:
    _dataset()

    if ss.set == "mdp":
        ss.df_mesh = fetch_data("mesh1km", 2020)

    _sidebar_date()

    # 年月の値を使ってデータを読み込む
    ss.df_2021 = fetch_data(ss.set, 2021)
    ss.df_2020 = fetch_data(ss.set, 2020)

    df_2021: pd.DataFrame = ss.df_2021.copy()
    df_2020: pd.DataFrame = ss.df_2020.copy()

    # 市区町村を選択していたら絞り込む
    if len(ss.citycode) > 0:
        ss.df_2021 = df_2021[df_2021["citycode"].isin(ss.citycode)]
        ss.df_2020 = df_2020[df_2020["citycode"].isin(ss.citycode)]

    _sidebar_flag()

    # メッシュコードのないデータはデータテーブルを出して終わり
    if ss.set == "fromto":
        with st.popover("市区町村単位発地別の滞在人口データ"):
            st.info(
                "市区町村別に、いつ、どこ（同市区町村／同都道府県／同地方／それ以外）から何人来たのかを収録したデータ"
            )

        # 絞り込み
        df_2021 = _filter(ss.df_2021)
        df_2020 = _filter(ss.df_2020)

        # 加工
        df_2021 = _datamap(df_2021)
        df_2020 = _datamap(df_2020)

        st.write(df_2021, df_2020)
        return

    # マップ表示
    with st.popover("1km メッシュ別の滞在人口データ"):
        st.info("1km メッシュ別に、いつ、何人が滞在したのかを収録したデータ")

    df_2021 = ss.df_2021.copy()
    df_2020 = ss.df_2020.copy()

    df_2021 = _filter(df_2021)
    df_2020 = _filter(df_2020)

    # st.write(df_2021, df_2020)

    df_mesh: pd.DataFrame | Any = ss.df_mesh.copy()

    # 滞在人口
    df_main = merge_df(
        df_2020, df_mesh, on="mesh1kmid", how="left", suffixes=("", "_drop"), drop=True
    )
    # st.write(df_main)

    # df_main: pd.DataFrame = df_main.dropna(subset=["population"])
    gdf_main: gpd.GeoDataFrame = make_polygons(df_main, "population")
    # st.write(gdf_main)

    df_latlon: pd.DataFrame = df_main[["lat", "lon"]]
    # st.write(df_latlon)

    # 差分
    df_diff: pd.DataFrame = merge_df(
        df_2021,
        df_2020,
        on="mesh1kmid",
        how="left",
        suffixes=("_2021", "_2020"),
        drop=False,
    )
    # st.write(df_diff)

    # 増減率を計算して新しいカラムを追加
    df_diff["diff"] = df_diff["population_2021"] / df_diff["population_2020"] - 1

    # 不要なカラムを削除して最終的なデータフレームを作成
    df_diff = df_diff[["mesh1kmid", "diff"]]
    # st.write(df_diff)

    # 前年同月増減率
    df_sub: pd.DataFrame = merge_df(
        df_diff, df_mesh, on="mesh1kmid", how="left", suffixes=("", "_drop"), drop=True
    )
    # st.write(df_sub)

    df_sub = df_sub.dropna(subset=["diff"])
    gdf_sub: gpd.GeoDataFrame = make_polygons(df_sub, "diff")
    # st.write(gdf_sub)

    with st.expander(f"*Geometry records: {len(gdf_main)}*"):
        st.caption("滞在人口")
        st.write(gdf_main)

        st.caption("増減率")
        st.write(gdf_sub)

    st.subheader("2020-2021 年比較")
    st.caption("2020 年の滞在人口と増減率（式:2021 年/2020 年-1）")

    if len(ss.citycode) == 0:
        zoom_start = 9
    elif len(ss.citycode) > 1:
        zoom_start = 10
    else:
        zoom_start = 11

    folium_map_builder(df_latlon, gdf_main, gdf_sub, "population", "diff", zoom_start)


def _datamap(df):
    from_area: dict[int, str] = CONST.from_area
    prefcode, citycode = prefcode_to_name()

    df["dayflag"] = df["dayflag"].map(dayflag)
    df["timezone"] = df["timezone"].map(timezone)
    df["prefcode"] = df["prefcode"].map(prefcode)
    df["citycode"] = df["citycode"].map(citycode)
    df["from_area"] = df["from_area"].map(from_area)

    return df


def _dataset() -> None:
    with st.sidebar:
        st.subheader("可視化対象", divider="orange")
        ss.set = st.segmented_control(
            "データセット",
            dataset,
            default=list(dataset)[0],
            format_func=lambda x: dataset[x],
            help="1km メッシュはマップで可視化します。",
        )

        st.subheader("滞在エリア", divider="orange")
        ss.prefcode = st.segmented_control(
            "都道府県",
            ss.pref,
            selection_mode="multi",
            default=ss.pref,
            format_func=lambda x: ss.pref[x],
        )

        ss.citycode = st.segmented_control(
            "市区町村",
            ss.city,
            selection_mode="multi",
            default=ss.city,
            format_func=lambda x: ss.city[x],
            help="選択なしで絞り込みを解除します。",
        )


def _sidebar_date() -> None:
    today: datetime = datetime.now()

    with st.sidebar:
        st.subheader("集計期間", divider="orange")
        ss.month = st.number_input(
            "月別",
            min_value=1,
            max_value=12,
            value=today.month,
            help="単月指定のみ。",
        )


def _sidebar_flag() -> None:
    with st.sidebar:
        ss.dayflag = st.segmented_control(
            "平休日",
            dayflag,
            selection_mode="single",
            format_func=lambda x: dayflag[x],
            default=list(dayflag)[-1],
        )

        ss.timezone = st.segmented_control(
            "時間帯",
            timezone,
            selection_mode="single",
            format_func=lambda x: timezone[x],
            default=list(timezone)[-1],
            help="昼:11時台〜14時台の平均・深夜:1時台〜4時台の平均・終日:0時台〜23時台の平均",
        )


def _filter(df) -> Any:
    df = df[df["dayflag"] == ss.dayflag]
    df = df[df["timezone"] == ss.timezone]

    return df


# アプリ本体=================================
st.title("全国市区町村における滞在人口の比較")
st.header("1 kmメッシュ、市区町村単位発地別")

step = StepByStep()

try:
    if ss.now == 0:
        st.subheader(f"*Step {ss.now + 1}: Select area*", divider="rainbow")
        step_1()

    elif ss.now == 1:
        st.subheader(f"*Step {ss.now + 1}: Visualize*", divider="rainbow")
        step_2()

    else:
        st.subheader(f"*Step {ss.now + 1}: TBD*", divider="rainbow")
        # st.balloons()
        st.snow()
except Exception:
    pass
finally:
    step.buttons(ss.now)

st.divider()

st.info(
    """
    [「全国の人流オープンデータ」（国土交通省）](https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto)
    を加工して作成

    出典:[「全国の人流オープンデータ」（国土交通省）](https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto)
    """
)
