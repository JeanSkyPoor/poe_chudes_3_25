import streamlit as st
import pandas as pd
from dashboard_classes import Dashboard
from secondary_defs import init_main_states

st.set_page_config(
    layout = "wide"
)

init_main_states()

dashboard = Dashboard()

dashboard.draw_head_google_doc()

columns = st.columns(2)
with columns[0]:
    dashboard.draw_combination_frequency_google_doc()
with columns[1]:
    dashboard.draw_coins_for_bosses_google_doc()
st.divider()


columns = st.columns(2)
with columns[0]:
    dashboard.draw_classes_frequency_google_doc()