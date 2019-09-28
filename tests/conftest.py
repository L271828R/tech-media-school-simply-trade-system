import sqlite3
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