import os 
from ohlc_data.utils import dropdown
from stratdev.utilities.file_utils import verify_filename, check_duplicates, create_folders, create_files
from stratdev.utilities.customize import set_strategy, set_timeframe

def main():
    """
    Create new backtesting session. Creates session folder, subfolders, 
    and session file templates.

    /Main directory/
        --> /Main session folder/
                --> /ohlc/
                --> /htmls/
                --> /stats/
                --> /trades/
                --> /pdfs/

                --> data_prep.py
                --> strategy.py
                --> backtest.py
    """ 
    pwd = os.getcwd()

    while True:
        new_directory = input("Enter name for session folder: ")
        if not verify_filename(new_directory) or check_duplicates(new_directory):
            continue
        else:
            os.mkdir(new_directory)
            create_folders(new_directory)
            create_files(new_directory)

            strat_name_yn = dropdown("Set Strategy Name? (Can be done later)", ["Yes","No"])
            if strat_name_yn == "Yes":
                strat_path = f"{pwd}/{new_directory}/strategy.py"
                bt_path = f"{pwd}/{new_directory}/backtest.py"
                set_strategy(init=True, strat_path=strat_path, bt_path=bt_path)
            timeframe_yn = dropdown("Set Timeframe? (Can be done later)", ["Yes", "No"])
            if timeframe_yn == "Yes":
                if not os.path.isdir('./ohlc_csv/'):
                    os.mkdir('./ohlc_csv/')
                data_prep_path = f"{pwd}/{new_directory}/data_prep.py"
                set_timeframe(ohlc_csv_path='./ohlc_csv/', data_prep_path=data_prep_path)
            break


if __name__ == "__main__":
    main()
   
