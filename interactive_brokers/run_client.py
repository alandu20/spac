from client import IBClient
import numpy as np
from order import Order
import pandas as pd
import sys
pd.options.display.max_columns = 100

# Protections
MAX_OUTSTANDING_ORDERS = 10
MAX_NOTIONAL = 10000
MAX_COMMISSION = 100

def get_cOID():
    """Create random customer order id between 0 and 1e6 (must be unique for 24h span)."""
    R = np.random.RandomState()
    random_order_id = R.random_integers(0, 1000000, 1)
    cOID = 'spac_order_' + str(random_order_id[0])
    return cOID

def calc_order_price(symbol):
    """Calculate limit price based on current best bid offer."""
    return .01

def calc_order_quantity(symbol):
    """Calculate order quantity based on 8-K type."""
    return 1

def main():
    # init client
    if len(sys.argv) == 0:
        print('Missing symbol argument')
    symbol = str(sys.argv[1])

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

    # current outstanding orders
    live_orders = ib_client.get_outstanding_orders()['orders']
    if len(live_orders)==0:
        print('No outstanding orders\n')
    else:
        print('Outstanding orders:')
        df_live_orders = pd.DataFrame.from_dict(live_orders)
        cols = ['acct','ticker','secType','orderDesc','remainingQuantity',
                'filledQuantity','status','orderId','order_ref']
        print(df_live_orders[cols],'\n')
        if len(df_live_orders) > MAX_OUTSTANDING_ORDERS:
            ib_client.logout()
            raise ValueError('Oustanding order count ({}) > MAX_OUTSTANDING_ORDERS ({})! Killed '
                             'session.'.format(len(df_live_orders), MAX_OUTSTANDING_ORDERS))

    # find conid identifier for symbol
    conid_warrant = ib_client.get_conid(symbol)[0]['sections'][0]['conid']
    print('Symbol and conid:', symbol, conid_warrant)

    # create new order for symbol
    cOID = get_cOID()
    side = 'BUY'
    limit_price = calc_order_price(symbol)
    quantity = calc_order_quantity(symbol)
    print('New child order id:', cOID)
    print('New order side:', side)
    print('New order price:', limit_price)
    print('New order quantity:', quantity, '\n')
    new_order = Order(conid = conid_warrant, secType = 'STK', cOID = cOID, parentId = cOID,
                      price = limit_price, side = side, ticker = symbol, quantity = quantity)

    # preview new order
    preview = ib_client.preview_order(new_order)
    notional = float(preview['amount']['amount'].replace(' USD',''))
    commission = float(preview['amount']['commission'].replace(' USD',''))
    total_notional = float(preview['amount']['total'].replace(' USD',''))
    print('Preview order:')
    print('amount:', notional)
    print('commission:', commission)
    print('total:', total_notional)
    print('warning:', preview['warn'].replace('\n',' '), '\n')

    # order protections
    if notional > MAX_NOTIONAL:
        raise ValueError('Order notional ({}) exceeded MAX_NOTIONAL ({})! '
                         'Order rejected.'.format(notional, MAX_NOTIONAL))
    if commission > MAX_COMMISSION:
        raise ValueError('Order notional ({}) exceeded MAX_COMMISSION ({})! '
                         'Order rejected.'.format(notional, MAX_COMMISSION))

    # send new order
    ib_client.new_order(new_order)
    print('Sent new order, order_ref =', cOID, '\n')

    # delete any active orders
    # does not work for paper trading ('Order is inactive')
    if len(live_orders)>0:
        df_active_orders = df_live_orders[df_live_orders['status']=='Submitted']
        for active_orderId in df_active_orders['status']:
            ib_client.delete_order(active_orderId)
            print('Deleted order:', active_orderId)

if __name__ == "__main__":
    main()