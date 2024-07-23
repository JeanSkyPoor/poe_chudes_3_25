import pandas as pd
import streamlit as st
from numpy import nan
from datetime import datetime




class GoogleDoc():
    link = "https://docs.google.com/spreadsheets/d/1XiP5ss6ijjE5iiBC09C7lUW0ngV3QJt0hGRa_Zwufy8/export#gid=690744568#gid=690744568&format=xlsx"

    main_columns = [
        "Логин",
        "Подкласс",
        "Умение",
        "Был реролл",
        "Пожиратель",
        "Экзарх",
        "Древний",
        "Создатель",
        "Кора",
        "Ол",
        "Ошаби",
        "Убер Древний",
        "Олрот",
        "Убер Атзири",
        "Сирус",
        "Мейвен",
        "Убийцы Древнего",
        "Сокрытые",
        "Убер Пожиратель",
        "Убер Экзарх",
        "Убер Убер Древний",
        "Убер Создатель",
        "Убер Кора",
        "Убер Сирус",
        "Убер Мейвен",
        "Внушающие страх",
        "Симулякр 15"
    ]

    bosses_columns = main_columns[4:]

    reroll_map = {
        nan: "Без реролла",
        1: "Один реролл",
        2: "Два реролла"
    }




    def __init__(self) -> None:

        self.load_data()
        self.find_duplicated_flag()
        self.find_nunique_players()
        self.prepare_df_combination_frequency()
        self.prepare_df_coins_for_bosses()
        self.prepare_df_classes_frequency()
        self.prepare_df_abilities_frequency()
        self.prepare_df_reroll_frequency()
        self.find_total_coins_for_bosses()
        self.find_total_players_with_coins_for_bosses()
        self.prepare_df_coins_frequency()


    def load_data(self):

        self.df_origin = pd.read_excel(
            self.link,
            sheet_name = "Участники",
            usecols = self.main_columns
        ).dropna(
            subset = [
                "Логин"
            ]
        )

        self.df_origin["Умение"] = pd.Categorical(
            self.df_origin["Умение"],
            categories = st.session_state["abilities"]
        )

        self.df_origin["Подкласс"] = pd.Categorical(
            self.df_origin["Подкласс"],
            categories = st.session_state["classes"]
        )

        
        self.df_origin["Был реролл"] = self.df_origin["Был реролл"].map(self.reroll_map)
        self.df_origin["Был реролл"] = pd.Categorical(
            self.df_origin["Был реролл"],
            categories = self.reroll_map.values()
        )




    def find_duplicated_flag(self):

        self.is_login_duplicated = True if self.df_origin["Логин"].duplicated().sum() > 0 else False


    
    def find_nunique_players(self):

        self.nunique_players = self.df_origin["Логин"].nunique()




    def prepare_df_combination_frequency(self):

        self.df_combination_frequency = self.df_origin.groupby(
            [
                "Подкласс",
                "Умение"
            ],
            as_index = False,
            observed = True
        ).size()\
        .rename(
            columns = {
                "size": "Количество игроков"
            }
        ).sort_values(
            [
                "Количество игроков",
                "Подкласс",
                "Умение"
            ],
            ascending = [
                False,
                True,
                True
            ]
        )



    
    def prepare_df_coins_for_bosses(self):

        self.df_coins_for_bosses = self.df_origin[self.bosses_columns].apply(
            [
                "sum",
                "count"
            ]
        ).T\
        .reset_index()\
        .rename(
            columns = {
                "sum": "Сумма монет",
                "count": "Количество убийств",
                "index": "Имя босса"
            }
        ).sort_values(
            [
                "Сумма монет",
                "Имя босса"
            ],
            ascending = [
                False,
                True
            ]
        )



    def prepare_df_classes_frequency(self):

        self.df_classes_frequency = self.df_origin["Подкласс"]\
        .value_counts()\
        .to_frame()\
        .reset_index()\
        .rename(
            columns = {
                "count": "Количество игроков"
            }
        ).sort_values(
            [
                "Количество игроков",
                "Подкласс"
            ],
            ascending = [
                False,
                True
            ]
        )

        self.df_classes_frequency["%"] = self.df_classes_frequency["Количество игроков"]\
        .div(self.nunique_players)\
        .mul(100)\
        .round(2)




    def prepare_df_abilities_frequency(self):

        self.df_abilities_frequency = self.df_origin["Умение"]\
        .value_counts()\
        .to_frame()\
        .reset_index()\
        .rename(
            columns = {
                "count": "Количество игроков"
            }
        ).sort_values(
            [
                "Количество игроков",
                "Умение"
            ],
            ascending = [
                False,
                True
            ]
        )

        self.df_abilities_frequency["%"] = self.df_abilities_frequency["Количество игроков"]\
        .div(self.nunique_players)\
        .mul(100)\
        .round(2)




    def prepare_df_reroll_frequency(self):

        self.df_reroll_frequency = self.df_origin["Был реролл"]\
        .value_counts()\
        .to_frame()\
        .reset_index()\
        .rename(
            columns = {
                "count": "Количество игроков",
                "Был реролл": "Количество рероллов"
            }
        ).sort_values(
            [
                "Количество рероллов"
            ],
            key = lambda x: x.map(self.reroll_map)
        )

        self.df_reroll_frequency["%"] = self.df_reroll_frequency["Количество игроков"]\
        .div(self.nunique_players)\
        .mul(100)\
        .round(2)
    



    def find_total_coins_for_bosses(self):

        self.total_coins_for_bosses = self.df_coins_for_bosses["Сумма монет"].sum().astype(int)



    
    def find_total_players_with_coins_for_bosses(self):

        self.players_with_reward_for_bosses = self.df_origin[self.bosses_columns]\
        .sum(axis = 1)\
        .to_frame()\
        .rename(
            columns = {
                0: "Сумма монет"
            }
        ).query(
            "`Сумма монет` >= 10"
        ).shape[0]
        


    
    def prepare_df_coins_frequency(self):

        self.df_coins_frequency = self.df_origin[self.bosses_columns]\
        .sum(axis = 1)\
        .value_counts()\
        .to_frame()\
        .reset_index()\
        .rename(
            columns = {
                "index": "Сумма монет",
                "count": "Количество игроков"
            }
        ).sort_values(
            [
                "Сумма монет"
            ],
            ascending = False
        )     


    








class Dashboard():
    

    def __init__(self) -> None:

        self.google_doc: GoogleDoc = self.load_google_doc()

        self.ladder: Ladder = self.load_ladder()




    @st.cache_resource(
            ttl = 60*60*2,
            show_spinner = "Загружаю данные из Google Docs"
    )
    @staticmethod
    def load_google_doc(_self):

        return GoogleDoc()
    


    @st.cache_resource(
            ttl = 60*60*2,
            show_spinner = "Загружаю данные из ладдера"
    )
    @staticmethod
    def load_ladder(_self):

        return Ladder()
    


    def clear_cache(self):

        self.load_ladder.clear()
        self.load_google_doc.clear()




    def draw_head_google_doc(self):

        columns = st.columns([9,1])

        with columns[0]:
            st.title(
                "Файл приватки из Google Docs"
            )

        with columns[1]:
            st.button(
                "ОБНОВИТЬ",
                on_click = self.clear_cache
            )

        st.divider()


        columns = st.columns(5)

        with columns[0]:
            
            st.button(
                "Скачать все таблицы"
            )
        
        with columns[1]:

            st.metric(
                "Всего уникальных игроков",
                self.google_doc.nunique_players
            )
        
        with columns[2]:
            
            st.metric(
                "Монет за боссов",
                self.google_doc.total_coins_for_bosses
            )

        with columns[3]:

            st.metric(
                "Игроков с наградой за боссов",
                self.google_doc.players_with_reward_for_bosses
            )

        with columns[4]:

            if self.google_doc.is_login_duplicated:
                st.warning(
                    "Имеются дубли по логину"
                )

            else:
                st.success(
                    "Дублей нет"
                )

        st.divider()




    def draw_combination_frequency_google_doc(self):

        df = self.google_doc.df_combination_frequency

        st.header(
            "Частота комбинаций"
        )

        columns = st.columns(2)

        with columns[0]:

            selected_class = st.multiselect(
                "Подкласс",
                options = st.session_state["classes"],
                key = "Частота комбинаций подкласс"
            )
        
        with columns[1]:

            selected_ability = st.multiselect(
                "Умение",
                options = st.session_state["abilities"],
                key = "Частота комбинаций умение"
            )

        if selected_class:
            
            df = df[
                df["Подкласс"].isin(selected_class)
            ]
        
        if selected_ability:

            df = df[
                df["Умение"].isin(selected_ability)
            ]

        st.dataframe(
            df,
            hide_index = True,
            use_container_width = True
        )
        


    
    def draw_coins_for_bosses_google_doc(self):

        df = self.google_doc.df_coins_for_bosses

        st.header(
            "Сумма монет по боссам"
        )

        selected_boss = st.multiselect(
            "Имя босса",
            options = self.google_doc.df_coins_for_bosses["Имя босса"]
        )

        if selected_boss:
            
            df = df[
                df["Имя босса"].isin(selected_boss)
            ]

        st.dataframe(
            df,
            hide_index = True,
            use_container_width = True
        )




    def draw_classes_frequency_google_doc(self):

        st.header(
            "Частота подклассов"
        )

        df = self.google_doc.df_classes_frequency


        selected_classes = st.multiselect(
            "Подкласс",
            options = st.session_state["classes"],
            key = "Частота подклассов"
        )

        if selected_classes:
            
            df = df[
                df["Подкласс"].isin(selected_classes)
            ]

        st.dataframe(
            df,
            hide_index = True,
            use_container_width = True
        )




    def draw_abilities_frequency_google_doc(self):

        st.header(
            "Частота умений"
        )

        df = self.google_doc.df_abilities_frequency


        selected_abilities = st.multiselect(
            "Умение",
            options = st.session_state["abilities"],
            key = "Частота умений"
        )

        if selected_abilities:
            
            df = df[
                df["Умение"].isin(selected_abilities)
            ]

        st.dataframe(
            df,
            hide_index = True,
            use_container_width = True
        )


    

    def draw_reroll_frequency_google_doc(self):

        st.header(
            "Частота рероллов"
        )

        st.dataframe(
            self.google_doc.df_reroll_frequency,
            hide_index = True,
            use_container_width = True
        )




    def draw_coins_frequency(self):

        st.header(
            "Частота сумм монет за боссов"
        )

        st.dataframe(
            self.google_doc.df_coins_frequency,
            use_container_width = True,
            hide_index = True
        )







    










class Ladder():
    pass
        






















































































# class GoogleDoc():

#     def __init__(self) -> None:
#         self.read_data()
#         self.prepare_df_combinations_frequency()
#         self.prepare_df_classes_frequency()
#         self.prepare_df_abilities_frequency()
#         self.prepare_df_rerolls()
#         self.prepare_df_bosses()



#     def read_data(self):

#         self.df_origin = pd.read_excel(
#             st.session_state["google_link"],
#             usecols = st.session_state["columns"],
#             sheet_name = "Участники"
#         ).dropna(
#             subset = [
#                 "Логин"
#             ]
#         )

#         self.df_origin["Подкласс"] = pd.Categorical(
#             self.df_origin["Подкласс"],
#             categories = st.session_state["classes"]
#         )
#         self.df_origin["Умение"] = pd.Categorical(
#             self.df_origin["Умение"],
#             categories = st.session_state["abilities"]
#         )

#         dict_to_replace = {
#             nan: "Без реролла",
#             1: "Один реролл",
#             2: "Два реролла"
#         }
#         self.df_origin["Был реролл"] = pd.Categorical(
#             self.df_origin["Был реролл"].map(dict_to_replace),
#             categories = dict_to_replace.values()
#         )



    
#     def prepare_df_combinations_frequency(self):

#         self.df_combinations = self.df_origin.groupby(
#             [
#                 "Подкласс",
#                 "Умение"
#             ],
#             as_index = False,
#             observed = True
#         ).size()\
#         .rename(
#             columns = {
#                 "size": "Количество игроков"
#             }
#         ).sort_values(
#             [
#                 "Количество игроков",
#                 "Подкласс",
#                 "Умение"
#             ],
#             ascending = [
#                 False,
#                 True,
#                 True
#             ]
#         )



    

#     def prepare_df_classes_frequency(self):

#         self.df_classes_frequency = self.df_origin["Подкласс"]\
#         .value_counts()\
#         .reset_index()\
#         .rename(
#             columns = {
#                 "count": "Количество игроков"
#             }
#         ).sort_values(
#             [
#                 "Количество игроков",
#                 "Подкласс"
#             ],
#             ascending = [
#                 False,
#                 True
#             ]
#         )




#     def prepare_df_abilities_frequency(self):

#         self.df_abilities_frequency = self.df_origin["Умение"]\
#         .value_counts()\
#         .reset_index()\
#         .rename(
#             columns = {
#                 "count": "Количество игроков"
#             }
#         ).sort_values(
#             [
#                 "Количество игроков",
#                 "Умение"
#             ],
#             ascending = [
#                 False,
#                 True
#             ]
#         )




#     def prepare_df_rerolls(self):

#         self.df_rerolls = self.df_origin["Был реролл"]\
#         .value_counts()\
#         .reset_index()\
#         .rename(
#             columns = {
#                 "Был реролл": "Количество рероллов",
#                 "count": "Количество игроков"
#             }
#         ).sort_values(
#             [
#                 "Количество рероллов"
#             ]
#         )




#     def prepare_df_bosses(self): 

#         self.df_bosses = self.df_origin[st.session_state["bosses_columns"]]\
#         .apply(
#             [
#                 "sum",
#                 "count"
#             ]
#         ).T\
#         .reset_index()\
#         .rename(
#             columns = {
#                 "index": "Имя босса",
#                 "sum": "Сумма монет",
#                 "count": "Количество убийств"
#             }
#         ).sort_values(
#             [
#                 "Сумма монет",
#                 "Имя босса"
#             ],
#             ascending = [
#                 False,
#                 True
#             ]
#         )










# class Dashboard():

#     def draw_google_title():

#         st.title(
#             "Файл приватки из Google Docs"
#         )
#         st.divider()




#     def draw_google_metrics():

#         columns = st.columns(5)

#         with columns[0]:
#             st.button(
#                 "Скачать все таблицы"
#             )
#         with columns[1]:
#             st.metric(
#                 "Всего уникальных игроков",
#                 st.session_state["unique_players"]
#             )
#         with columns[2]: 
#             st.metric(
#                 "Заработано монет с боссов",
#                 2
#             )
#         with columns[3]:
#             st.metric(
#                 "Игроков с наградами",
#                 3
#             )
#         with columns[4]:
#             if st.session_state["duplicated_nickname"] > 0:
#                 st.warning(
#                     "Есть дубли по логину"
#                 )
#             else:
#                 st.success(
#                     "Дублей по логину нет"
#                 )
#         st.divider()




#     def draw_combination_frequency():

#         st.header(
#             "Частота комбинаций"
#         )

#         df = st.session_state["google_doc"].df_combinations

#         columns = st.columns(2)
#         with columns[0]:
#             selected_class = st.multiselect(
#                 "Подкласс",
#                 options = st.session_state["classes"],
#                 default = None,
#                 key = "combination_class"
#             )

#             if selected_class:
#                 df = df[
#                     df["Подкласс"].isin(selected_class)
#                 ]

#         with columns[1]:
#             selected_ability = st.multiselect(
#                 "Умение",
#                 options = st.session_state["abilities"],
#                 default = None,
#                 key = "combination_abilities"
#             )

#             if selected_ability:

#                 df = df[
#                     df["Умение"].isin(selected_ability)
#                 ]

#         st.dataframe(
#             df,
#             hide_index = True,
#             use_container_width = True
#         )



    
#     def draw_bosses_coins():

#         st.header(
#             "Сумма монет по боссам"
#         )

#         df = st.session_state["google_doc"].df_bosses

#         selected_bosses = st.multiselect(
#             "Имя босса",
#             options = df["Имя босса"].sort_values().to_list(),
#             default = None
#         )

#         if selected_bosses:
#             df = df[
#                 df["Имя босса"].isin(selected_bosses)
#             ]

#         st.dataframe(
#             df,
#             hide_index = True,
#             use_container_width = True
#         )



    
#     def draw_classes_frequency():

#         st.header(
#             "Частота подклассов"
#         )
        
#         df = st.session_state["google_doc"].df_classes_frequency


#         selected_classes = st.multiselect(
#             "Подкласс",
#             options = st.session_state["classes"],
#             default = None,
#             key = "simple_class"
#         )

#         if selected_classes:

#             df = df[
#                 df["Подкласс"].isin(selected_classes)
#             ]

#         st.dataframe(
#             df,
#             hide_index = True,
#             use_container_width = True
#         )




#     def draw_abilities_frequency():
        
#         st.header(
#             "Частота умений"
#         )

#         df = st.session_state["google_doc"].df_abilities_frequency

#         selected_abilites = st.multiselect(
#             "Умение",
#             options = st.session_state["abilities"],
#             default = None,
#             key = "simple_abilities"
#         )

#         if selected_abilites:
#             df = df[
#                 df["Умение"].isin(selected_abilites)
#             ]
        
#         st.dataframe(
#             df,
#             hide_index = True,
#             use_container_width = True
#         )



    
#     def draw_rerolls():

#         st.header(
#             "Частота рероллов"
#         )

#         st.dataframe(
#             st.session_state["google_doc"].df_rerolls,
#             use_container_width = True,
#             hide_index = True
#         )



    