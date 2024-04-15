from dash import Dash, html, dcc, Input, Output, State, callback
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import date


def getIndicator(df):  # df(for one item): stock price or etf price
    def return_fn(df):
        return df.pct_change().fillna(
            0
        )  # pct_change() -> (다음행 - 현재행) / 현재형 -> 일일수익률

    def cum_return_fn(df_return):  # 누적승률
        # 승률 = (성공한 매매횟수 / 전체 매매횟수) : 한번의 매매에서 익절을 할 확률
        # 손익비 = 평균 이익금 / 평균 손실금
        return (1 + df_return).cumprod()  # (1 + 0.3)*(1 - 0.1)*(1 +  0.1),....

    df["Return"] = return_fn(df)
    df["CumReturn"] = cum_return_fn(df["Return"])
    df["MaxCumReturn"] = df["CumReturn"].cummax()
    # drawdown: how much an investment is down from the peak before it recovers back to the peak(%)
    # 시작일자부터 현재까지 기간 중 최고점에서 몇프로 빠졌나
    df["DrawDown"] = round(((df["CumReturn"] / df["MaxCumReturn"]) - 1) * 100, 2)

    return df


def change_date_format(datetime):
    # datetime -> str
    year = datetime.year
    month = datetime.month
    day = datetime.day
    return f"{year} / {month} / {day}"


# load df
df = pd.read_pickle("app/data/etf.pkl")

# kodex columns
# cols = [col for col in df.columns if 'kodex' in col.lower()]

# options
options = [{"label": col, "value": col} for col in df.columns]

# 2. create app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    requests_pathname_prefix="/quiz/dashboard/",
)

app.layout = html.Div(
    [
        html.Br(),
        html.H1("ETF Dashboard"),
        html.Div(
            id="layout1",
            children=[
                html.H3("Select one of ETF :"),
                dcc.Dropdown(
                    id="idx",
                    options=options,
                    value="KODEX 200",
                    style={"width": "350px"},
                ),
            ],
            style={"display": "inline-block", "verticalAlign": "top", "width": "30vw"},
        ),
        html.Br(),
        html.Br(),
        html.Div(
            id="layout2",
            children=[
                dcc.DatePickerRange(
                    id="date1",
                    min_date_allowed=date(2012, 2, 11),
                    max_date_allowed=date(2022, 4, 1),
                    initial_visible_month=date(2021, 1, 1),
                    start_date=date(2021, 1, 1),
                    end_date=date(2021, 12, 31),
                ),
                html.Br(),
                html.Br(),
                html.Button(
                    "Submit", id="btn1", n_clicks=0, style={"fontSize": "16px"}
                ),
            ],
        ),
        # https://dash.plotly.com/dash-core-components/store
        # https://dash.plotly.com/sharing-data-between-callbacks
        dcc.Store(id="save_data"),
        dcc.Graph(id="chart1"),
        dcc.Graph(id="chart2"),
        html.Div(
            id="layout3",
            children=[
                dcc.Dropdown(
                    id="two_idx",
                    options=options,
                    placeholder="Please select two indices.",
                    style={"width": "350px"},
                    value=["KODEX 200", "KODEX 반도체"],
                    multi=True,  # value is an array of items with values corresponding to those in the options prop.
                ),
            ],
            style={"display": "inline-block", "verticalAlign": "top", "width": "30vw"},
        ),
        html.Br(),
        html.Br(),
        html.Div(
            id="layout4",
            children=[
                dcc.DatePickerRange(
                    id="date2",
                    min_date_allowed=date(2012, 2, 11),
                    max_date_allowed=date(2022, 4, 1),
                    initial_visible_month=date(2021, 1, 1),
                    start_date=date(2021, 1, 1),
                    end_date=date(2021, 12, 31),
                ),
                html.Br(),
                html.Br(),
                html.Button(
                    "Submit", id="btn2", n_clicks=0, style={"fontSize": "16px"}
                ),
            ],
        ),
        dcc.Graph(id="chart3"),
    ]
)


@app.callback(
    Output(component_id="chart1", component_property="figure"),
    Output(component_id="chart2", component_property="figure"),
    Input(component_id="btn1", component_property="n_clicks"),
    State(component_id="idx", component_property="value"),
    State(component_id="date1", component_property="start_date"),
    State(component_id="date1", component_property="end_date"),
)
def showPlot(n_clicks, col, start_date, end_date):

    df = pd.read_pickle("app/data/etf.pkl")
    df = df.loc[start_date:end_date, [col]].dropna()

    trace1 = go.Scatter(x=df.index, y=df[col], mode="lines", name=f"{col}")
    layout1 = go.Layout(
        title="{}".format(col),
        xaxis={
            "title": change_date_format(df.index[0])
            + " ~ "
            + change_date_format(df.index[-1])
        },
        yaxis={"tickformat": ","},
    )
    fig1 = go.Figure(trace1, layout1)

    # calculate drawdown
    drawdown_df = getIndicator(df)
    trace2 = go.Scatter(
        x=drawdown_df.index,
        y=drawdown_df["DrawDown"],
        mode="lines",
        name=f"{col} drawdown",
        fill="tonexty",
    )
    layout2 = go.Layout(
        title=f"DrawDown of {col}",
        xaxis={
            "title": change_date_format(df.index[0])
            + " ~ "
            + change_date_format(df.index[-1])
        },
        yaxis={"tickformat": "%"},
    )

    fig2 = go.Figure(trace2, layout2)

    return fig1, fig2


@app.callback(
    Output(component_id="chart3", component_property="figure"),
    Input(component_id="btn2", component_property="n_clicks"),
    State(component_id="two_idx", component_property="value"),
    State(component_id="date2", component_property="start_date"),
    State(component_id="date2", component_property="end_date"),
)
def update_correlation(n_clicks, two_idx: list, start, end):

    # load original data
    df = pd.read_pickle("app/data/etf.pkl")
    df = df[two_idx]

    # filter by date and drop NaN value
    df = df.loc[start:end].dropna()

    # column name
    kind1, kind2 = two_idx

    # calculate correation
    correlation = df.corr(method="pearson")
    correlation = correlation.loc[kind1, kind2]
    correlation = round(correlation, 2)

    # 1. data
    X, y = df[kind1], df[kind2]

    # 2. scatter
    trace = go.Scatter(
        x=X,
        y=y,
        mode="markers",
        marker=dict(size=6, symbol="circle"),
        line=dict(width=2),
    )

    # 3. layout

    layout = go.Layout(
        title=f"{kind1} & {kind2} Scatter Plot <br> Correlation: {correlation}",
        xaxis={"title": f"{kind1}", "tickformat": ","},
        yaxis={"title": "{}".format(kind2), "tickformat": ","},
    )

    # 4. figure
    fig = go.Figure(data=trace, layout=layout)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
