import streamlit as st
from streamlit.navigation.page import StreamlitPage


def navigation() -> None:
    pages: dict[str, list[StreamlitPage]] = {
        "Contents": [
            st.Page("pages/comparison.py", title="Comparison"),
        ],
        "Resources": [
            # st.Page("pages/learn.py", title="Learn about me"),
            st.Page("pages/overview.py", title="Overview"),
        ],
    }

    pg: StreamlitPage = st.navigation(pages)
    pg.run()


def page_config() -> None:
    TITLE = "全国市区町村における滞在人口の比較"

    st.set_page_config(
        page_title=TITLE,
        page_icon="🗾",
        layout="wide",
    )
