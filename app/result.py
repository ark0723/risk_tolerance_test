from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL

from models import Quiz, Participant
import pandas as pd

import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, State, callback


# 데이터베이스 연결 설정
engine = create_engine(SQLALCHEMY_DATABASE_URL)
conn = engine.connect()

# create session object to initiate query in database
Session = sessionmaker(bind=engine)
session = Session()

# load all data from quiz table
sql = "SELECT * FROM quiz"
df = pd.read_sql(sql, conn, index_col="id")
df["point"] = None


def calculate_q1(x):
    if x == "19세 이하":
        return 12.5
    elif x == "20세~40세":
        return 12.5
    elif x == "41세~50세":
        return 9.3
    elif x == "51세~60세":
        return 6.2
    elif x == "61세 이상":
        return 3.1
    else:
        return 0


def calculate_q2(x):
    if x == "less_six_months":
        return 3.1
    elif x == "less_one_year":
        return 6.2
    elif x == "less_two_year":
        return 9.3
    elif x == "less_three_year":
        return 12.5
    elif x == "more_than_three":
        return 15.6
    else:
        return 0


def calculate_q3(x):
    if x == "opt1":
        return 3.1
    elif x == "opt2":
        return 6.2
    elif x == "opt3":
        return 9.3
    elif x == "opt4":
        return 12.5
    elif x == "opt5":
        return 15.6
    else:
        return 0


def calculate_q4(x):
    if x == "very_low":
        return 3.1
    elif x == "low":
        return 6.2
    elif x == "intermediate":
        return 9.3
    elif x == "high":
        return 12.5
    else:
        return 0


def calculate_q5(x):
    if x == "less_10_percent":
        return 15.6
    elif x == "less_20_percent":
        return 12.5
    elif x == "less_30_percent":
        return 9.3
    elif x == "less_40_percent":
        return 6.2
    elif x == "more_40_percent":
        return 3.1
    else:
        return 0


def calculate_q6(x):
    if x == "increase":
        return 9.3
    elif x == "decrease":
        return 6.2
    elif x == "retirement_fund":
        return 3.1
    else:
        return 0


def calculate_q7(x):
    if x == "no_loss":
        return -6.2
    elif x == "less_10":
        return 6.2
    elif x == "less_20":
        return 12.5
    elif x == "high_risk":
        return 18.7
    else:
        return 0


# data preprocessing
df.loc[df["question_id"] == 1, "point"] = df[df["question_id"] == 1][
    "chosen_answer"
].apply(calculate_q1)
df.loc[df["question_id"] == 2, "point"] = df[df["question_id"] == 2][
    "chosen_answer"
].apply(calculate_q2)
df.loc[df["question_id"] == 3, "point"] = df[df["question_id"] == 3][
    "chosen_answer"
].apply(calculate_q3)
df.loc[df["question_id"] == 4, "point"] = df[df["question_id"] == 4][
    "chosen_answer"
].apply(calculate_q4)
df.loc[df["question_id"] == 5, "point"] = df[df["question_id"] == 5][
    "chosen_answer"
].apply(calculate_q5)
df.loc[df["question_id"] == 6, "point"] = df[df["question_id"] == 6][
    "chosen_answer"
].apply(calculate_q6)
df.loc[df["question_id"] == 7, "point"] = df[df["question_id"] == 7][
    "chosen_answer"
].apply(calculate_q7)

print(df.head(20))


# 1. participant 총 점수 구하기
def calculate_total_points(df, participant_id: int):
    # get dataframe by participant_id
    total_points = df[df["participant_id"] == participant_id]["point"].sum()
    print(total_points)

    if total_points <= 20:
        return "안정형"
    elif total_points <= 40:
        return "안정추구형"
    elif total_points <= 60:
        return "위험중립형"
    elif total_points <= 80:
        return "적극투자형"
    else:
        return "공격투자형"


def draw_inv_type_ratio(df):
    # participant id list
    p_id_list = df["participant_id"].unique()

    # calculate ratio
    labels = ["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"]
    ratio_data = [calculate_total_points(df, p) for p in p_id_list]
    ratio_count = [ratio_data.count(label) for label in labels]

    # data for piechart
    pie_df = pd.DataFrame(ratio_count)
    pie_df.index = labels
    pie_df.columns = ["Type"]

    trace = go.Pie(labels=pie_df.index, values=pie_df["Type"])
    layout = go.Layout(title="투자성향 분포도")
    fig = go.Figure(data=trace, layout=layout)
    fig.write_html("app/templates/inv_type.html")


draw_inv_type_ratio(df)


def draw_participant_attributes():
    # get dataframe by participant_id
    df = pd.read_sql_query(
        sql=session.query(Participant.age, Participant.gender).statement,
        con=engine,
    )


# 1. participant 총 점수 구하기
def get_total_points(participant_id: int):
    # get dataframe by participant_id
    df = pd.read_sql_query(
        sql=session.query(Quiz.question_id, Quiz.chosen_answer)
        .filter(Quiz.participant_id == participant_id)
        .statement,
        con=engine,
    )
