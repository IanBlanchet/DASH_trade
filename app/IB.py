from app.config import Config
import pandas as pd
from ib_insync import *
from datetime import datetime

token = Config.token

ib = IB()
ib.connect('127.0.0.1', 4001, 123) # 7497 avec tws ou rien

#extrait les transactions de l'année précédente
mon_rapport = FlexReport(token=token,queryId='517875')

transactions = mon_rapport.df('Trade')
transactions = transactions[transactions.multiplier == 100]
print(transactions.info())
transactions = transactions[['symbol','underlyingSymbol', 'quantity', 'tradeDate', 'buySell',
 'netCash', 'strike', 'expiry', 'fifoPnlRealized', 'underlyingListingExchange', 'currency']]

transactions['tradeDate'] = pd.to_datetime(transactions['tradeDate'])
transactions['expiry'] = pd.to_datetime(transactions['expiry'])
transactions['netCash'] = transactions['netCash'].apply(lambda x : int(x))
transactions.to_excel('transactions.xlsx')
transactions = transactions.sort_values('tradeDate')

#créer un dataframe des données historiques de tous les titres sur lequel il y a un trade
unique_df = transactions.drop_duplicates(subset=['underlyingSymbol'])
unique_df.reset_index(inplace=True)

date = []
IV = []
prix = []
le_ticker = []
for i in range(len(unique_df)):
    try:
        le_contract = Stock(unique_df.loc[i,'underlyingSymbol'], 'SMART', 'USD')# a revoir, unique_df.loc[i,'underlyingListingExchange'])
        ib.qualifyContracts(le_contract)
        historical_implied = ib.reqHistoricalData(
            le_contract,
            '',
            barSizeSetting='1 day',
            durationStr='52 W',
            whatToShow='OPTION_IMPLIED_VOLATILITY',
            useRTH=True
        )
        historical_midpoint = ib.reqHistoricalData(
            le_contract,
            '',
            barSizeSetting='1 day',
            durationStr='52 W',
            whatToShow='MIDPOINT',
            useRTH=True
        )
        print(len(historical_implied), len(historical_midpoint))

        if len(historical_implied) == len(historical_midpoint):
            for item in historical_implied:
                IV.append(item.close)
                le_ticker.append(unique_df.loc[i,'underlyingSymbol'])
            for item in historical_midpoint:
                date.append(item.date)
                prix.append(item.close)

        else:
           continue


    except:
        pass

dicto = {'Date':date, 'ticker':le_ticker, 'prix(close)':prix, 'IV(close)':IV}
historique_df = pd.DataFrame(dicto)
historique_df.to_excel('historique.xlsx')


ib.disconnect()







