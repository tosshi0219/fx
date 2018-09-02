from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

import renom as rm
from renom.optimizer import Adam, Adagrad
from renom.cuda import set_cuda_active
# if you would like to use GPU, set True, otherwise you should be set to False
set_cuda_active(False)

import sys
import os
import talib
sys.path.append('/Users/toshio/project/fx')
from config import token, gran, look_back, pred_length
from lib.preprocess import Preprocess

import oandapy

class Inference:
    def __init__(self):
        self.stds, self.means = self.load_scaler()
        self.sequential = rm.Sequential([
                                    rm.Lstm(30),
                                    rm.Lstm(10),
                                    rm.Dense(pred_length)
                                    ])
        self.oanda = oandapy.API(environment="practice", access_token=token)
        self.res = self.oanda.get_history(instrument="USD_JPY", granularity=gran, count = look_back + pred_length + 78)
        self.prep = Preprocess(self.res)
        self.df = self.prep.data
        self.data = self.standardize()
        self.exp, self.target = self.create_dataset()
        self.pred = self.predict()
        
    def load_scaler(self):
        with open('../model/std_scaler_{}.pickle'.format(gran), mode='rb') as f:
            stds = pickle.load(f)
        with open('../model/mean_scaler_{}.pickle'.format(gran), mode='rb') as f:
            means = pickle.load(f)
        return stds, means
    
    def load_model(self):
        self.lstm = self.lstm.load("../model/lstm_{}_{}.h5".format(gran, look_back))
        
    def standardize(self):
        df_std = self.df.copy()
        for i, col in enumerate(self.df):
            df_std[col] = (self.df[col] - self.means[i]) / self.stds[i]
        data = np.array(df_std)
        return data
    
    def create_dataset(self):
        exp, target = [], []
        for i in range(len(self.data) - look_back - pred_length):
            exp.append(self.data[i : i+look_back, :])
            target.append(self.data[i + look_back : i + look_back + pred_length, 9].T[0])

        n_features = np.array(exp).shape[2]
        exp = np.reshape(np.array(exp), [-1, look_back, n_features])
        target = np.reshape(np.array(target), [-1, 1])
        return exp, target
    
    def predict(self):
        X, y = self.create_dataset()
        T = X.shape[1]
        for t in range(T):
            y_pred = self.sequential(X[:, t, :])
        self.sequential.truncate()
        prediction = y_pred * self.stds[9] + self.means[9]
        return prediction
    
if __name__ == '__main__':
    inf = Inference()
    print(inf.pred)