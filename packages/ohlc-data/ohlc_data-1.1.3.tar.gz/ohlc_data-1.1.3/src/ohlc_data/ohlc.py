import os
import re
import pandas as pd
from dotenv import load_dotenv
from datetime import date, timedelta

import yfinance as yf
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.historical import StockHistoricalDataClient 


class OHLC:
    """
    Get OHLC data using either yfinance or alpaca APIs.

    args:
        symbol: Ticker symbol. Format: 'ABC' (All caps)
        period: Lookback period from the end date. End date is most recent trading day by default
        interval: Time period represented by a single candelstick
        start: Start date. Format: YYYY-MM-DD
        end: End date. Format: YYYY-MM-DD
        path: Path for exported CSV file
    """

    def __init__(self,
                symbol: str,
                period: str = '1y',
                interval: str = '1d',
                start: str | date = None,
                end: str | date = None,
                path: str = None
                ):
        
        # Instance variables
        self.symbol = symbol
        self.period = period if start == None else None
        self.interval = interval
        self.start = start
        self.end = end
        self.path = path


    def _round_ohlc(self, df:pd.DataFrame, dec_pl: int=2) -> pd.DataFrame:
        """
        Round Open High Low Close colunms to x decimal places.
        args:
            - df: dataframe
            - dec_pl: number of decimal places to round to
        """

        decimal_places = pd.Series([dec_pl for i in range(4)], index=['Open','High','Low','Close'])

        return df.round(decimal_places)
    

    def _ohlc_agg(self) -> dict:
        """
        For resampling OHLC timeframes
        """
        ohlc_agg = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
        }

        return ohlc_agg
        
        
    def from_yfinance(self, auto_adjust: bool=False, progress: bool=False, prepost: bool=False) -> pd.DataFrame:
        """
        Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo 

        1m data cannot extend past 7 days
        2m - 30m data, and 90m data cannot extend past 60 days
        1h data cannot extend past 730 days
        1d - 3mo data allows max available data

        auto_adjust, progress and prepost arguments set to False by default but can be adjusted
        """

        # Start and End date is specified
        if self.start != None and self.end != None:
            download = yf.download(self.symbol, period=self.period, interval=self.interval,
                                   start=self.start, end=self.end, auto_adjust=auto_adjust,
                                   progress=progress, prepost=prepost)
        
        # Start and End dates not specified, None
        else:
            download = yf.download(self.symbol, period=self.period, interval=self.interval,
                                   auto_adjust=auto_adjust, progress=progress, prepost=prepost)
            
        # Clean downloaded dataframe
        df = download.drop(columns='Adj Close'.strip())
        df.columns = df.columns.get_level_values(0) # Get rid of multi-index
        df = df[['Open','High','Low','Close','Volume']]
        df = self._round_ohlc(df)
        if 'd' not in self.interval and 'wk' not in self.interval:
            df.index = pd.to_datetime(df.index).tz_convert('US/Eastern').tz_localize(None)
        else:
            df.index = pd.to_datetime(df.index)

        if not self.path:
            return df
        else:
            if not self.period:
                df.to_csv(f'{self.symbol}_{str(self.start)[:4]}_{str(self.end)[:4]}_{self.interval}.csv')
            else:
                df.to_csv(f'{self.symbol}_{self.period}_{self.interval}.csv')
        
        return df
    

    def from_alpaca(self, pre_post=False) -> pd.DataFrame:
        """
        Data from 2016 to present is available for all intervals.
        """

        load_dotenv()

        api_key = os.environ.get('API_KEY')
        secret_key = os.environ.get('SECRET_KEY')

        client = StockHistoricalDataClient(api_key=api_key, secret_key=secret_key)

        if self.period:
            period_split = re.split('(\\d+)', self.period)
            days = 365*int(period_split[1] if 'y' in self.period else int(period_split[1]))

        interval_split = re.split('(\\d+)', self.interval)
        timeframe = (
            TimeFrame.Day if 'd' in self.interval 
            else TimeFrame(amount=int(interval_split[1]), unit=TimeFrameUnit.Hour) if 'h' in self.interval 
            else TimeFrame(amount=int(interval_split[1]), unit=TimeFrameUnit.Minute)
        )

        market_close= timedelta(hours=16, minutes=00)
        intraday_end = str(market_close - timedelta(minutes=int(interval_split[1])))

        # Start and end dates specified
        if self.start != None and self.end != None:
            start_datetime = pd.to_datetime(self.start, utc=True)
            end_datetime = pd.to_datetime(self.end, utc=True)

        # Start and end dates not specified, period provided
        elif self.start == None and self.end == None:
            start_datetime = date.today() - timedelta(days=days)
            end_datetime = date.today()

        # Start and end date not specified, no period specified, default period is 1 year
        else: 
            start_datetime = date.today() - timedelta(days=365)
            end_datetime = date.today()

        request_params = StockBarsRequest(
        symbol_or_symbols = self.symbol,
        timeframe=timeframe,
        adjustment="split",
        start=start_datetime,
        end=end_datetime
        )

        # Raw DataFrame
        stock = client.get_stock_bars(request_params)
        raw_data = stock.df

        df = raw_data.reset_index(level=0, drop=True)
        df = df[~df.index.duplicated(keep='first')]         # in case of duplicate index
        df = df.rename(columns={'open':'Open','high':'High',
                            'low':'Low','close':'Close',
                            'volume':'Volume'})
        df = self._round_ohlc(df)
        df = df.drop(columns=['trade_count','vwap'])
        df['Volume'] = df['Volume'].astype(int)

        if 'd' in self.interval:
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
            df.index = pd.to_datetime(df.index)
            df.index.names = ['Date']
        else:
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M:%S')
            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize('UTC').tz_convert('US/Eastern')
            df.index = df.index.tz_localize(None)
            df.index.names = ['Datetime']

            if pre_post == False:
                df = df.between_time('09:30', intraday_end)

        if not self.path:
            return df
        else:
            if not self.period:
                df.to_csv(f'{self.symbol}_{str(self.start)[:4]}_{(self.end)[:4]}_{self.interval}.csv')
            else:
                df.to_csv(f'{self.symbol}_{self.period}_{self.interval}.csv')
        
        return df




        

