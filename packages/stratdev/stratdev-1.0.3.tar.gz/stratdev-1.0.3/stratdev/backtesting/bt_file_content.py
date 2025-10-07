
"""
Content for backtesting session py files
"""

strategy = (
"""
import pandas as pd
from datetime import datetime, time
from backtesting import Strategy, Backtest


class StratName(Strategy):
    """
    
    """

    def init(self):
        pass


    def next(self):

        price = self.data.Close[-1]


        if not self.position:
            pass
"""
)

data_prep = (
"""
import pandas_ta as ta
from stratdev.utilities.get_utils import get_dfs

ohlc_csv_path = '../ohlc_csv/'
updated_ohlc_path = './ohlc/'
period = ''
interval = ''

dfs = get_dfs(ohlc_csv_path, period, interval)   

for ticker in dfs.keys():
    df = dfs[ticker]
    # Modify or add to DataFrame (calculations, indicators, etc)
    df.to_csv(f'{updated_ohlc_path}{ticker}_{period}_{interval}_updated.csv')

updated_dfs = get_dfs(updated_ohlc_path, period, interval, from_main=False)
"""
)

backtest = (
"""
from stratdev.backtesting.run_backtest import backtest_analysis   
from strategy import StratName 
from data_prep import updated_dfs 

backtest_analysis(StratName, updated_dfs)
"""
)