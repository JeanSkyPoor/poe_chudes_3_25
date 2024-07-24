import pandas as pd
import streamlit as st


def init_main_states():

    st.session_state["abilities"] = pd.read_csv(
        "умения.csv"
    )["Умение"].to_list()

    st.session_state["classes"] = pd.read_csv(
        "подклассы.csv"
    )["Подкласс"].to_list()

    st.session_state["last_update"] = None