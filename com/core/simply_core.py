import sqlite3
from datetime import datetime
from datetime import timedelta
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


def run(conf):
    conn = create_connection(conf)

    with conn:
        while(True):
            screens.clear_screen()
            portfolio_value = get_portfolio_value(conn)
            cash_balance = get_cash_balance(conn)
            screens.print_banner()
            screens.print_options_screen(cash_balance, portfolio_value)
            print("")
            print("-------------------------------")
            run_alerts(conn)
            print("-------------------------------")
            ans = input(">> ")
            if ans == "1":
                trade_screen(conn)
            elif ans == "2":
                get_todays_activity(conn)
            elif ans == "3":
                deposit_screen(conn)
            elif ans == "4":
                portfolio_screen(conn)
            elif ans == "5":
                enter_prices(conn)
            elif ans == "6":
                exit()

def run_alerts(conn):
    print('Alerts')

def get_last_price_type_date_by_ticker(conn, ticker):
    sql_template = """
        SELECT price, price_types.name, max(price_date) FROM prices, 
        price_types, 
        tickers 
        where 
        prices.ticker_id = tickers.id 
        and 
        price_type_id = price_types.id
        and 
        tickers.ticker = '__TICKER__'
    """
    sql = sql_template.replace('__TICKER__', ticker)
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    return result 

def enter_price_logic(conn, ticker):
    sql_price_insert_template = """
    INSERT INTO prices 
    (price, ticker_id, price_date, price_type_id)
    VALUES(
    __PRICE__,
    __TICKER_ID__,
    '__PRICE_DATE__',
    __PRICE_TYPE_ID__)
    """
    sql_price_delete_template = """
    DELETE FROM prices 
    WHERE
    ticker_id = __TICKER_ID__
    AND
    price_date = '__PRICE_DATE__'
    AND
    price_type_id = __PRICE_TYPE_ID__
    """

    print("Ticker Chosen", ticker)
    price = input("enter price\r\n")
    price_type = input("Enter Price Type: [E]OD [I]ntra-day\r\n").lower()
    today_date = datetime.now()
    yesterday_date = today_date - timedelta(days=1)
    ans = input(f"""
    For which day?
    [1] {today_date.year}-{today_date.month}-{today_date.day}
    [2] {yesterday_date.year}-{yesterday_date.month}-{yesterday_date.day}\r\n
    """)
    date_to_use = None
    if ans == "1" and price_type == 'e':
        date_to_use = today_date.strftime('%Y-%m-%d 23:59:59')
    elif ans == "2" and price_type == 'e':
        # date_to_use = yesterday_date.strftime('%Y-%m-%d %H:%M:%S')
        date_to_use = yesterday_date.strftime('%Y-%m-%d 23:59:59')
    elif ans == "1" and price_type == 'i':
        date_to_use = today_date.strftime('%Y-%m-%d %H:%M:%S')
    elif ans == "2" and price_type == 'i':
        date_to_use = yesterday_date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return False

    sql_price_type_template = "SELECT id from price_types where name = '__NAME__'"
    if 'e' in price_type:
        sql = sql_price_type_template.replace('__NAME__', 'EOD')
    elif 'i' in price_type:
        sql = sql_price_type_template.replace('__NAME__', 'INTRA_DAY')
    cursor = conn.execute(sql)
    price_type_id = cursor.fetchone()[0]
    ticker_id = get_ticker_id(conn, ticker)

    sql_delete = sql_price_delete_template.replace('__PRICE_DATE__', date_to_use)
    sql_delete = sql_delete.replace('__PRICE_TYPE_ID__', str(price_type_id))
    sql_delete = sql_delete.replace('__TICKER_ID__', ticker_id)
    conn.execute(sql_delete)
    conn.commit()

    sql_insert = sql_price_insert_template.replace('__PRICE__', price)
    sql_insert = sql.replace('__PRICE_DATE__', date_to_use)
    sql_insert = sql.replace('__PRICE_TYPE_ID__', str(price_type_id))
    sql_insert = sql.replace('__TICKER_ID__', ticker_id)
    conn.execute(sql_insert)
    conn.commit()


def enter_prices(conn):
    while(True):
        portfolio = get_portfolio(conn)
        screens.clear_screen()
        print("*" * 55)
        print("***             Price Entry Screen              ***")
        print("*" * 55)
        print("")
        s = "{:<5}{:<10}{:<15}{:<10}{:<10}".format("#", "ticker", "last price", "source", "date")
        print(s)
        for i, row in enumerate(portfolio):
            ticker = row['ticker']
            last_price, price_type, date = get_last_price_type_date_by_ticker(conn, ticker)
            print(f"{i:<5}{ticker:<10}{last_price:<15}{price_type:<10}{date:<10}")
        print("")
        print("----------------------")
        ans = input("Enter number for ticker you want to enter prices for. [M]enu\r\n").lower()
        if ans == 'm':
            break
        if ans.isdigit():
            enter_price_logic(conn, portfolio[int(ans)]['ticker'])
        input("[ENTER]")
        screens.clear_screen()
    

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

def insert_transaction(conn, ticker, shares, price, date, action):
    sql_template = """
        INSERT INTO transactions (ticker_id, shares, action, trade_date, price) VALUES (
        '__TICKER_ID__',
        __SHARES__,
        '__ACTION__',
        '__TRADE_DATE__',
        __PRICE__)
        """


    sql = sql_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    if action == ActionType.SELL:
        sql = sql.replace('__SHARES__', str(shares * -1))
    elif action == ActionType.BUY:
        sql = sql.replace('__SHARES__', str(shares))

    sql = sql.replace('__ACTION__', str(action)) 
    sql = sql.replace('__PRICE__', str(price))
    sql = sql.replace('__TRADE_DATE__', str(date))
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


def trade(conn, ticker, shares, price, action, date = None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    transaction_id = insert_transaction(conn, ticker, shares, price, date, action)
    add_to_pricing_table(conn, action, price, ticker, transaction_id) 
    amount = shares * price
    move_cash(conn, amount, action, transaction_id)
    return True

def transaction(conn, ticker, shares, price, action, date=datetime.now().strftime("%Y-%m-%d")):
    tran_amount = round(shares * price, 2)
    screens.print_trade_preview(ticker, action, price, shares, tran_amount)
    if not trade_validation(conn, action, shares, price, ticker, tran_amount):
        screens.clear_screen()
        return False
    while(True):
        ans = input("are you sure? ")
        if 'y' in ans:
            if action == ActionType.BUY:
                if not does_symbol_exist(conn, ticker):
                    create_ticker(conn, ticker)
            return trade(conn, ticker, shares, price, action, date)
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
    # if not does_symbol_exist(conn, ticker):
    #     ans = input('symbol ' + ticker + ' does not exist. create? y/n ')
    #     if 'y' in ans.lower():
    #         create_ticker(conn, ticker)
    #     else:
    #         exit()
    shares = int(input('please enter shares '))
    action = enter_trade_action("please enter [b]uy or [s]ell ", ActionType)
    price = float(input('please enter price '))
    action = parse_action(action, ActionType)
    if transaction(conn, ticker, shares, price, action):
        print("Trade Successful")
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
    input("[M]enu [E]xport total activity")
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
    MAX(p.id) 
    FROM prices p, 
    tickers 
    WHERE 
    p.ticker_id = tickers.id 
    GROUP BY p.ticker_id;
    """

    sql_get_second_last_prices_template = """
    SELECT 
    price, 
    tickers.ticker, 
    MAX(p.id) 
    FROM prices p,
    tickers
    WHERE p.ticker_id = tickers.id
    AND 
    tickers.ticker = '__TICKER__'
    AND
    p.id < (
        SELECT MAX(p.id)
        FROM prices p,
        tickers
        WHERE p.ticker_id = tickers.id
        AND 
        tickers.ticker = '__TICKER__'); 
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
        sql = sql_get_second_last_prices_template.replace('__TICKER__', open_pos[TICKER])
        cursor = conn.execute(sql)
        price_prior = cursor.fetchone()[0]
        for last_price in last_prices:
            if open_pos[TICKER] == last_price[TICKER]:
                price  = last_price[PRICE] 
                if price_prior is None:
                    price_prior = price
                shares = open_pos[SHARES]
                arr.append({
                    'ticker': open_pos[TICKER],
                    'shares': shares,
                    'price': price,
                    'price_prior': price_prior,
                    'market_value': price * shares})
    return arr

def get_portfolio_value(conn):
    port_items = get_portfolio(conn)
    mv = sum([x['market_value'] for x in port_items])
    return mv

def portfolio_screen(conn):
    portfolio = get_portfolio(conn)
    screens.print_portfolio_screen(portfolio)
