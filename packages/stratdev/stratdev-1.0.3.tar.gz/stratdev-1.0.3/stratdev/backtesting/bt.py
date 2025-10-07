import pandas as pd
from backtesting import Backtest

class BacktestingPy:

    def __init__(self, strategy: object, dfs: dict[pd.DataFrame]=None,
                 html_path: str=None, stats_path: str=None, trades_path: str=None):
        
        self.strategy = strategy
        self.dfs = dfs
        self.html_path = html_path
        self.stats_path = stats_path
        self.trades_path = trades_path
        self.strat_name = self.strategy.__name__


    def _clean_stats(self, stats: object) -> pd.Series:
        """
        Isolate stats in stats object. Return pd.Series of stats rounded to nearest hundredth.

        Stats included in pd.Series:

        Start, End, Duration, Exposure Time [%], Equity Peak [$], Return [$], Buy & Hold Return [%],
        Return (Ann.) [%], CAGR [%], Sharpe Ratio, Sortino Ratio, Calmar Ratio, Alpha [%],
        Beta, Max. Drawdown [%], Avg. Drawdown [%], Max. Drawdown Duration, Avg. Drawdown Duration,
        Trades, Win Rate [%], Best Trade [%], Worst Trade [%], Avg. Trade [%], Max. Trade Duration
        Avg. Trade Duration, Profit Factor, Expectancy [%], SQN, Kelly Criterion
        """

        stats_index = []
        stats_column = []

        for i in range(30):
            stats_index.append(stats.index[i])
            stats_column.append(stats.iloc[i])

        stats_series = pd.Series(stats_column, index=stats_index)
        stats_series = stats_series.apply(lambda x: round(x, 2) if isinstance(x, float) else x)
        
        return stats_series


    def _multi_stats(self, stats: dict) -> pd.DataFrame:
        """
        Convert dictionary of stats to pd.DataFrame
        """
        return pd.DataFrame(stats).T
    

    def _multi_trades(self, trades: dict) -> pd.DataFrame:
        """
        Combine all trades dataframes into one pd.DataFrame
        """
        return pd.concat(trades)


    def _multi_equity_curves(self, equity_curves: dict) -> pd.DataFrame:
        """
        Converts dictionary of equity curves and drawdowns into pd.DataFrame
        """
        return pd.concat(equity_curves)


    def backtest(self, i: int=0, *, cash: int=10000, spread: float=0.0, commission: float=0.0,
                 margin: float=1.0, trade_on_close: bool=False, hedging: bool=False,
                 exclusive_orders: bool=False, finalize_trades: bool=False) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
        """
        Run backtest using backtesting.Backtest for one ticker
        """
        ticker = list(self.dfs.keys())[i]
        df = self.dfs[ticker]

        bt = Backtest(df, self.strategy, cash=cash, spread=spread, commission=commission, margin=margin,
                      trade_on_close=trade_on_close, hedging=hedging, exclusive_orders=exclusive_orders,
                      finalize_trades=finalize_trades)

        full_stats = bt.run()
        stats = self._clean_stats(full_stats).fillna(0)
        trades = full_stats._trades
        equity_curve = full_stats._equity_curve

        if self.html_path:
            bt.plot(filename=f'{self.html_path}{ticker}_{self.strat_name}.html', open_browser=False)
        else:
            bt.plot()

        if self.stats_path:
            stats.to_csv(f'{self.stats_path}{ticker}_{self.strat_name}_stats.csv')
        if self.trades_path:
            trades.to_csv(f'{self.trades_path}{ticker}_{self.strat_name}_trades.csv')
        
        return stats, trades, equity_curve


    def multi_backtest(self, cash: int=10000, spread: float=0.0, commission: float=0.0,
                 margin: float=1.0, trade_on_close: bool=False, hedging: bool=False,
                 exclusive_orders: bool=False, finalize_trades: bool=False) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Perform backtest on all tickers using backtesting.Backtest
        """

        stats_dict = {}
        trades_dict = {}
        equity_curves_dict = {}

        for i in range(len(self.dfs.keys())):
            ticker = list(self.dfs.keys())[i]
            stats, trades, equity_curve = self.backtest(i=i, cash=cash, spread=spread, commission=commission, margin=margin,
                                        trade_on_close=trade_on_close, hedging=hedging, exclusive_orders=exclusive_orders,
                                        finalize_trades=finalize_trades)
            
            stats_dict[ticker] = stats
            trades_dict[ticker] = trades
            equity_curves_dict[ticker] = equity_curve[~equity_curve.index.duplicated(keep='first')]
        
        all_stats = self._multi_stats(stats_dict)
        all_trades = self._multi_trades(trades_dict)
        all_equity_curves = self._multi_equity_curves(equity_curves_dict)

        return all_stats, all_trades, all_equity_curves


# if __name__ == "__main__":
#     from backtesting import Backtest, Strategy
#     from backtesting.lib import crossover

#     from backtesting.test import SMA
#     from package_dev.btpy_session.src.btpy_session.get_dfs import get_dfs

#     html_path = './htmls/'
#     stats_path = './stats/'
#     trades_path = './trades/'

#     class SmaCross(Strategy):
#         n1 = 10
#         n2 = 20

#         def init(self):
#             close = self.data.Close
#             self.sma1 = self.I(SMA, close, self.n1)
#             self.sma2 = self.I(SMA, close, self.n2)

#         def next(self):
#             if crossover(self.sma1, self.sma2):
#                 self.position.close()
#                 self.buy()
#             elif crossover(self.sma2, self.sma1):
#                 self.position.close()
#                 self.sell()
    
#     dfs = get_dfs('../ohlc_csv/', '4y', '1d')

#     btpy = BacktestingPy(SmaCross, dfs, html_path, stats_path, trades_path)

#     bt = btpy.backtest()

    # mbt = btpy.multi_backtest()
    
