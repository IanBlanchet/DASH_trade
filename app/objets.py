
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CreeContrat:
    def __init__(self, df, ticker, fig):
       self.ticker = ticker
       self.df = df
       self.fig = fig
       self.df['bif'] = False
    
    def create_contrat(self):
        df_actif = self.df
        dict_contrat = {}
        for i in range(len(df_actif)):
            if df_actif.loc[i,'buySell'] == 'SELL' and df_actif.loc[i,'bif'] == False:
                tradedate = df_actif.loc[i, 'tradeDate']
                strike = df_actif.loc[i, 'strike']
                echeance = df_actif.loc[i, 'expiry']

                df_open = df_actif[(df_actif.expiry == echeance) &
                                    (df_actif.tradeDate == tradedate) &
                                    (df_actif.bif == False) ][:2]
                
                
                df_close = df_actif[(df_actif.expiry == echeance) &
                                    (df_actif.tradeDate != tradedate) &
                                    (df_actif.bif == False) ][:2]
                
                if len(df_open) <= 1:
                    type_cont = 'naked'
                    if len(df_close) == 0 :
                        statut = 'open'
                        closer = None
                        date_fermeture = None
                        rachat = None
                    else:
                        statut = 'close'
                        closer = df_close.loc[df_close.index[0]]
                        date_fermeture = closer.tradeDate
                        rachat = closer.netCash
                    le_contrat = {'ticker':self.ticker,
                                  'type_cont':type_cont,
                                  'leg_haut':df_open.loc[df_open.index[0],'strike'],
                                  'leg_bas':None,
                                  'risque':df_open.loc[df_open.index[0],'strike']*100*0.3,
                                  'date_ouverture':df_open.loc[df_open.index[0],'tradeDate'],
                                  'date_fermeture':date_fermeture,
                                  'echeance':echeance,
                                  'vente':df_open.loc[df_open.index[0],'netCash'],
                                  'rachat':rachat,
                                  'statut':statut}
                    dict_contrat[self.ticker+str(i)] = le_contrat
                    df_actif.loc[df_open.index,'bif'] = True
                    df_actif.loc[df_close.index,'bif'] = True

                if len(df_open) > 1:
                    type_cont = 'vertical'
                    if len(df_close) == 0 :
                        statut = 'open'
                        closer = None
                        date_fermeture = None
                        rachat = None
                    else:
                        statut = 'close'
                        date_fermeture = df_close.loc[df_close.index[0], 'tradeDate']
                        if len(df_close) == 1 :
                            rachat = df_close.loc[df_close.index[0], 'netCash']
                        else:
                            rachat = df_close.loc[df_close.index[0], 'netCash']+ df_close.loc[df_close.index[1], 'netCash']
                    le_contrat = {'ticker':self.ticker,
                                  'type_cont':type_cont,
                                  'leg_haut':df_open.loc[df_open.index[0],'strike'],
                                  'leg_bas':df_open.loc[df_open.index[1],'strike'],
                                  'risque':(df_open.loc[df_open.index[0],'strike']-df_open.loc[df_open.index[1],'strike'])*100,
                                  'date_ouverture':df_open.loc[df_open.index[0],'tradeDate'],
                                  'date_fermeture':date_fermeture,
                                  'echeance':echeance,
                                  'vente':df_open.loc[df_open.index[0],'netCash'] + df_open.loc[df_open.index[1],'netCash'],
                                  'rachat':rachat,
                                  'statut':statut}
                    dict_contrat[self.ticker+str(i)] = le_contrat                    
                    df_actif.loc[df_open.index,'bif'] = True
                    df_actif.loc[df_close.index,'bif'] = True


        contrat_df = pd.DataFrame.from_dict(dict_contrat, orient='index')
        contrat_df['duree'] = contrat_df.apply(lambda x : x['date_fermeture']- x['date_ouverture'] if x['statut'] == 'close' else None, axis=1)
        contrat_df['gain'] = contrat_df.apply(lambda x : x['vente'] + x['rachat'] if x['statut'] == 'close' else None, axis=1)
        contrat_df['delai'] = contrat_df.apply(lambda x : datetime.utcnow() - x['date_ouverture'], axis=1)
        contrat_df.drop(contrat_df[(contrat_df.delai > timedelta(days=100))&(contrat_df.statut=='open')].index)
        contrat_df['leg_bas'] = pd.to_numeric(contrat_df['leg_bas'])
        contrat_df.reset_index(inplace=True)
        print(contrat_df.head(), contrat_df.info())
        return contrat_df

                
    def PlotContrat(self, contrat_df):
                
        for j in range(len(contrat_df)):
            
            self.fig.add_trace(go.Scatter(
                                name=str(contrat_df.loc[j,'index']),
                                x=[contrat_df.loc[j, 'date_ouverture']],
                                y=[(contrat_df.loc[j,'leg_haut'])-(contrat_df.loc[j,'vente']/100)],
                                text=str(contrat_df.loc[j,'leg_haut'])+'/'+str(contrat_df.loc[j,'leg_bas']),
                                error_y=dict(
                                    type='data',
                                    symmetric=False,
                                    array=[(contrat_df.loc[j,'vente']/100)],
                                    arrayminus=[((contrat_df.loc[j,'leg_haut'])-(contrat_df.loc[j,'vente']/100))-(contrat_df.loc[j,'leg_bas'])],
                                    width=5,
                                    color='red'
                                )
                                ))
            if contrat_df.loc[j,'statut'] == 'close':
                self.fig.add_trace(go.Scatter(
                                name=str(contrat_df.loc[j,'index'])+'close',
                                x=[contrat_df.loc[j, 'date_fermeture']],
                                y=[(contrat_df.loc[j,'leg_haut'])],
                                text='Gain :'+str(int(contrat_df.loc[j,'vente']+contrat_df.loc[j,'rachat'])),
                                marker_color='green'
                                ))
            self.fig.add_trace(go.Scatter(
                                x=[contrat_df.loc[j, 'date_ouverture'],contrat_df.loc[j, 'echeance']],
                                y=[contrat_df.loc[j,'leg_haut'],contrat_df.loc[j,'leg_haut']],
                                mode='lines',
                                marker_color='yellow',
                                opacity=0.5
                                ))

        
''' enlever le commentaire pour tester localement
transactions = pd.read_excel('transactions.xlsx')
baba_df = transactions[transactions.underlyingSymbol == 'PETS']
baba_df  = baba_df.sort_values(['tradeDate', 'quantity'])
baba_df.reset_index(inplace=True)

fig = make_subplots(specs=[[{"secondary_y": True}]])
le_vertical = CreeContrat(baba_df, 'PETS', fig)
contrat = le_vertical.create_contrat()
#le_vertical.PlotContrat(contrat)'''



