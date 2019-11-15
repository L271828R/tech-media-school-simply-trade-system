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





def test_transaction_buy_unknown_ticker(db_connection):
    deposit(db_connection, '100')
    conf = {}
    conf['cash_validation'] = True
    conf['is_prod'] = False
    ticker = 'DOES_NOT_EXIST'
    shares = 1
    price = 1
    action = ActionType.BUY
    result = transaction(conn=db_connection, conf=conf, ticker=ticker, shares=shares, price=price, action=action)
    result_ticker = db_connection.execute("SELECT * FROM tickers").fetchone()
    assert result_ticker[1] == 'DOES_NOT_EXIST'
    assert result == True


def test_transaction_sell_unknown_ticker(db_connection):
    deposit(db_connection, '100')
    conf = {}
    conf['cash_validation'] = True
    conf['is_prod'] = False
    ticker = 'DOES_NOT_EXIST'
    shares = 1
    price = 1
    action = ActionType.SELL
    result = transaction(conn=db_connection, conf=conf, ticker=ticker, shares=shares, price=price, action=action)
    result_ticker = db_connection.execute("SELECT * FROM tickers").fetchone()
    assert result_ticker[1] == 'DOES_NOT_EXIST'
    assert result == False

def test_transaction_sell_unknown_ticker_margin(db_connection):
    deposit(db_connection, '100')
    conf = {}
    conf['cash_validation'] = False
    conf['is_prod'] = False
    ticker = 'DOES_NOT_EXIST'
    shares = 1
    price = 1
    action = ActionType.SELL
    result = transaction(conn=db_connection, conf=conf, ticker=ticker, shares=shares, price=price, action=action)
    result_ticker = db_connection.execute("SELECT * FROM tickers").fetchone()
    assert result_ticker[1] == 'DOES_NOT_EXIST'
    assert result == False

def test_cash_validation_off(db_connection):
    deposit(db_connection, '0')
    ticker = 'MU'
    create_ticker(db_connection, ticker)
    price = 33
    shares = 1
    action = ActionType.BUY
    trade(conn=db_connection, ticker=ticker, shares=shares, price=price, action=action)
    port = get_portfolio(db_connection)
    expected = {'market_value': 33, 'price': 33, 'price_prior': 33, 'shares': 1, 'ticker': 'MU' }



def test_get_last_price_type_date_by_ticker(db_connection):
    db_connection.execute("INSERT INTO tickers (id, ticker) VALUES (1, 'AAPL')")
    db_connection.commit()
    db_connection.execute("""
    INSERT INTO prices (ticker_id, price, price_date, price_type_id)
    VALUES (1, 33, '2019-05-01', 1)
    """)
    db_connection.execute("""
    INSERT INTO prices (ticker_id, price, price_date, price_type_id)
    VALUES (1, 44, '2019-04-01', 1)
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
    trade(conn=db_connection, ticker=ticker, shares=shares, price=price, action=action, date='2019-03-02')
    # port = get_portfolio(db_connection)
    # expected = {'market_value': price * shares, 'price': price, 'price_prior': price, 'shares': 1, 'ticker': 'MU' }
    # assert expected ==  port[0]
    prior_price = 100
    price = 101
    added_shares = 1
    # time.sleep(1)
    trade(conn=db_connection, ticker=ticker, shares=added_shares, price=price, action=action, date='2019-03-03')
    port = get_portfolio(db_connection)
    expected = {'market_value': (added_shares + shares) * price,
     'price': price,
     'price_prior': prior_price,
     'shares': added_shares + shares,
     'ticker': 'MU' }
    assert expected == port[0]

def test_buy_eod_portfolio(db_connection):
    deposit(db_connection, '1000')
    ticker = 'MU'
    create_ticker(db_connection, ticker)
    price = 100
    shares = 1
    action = ActionType.BUY
    trade(conn=db_connection, ticker=ticker, shares=shares, price=price, action=action, date='2019-02-05')
    EOD = 3
    ticker_id = get_ticker_id(db_connection, 'MU')
    prior_price = '80'
    execute_price(db_connection, '2019-02-04', EOD, ticker_id, prior_price)
    port = get_portfolio(db_connection)
    expected = {'market_value': (shares) * price,
     'price': price,
     'price_prior': float(prior_price),
     'shares': shares,
     'ticker': 'MU'} 
    assert expected == port[0]
