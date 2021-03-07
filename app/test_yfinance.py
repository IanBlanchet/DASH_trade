import yfinance as yf
import pandas as pd
from datetime import datetime

baba = yf.Ticker("msft")
print(type(baba.info))

df = baba.financials
print(df)

opt = baba.option_chain('2021-03-05')
print(opt)