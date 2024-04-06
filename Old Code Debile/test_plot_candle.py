import plotly.graph_objects as go
import pandas as pd

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import flask
import waitress
from waitress import serve


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

print(len(df))
print(df['AAPL.Open'][0])

server = flask.Flask(__name__)

app = dash.Dash(__name__)

app.layout = html.Div(
    html.Div([
        dcc.Graph(id='live-update-graph-scatter', animate=True),
        dcc.Interval(
            id='interval-component',
            disabled=False,
            interval=1*5000,
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-graph-scatter', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_scatter(n):


    rec = pd.read_sql_table('crypto', engine)
    rec1 = pd.DataFrame(rec)
    print(rec1)
    rec1.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'EMA', 'EMA2']

    rec1['date'] = pd.to_datetime(rec1['date'])
    rec1.set_index('date', inplace=True)

    ###SUBPLOT AND Candlestick CHART
    fig = make_subplots(rows=4, cols=1)

    fig.add_trace(go.Candlestick(
        x=rec1.index,
        open=rec1['open'],
        high=rec1['high'],
        low=rec1['low'],
        close=rec1['close']),
        row=1,
        col=1,
    )

    ###### ADD INDICATOR TRACES:
#    fig.add_trace(
#        go.Scatter(
#            x=rec1.index,
#            y=rec1['EMA'],
#            marker=dict(color='blue')
#        ),
#        row=1,
#        col=1
#    )
#    fig.add_trace(
#        go.Scatter(
#            x=rec1.index,
#            y=rec1['EMA2'],
#            marker=dict(color='red')
#        ),
#        row=1,
#        col=1
#    )



    return fig


if __name__ == '__main__':
    serve(app.server, host="localhost", port=5005)

#fig = go.Figure(data=[go.Candlestick(x=df['Date'],
#                open=df['AAPL.Open'], high=df['AAPL.High'],
#                low=df['AAPL.Low'], close=df['AAPL.Close'])
#                      ])
#
#fig.update_layout(
#    title='The Great Recession',
#    yaxis_title='AAPL Stock',
#    shapes = [dict(
#        x0='2016-12-09', x1='2016-12-09', y0=0, y1=1, xref='x', yref='paper',
#        line_width=2)],
#    annotations=[dict(
#        x='2016-12-09', y=0.05, xref='x', yref='paper',
#        showarrow=False, xanchor='left', text='Increase Period Begins')]
#)
#
#fig.show()