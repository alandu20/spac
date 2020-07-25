from backtest import strategy, data
import backtrader as bt
import sec_scraper


def main():
    ticker = "NEBU"
    sec_map = sec_scraper.SEC()
    company_name = sec_map.get_name_by_ticker(ticker)
    cik = sec_map.get_cik_by_ticker(ticker)
    co = sec_scraper.Company(company_name, cik)
    filings = co.get_all_filings("8-K")

    cerebro = bt.Cerebro()
    data_feed = data.create_data_feed("data/prices_td/%sW_prices.csv" % ticker)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy.NaiveStrategy, filings=filings)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    cerebro.run()
    cerebro.plot()

if __name__ == "__main__":
    main()


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