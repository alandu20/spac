class Order(object):
    """ Definitions:
        1. (optional) acctId: It should be one of the accounts returned by /iserver/accounts.
        If not passed, the first one in the list is selected.
        2. conid: conid is the identifier of the security you want to trade, you can find the conid with
        /iserver/secdef/search.
        3. secType: conid:type for example 265598:STK
        4. cOID: Customer Order ID. An arbitrary string that can be used to identify the order, e.g
        "my-fb-order". The value must be unique for a 24h span. Please do not set this value for child
        orders when placing a bracket order.
        5. parentId: When placing bracket orders, the child parentId must be equal to the cOId (customer
        order id) of the parent.
        6. orderType: orderType can be one of MKT (Market), LMT (Limit), STP (Stop) or STP_LIMIT (stop limit)
        7. (optional) listingExchange: By default we use "SMART" routing. Possible values
        are available via this end point: iserver/contract/{conid}/info, see valid_exchange
        8. outsideRTH: set to true if the order can be executed outside regular trading hours.
        9. price: optional if order is MKT, for LMT, this is the limit price. For STP this is the stop price.
        10. side: SELL or BUY
        11. ticker: ticker
        12. tif: GTC (Good Till Cancel) or DAY. DAY orders are automatically cancelled at the end of the Day
        13. referrer: for example QuickTrade
        14. quantity: usually integer, for some special cases can be float numbers
        15. fxQty: double number, this is the cash quantity field which can only be used for FX conversion order.
        16. useAdaptive: If true, the system will use the Adaptive Algo to submit the order
        https://www.interactivebrokers.com/en/index.php?f=19091
        17. isCurrencyConversion: set to true if the order is a FX conversion order
    """
    def __init__(self, conid: str, secType: str, cOID: str, parentId: str, price: float,
                 side: str, ticker: str, quantity: int):
        self.acctId = open('account_info.txt', 'r').read()
        self.conid = conid
        self.secType = secType
        self.cOID = cOID
        self.parentId = parentId
        self.orderType = 'LMT'
        self.listingExchange = 'SMART'
        self.outsideRTH = 'true'
        self.price = price
        self.side = side
        self.ticker = ticker
        self.tif = 'DAY'
        self.referrer = 'QuickTrade'
        self.quantity = quantity
        self.fxQty = 0
        self.useAdaptive = 'true'
        self.isCurrencyConversion = 'false'

    def get_acctId():
        return self.acctId

    def get_conid():
        return self.conid

    def get_secType():
        return self.secType

    def get_cOID():
        return self.cOID

    def get_parentId():
        return self.parentId

    def get_orderType():
        return self.orderType

    def get_listingExchange():
        return self.listingExchange

    def get_outsideRTH():
        return self.outsideRTH

    def get_price():
        return self.price

    def get_side():
        return self.side

    def get_ticker():
        return self.ticker

    def get_tif():
        return self.tif

    def get_referrer():
        return self.referrer

    def get_quantity():
        return self.quantity

    def get_fxQty():
        return self.fxQty

    def get_useAdaptive():
        return self.useAdaptive

    def get_isCurrencyConversion():
        return self.isCurrencyConversion
