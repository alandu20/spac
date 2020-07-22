from datetime import datetime
import backtrader as bt
import pandas as pd


def convert_datetime(timestamp: str) -> datetime.date:
    """Convert string datetime to date time object.

    Given timestamp convert to datetime w/ expected pattern
    '%Y-%m-%d %H:%M:%S.%f'.
    Args:
        timestamp: Given string timestamp.
    Returns:
        datetime date object.
    """
    date_time_obj = datetime.strptime(
        timestamp, '%Y-%m-%d %H:%M:%S.%f')
    return date_time_obj


def create_data_feed(pathway: str) -> bt.DataBase:
    """Given data pathway create backtrader data feed object.

    Take price data pathway, apply transformations on date time column to
    turn strings into datetime objects.
    Args:
        pathway: String pathway of csv price data.
    Returns:
        Backtrader database.
    """
    price_data = pd.read_csv(pathway)
    price_data.datetime = price_data.datetime.apply(convert_datetime)
    data_feed = bt.feeds.PandasData(dataname=price_data, datetime=-1)
    return data_feed
