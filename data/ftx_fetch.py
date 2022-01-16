import time
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import statsmodels.tsa.stattools as ts
import pickle
def retrieve_ftx_futures_data(symbol, interval_in_seconds, from_timestamp,to_timestamp):
    resp = requests.get('https://ftx.com/api/markets/{}/candles?resolution={}&start_time={}&end_time={}'.format(symbol,interval_in_seconds, from_timestamp,to_timestamp)) 
    
    ohlcvs = resp.json()['result']
    if len(ohlcvs) == 0:
        return pd.DataFrame({'A':[]})
    df = pd.DataFrame(ohlcvs)
    close = df['close'].to_numpy()
    timestamp = df['time'].to_numpy()
    timestamp = [int(x) for x in timestamp]
    dict = {'Timestamp': timestamp, 'Price': close}
    df = pd.DataFrame.from_dict(dict)
    df = df.set_index('Timestamp')
    
    return df
    
def fetch_data():
    index = ["BTC"]
    for i in range(len(index)):
        
        from_timestamp =  pd.Timestamp(2020,1,1,0).timestamp()
        to_timestamp =  pd.Timestamp(2021,12,30,0).timestamp()
        counter = 0
        while from_timestamp < to_timestamp:
            end_timestamp = from_timestamp + 86340   
            current_datetime = datetime.fromtimestamp(from_timestamp)
            print('Fetching candles starting from {}'.format(current_datetime))
            df = retrieve_ftx_futures_data(f'{index[i]}-PERP',60,from_timestamp,end_timestamp) 
            if (counter == 0) and (df.empty == False):
                df_concat = df
                counter = 1
            else:
                if df.empty == False:
                    df_concat = pd.concat([df_concat, df])
            time.sleep(0.5)
            from_timestamp = from_timestamp + 80000
        df_concat = df_concat.reset_index()
        df_concat = df_concat.drop_duplicates()
        df_concat = df_concat.set_index('Timestamp')

        df_concat.to_csv(f'FTX_{index[i]}.csv')

def data_preprocess():
    index = ["ALT", "DEFI", "DRGN", "EXCH", "MID", "PRIV", "SHIT", "BTC"]
    data = []
    for i in range(len(index)):
        temp = pd.read_csv(f"FTX_{index[i]}PERP.csv")
        temp.set_index("Timestamp", inplace = True)
        temp.rename(columns = {"Price":index[i]}, inplace = True)
        data.append(temp)
    df1 = pd.concat(data, join = "outer", axis = 1)
    print(df1)
    df1.to_pickle('FTX_PERP.pkl')

def data_seperate():
    data = pd.read_pickle('FTX_PERP.pkl')
    coint_day_period = 90
    timeperiod = 86400000 * coint_day_period 
    N = len(data.index)
    n = len(data.columns)
    temp_1 = data.index[0]
    count = 0
    while temp_1 < data.index[N-1]:

        temp_2 = temp_1 + timeperiod
        temp_data = data.loc[temp_1:temp_2,:]
        temp_1 = temp_1 + int(coint_day_period/3)*86400000 
        temp_data.to_csv(f'seperate_data/FTX_PERP_seperate_{count}.csv')
        count += 1
    f.close()
    print(count)
