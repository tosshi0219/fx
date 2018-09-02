from datetime import datetime, timedelta
import oandapy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys
import os
import talib
sys.path.append('/Users/toshio/project/fx')
from config import token
from lib.indicator import ichimoku

class Preprocess:
    def __init__(self, res, df = None):
        self.res = res
        if df is None:
            self.df = self.res_to_df()
        else:
            self.df = df
        self.df = self.res_to_df()
        self.arr_ask, self.arr_bid, self.df_ask = self.prep_ohlcv()
        self.delta = self.prep_delta()
        self.sma = self.prep_sma()
        self.macd = self.prep_macd()
        self.rsi = self.prep_rsi()
        self.bband = self.prep_bband()
        self.adx = self.prep_adx()
        self.di = self.prep_di()
        self.sar = self.prep_sar()
        self.ichi = self.prep_ichi()
        self.data = self.prep_concat()
        
    def res_to_df(self):
        df = pd.DataFrame(self.res['candles'])
        df = df.drop(['complete'], axis = 1)
        df['time'] = df['time'].str[:-8]
        df['time'] = df['time'].str.replace('T',' ')
        times = [datetime.strptime(v, '%Y-%m-%d %H:%M:%S') for v in df['time']]
        df['time'] = times
        df = df.set_index('time',drop = True)
        return df

    def prep_ohlcv(self):
        df_ask = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])
        df_ask['open'] = self.df['openAsk']
        df_ask['high'] = self.df['highAsk']
        df_ask['low'] = self.df['lowAsk']
        df_ask['close'] = self.df['closeAsk']
        df_ask['volume'] = self.df['volume']
        arr_ask = np.array(df_ask)

        df_bid = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])
        df_bid['open'] = self.df['openBid']
        df_bid['high'] = self.df['highBid']
        df_bid['low'] = self.df['lowBid']
        df_bid['close'] = self.df['closeBid']
        df_bid['volume'] = self.df['volume']
        arr_bid = np.array(df_bid)
        return arr_ask, arr_bid, df_ask

    def prep_delta(self):
        delta = pd.DataFrame(index = self.df.index, columns = ['delta_close'])
        delta['delta_close'] = self.df_ask['close'].diff()
        return delta

    def prep_sma(self):
        sma = pd.DataFrame(index = self.df.index, columns = ['sma5', 'sma25', 'sma50', 'sma75'])
        sma['sma5'] = talib.SMA(self.arr_ask[:,3], timeperiod = 5)
        sma['sma25'] = talib.SMA(self.arr_ask[:,3], timeperiod = 25)
        sma['sma50'] = talib.SMA(self.arr_ask[:,3], timeperiod = 50)
        sma['sma75'] = talib.SMA(self.arr_ask[:,3], timeperiod = 75)
        return sma

    def prep_macd(self):
        macd = pd.DataFrame(index = self.df.index, columns = ['macd', 'macdsignal', 'macdhist'])
        macd['macd'] =  talib.MACD(self.arr_ask[:,3],fastperiod=12, slowperiod=26, signalperiod=9)[0]
        macd['macdsignal'] =  talib.MACD(self.arr_ask[:,3],fastperiod=12, slowperiod=26, signalperiod=9)[1]
        macd['macdhist'] =  talib.MACD(self.arr_ask[:,3],fastperiod=12, slowperiod=26, signalperiod=9)[2]
        return macd

    def prep_rsi(self):
        rsi = pd.DataFrame(index = self.df.index, columns = ['rsi'])
        rsi['rsi'] =  talib.RSI(self.arr_ask[:,3], timeperiod = 14)
        return rsi

    def prep_bband(self):
        bband = pd.DataFrame(index = self.df.index, columns = ['-3sigma', '-2sigma', '-1sigma', '+1sigma', '+2sigma', '+3sigma'])
        bband['+1sigma'] = talib.BBANDS(self.arr_ask[:,3], timeperiod=15, nbdevup=1, nbdevdn=1)[0]
        bband['-1sigma'] = talib.BBANDS(self.arr_ask[:,3], timeperiod=15, nbdevup=1, nbdevdn=1)[2]
        bband['+2sigma'] = talib.BBANDS(self.arr_ask[:,3], timeperiod=15, nbdevup=2, nbdevdn=2)[0]
        bband['-2sigma'] = talib.BBANDS(self.arr_ask[:,3], timeperiod=15, nbdevup=2, nbdevdn=2)[2]
        bband['+3sigma'] = talib.BBANDS(self.arr_ask[:,3], timeperiod=15, nbdevup=3, nbdevdn=3)[0]
        bband['-3sigma'] = talib.BBANDS(self.arr_ask[:,3], timeperiod=15, nbdevup=3, nbdevdn=3)[2]
        return bband

    def prep_adx(self):
        adx = pd.DataFrame(index = self.df.index, columns = ['adx'])
        adx['adx'] = talib.ADX(self.arr_ask[:,1], self.arr_ask[:,2], self.arr_ask[:,3], timeperiod =14)
        return adx

    def prep_di(self):
        di = pd.DataFrame(index = self.df.index, columns = ['+di', '-di'])
        di['+di'] = talib.PLUS_DI(self.arr_ask[:,1], self.arr_ask[:,2], self.arr_ask[:,3], timeperiod = 14)
        di['-di'] = talib.MINUS_DI(self.arr_ask[:,1], self.arr_ask[:,2], self.arr_ask[:,3], timeperiod = 14)
        return di

    def prep_sar(self):
        sar = pd.DataFrame(index = self.df.index, columns = ['sar'])
        sar['sar'] = talib.SAR(self.arr_ask[:,1], self.arr_ask[:,2], acceleration=0.05, maximum=0.2)
        return sar

    def prep_ichi(self):
        ichi = ichimoku(self.df_ask).drop('close', axis = 1)
        return ichi

    def prep_concat(self):
        adder = [self.delta, self.sma, self.macd, self.rsi, self.bband, self.adx, self.di, self.sar, self.ichi]
        data = self.df.join(adder)
        data = data.drop('chiko', axis = 1)
        data = data.dropna()
        return data
    
if __name__ == '__main__':
    gran = 'H1'
    look_back = 10
    oanda = oandapy.API(environment="practice", access_token=token)
    res = oanda.get_history(instrument="USD_JPY",granularity=gran, count = 77 + look_back)
    prep = Preprocess(res)
    data = prep.data    

    with open('../intermediate_data/prep_data_{}.pickle'.format(gran), mode='wb') as f:
    pickle.dump(data, f)