from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def ichimoku(df):
    max9 = df.rolling(9).max()
    min9 = df.rolling(9).min()
    max26 = df.rolling(26).max()
    min26 = df.rolling(26).min()
    max52 = df.rolling(52).max()
    min52 = df.rolling(52).min()
#     chikoindex = [df.index[0] +  timedelta(days = a) for a in range(-26,0)]
    chikoindex = [df.index[0] +  timedelta(minutes = a) for a in range(-26 *15,0,15)]
    chikoadder = list(df.index[:-26])
    chikoindex.extend(chikoadder)
    senkoindex = list(df.index[26:])
#     senkoadder = [df.index[-1] +  timedelta(days = a) for a in range(1,27)]
    senkoadder = [df.index[-1] +  timedelta(days = a) for a in range(15,27*15,15)]
    senkoindex.extend(senkoadder)

    tenkan = (max9 + min9) / 2
    kijun = (max26 + min26) / 2
    chiko = df.copy()
    chiko['time'] = chikoindex
    chiko = chiko.set_index('time', drop = True)
    senko1 = (tenkan + kijun) / 2
    senko2 = (max52 + min52) / 2
    senko1['time'] = senkoindex
    senko1 = senko1.set_index('time', drop = True)
    senko2['time'] = senkoindex
    senko2 = senko2.set_index('time', drop = True)

    ichi =pd.DataFrame()
    col = 'close'
    ichi['close'] = df[col]
    ichi['tenkan'] = tenkan[col]
    ichi['kijun'] = kijun[col]
    ichi['chiko'] = chiko[col]
    ichi['senko1'] = senko1[col]
    ichi['senko2'] = senko2[col]

    return ichi
