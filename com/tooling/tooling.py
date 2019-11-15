import sqlite3
# from ..core.simply_core import ActionType

class UnknownActionType(Exception):
    pass

def create_ticker(conn, ticker):
    sql_template = "INSERT INTO tickers (ticker) VALUES ('__TICKER__');"
    sql = sql_template.replace('__TICKER__', ticker)
    conn.execute(sql)
    conn.commit()
    return True

def create_connection(conf):
    return sqlite3.connect(conf['db_location'])

def get_ticker_id(conn, ticker):
    sql_templte = "SELECT id, is_active FROM tickers where ticker = '__TICKER__'"
    sql = sql_templte.replace('__TICKER__', ticker)
    result = conn.execute(sql)
    result = result.fetchone()
    if result[1] == False or result[1] is not None:
        raise Exception("This ticker has been deactivated")
    return str(result[0])

def parse_action(action, ActionType):
    if 'b' in action.lower():
        action = ActionType.BUY
    elif 's' in action.lower():
        action = ActionType.SELL
    else:
        raise UnknownActionType
    return action

def does_symbol_exist(conn, ticker):
    sql_template = "select ticker from tickers where ticker = '__TICKER__'"
    sql = sql_template.replace('__TICKER__', ticker)
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result is None:
        return False
    else:
        return True


def enter_trade_action(text, ActionType):
    while(True):
        action = input(text)
        if action.lower()[0] == 'b':
            return ActionType.BUY
        if action.lower()[0] == 's':
            return ActionType.SELL

def get_ticker_from_id(conn, ticker_id):
    sql_template = "SELECT ticker from tickers WHERE id = __ID__"
    sql = sql_template.replace('__ID__', str(ticker_id))
    cursor = conn.execute(sql)
    result = cursor.fetchone()[0]
    return result