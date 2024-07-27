import pandas as pd
import streamlit as st
from numpy import nan
from time import sleep
import requests


TTL_TIME = 60 * 30


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

        self.is_login_duplicated = self.df_origin["Логин"].duplicated().any()


    
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

        self.df_classes_frequency = self.df_origin.groupby(
            [
                "Подкласс"
            ],
            as_index = False
        ).agg(
            **{
                "Количество игроков": (
                    "Логин", "count"
                ),
                "Уникальных умений": (
                    "Умение", "nunique"
                )
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
        self.df_classes_frequency["% игроков"] = self.df_classes_frequency["Количество игроков"]\
        .div(self.nunique_players)\
        .mul(100)\
        .round(2)




    def prepare_df_abilities_frequency(self):

        self.df_abilities_frequency = self.df_origin.groupby(
            [
                "Умение"
            ],
            as_index = False
        ).agg(
            **{
                "Количество игроков": (
                    "Логин", "count"
                ),
                "Уникальных подклассов": (
                    "Подкласс", "nunique"
                )
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
        self.df_abilities_frequency["% игроков"] = self.df_abilities_frequency["Количество игроков"]\
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

        self.df_reroll_frequency["% игроков"] = self.df_reroll_frequency["Количество игроков"]\
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
            ttl = TTL_TIME,
            show_spinner = "Загружаю данные из Google Docs"
    )
    @staticmethod
    def load_google_doc(_self):

        data_class = GoogleDoc()

        return data_class
    


    @st.cache_resource(
            ttl = TTL_TIME,
            show_spinner = "Загружаю данные из ладдера"
    )
    @staticmethod
    def load_ladder(_self):

        data_class = Ladder()

        return data_class




    def clear_cache(self):

        self.load_google_doc.clear()

        self.load_ladder.clear()




    def draw_head_google_doc(self):

        columns = st.columns([3.1, 1])

        with columns[0]:
            
            st.title(
                "Файл приватки из Google Docs"
            )

        with columns[1]:

            st.header(
                "**Дата завершения** 24.09.2024"
            )

        st.divider()


        columns = st.columns(4)
        
        with columns[0]:

            st.metric(
                "Всего уникальных игроков",
                self.google_doc.nunique_players
            )
        
        with columns[1]:
            
            st.metric(
                "Монет за боссов",
                self.google_doc.total_coins_for_bosses
            )

        with columns[2]:

            st.metric(
                "Игроков с наградой за боссов",
                self.google_doc.players_with_reward_for_bosses
            )

        with columns[3]:

            if self.google_doc.is_login_duplicated:
                st.warning(
                    "Имеются дубли по логину"
                )

            else:
                st.success(
                    "Дублей по логину нет"
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



    def draw_ladder_headers(self):

        st.title(
            "Файл ладдера с сайта"
        )

        columns = st.columns(3)

        with columns[0]:
            
            st.metric(
                "Всего персонажей",
                self.ladder.total_characters
            )

        with columns[1]:

            st.metric(
                "Уникальных игроков",
                self.ladder.nunique_players
            )

        with columns[2]:

            st.metric(
                "Максимальная грубина соло",
                self.ladder.max_depth_solo
            )
        
        st.divider()




    def draw_classes_info_ladder(self):

        st.header(
            "Характеристика подклассов"
        )

        st.dataframe(
            self.ladder.df_classes_frequency,
            use_container_width = True,
            hide_index = True
        )




    def draw_level_frequency_ladder(self):

        st.header(
            "Распределение уровней"
        )

        st.dataframe(
            self.ladder.df_level_frequency,
            use_container_width = True,
            hide_index = True
        )




    def draw_character_per_account_ladder(self):

        st.header(
            "Персонажей на аккаунт"
        )
        
        st.dataframe(
            self.ladder.df_character_per_account,
            hide_index = True,
            use_container_width = True
        )




    def draw_challenges_dist_ladder(self):

        st.header(
            "Ачивки"
        )

        st.dataframe(
            self.ladder.df_challenges_frequency,
            use_container_width = True,
            hide_index = True
        )








class Ladder():

    def __init__(self) -> None:
        
        self.load_data()
        self.prepare_main_metrics()
        self.prepare_df_classes_frequency()
        self.prepare_df_level_frequency()
        self.prepare_df_challenges_frequency()
        self.prepare_df_character_per_account()
    



    def load_data(self):

        offset = 0

        raw_data = []

        while True:
            
            link = f"https://ru.pathofexile.com/api/ladders?offset={offset}&limit=200&id=PoE%20Chudes%20SoK%20by%20Cardiff%20(PL49476)&realm=pc&_=1694455499930"

            request = requests.get(
                link,
                headers = {
                    "User-Agent": "Opera"
                }
            ).json()["entries"]

            for record in request:

                character_rank = record.get("rank")

                is_dead = record.get("dead")

                is_public = record.get("public")

                character = record.get("character")

                character_id = character.get("id")

                character_name = character.get("name")
                
                character_level = character.get("level")

                character_class = character.get("class")
                
                character_depth_solo = None
                if "depth" in character.keys():

                    character_depth_solo = character.get("depth").get("solo")

                account = record.get("account")

                account_name = account.get("name")

                challenges = account.get("challenges").get("completed")

                raw_data.append(
                    [
                        character_rank,
                        is_dead,
                        is_public,
                        account_name,
                        character_id,
                        character_name,
                        character_level,
                        character_class,
                        character_depth_solo,
                        challenges
                    ]
                )
            
            if len(request) == 200:

                offset += 200

                sleep(1)

                continue
            else:
                break
            
        
        self.df_origin = pd.DataFrame(
            columns = [
                "rank",
                "is_dead",
                "is_public",
                "account",
                "character_id",
                "character_name",
                "character_level",
                "character_class",
                "solo_depth",
                "challenges"  
            ],
            data = raw_data
        )




    def prepare_main_metrics(self):

        self.total_characters = self.df_origin["character_name"].nunique()

        self.nunique_players = self.df_origin["account"].nunique()

        self.max_depth_solo = self.df_origin["solo_depth"].max().astype(int)




    def prepare_df_classes_frequency(self):

        self.df_classes_frequency = self.df_origin.groupby(
            [
                "character_class"
            ],
            as_index = False
        ).agg(
            **{
                "Количество персонажей": (
                    "character_class", "count"
                ),

                "Минимальный уровень": (
                    "character_level", "min"
                ),

                "Средний уровень": (
                    "character_level", "mean"
                ),

                "Максимальный уровень": (
                    "character_level", "max"
                )
            }
        ).sort_values(
            [
                "Количество персонажей"
            ],
            ascending = False
        ).rename(
            columns = {
                "character_class": "Подкласс"
            }
        )

        self.df_classes_frequency["Средний уровень"] = self.df_classes_frequency["Средний уровень"].round(1)
        
    


    def prepare_df_challenges_frequency(self):

        self.df_challenges_frequency = self.df_origin["challenges"]\
        .value_counts()\
        .to_frame()\
        .reset_index()\
        .rename(
            columns = {
                "challenges": "Количество испытаний",
                "count": "Количество игроков"
            }
        ).sort_values(
            [
                "Количество испытаний"
            ],
            ascending = False
        )



    
    def prepare_df_level_frequency(self):

        self.df_level_frequency = self.df_origin["character_level"]\
        .value_counts()\
        .to_frame()\
        .reset_index()\
        .rename(
            columns = {
                "character_level": "Уровень персонажа",
                "count": "Количество персонажей"
            }
        ).sort_values(
            [
                "Уровень персонажа",
            ],
            ascending = False
        )




    def prepare_df_character_per_account(self):

        self.df_character_per_account = self.df_origin["account"]\
        .value_counts()\
        .value_counts()\
        .to_frame()\
        .rename(
            columns = {
                "count": "Количество игроков"
            }
        ).reset_index()\
        .rename(
            columns = {
                "count": "Количество персонажей на аккаунт"
            }
        ).sort_values(
            [
                "Количество персонажей на аккаунт"
            ]
        )



