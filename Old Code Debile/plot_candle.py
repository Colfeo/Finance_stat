#import plotly.graph_objects as go
#import pandas as pd
#
#
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
#
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








import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
  
X = deque(maxlen = 5)
X.append(1)
  
Y = deque(maxlen = 5)
Y.append(1)
  
app = dash.Dash(__name__)
  
app.layout = html.Div(
    [
        dcc.Graph(id = 'live-graph', animate = True),
        
        dcc.Interval(
            id = 'graph-update',
            interval = 1000,
            n_intervals = 0
        ),
    ]
)
  
@app.callback(
    Output('live-graph', 'figure'),
    [ Input('graph-update', 'n_intervals') ]
)
  
def update_graph_scatter(n):
    X.append(X[-1]+1)
    Y.append(Y[-1]+Y[-1] * random.uniform(-0.1,0.1))
  
    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
    )
  
    return {'data': [data],
            'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),yaxis = dict(range = [min(Y),max(Y)]),)}
  
if __name__ == '__main__':
    app.run_server()

