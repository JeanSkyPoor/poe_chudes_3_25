import streamlit as st
import pandas as pd
from dashboard_classes import Dashboard
from secondary_defs import init_main_states
import logging

st.set_page_config(
    layout = "wide"
)

st.write("#")

init_main_states()
try:
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
    with columns[1]:
        dashboard.draw_abilities_frequency_google_doc()
    st.divider()

    columns = st.columns(2)
    with columns[0]:
        dashboard.draw_reroll_frequency_google_doc()
    with columns[1]:
        dashboard.draw_coins_frequency()

    st.divider()

    dashboard.draw_ladder_headers()

    columns = st.columns([2, 1])
    with columns[0]:
        dashboard.draw_classes_info_ladder()
    with columns[1]:
        dashboard.draw_level_frequency_ladder()

    columns = st.columns(2)
    with columns[0]:
        dashboard.draw_character_per_account_ladder()
    with columns[1]:
        dashboard.draw_challenges_dist_ladder()





    st.divider()
    st.write(
        "Мой дс: **@Jean_Sky_Poor**"
    )

except Exception as e:
    logging.error(
        e
    )
    
    st.warning(
        "Что-то пошло не так. Прошу написать мне в дсе или в телеграмме Jean_Sky_Poor"
    )