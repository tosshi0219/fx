from datetime import datetime, timedelta
import numpy as np
import oandapy
import sys
sys.path.append('/home/toshio/project/fx')
from config import *
from lib.inference import Inference
from lib.trader import Trader
import time
import pickle

ENV = 'practice'
oanda = oandapy.API(environment=ENV, access_token=token)
trader = Trader()
logs = []

#取引単位
volume = 100

#利確、損確の設定
set_profit = 0.1
set_loss = 0.5

#取引回数
transaction_times = 10000

j = 0
jst = 1
while j < transaction_times:
    j +=1
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print('------transaction_{0:05}------'.format(j))
    print(now)
    inf = Inference()
    pred_delta=float(inf.pred[0][0])
    pred_side = inf.pred_side
    print('1時間後の推定差額は{}'.format(np.round(pred_delta, 4)))
    #現在価格の取得
    current_price = oanda.get_prices(instruments='USD_JPY')['prices'][0]
    current_ask_price = current_price['ask']
    current_bid_price = current_price['bid']

    #現在のポジション確認
    open_trades = oanda.get_trades(account_id)
    if len(open_trades['trades']) == 0:
        current_side = 'zero'
    else:
        #取引からの経過時間が1時間を超えているものを約定させる
        for tr in open_trades['trades']:
            trade_time = datetime.strptime(tr['time'], '%Y-%m-%dT%H:%M:%S.000000Z')
            current_time = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
            elapsed_time = (current_time - trade_time).seconds/60.0
            print('id:{0},経過時間:{1:0.1f}分'.format(tr['id'],elapsed_time))
            if elapsed_time > 60.0:
                closed_trades = oanda.close_trade(account_id, tr['id'])
                profit = closed_trades['profit']
                print('profit:{}'.format(profit))
        #約定させた後の現在のポジションの確認
        if len(open_trades['trades']) == 0:
            current_side = 'zero'
        else:
            current_side = open_trades['trades'][-1]['side']
    print('現在のポジション:',current_side)

    #利確、損確価格を計算
    buy_take_profit = current_ask_price + set_profit
    buy_stop_loss = current_bid_price - set_loss
    sell_take_profit = current_bid_price - set_profit
    sell_stop_loss = current_ask_price + set_loss

    #zeroポジの場合は、予測ポジションに注文
    #今のポジションと同じ予測ポジションなら注文
    if (current_side == 'zero') & (pred_side == 'buy'):
        print("Let's buy!")
        trader._market_order(pred_side, volume, buy_take_profit, buy_stop_loss)
    elif (current_side == 'zero') & (pred_side == 'sell'):
        print("Let's sell!")
        trader._market_order(pred_side, volume, sell_take_profit, sell_stop_loss)
    elif (current_side == 'buy') & (pred_side == 'buy'):
        print("Let's buy!")
        trader._market_order(pred_side, volume, buy_take_profit, buy_stop_loss)
    elif (current_side == 'sell') & (pred_side == 'sell'):
        print("Let's sell!")
        trader._market_order(pred_side, volume, sell_take_profit, sell_stop_loss)
    else:
        print('do nothing')
        pass
    print('-------------------------------------')
    log = {'time': now,
               'current_ask_price': current_ask_price,
               'current_bid_price': current_bid_price,
               'pred_delta': pred_delta,
               'pred_side': pred_side}
    logs.append(log)
    if j % 50 ==0:
        print('一旦logをpickle化...transaction_{0:05}-{1:05}'.format(jst,j))
        with open ('../log/log_transaction_{0:05}-{1:05}'.format(jst,j), 'wb') as f:
            pickle.dump(logs, f)
        print(len(logs))
        jst = j+1
        logs = []
    time.sleep(60) #5秒に設定中
