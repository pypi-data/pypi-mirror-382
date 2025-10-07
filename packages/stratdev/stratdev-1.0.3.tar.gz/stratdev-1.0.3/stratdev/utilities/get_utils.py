import os
import pandas as pd

def get_dfs(ohlc_path: str, period: str, interval: str, from_main: bool=True) -> dict[pd.DataFrame]:
    """
    Retrieves OHLC DataFrame from main ohlc folder (ohlc_csv) or local ohlc folder. Returns dictionary of DataFrames 
    matching specific period and interval
    """
    dfs = {}
    path = os.listdir(f'{ohlc_path}') if from_main == False else os.listdir(f'{ohlc_path}{interval}/')
    for file in path:
        split = file.split('_')
        symbol = split[0]
        datetime_col = 'Datetime' if 'd' not in interval else 'Date'
        
        df = pd.read_csv(f'{ohlc_path}{symbol}_{period}_{interval}_updated.csv') if from_main == False else pd.read_csv(f'{ohlc_path}{interval}/{symbol}_{period}_{interval}.csv')
        df = df.set_index(datetime_col)
        df.index = pd.to_datetime(df.index)

        dfs[symbol] = df


    return dfs

def get_line_numbers(path: str, target_lines: list[str]):
    """
    Read a text or py file and return the line numbers for target lines.
    """
    target_line_numbers = []
    with open(path, 'r', encoding='utf-8') as file:
        for target in target_lines:
            file.seek(0)
            for line_num, line in enumerate(file, 1):
                if target in line:
                    target_line_numbers.append(line_num)


    return target_line_numbers

