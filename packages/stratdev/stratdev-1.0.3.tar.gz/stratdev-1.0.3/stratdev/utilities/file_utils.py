import os
from stratdev.backtesting.bt_file_content import data_prep, strategy, backtest


def create_file(name: str, content: str, folder: str) -> None:
    """
    Create Python file with pre-written content
    """
    with open(f'./{folder}/{name}.py', 'w') as f:
        f.write(content)
        

def create_files(path: str='./') -> None:
    """
    Create backtesting session files
    """
    filenames = ['data_prep','strategy','backtest']
    files = [data_prep, strategy, backtest]

    for name, content in zip(filenames, files):
        create_file(name, content, path)


def create_folders(path: str='./') -> None:
    """
    Create necessary folders for backtesting session
    """
    folder_names = ['ohlc','htmls','stats','trades','pdfs']

    # Check if folders already exists
    folder_check = [os.path.isdir(f'{path}/{folder}') for folder in folder_names]

    # Create Main folders
    if True not in folder_check:
        for name in folder_names:
            os.mkdir(f'{path}/{name}')
        print('Folders created')
    elif False not in folder_check:
        print('All necessary folders found')
    else:
        i = 0
        while i < len(folder_check):
            false_idx = folder_check.index(False, i)
            os.mkdir(f'{path}/{folder_names[false_idx]}')
            print(f'{folder_names[false_idx]} was created because it was not found')
            i = false_idx + 1


def write_to_file(file: str, new_lines: list, line_nums: list[int]) -> None:
    """
    Write new lines or replace lines in a file by selecting which line numbers to replace / write
    """
    with open(file, 'r') as f:
        lines = f.readlines()
    
    for line, num in zip(new_lines, line_nums):
        lines[num - 1] = line + '\n'

    with open(file, 'w') as f:
        f.writelines(lines)


def verify_paths(paths: list[str]) -> None:
    """
    Verifies existance of list of files/folders
    """
    not_found = False
    for path in paths:
        check_folder = os.path.isdir(path)
        check_files = os.path.isfile(path)
        if not check_folder and not check_files:
            print(f"{path} not found.")
            not_found = True
        else:
            continue
    if not_found:
        print("Check that you are in the correct directory or that the necessary files/folders exist.")


def verify_filename(filename: str) -> bool:
    """
    Verifies whether folder or file name contains valid characters.
    """
    forbidden_char = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '.', ',']

    if any(f in filename for f in forbidden_char):
        invalid_chars = [f for f in forbidden_char if f in filename]
        print(f"{filename} contains invalid character(s): {str(invalid_chars).strip('[').strip(']')}")
        return False
    else:
        return True
    

def check_duplicates(name: str) -> bool:
    """
    """
    check_name_folder = os.path.isdir(name)
    check_name_file = os.path.isfile(name)

    if check_name_folder or check_name_file:
        print("File or Folder already exists")
        return True
    else:
        return False

