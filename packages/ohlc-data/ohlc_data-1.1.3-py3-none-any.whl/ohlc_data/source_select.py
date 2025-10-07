import os
import importlib

import ohlc_data
from ohlc_data.authenticate import authenticate_alpaca
from ohlc_data.utils import dropdown


def source_select():
    """
    Select source for OHLC download: Alpaca or Yfinance
    """
    # .env path for alpaca keys
    env_path = os.path.dirname(ohlc_data.__file__)
    ohlc_data_files = [f for f in os.listdir(env_path)]

    # Choose source
    source_selected = dropdown('Choose source: ', ['Alpaca','Yfinance'])

    # Authentication
    while True:
        if source_selected == 'Alpaca' and '.env' not in ohlc_data_files:
            authenticate_alpaca(env_path)
            importlib.reload(ohlc_data.ohlc)
            break
        else:
            break

    return source_selected