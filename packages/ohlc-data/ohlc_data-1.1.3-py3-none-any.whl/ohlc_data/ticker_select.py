import os
import json
import ast
from datetime import datetime

import ohlc_data
from ohlc_data.utils import  dropdown
from ohlc_data.utils import validate_ticker, dropdown

module_path = os.path.dirname(ohlc_data.__file__)
prev_ticker_path = f'{module_path}/multi_tickers.json'


def tickers_to_json(tickers: str) -> None:
    """
    Saves dictionary of list of tickers to json, or
    adds to existing json.
    """

    if not os.path.isfile(f'{prev_ticker_path}'): 
        tickers_dict = {}
        tickers_dict[str(datetime.today())] = str(tickers)
        with open(f'{prev_ticker_path}', 'w') as f:
            json.dump(tickers_dict, f)
    else:
        with open(f'{prev_ticker_path}', 'r') as f:
            data = json.load(f)
            if str(tickers) not in data.values():
                data[str(datetime.today())] = str(tickers)
    
        with open(f'{prev_ticker_path}', 'w') as f:
            json.dump(data, f, indent=4)


def enter_multi_ticker() -> list:
    """
    Enter multiple tickers manually, returns list   
    """
    while True:
        print('\n')
        ticker_list = input('Enter tickers (separate tickers with single space, not case-sensitive): ').strip().upper()

        if not ticker_list:
            print('\n')
            print('You must enter at least one ticker.')
            continue
        
        ticker_split= ticker_list.split(' ')
        tickers = [ticker.strip() for ticker in ticker_split if ticker.strip()]
        ticker_check = [validate_ticker(ticker) for ticker in tickers]

        if False in ticker_check:
            print('\n')
            print('At least one ticker might have been input incorrectly, make sure to separate each ticker with a space')
            continue
        else:
            break

    return tickers


def ticker_select() -> str | list[str]:
    """
    Full ticker select script
    """

    ticker_selected = dropdown('Download data for: ', ['Single ticker', 'Multiple tickers'])

    # Single Ticker chosen
    if ticker_selected == 'Single ticker':
        while True:
            print('\n')
            ticker = input('Enter ticker: ').strip().upper()
            
            if validate_ticker(ticker):
                break
            else:
                print('You may have entered an invalid or unsupported ticker, try again')
        return ticker

    # Multi-Ticker chosen
    elif ticker_selected == 'Multiple tickers':

        # check for json
        if os.path.isfile(f'{module_path}/multi_tickers.json'):
            manual_or_list = dropdown("", ["Enter tickers manually", "Select from previous tickers"])

            if manual_or_list == "Select from previous tickers":
                with open(f'{prev_ticker_path}', 'r') as f:
                    data = json.load(f)
                previous_tickers = dropdown("Previous tickers: ", [t_list for t_list in data.values()])
                tickers = ast.literal_eval(previous_tickers)
            else:
                tickers = enter_multi_ticker()

        # no json
        else:
            tickers = enter_multi_ticker()

        # save tickers to json
        tickers_to_json(tickers=tickers)

        return tickers