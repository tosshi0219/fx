from datetime import datetime, timedelta
import oandapy
import sys
sys.path.append('/Users/toshio/project/fx')
from config import token, acc_id
from lib.inference import Inference

def transaction():
    oanda = oandapy.API(environment="practice", access_token=token)

    # set the trade to expire after one day
    trade_expire = datetime.utcnow() + timedelta(days=1)
    trade_expire = trade_expire.isoformat("T") + "Z"

    response = oanda.get_prices(instruments='USD_JPY')
    prices = response.get("prices")
    asking_price = prices[0].get("ask")

    response = oanda.create_order(acc_id,
        instrument='USD_JPY',
        units=100,
        side='buy',
        type='limit',
        price=asking_price,
        expiry=trade_expire
    )

# if __name__ == '__main__':
#     inf = Inference()
#     print(inf.pred)
#     if inf.pred > 0.1:
#         transaction()
#     else:
#         pass