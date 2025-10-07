import os
import yfinance as yf
from datetime import datetime
from simple_term_menu import TerminalMenu

from ohlc_data.ohlc import OHLC


def create_ohlc_folder(ohlc_path: str) -> None:
    """
    Creates ohlc_csv folder and timeframe subfolders 
    """

    # Check for ohlc_csv folder
    print('\nChecking for ohlc_csv folder...\n')
    if not os.path.isdir(ohlc_path):
        print(f'\nohlc_csv folder not found, creating ohlc_csv folder at {os.getcwd()}\n')

        # Create ohlc_csv folder 
        os.mkdir(ohlc_path)
        print('\nohlc_csv folder created\n')
    else:
        print('\nohlc_csv found\n')


def validate_date(date: str, format_str: str):
    """
    Validate whether date string is in appropriate datetime format
    """
    try: 
        datetime.strptime(date, format_str)
        return True
    except ValueError:
        return False
    

def validate_ticker(ticker: str):
    """
    Validate whether ticker exists on American stock exchange
    """
    check = yf.Ticker(ticker).history(period='1d', interval='1d')
    if check.empty:
        return False
    else:
        return True
                

def dropdown(prompt:str, options: list[str | int], show_selection: bool=True) -> str:
    """
    
    """
    print('\n')
    print(prompt)

    menu_options = options
    menu = TerminalMenu(menu_options)
    menu_select = menu.show()
    menu_selected = menu_options[menu_select]

    if show_selection == True:
        print(menu_selected)
    
    return menu_selected


def custom_period(intraday=False) -> tuple[str, str]:

    start_date = None
    end_date = None
    date_format = '%Y-%m-%d'
    datetime_format = '%Y-%m-%d %H:%M:%S'

    if intraday == True:
        while True:
            start_input = input('Start Datetime (YYYY-MM-DD HH:MM:SS) : ')
            if not validate_date(start_input, datetime_format):
                print('Invalid datetime, ensure YYYY-MM-DD HH:MM:SS')
                continue
            else:
                start_date = start_input
                break

        while True:
            end_input = input('End Datetime (YYYY-MM-DD HH:MM:SS) : ')
            if not validate_date(end_input, datetime_format):
                print('Invalid datetime, ensure YYYY-MM-DD HH:MM:SS')
                continue
            else:
                end_date = end_input
                break
    else:
        while True:
            print('\n')
            start_input = input('Start date (YYYY-MM-DD): ')
            if not validate_date(start_input, date_format):
                print('Invalid date, ensure YYYY-MM-DD format')
                continue
            else:
                start_date = start_input
                break

        while True:
            print('\n')
            end_input = input('End date (YYYY-MM-DD): ')
            if not validate_date(end_input, date_format):
                print('Invalid date, ensure YYYY-MM-DD format')
                continue
            else:
                end_date = end_input
                break
    
    return start_date, end_date


def download_and_save(path: str, ticker: str, source: str, period: str = None, 
                    interval: str = None, start_date: str = None, end_date: str = None,
                    pre_post: bool = False) -> None:
    
    if source not in ['yfinance','alpaca']:
        raise ValueError('Incorrect source input. (yfinance or alpaca)')

    if source == 'yfinance':
        if pre_post != False:
            print('Yfinance does not provide pre/post data')
        df = OHLC(ticker, period, interval, start_date, end_date).from_yfinance()
    else:
        df = OHLC(ticker, period, interval, start_date, end_date).from_alpaca(pre_post=pre_post)

    # Save to CSV
    if start_date and end_date:
        filename = f'{ticker}_{start_date[:4]}{start_date[5:7]}_{end_date[:4]}{end_date[5:7]}_{interval}'
    elif end_date:
        filename = f'{ticker}_{end_date[:4]}{end_date[5:7]}_{period}_{interval}'
    else:
        filename = f'{ticker}_{period}_{interval}'
    
    pm_suffix = '_pm' if pre_post and source == 'alpaca' else ''

    df.to_csv(f'{path}{interval}/{filename}{pm_suffix}.csv')

