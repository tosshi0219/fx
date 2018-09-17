import os
import sys
import time
from datetime import timedelta, datetime
import numpy as np
import oandapy
sys.path.append('/Users/toshio/project/fx')
from config import *

ENV = "practice"
class Trader(object):

    oanda = oandapy.API(environment=ENV, access_token=token)
    _account_id = None
    _currency_pair = None

    def __init__(self, pair="USD_JPY"):
        self._currency_pair = pair

    def _market_order(self, side, volume, take_profit, stop_loss):
        assert side in ["sell", "buy"], "The argument 'side' is illegal."
        order = self.oanda.create_order(self.account_id,
                              instrument=self._currency_pair,
                              units=volume,
                              side=side,
                              takeProfit=take_profit,
                              stopLoss=stop_loss,
                              type="market")
        return order


    def buy(self, volume, take_profit=None, stop_loss=None):
        """Market Order
        Args:
            volume(Int): Trade volume.
            expire_time(timedelta): Expired time. By default, order will be expired in 1 hour.
        """
        self._market_order(side="buy", volume=volume, take_profit=take_profit, stop_loss=stop_loss)

    def sell(self, volume, take_profit=None, stop_loss=None):
        """Market Order
        Args:
            volume(Int): Trade volume.
            expire_time(timedelta): Expired time. By default, order will be expired in 1 hour.
        """
        self._market_order(side="sell", volume=volume, take_profit=take_profit, stop_loss=stop_loss)

    def _limit_order(self, side, price, volume, take_profit, stop_loss, expire_time):
        limit_order = self.oanda.create_order(self.account_id,
                              instrument=self._currency_pair,
                              units=volume,
                              price=price,
                              side=side,
                              takeProfit=take_profit,
                              stopLoss=stop_loss,
                              expiry=self._transform_time2iso(datetime.now() + expire_time),
                              type="limit")

    def buy_at(self, price, volume, take_profit=None, stop_loss=None, expire_time=timedelta(hours=1)):
        """Limit Order
        Args:
            volume(Int): Trade volume.
            expire_time(timedelta): Expired time. By default, order will be expired in 1 hour.
        """
        self._limit_order(sied="buy", price=price, volume=volume,
            take_profit=take_profit, stop_loss=stop_loss, expire_time=expire_time)

    def sell_at(self, price, volume, take_profit=None, stop_loss=None, expire_time=timedelta(hours=1)):
        """Limit Order
        Args:
            volume(Int): Trade volume.
            expire_time(timedelta): Expired time. By default, order will be expired in 1 hour.
        """
        self._limit_order(sied="sell", price=price, volume=volume, 
            take_profit=take_profit, stop_loss=stop_loss, expire_time=expire_time)

    def close_all(self):
        close_order = self.oanda.close_position(account_id, self._currency_pair)

    def get_account_info(self):
        return self.oanda.get_account(self.account_id)

    @property
    def account_id(self):
        if self._account_id is None:
            self._account_id = self.oanda.get_accounts()["accounts"][0]["accountId"]
        return self._account_id

    # Miscs
    def _transform_time2iso(self, dateobj):
        date_str = dateobj.isoformat("T") + "Z"
        return date_str

    def _handle_error(self, method):
        pass

if __name__ == "__main__":
    assert ENV=="practice", "Environment is not demo, are you sure?"
    trader = Trader()
    trader.get_account_info()
    trader.buy(volume=100)
    trader.buy(volume=100)
