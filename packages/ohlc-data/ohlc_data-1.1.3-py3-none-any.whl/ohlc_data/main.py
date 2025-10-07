from ohlc_data.source_select import source_select
from ohlc_data.ticker_select import ticker_select
from ohlc_data.utils import create_ohlc_folder, dropdown
from ohlc_data.scripts import yfinance_script, alpaca_script

def download_ohlc(ohlc_path: str) -> None:
    """
    Prompt user for tickers and source, then download ohlc data from chosen source (yfinance or alpaca)
    """

    # Select tickers
    get_tickers = ticker_select()

    # Source
    get_source = source_select()

    if get_source == 'Yfinance':
        yfinance_script(get_tickers, ohlc_path)
    else:
        alpaca_script(get_tickers, ohlc_path)

    # Rerun script to download more OHLC Data
    rerun = dropdown("", ["Download More OHLC Data", "Finish"])
    if rerun == "Download More OHLC Data":
        download_ohlc(ohlc_path)


def main() -> None:
    ohlc_path = './ohlc_csv/'
    create_ohlc_folder(ohlc_path=ohlc_path)
    download_ohlc(ohlc_path=ohlc_path)

if __name__ == "__main__":
    main()