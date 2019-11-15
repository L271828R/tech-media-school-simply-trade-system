import sqlite3
import sys
from com.tooling.tooling import *
from com.core.simply_core import ActionType
import pytest

def test_get_ticker_from_id(db_connection):
    db_connection.execute("INSERT INTO tickers (id, ticker) VALUES (1, 'AAPL')")
    db_connection.commit()
    ticker = get_ticker_from_id(db_connection, 1)
    assert(ticker == 'AAPL')

def test_does_symbol_exist(db_connection):
    db_connection.execute("INSERT INTO tickers (id, ticker) VALUES (1, 'AAPL')")
    db_connection.commit()
    ans = does_symbol_exist(db_connection, 'MU')
    assert(ans == False)
    ans = does_symbol_exist(db_connection, 'AAPL')
    assert(ans == True)

def test_get_ticker_id(db_connection):
    db_connection.execute("INSERT INTO tickers (id, ticker) VALUES (1, 'AAPL')")
    db_connection.commit()
    ans = does_symbol_exist(db_connection, 'AAPL')
    assert(ans == True)

def test_create_ticker(db_connection):
    db_connection.execute("DELETE FROM tickers WHERE ticker = 'AAPL'")
    db_connection.commit()
    create_ticker(db_connection, "AAPL")
    cursor = db_connection.execute("SELECT ticker FROM tickers WHERE ticker = 'AAPL'")
    result = cursor.fetchone()
    assert(result[0] == 'AAPL')

def test_parse_action(db_connection):
    assert( ActionType.BUY == parse_action("BUY", ActionType) )
    assert( ActionType.SELL == parse_action("SELL", ActionType) )
