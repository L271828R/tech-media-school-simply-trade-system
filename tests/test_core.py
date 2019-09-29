import sqlite3
# import tooling 
import sys
sys.path.append('..')
sys.path.append('.')
from com.tooling.tooling import *
from com.core.simply_core import *
import pytest




def test_sample():
    assert 1 == 1


def test_get_last_price_type_date_by_ticker(db_connection):
    db_connection.execute("INSERT INTO tickers (id, ticker) VALUES (1, 'AAPL')")
    db_connection.commit()
    db_connection.execute("""
    INSERT INTO prices (ticker_id, price, price_date, price_type_id)
    VALUES (1, 33, '2019-05-01', 1)
    """)
    db_connection.commit()
    price, price_type, date, _id = get_last_price_type_date_id_by_ticker(db_connection, 'AAPL')
    assert price == 33
    assert price_type == 'FROM_SALE'
    assert date == '2019-05-01'
    assert _id == 1


def test_get_portfolio(db_connection):
    deposit(db_connection, '1000')
    ticker = 'MU'
    create_ticker(db_connection, ticker)
    price = 33
    shares = 1
    action = ActionType.BUY
    trade(conn=db_connection, ticker=ticker, shares=shares, price=price, action=action)
    port = get_portfolio(db_connection)
    expected = {'market_value': 33, 'price': 33, 'price_prior': 33, 'shares': 1, 'ticker': 'MU' }
    assert expected ==  port[0]

def test_get_portfolio_2buys(db_connection):
    deposit(db_connection, '1000')
    ticker = 'MU'
    create_ticker(db_connection, ticker)
    price = 100
    shares = 1
    action = ActionType.BUY
    trade(conn=db_connection, ticker=ticker, shares=shares, price=price, action=action)
    # port = get_portfolio(db_connection)
    # expected = {'market_value': price * shares, 'price': price, 'price_prior': price, 'shares': 1, 'ticker': 'MU' }
    # assert expected ==  port[0]
    prior_price = 100
    price = 101
    added_shares = 1
    trade(conn=db_connection, ticker=ticker, shares=added_shares, price=price, action=action)
    port = get_portfolio(db_connection)
    cursor = db_connection.execute("SELECT * FROM prices")
    results_prices = cursor.fetchall()
    expected = {'market_value': (added_shares + shares) * price,
     'price': price,
     'price_prior': prior_price,
     'shares': added_shares + shares,
     'ticker': 'MU' }
    assert expected == port[0]
