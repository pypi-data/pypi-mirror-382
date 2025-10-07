import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from stratdev.backtesting.bt import BacktestingPy
from stratdev.backtesting.analysis import *


# Export Paths 
htmls_path = './htmls/'
trades_path = './trades/'
stats_path = './stats/'
pdfs_path = './pdfs/'

def backtest_analysis(strategy: object,
                dfs: dict[pd.DataFrame],
                cash: int=10000,
                spread: float=0.0,
                commission: float=0.0,
                margin: float=1.0,
                trade_on_close: bool=False,
                hedging: bool=False,
                exclusive_orders: bool=False,
                finalize_trades: bool=False
                ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run backtest on dictionary of OHLC DataFrames. Results of backtests are saved to appropriate
    folders. Analysis plots saved to appropriate folder(s).
    """

    btpy = BacktestingPy(strategy, 
                        dfs, 
                        html_path=htmls_path, 
                        stats_path=stats_path,
                        trades_path=trades_path)
    
    stats, trades, equity_curves = btpy.multi_backtest(cash=cash,
                                                              spread=spread,
                                                              commission=commission,
                                                              margin=margin,
                                                              trade_on_close=trade_on_close,
                                                              hedging=hedging,
                                                              exclusive_orders=exclusive_orders,
                                                              finalize_trades=finalize_trades)

    # Analysis
    return_v_dd = returns_vs_drawdowns(btpy, stats)
    ec_plot = plot_equity_curves(btpy, equity_curves)
    ratios_plot = ratios(btpy, stats)

    # Export to PDF
    with PdfPages(f'{pdfs_path}returns_vs_drawdowns.pdf') as pdf:
        pdf.savefig(return_v_dd)

    with PdfPages(f'{pdfs_path}equity_curves.pdf') as pdf:
        pdf.savefig(ec_plot)

    with PdfPages(f'{pdfs_path}ratios.pdf') as pdf:
        pdf.savefig(ratios_plot)

    return stats, trades, equity_curves


# if __name__ == "__main__":

    # from backtesting import Backtest, Strategy
    # from backtesting.lib import crossover

    # from backtesting.test import SMA
    # from get_dfs import get_dfs

    # html_path = './htmls/'
    # stats_path = './stats/'
    # trades_path = './trades/'

    # class SmaCross(Strategy):
    #     n1 = 10
    #     n2 = 20

    #     def init(self):
    #         close = self.data.Close
    #         self.sma1 = self.I(SMA, close, self.n1)
    #         self.sma2 = self.I(SMA, close, self.n2)

    #     def next(self):
    #         if crossover(self.sma1, self.sma2):
    #             self.position.close()
    #             self.buy()
    #         elif crossover(self.sma2, self.sma1):
    #             self.position.close()
    #             self.sell()


    # dfs = get_dfs('../ohlc_csv/', '4y', '1d')
    # backtest_analysis(SmaCross, dfs, finalize_trades=True)   

