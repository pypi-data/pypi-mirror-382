import os
import pandas as pd
from datetime import datetime, timedelta
from ohlc_data.utils import validate_date, dropdown, custom_period, download_and_save


def alpaca_script(ticker_input: str | list[str], path) -> None:
    """
    Download OHLC data through Alpaca API. More flexible with intervals, lookback
    period limited to 2016 - today. Pre/Post market data available.
    """
    
    date_format = '%Y-%m-%d'
    datetime_format = '%Y-%m-%d %H:%M:%S'

    start_date = None
    end_date = None

    # Choose Period
    period_selected = dropdown('Choose lookback period: ', ['Days','Years', 'Custom'])

    if period_selected != 'Custom':
        print('Note: Data from Alpaca only goes as far back as 2016')
        while True:
            period = input(f'Number of {period_selected.lower()}: ') + period_selected[0].lower()
            if period_selected == 'Years' and datetime.today().year - int(period[:-1]) < 2016:
                print('Lookback limit exceeded. Alpaca only provides data as far back as 2016.')
                continue
            elif period_selected == 'Days' and (datetime.today().year * 365) - int(period[:-1]) < (2016 * 365):
                print('Lookback limit exceeded. Alpaca only provides data as far back as 2016.')
                continue
            else:
                break

        # Choose Interval
        interval_timeframe = dropdown('Choose interval timeframe: ', ['Minutes', 'Hours', 'Daily'])
        if interval_timeframe == 'Daily':
            interval = '1d'
            print('Daily intervals selected')
        else:
            interval_selected = input(f"Number of {interval_timeframe.lower()}: ")
            interval = interval_selected + interval_timeframe[0].lower()
            print(interval_selected)

    else:
        period = None
        interval_timeframe = dropdown('Choose interval timeframe: ', ['Minutes', 'Hours', 'Daily'])
        if interval_timeframe == 'Daily':
            start_date, end_date = custom_period()
            interval = '1d'
            print('Daily intervals selected')
        else:
            interval_selected = input(f'Number of {interval_timeframe.lower()}: ')
            interval = interval_selected + interval_timeframe[0].lower()
            start_date, end_date = custom_period(intraday=True)

    # Optional End date
    opt_end_datetime = (
        'End date (YYYY-MM-DD) (optional): ' if 'd' in interval else
        'End Datetime (YYYY-MM-DD HH:MM:SS) (optional): '
    )

    opt_end_error = (
        'Invalid date, ensure YYYY-MM-DD format' if 'd' in interval else
        'Invalid datetime, ensure YYYY-MM-DD HH:MM:SS'
    )

    if period_selected == 'Days':

        while True:
            print('\n')
            end_input = input(opt_end_datetime)
            if end_input and not validate_date(end_input, datetime_format):
                print(opt_end_error)
                continue
            elif end_input and validate_date:
                if pd.to_datetime(end_input) - timedelta(days=int(period[:-1])) < pd.to_datetime('2016-01-01 09:30:00'):
                    print('Lookback goes beyond 2016 limit')
                else:
                    break
                continue
            else:
                end_date = end_input if end_input else None
                break

    elif period_selected == 'Years':
        while True:
            print('\n')
            end_input = input(opt_end_datetime)
            if end_input and not validate_date(end_input, date_format):
                print(opt_end_error)
                continue
            elif end_input and validate_date:
                if pd.to_datetime(end_input) - timedelta(weeks=int(period[:-1]) * 52) < pd.to_datetime('2016-01-01 09:30:00'):
                    print('Lookback goes beyond 2016 limit')
                else:
                    break
                
            else:
                end_date = end_input if end_input else None
                break

    # Create new folder for new timeframe / interval
    if interval not in os.listdir(path):
        os.mkdir(f'{path}{interval}/')

    # Pre/Post Market Data or Regular Hours
    if 'd' not in interval:
        pre_post_prompt = dropdown('Include Pre/Post Market Data?: ', ['Yes','No'])
        pre_post = True if pre_post_prompt == 'Yes' else False
    else:
        pre_post = False

    # Download OHLC data, save as CSV
    print('\n')
    print('Downloading OHLC data...','\n')

    if isinstance(ticker_input, list):
        for ticker in ticker_input:
            download_and_save(path, ticker, 'alpaca', period, interval, start_date, end_date, pre_post=pre_post)
    else:
        download_and_save(path, ticker_input, 'alpaca', period, interval, start_date, end_date, pre_post=pre_post)
        
    print("OHLC data downloaded successfully!")


def yfinance_script(ticker_input: str | list[str], path: str) -> None:
    """
    Download OHLC data through Yfinance API. Intervals and periods are strict. Daily data
    can span a few decades for some stocks.
    """
    
    start_date = None
    end_date = None

    period_selected = dropdown('Choose lookback period: ', ['Days','Years','Custom'])

    if period_selected == 'Days':
        num_period = int(input('Number of days: '))

        if num_period <= 7: 
            interval_selected = dropdown('Choose interval: ', ['1m', '2m', '5m', '15m', '30m', '1h', '4h', '1d'])
        elif num_period > 7 and num_period <= 60:
            interval_selected = dropdown('Choose interval: ', ['5m', '15m', '30m', '1h', '4h', '1d'])
        elif num_period > 60 and num_period < 730:
            interval_selected = dropdown('Choose interval: ', ['1h', '4h', '1d'])
        else:
            print("Number of days is greater than 730 and therefore the only interval available for yfinance is '1d' (Daily bars).")
            interval_selected = '1d'

    elif period_selected == 'Years': 
        num_period = int(input('Number of years: '))

        if num_period <= 2:
            interval_selected = dropdown('Choose interval: ', ['1h', '4h', '1d'])
        else:
            interval_selected = dropdown('Choose interval: ', ['1d','1wk'])

    else:
        period = None
        interval_timeframe = dropdown('Choose interval type: ', ['Intraday', 'Daily +'])
        start_date, end_date = custom_period() 
        date_delta = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days 
        
        if interval_timeframe == 'Daily +':
            if date_delta < 15:
                interval_selected = '1d'
            else:
                interval_selected = dropdown('Choose interval: ', ['1d','1wk'])
        else:
            if date_delta <= 7:
                interval_selected = dropdown('Choose interval: ', ['1m', '2m', '5m', '15m', '30m', '1h', '4h', '1d'])
            elif date_delta > 7 and date_delta <= 60:
                interval_selected = dropdown('Choose interval: ', ['5m', '15m', '30m', '1h', '4h', '1d'])
            elif date_delta > 60 and date_delta < 730:
                interval_selected = dropdown('Choose interval: ', ['1h', '4h', '1d'])
            
    if period_selected != 'Custom':
        period = str(num_period) + period_selected[0].lower()

    if interval_selected not in os.listdir(path):
        os.mkdir(f'{path}{interval_selected}/')

    # Save multiple ticker to csv folder
    if isinstance(ticker_input, list):
        for ticker in ticker_input:
            download_and_save(path, ticker, 'yfinance', period, interval_selected, start_date, end_date)
    # Save single ticker to csv folder 
    else:
        download_and_save(path, ticker_input, 'yfinance', period, interval_selected, start_date, end_date)

    print("OHLC data downloaded successfully!")