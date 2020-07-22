import backtrader as bt


class NaiveStrategy(bt.Strategy):
    """Naive rules based trading strategy."""

    def __init__(self):
        """Construct new strategy.

        A backtrader.Cerebro object is needed to pass in parameters into this
        object. Sample construction of strategy object is the following:
        cerebro.addstrategy(
            NaiveStrategy TODO: add parameters.
        )
        Parameters for the strategy are passed in as arguments in the
        addstrategy method of a cerebro object.
        """
        self.step = 0
        print(self.datas[0].datetime.datetime)

    def log(self, txt: str, datetime=None):
        """Logging function for this strategy.

        Args:
            txt: A string output message.
            datetime: A datetime object.
        """
        # Logging function for this strategy.
        datetime = datetime or self.data.datetime.datetime(0)
        print('%s, %s' % (datetime.isoformat(), txt))

    def notify_order(self, order):
        """Receives an order when there has been a change in one.

        Outputs messages related to changes in the statuses of orders placed.
        Whether these be buy or sell orders.
        Args:
            order: Backtrader order object that has had its status changed.
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed.
        # Broker could reject order if not enough cash.
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log('Order Canceled/Margin/Rejected')
            return

    def notify_trade(self, trade):
        """Notifies whenever there is a change in trade status.

        A trade is open when the position in an instrument goes from zero to
        non-zero, and is closed when it goes from non-zero to zero. This logs
        the profit/loss and commission associated with the trade.
        Args:
            trade: A backtrader trade object for tracking open positions.
        """
        if not trade.isclosed:
            return

        # Log the profit/loss and commission with the trading period.
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        """Called on all data points to simulate strategy behavior."""
        # Get the current time stamp.
        self.log("PRICE: %s" % str(self.data.close[0]))
        print(self.datas[0].datetime.datetime(0))

