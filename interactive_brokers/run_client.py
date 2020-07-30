from client import IBClient
import numpy as np
from order import Order

def get_cOID():
    """Create random customer order id between 0 and 1e6 (must be unique for 24h span)."""
    R = np.random.RandomState()
    random_order_id = R.random_integers(0, 1000000, 1)
    cOID = 'spac_order_' + str(random_order_id[0])
    return cOID

def calc_order_price(symbol):
    """Calculate limit price based on current best bid offer."""
    return np.nan

def calc_order_quantity(symbol):
    """Calculate order quantity based on 8-K type."""
    return np.nan

def main():
    # init client
    ib_client = IBClient()

    # re-authenticate if needed
    if ib_client.is_authenticated()['authenticated'] is False:
        print('No longer authenticated. Gateway timeouts if idle for a few minutes. '
              'Run ib_client.tickle() more often. Re-authenticating...\n')
        ib_client.reauthenticate()

    # check user sso validated
    print('Validated user:', ib_client.validate()['USER_NAME'], '\n')

    # todo: figure out why get_account_balance breaks. STATUS CODE: 500
    # balance = ib_client.get_account_balance()
    # print(balance)

    # current live orders
    live_orders = ib_client.get_live_orders()['orders']
    if len(live_orders)==0:
        print('No live orders\n')
    else:
        print('Current live orders:')
        df_live_orders = pd.DataFrame.from_dict(live_orders)
        print(df_live_orders)

    # find cOID identifier for symbol
    symbol = 'FMCI'
    conid = ib_client.get_conid(symbol)[0]['conid']
    print('Symbol and conid:', symbol, conid)

    # create new order for symbol
    # cOID = get_cOID()
    # limit_price = calc_order_price(symbol)
    # side = 'BUY'
    # quantity = calc_order_quantity(symbol)
    # new_order = Order(conid = conid, secType = 'STK', cOID = cOID, parentId = cOID,
    #                   price = limit_price, side = side, ticker = symbol, quantity = quantity)

    # send new order
    # ib_client.place_order(new_order)

if __name__ == "__main__":
    main()