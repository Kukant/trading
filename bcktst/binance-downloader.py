import pandas as pd
from binance.client import Client
import datetime

# YOUR API KEYS HERE
api_key = "G4VuboNcSL8YHWwu5KF84BW8TXeZMc2c42eM7LokvZvxOAYcLTIJeKHsWKnVBb0e"    #Enter your own API-key here
api_secret = "w449635ZjhrGGhrt0FxSuZElzbXD4gGhuIv1yg348YEGzGpPDv9igHshzGInCqDg" #Enter your own API-secret here

bclient = Client(api_key=api_key, api_secret=api_secret)

start_date = datetime.datetime.strptime('9 Feb 2021', '%d %b %Y')
end_date = datetime.datetime.strptime('14 Feb 2021', '%d %b %Y')

def binanceBarExtractor(symbol):
    print('working...')
    filename = '../data/{}_5m_{}-{}.csv'.format(
        symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    klines = bclient.get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, start_date.strftime("%d %b %Y %H:%M:%S"), end_date.strftime("%d %b %Y %H:%M:%S"), 1000)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore']
    )
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

    data.set_index('timestamp', inplace=True)
    data.to_csv(filename)
    print('finished!')


if __name__ == '__main__':
    # Obviously replace BTCUSDT with whichever symbol you want from binance
    # Wherever you've saved this code is the same directory you will find the resulting CSV file
    binanceBarExtractor('BTCUSDT')