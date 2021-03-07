#from app.config import Config
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app.IB import historique_df, transactions
from app.objets import CreeContrat
import pandas as pd
#from ib_insync import *
'''decommenter pour travailler local
transactions=pd.read_excel('transactions.xlsx')
historique_df=pd.read_excel('historique.xlsx')'''

#l'application DASH
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#app.config.from_object(Config)

fig = make_subplots(specs=[[{"secondary_y": True}]])


app.layout = html.Div(children=[
    html.H1(children='BACKTEST'),

    html.Div(children='''
        Un dashboard qui permet de backtester nos trades
    '''),

    dcc.Dropdown(
        id='ticker',
        options=[{'label':value, 'value':value} for value in pd.unique(transactions.underlyingSymbol)],
        placeholder='select un ticker'       
    ),

    dcc.Graph(
        id='graphique',
        ),
    dash_table.DataTable(
        id='table',
        ),
    
])

@app.callback(
    Output(component_id='graphique', component_property='figure'),
    Output(component_id='table', component_property='data'),
    Output(component_id='table', component_property='columns'),
    Input(component_id='ticker', component_property='value')
)
def update_output_div(ticker):
    fig.data = []
    ticker_df = transactions[transactions.underlyingSymbol == ticker]
    ticker_df  = ticker_df.sort_values(['tradeDate', 'quantity'])
    ticker_df.reset_index(inplace=True)
    #trace l'historique du titre (volatilité et prix)
    histo = historique_df[historique_df.ticker == ticker]
    fig.add_trace(go.Scatter(x=histo.Date,
                            y=histo['prix(close)'],
                            mode='lines',
                            name='Prix',
                            marker_color='blue'
                            ), secondary_y=False)
    fig.add_trace(go.Scatter(x=histo.Date,
                            y=histo['IV(close)'],
                            mode='lines',
                            name='IV',
                            marker_color='purple'
                            ), secondary_y=True)
    #fait afficher le vertical
    les_contrats = CreeContrat(ticker_df, ticker, fig)
    contrat_df = les_contrats.create_contrat()
    les_contrats.PlotContrat(contrat_df)

    #affiche le ticker en titre
    fig.update_layout(
    barmode='relative', title_text=ticker
)
    return fig, contrat_df.to_dict('records'), [{"name":i, "id":i} for i in contrat_df.columns]


if __name__ == '__main__':
    app.run_server(debug=True, port=5000, use_reloader=False)