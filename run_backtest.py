from datetime import datetime
from backtest import strategy, data
import backtrader as bt
import pandas as pd


def convert_datetime(timestamp):
    """Convert string datetime to date time object."""
    date_time_obj = datetime.strptime(
        timestamp, '%Y-%m-%d %H:%M:%S.%f')


cerebro = bt.Cerebro()
data_feed = data.create_data_feed("data/prices_td/FMCIW_prices.csv")
cerebro.adddata(data_feed)
cerebro.addstrategy(strategy.NaiveStrategy)

# Set our desired cash start
cerebro.broker.setcash(100000.0)

cerebro.run()
portvalue = cerebro.broker.getvalue()
print("DONE")
print(portvalue)



# startcash = 10000
#
# #Create an instance of cerebro
# cerebro = bt.Cerebro()
#
# #Add our strategy
# cerebro.addstrategy(dsf, oneplot=False)
#
# #create our data list
# datalist = [
#     ('data/CAD_CHF-2005-2017-D1.csv', 'CADCHF'), #[0] = Data file, [1] = Data name
#     ('data/EUR_USD-2005-2017-D1.csv', 'EURUSD'),
#     ('data/GBP_AUD-2005-2017-D1.csv', 'GBPAUD'),
# ]
#
# #Loop through the list adding to cerebro.
# for i in range(len(datalist)):
#     data = OandaCSVData(dataname=datalist[i][0])
#     cerebro.adddata(data, name=datalist[i][1])
#
#
# # Set our desired cash start
# cerebro.broker.setcash(startcash)
#
# # Run over everything
# cerebro.run()
#
# #Get final portfolio Value
# portvalue = cerebro.broker.getvalue()
# pnl = portvalue - startcash
#
# #Print out the final result
# print('Final Portfolio Value: ${}'.format(portvalue))
# print('P/L: ${}'.format(pnl))
#
# #Finally plot the end results
# cerebro.plot(style='candlestick')