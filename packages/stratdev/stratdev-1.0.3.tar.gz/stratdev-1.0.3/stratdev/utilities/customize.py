import os
from ohlc_data.utils import dropdown
from stratdev.utilities.file_utils import write_to_file, verify_paths, verify_filename
from stratdev.utilities.get_utils import get_line_numbers


def set_timeframe(ohlc_csv_path: str='../ohlc_csv/', data_prep_path: str='./data_prep.py') -> None:
    """
    Run script to change the period and interval in data_prep.py
    """
    verify_paths([ohlc_csv_path, data_prep_path])
    intervals = os.listdir(ohlc_csv_path)

    line_nums = get_line_numbers(data_prep_path, ["period =", "interval ="])
    period_line_num = line_nums[0]
    interval_line_num = line_nums[1]

    # If no ohlc_csv timeframe subfolders
    if len(intervals) == 0:
        manual_yn = dropdown("Main OHLC folder contains no timeframe subfolders, manually enter period and interval?", ["Yes","No"])
        if manual_yn:
            while True:
                period_select = input("Enter period ([n]y or [n]d for number of years or number of days): ")
                if period_select[-1] not in ['y', 'd']:
                    print("Invalid period. Specify number of years ('[n]y') or number of days ('[n]d')")
                    continue
                else:
                    break
            while True:
                interval_select = input("Enter interval ([n]d - days, [n]h - hours, [n]m - minutes): ")
                if interval_select[-1] not in ['d', 'h', 'm']:
                    print("Invalid interval. Specify number of days ('[n]d'), number of hours ('[n]h') or number of minutes ('[n]m')")
                else:
                    break

    else:
        # INTERVAL
        interval_select = dropdown('Choose interval: ', intervals)

        interval_csvs = os.listdir(f'{ohlc_csv_path}{interval_select}/')

        # PERIOD 
        periods = []
        for file in interval_csvs:
            file_split = file.split('_')
            if len(file_split) > 3:
                if file_split[1:3] not in periods:
                    periods.append(file_split[1:3])
            else:
                if file_split[1] not in periods:
                    periods.append(file_split[1])

        period_select = dropdown('Choose period: ', periods)

    # Write new period and inteval in data_prep.py
    new_lines = [
        f"period = '{period_select}'",
        f"interval = '{interval_select}'"
    ]

    line_nums = [period_line_num, interval_line_num]

    write_to_file(data_prep_path, new_lines, line_nums)



def set_strategy(init:bool=False, strat_path: str='./strategy.py', bt_path: str='./backtest.py') -> None:
    """
    Run script to change strategy name in strategy.py and backtest.py
    """
    verify_paths([strat_path, bt_path])
    line_num_strat = get_line_numbers(strat_path, ["class"])
    line_nums_bt = get_line_numbers(bt_path, ["strategy", "backtest_analysis("])
    
    with open(strat_path, 'r') as file:
        lines = file.readlines()
        curr_strat_line = lines[line_num_strat[0] - 1]
        curr_strat = curr_strat_line[6:].split('(')[0]

    if init == True:
        change_name = 'Yes'
    else:
        change_name = dropdown(f"Current name for strategy is: '{curr_strat}'. Change name?", ['Yes','No'])

    if change_name == 'Yes':
        while True:
            strat_name = input("New Strategy Name: ")
            strat_name = strat_name.replace(" ", "").strip()
            if not verify_filename(strat_name):
                continue
            else:
                break

        new_strat_line_strategy = f"class {strat_name}(Strategy):"
        new_strat_line_import = f"from strategy import {strat_name}"
        new_strat_line_backtest = f"backtest_analysis({strat_name}, updated_dfs)"

        write_to_file(strat_path, [new_strat_line_strategy], [line_num_strat[0]])
        write_to_file(bt_path, [new_strat_line_import], [line_nums_bt[0]])
        write_to_file(bt_path, [new_strat_line_backtest], [line_nums_bt[1]])
       
