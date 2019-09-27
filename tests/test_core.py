import sqlite3
# import tooling 
import sys
sys.path.append('..')
sys.path.append('.')
from com.tooling.tooling import *
from com.core.simply_core import ActionType
import pytest

@pytest.fixture(scope="function")
def db_connection():
    seed_location = "/Users/luisrueda/Dropbox/scripts/simple_trading_system/sql_tools/seed.sql"
    conn = sqlite3.connect("file::memory:?cache=shared")
    with open(seed_location, 'r') as f:
            sql = f.read()
            conn.executescript(sql)
    conn.commit()
    return conn


def test_sample():
    assert 1 == 1