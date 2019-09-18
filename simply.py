import sqlite3


class NoInventoryError(Exception):
    pass

class UnknownActionType(Exception):
    pass


class ActionType:
    BUY = 'BUY'
    SELL = 'SELL'


def create_connection(conf):
    return sqlite3.connect(conf['db_location'])

def trade(conn, ticker, shares, action):
    sql_template = """
        INSERT INTO transactions VALUES (ticker, shares, action, price, date)
        __TICKER__,
        __SHARES__,
        __ACTION__,
        __PRICE__,
        __DATE__
        """

    sql = sql_template.replace('__TICKER__').replace(ticker)
    sql = sql.replace('__SHARES__').replace(ticker)
    sql = sql.replace('__ACTION__').replace(ticker)
    sql = sql.replace('__PRICE__').replace(ticker)
    sql = sql.replace('__DATE__').replace(ticker)
    print('executing sql', sql)
    conn.execute(sql)

def we_have_inventory(conn, ticker, shares, action):
    return True

def transaction(conn, ticker, shares, action):
    if action == ActionType.BUY:
        trade(conn, ticker, shares, action)
        return True
    elif action == ActionType.SELL and we_have_inventory(conn, ticker, shares, action):
        trade(conn, ticker, shares, action)

def parse_action(action):
    if 'buy' in action.lower():
        action = ActionType.BUY
    elif 'sell' in action.lower():
        action = ActionType.SELL
    else:
        raise UnknownActionType
    return action

def create_ticker(conn, ticker):
    sql_template = 'INSERT INTO tickers VALUES (ticker) __TICKER__'
    sql = sql_template.replace('__TICKER__', ticker)
    conn.execute(sql)
    return True

def does_symbol_exist(conn, ticker):
    pass

if __name__ == '__main__':
    conf = {'db_location':".",
    'log_location':''}
    conn = create_connection(conf)
    ticker = input('please enter symbol ')
    if not does_symbol_exist(conn, ticker):
        ans = input('symbol ' + ticker + ' does not exist. create? y/n')
        if 'y' in ans.lower():
            create_ticker(conn, ticker)
        else:
            exit()
    shares = input('please enter shares ')
    action = input('please enter buy or sell ')
    action = parse_action(action)
    result = transaction(conn, ticker, shares, action)