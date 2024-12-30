"""step by step


FYI: https://nttdocomo-developers.jp/entry/20231216_1
"""

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.state.session_state_proxy import SessionStateProxy


@st.fragment
class StepByStep:
    def __init__(self) -> None:
        self.ss: SessionStateProxy = st.session_state
        self.initialize_state()

    def initialize_state(self) -> None:
        """初期化"""
        if "now" not in self.ss:
            self.ss.now = 0
            self.ss.rst = False

    def countup(self, reset: bool) -> None:
        """コールバック関数(1/3):次へ"""
        self.ss.now += 1
        self.ss.rst = reset

    def countdown(self) -> None:
        """コールバック関数(2/3):戻る"""
        self.ss.now -= 1

    def reset(self) -> None:
        """コールバック関数(3/3):リセット"""
        self.ss.now = 0

    def buttons(self, now: int, _reset: bool = False) -> None:
        """
        Step by Step.

        Args:
            now (int): Step No.
            _reset (bool, optional): Do Reset. Defaults to False.
        """
        col: list[DeltaGenerator] = st.columns([1, 1, 2])
        if now <= 1:
            col[0].button(
                "次へ進む", type="primary", on_click=self.countup, args=(_reset,)
            )
        if now >= 1:
            col[1].button("前へ戻る", on_click=self.countdown)
        if now >= 2:
            col[2].button("はじめからやり直す", on_click=self.reset)
