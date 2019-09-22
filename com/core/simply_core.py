import sqlite3
from datetime import datetime
import os
import sys
from ..print_screens import screens
from ..tooling.tooling import create_ticker
from ..tooling.tooling import get_ticker_from_id
from ..tooling.tooling import get_ticker_id
from ..tooling.tooling import does_symbol_exist
from ..tooling.tooling import enter_trade_action
from ..tooling.tooling import parse_action
from ..tooling.tooling import create_connection

# class NoInventoryError(Exception):
#     pass


# class NotEnoughSharesException(Exception):
#     pass

class ActionType:
    BUY = 'BUY'
    SELL = 'SELL'

def get_transaction_id(conn, ticker, shares, price, date, action):
    sql_transaction_id_template = """
     SELECT max(id) FROM transactions WHERE 
        ticker_id = '__TICKER_ID__' and
        shares = __SHARES__ and
        action = '__ACTION__' and
        price = __PRICE__ and
        date(trade_date) = '__DATE__'
    """
    sql_id = sql_transaction_id_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    sql_id = sql_id.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    
    if action == ActionType.SELL:
        sql_id = sql_id.replace('__SHARES__', str(shares * -1))
    elif action == ActionType.BUY:
        sql_id = sql_id.replace('__SHARES__', str(shares))

    sql_id = sql_id.replace('__ACTION__', str(action))
    sql_id = sql_id.replace('__PRICE__', str(price))
    sql_id = sql_id.replace('__DATE__', str(date))
    cursor = conn.execute(sql_id)
    result = cursor.fetchone()
    return result[0]

def trade(conn, ticker, shares, price, date, action):
    sql_template = """
        INSERT INTO transactions (ticker_id, shares, action, price) VALUES (
        '__TICKER_ID__',
        __SHARES__,
        '__ACTION__',
        __PRICE__)
        """


    sql = sql_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    if action == ActionType.SELL:
        sql = sql.replace('__SHARES__', str(shares * -1))
    elif action == ActionType.BUY:
        sql = sql.replace('__SHARES__', str(shares))

    sql = sql.replace('__ACTION__', str(action)) 
    sql = sql.replace('__PRICE__', str(price))
    # sql = sql.replace('__DATE__', str(date))
    conn.execute(sql)
    conn.commit()

    return get_transaction_id(conn, ticker, shares, price, date, action)

def we_have_inventory_for_sale(conn, ticker, shares):
    sql_template = """
        SELECT SUM(shares) from transactions where ticker_id = '__TICKER_ID__'
        GROUP BY shares;
        """
    sql = sql_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result is not None:
        if result[0] - shares < 0:
            return False
        else:
            return True
    else:
        return False

def get_inventory(conn, ticker):
    sql_template = """
        SELECT SUM(shares) from transactions where ticker_id = '__TICKER_ID__'
        GROUP BY shares;
        """
    sql = sql_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result is not None:
        return result[0] 
    else:
        return "0"

def get_share_balance(conn, ticker):
    sql_template = "SELECT SUM(shares) FROM transactions WHERE ticker_id = '__TICKER_ID__'"
    sql = sql_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result[0] is None:
        return 0
    else:
        return result[0]
    
def trade_validation(conn, action, shares, price, ticker, tran_amount):
    if action == ActionType.BUY:
        cash_bal = get_cash_balance(conn)
        if float(cash_bal) - (shares * price) < 0:
            screens.print_not_enough_cash_screen(cash_bal, tran_amount)
            return False
        else:
            return True
    elif action == ActionType.SELL:
        shares_bal = get_share_balance(conn, ticker)
        if shares_bal - shares < 0:
            screens.print_not_enough_shares_screen(shares_bal, shares, ticker)
            return False
        else:
            return True

def get_pricing_type(conn, action):
    sql_template = "SELECT id from price_types where name = '__NAME__'"
    sql = ""
    if action == ActionType.BUY:
        sql = sql_template.replace('__NAME__', "FROM_BUY")
    elif action == ActionType.SELL:
        sql = sql_template.replace('__NAME__', "FROM_SALE")

    cursor = conn.execute(sql)
    result = cursor.fetchone()
    return result[0]

def add_to_pricing_table(conn, action, price, ticker, transaction_id):
    ticker_id = get_ticker_id(conn, ticker)
    pricing_id = get_pricing_type(conn, action)

    sql_template = """
    INSERT INTO prices 
    (ticker_id, price_type_id, price, transaction_id)
    values (
    __TICKER_ID__,
    __PRICE_TYPE_ID__,
    __PRICE__,
    __TRANSACTION_ID__ )
    """
    sql = sql_template.replace('__TICKER_ID__', ticker_id)
    sql = sql.replace('__TICKER_ID__', ticker_id)
    sql = sql.replace('__PRICE_TYPE_ID__', str(pricing_id))
    sql = sql.replace('__PRICE__', str(price))
    sql = sql.replace('__TRANSACTION_ID__', str(transaction_id))
    conn.execute(sql)
    conn.commit()
    return True

def move_cash(conn, amount, action, transaction_id):
    sql_template = """
        INSERT INTO cash_balance
        (type, transaction_id, amount)
        VALUES
        (
            '__TYPE__',
            __TRANSACTION_ID__,
            __AMOUNT__
        )
    """
    sql = sql_template.replace('__TYPE__', action)
    sql = sql.replace('__TRANSACTION_ID__', str(transaction_id))

    if action == ActionType.BUY:
        amount = amount * -1

    sql = sql.replace('__AMOUNT__', str(amount))
    conn.execute(sql)
    conn.commit()
    return True

def transaction(conn, ticker, shares, price, action):
    date = datetime.now().strftime("%Y-%m-%d")
    tran_amount = round(shares * price, 2)
    screens.print_trade_preview(ticker, action, price, shares, tran_amount)
    if not trade_validation(conn, action, shares, price, ticker, tran_amount):
        screens.clear_screen()
        return False
    while(True):
        ans = input("are you sure? ")
        transaction_id = -1
        if 'y' in ans:
            if action == ActionType.BUY:
                transaction_id = trade(conn, ticker, shares, price, date, action)
            elif action == ActionType.SELL and we_have_inventory_for_sale(conn, ticker, shares):
                transaction_id = trade(conn, ticker, shares, price, date, action)

            add_to_pricing_table(conn, action, price, ticker, transaction_id) 
            amount = shares * price
            move_cash(conn, amount, action, transaction_id)
            return True

        if 'n' in ans:
            return False

def trade_screen(conn):
    while(True):
        ticker = input('please enter symbol ').upper()
        if ticker.isalpha():
            break
        else:
            print("")
            print("please enter letters only")
    # ticker = 'SVXY'
    if not does_symbol_exist(conn, ticker):
        ans = input('symbol ' + ticker + ' does not exist. create? y/n ')
        if 'y' in ans.lower():
            create_ticker(conn, ticker)
        else:
            exit()
    shares = int(input('please enter shares '))
    action = enter_trade_action("please enter [b]uy or [s]ell ", ActionType)
    price = int(input('please enter price '))
    action = parse_action(action, ActionType)
    if transaction(conn, ticker, shares, price, action):
        print("Trade Filled")
        input("[ENTER]")
        screens.clear_screen()

class CashEntryType:
    BANK = "BANK"
    SALE = "SALE"
    PURCHASE = "PURCHASE"

def deposit(conn, amount):
    sql_template = "INSERT INTO cash_balance (type, amount, date) VALUES ('__TYPE__', __AMOUNT__, '__DATE__')"

    sql = sql_template.replace("__TYPE__", CashEntryType.BANK)
    sql = sql.replace("__AMOUNT__", amount)
    sql = sql.replace("__DATE__", datetime.now().strftime("%Y-%m-%d"))
    # print(sql)
    conn.execute(sql)
    conn.commit()
    return True

def deposit_screen(conn):
    print(" How much would you like to deposit? ")
    ans =input()
    if ans.isnumeric():
        deposit(conn, ans)
    print("Amoutn deposited")
    input("[ENTER]")
    screens.clear_screen()

def get_cash_balance(conn):
    sql = "SELECT SUM(amount) FROM cash_balance"
    cursor = conn.execute(sql)
    res = cursor.fetchone()
    if res[0] is None:
        return "0"
    else:
        return res[0]

def format_activity(conn, row):
    ticker = get_ticker_from_id(conn, row[1])
    s = f"Tran Id={row[0]} Ticker={ticker} {row[2]} @ {row[4]} {row[5]}"
    print(s)

def get_todays_activity(conn):
    sql_template = "SELECT * FROM transactions where date(trade_date) = '__TRADE_DATE__'"
    sql = sql_template.replace('__TRADE_DATE__', datetime.now().strftime("%Y-%m-%d"))
    results = conn.execute(sql)
    screens.clear_screen()
    screens.print_activity_banner()
    for row in results:
        format_activity(conn, row)
    input("[ENTER]")
    screens.clear_screen()

def get_portfolio(conn):
    sql_open_positions = """
    SELECT
    ticker,
    SUM(shares) 
    FROM 
    transactions tr,
    tickers tk
    WHERE 
    tr.ticker_id = tk.id group by ticker
    HAVING SUM(shares) > 0;"""

    sql_last_prices = """
    SELECT
    ticker, 
    price,
    MAX(price_date) 
    FROM prices, 
    tickers 
    WHERE 
    prices.ticker_id = tickers.id 
    GROUP BY ticker_id;
    """
    cursor = conn.execute(sql_open_positions)
    open_positions = cursor.fetchall()
    cursor = conn.execute(sql_last_prices)
    last_prices = cursor.fetchall()
    TICKER = 0
    SHARES = 1
    PRICE  = 1
    arr = []
    for open_pos in open_positions:
        for last_price in last_prices:
            if open_pos[TICKER] == last_price[TICKER]:
                price  = last_price[PRICE] 
                shares = open_pos[SHARES]
                arr.append({
                    'ticker': open_pos[TICKER],
                    'shares': shares,
                    'price': price,
                    'market_value': price * shares})
    return arr

def get_portfolio_value(conn):
    port_items = get_portfolio(conn)
    mv = sum([x['market_value'] for x in port_items])
    return mv

def portfolio_screen(conn):
    portfolio = get_portfolio(conn)
    screens.print_portfolio_screen(portfolio)
