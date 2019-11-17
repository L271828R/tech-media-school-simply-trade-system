import sqlite3
import os
import sys
from datetime import datetime as dt
from datetime import timedelta
from ..print_screens import screens
from ..tooling.tooling import create_ticker
from ..tooling.tooling import get_ticker_from_id
from ..tooling.tooling import get_ticker_id
from ..tooling.tooling import does_symbol_exist
from ..tooling.tooling import enter_trade_action
from ..tooling.tooling import parse_action
from ..tooling.tooling import create_connection
from com.sql_templates import sql as sql_t
from com.print_screens.screens import print_banner
from com.core.price_lib import get_pricing_type, print_open_prices
from com.core.simply_constants import ActionType, CashEntryType
from com.core.portfolio_libs import get_portfolio
from com.core.portfolio_libs import get_portfolio_value

def enter_price_logic(conn, ticker):
    print("Ticker Chosen", ticker)
    price = input("enter price\r\n")
    price_type = input("Enter Price Type: [E]OD [I]ntra-day\r\n").lower()
    today_date = dt.now()
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
        raise Exception

    sql_price_type_template = "SELECT id from price_types where name = '__NAME__'"
    if 'e' in price_type:
        sql = sql_price_type_template.replace('__NAME__', 'EOD')
    elif 'i' in price_type:
        sql = sql_price_type_template.replace('__NAME__', 'INTRA_DAY')
    cursor = conn.execute(sql)
    price_type_id = cursor.fetchone()[0]
    ticker_id = get_ticker_id(conn, ticker)
    execute_price(conn, date_to_use, price_type_id, ticker_id, price)

def execute_price(conn, date_to_use, price_type_id, ticker_id, price):
    sql_price_insert_template = sql_t.sql_price_insert_template
    sql_price_delete_template = sql_t.sql_price_delete_template

    sql_delete = sql_price_delete_template.replace('__PRICE_DATE__', date_to_use)
    sql_delete = sql_delete.replace('__PRICE_TYPE_ID__', str(price_type_id))
    sql_delete = sql_delete.replace('__TICKER_ID__', ticker_id)
    conn.execute(sql_delete)
    conn.commit()

    sql_insert = sql_price_insert_template.replace('__PRICE__', price)
    sql_insert = sql_insert.replace('__PRICE_DATE__', date_to_use)
    sql_insert = sql_insert.replace('__PRICE_TYPE_ID__', str(price_type_id))
    sql_insert = sql_insert.replace('__TICKER_ID__', ticker_id)
    conn.execute(sql_insert)
    conn.commit()

def enter_prices(conn):
    portfolio = get_portfolio(conn)
    while(True):
        print_banner("Price Entry")
        print_open_prices(conn)
        ans = input("Enter number for ticker you want to enter prices for. [M]enu\r\n").lower()
        if ans == 'm':
            break
        if ans.isdigit():
            enter_price_logic(conn, portfolio[int(ans)]['ticker'])
        input("[ENTER]")
        screens.clear_screen()


def get_transaction_id(conn, ticker, shares, price, date, action):
    sql_transaction_id_template = sql_t.sql_transaction_id_template
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

    sql_insert_transaction_template = sql_t.sql_insert_transaction_template
    sql = sql_insert_transaction_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
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
    sql_we_have_inventory_for_sale_template = sql_t.sql_we_have_inventory_for_sale_template
    sql = sql_we_have_inventory_for_sale_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
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
    sql_get_inventory_template = sql_t.sql_get_inventory_template
    sql = sql_get_inventory_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return "0"

def get_share_balance(conn, ticker):
    sql_get_shares_balance_template = sql_t.sql_get_shares_balance_template
    sql = sql_get_shares_balance_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result[0] is None:
        return 0
    else:
        return result[0]

def trade_validation(conn, conf, action, shares, price, ticker, tran_amount):
    if action == ActionType.BUY:
        cash_bal = get_cash_balance(conn)
        if conf['cash_validation'] == False:
            return True
        elif float(cash_bal) - (shares * price) < 0:
            screens.print_not_enough_cash_screen(cash_bal, tran_amount, conf)
            return False
        else:
            return True
    elif action == ActionType.SELL:
        shares_bal = get_share_balance(conn, ticker)
        if shares_bal - shares < 0:
            screens.print_not_enough_shares_screen(conf, shares_bal, shares, ticker)
            return False
        else:
            return True

def add_to_pricing_table(conn, action, price, ticker, transaction_id, date=None):
    ticker_id = get_ticker_id(conn, ticker)
    pricing_id = get_pricing_type(conn, action)

    if date is None:
        sql_insert_into_prices_template = sql_t.sql_insert_into_prices_template_no_date
    else:
        sql_insert_into_prices_template = sql_t.sql_insert_into_prices_template_with_date
        sql_insert_into_prices_template = sql_insert_into_prices_template.replace('__PRICE_DATE__', date)

    sql = sql_insert_into_prices_template.replace('__TICKER_ID__', ticker_id)
    sql = sql.replace('__TICKER_ID__', ticker_id)
    sql = sql.replace('__PRICE_TYPE_ID__', str(pricing_id))
    sql = sql.replace('__PRICE__', str(price))
    sql = sql.replace('__TRANSACTION_ID__', str(transaction_id))
    conn.execute(sql)
    conn.commit()
    return True

def move_cash(conn, amount, action, transaction_id):
    sql_move_cash_template = sql_t.sql_move_cash_template
    sql = sql_move_cash_template.replace('__TYPE__', action)
    sql = sql.replace('__TRANSACTION_ID__', str(transaction_id))

    if action == ActionType.BUY:
        amount = amount * -1

    sql = sql.replace('__AMOUNT__', str(amount))
    conn.execute(sql)
    conn.commit()
    return True


def trade(conn, ticker, shares, price, action, date = None):
    if date is None:
        date = dt.now().strftime("%Y-%m-%d %H:%M:%S")

    transaction_id = insert_transaction(conn, ticker, shares, price, date, action)
    add_to_pricing_table(conn, action, price, ticker, transaction_id, date) 
    amount = shares * price
    move_cash(conn, amount, action, transaction_id)
    return True

def transaction(conn, conf, ticker, shares, price, action, date=dt.now().strftime("%Y-%m-%d %H:%M:%S")):
    tran_amount = round(shares * price, 2)
    screens.print_trade_preview(ticker, action, price, shares, tran_amount)
    if not does_symbol_exist(conn, ticker):
        create_ticker(conn, ticker)
    if not trade_validation(conn, conf, action, shares, price, ticker, tran_amount):
        screens.clear_screen()
        return False
    while(True):
        if conf['is_prod'] == True:
            ans = input("are you sure? ")
        else:
            ans = 'y'
        if 'y' in ans:
            return trade(conn, ticker, shares, price, action, date)
        if 'n' in ans:
            return False

def trade_screen(conn, conf):
    while(True):
        print("blank and enter to exit")
        print("")
        ticker = input('please enter symbol >> ').upper()
        if ticker == "":
            return False
        if ticker.isalnum():
            break
        else:
            print("")
            print("please enter letters only")
    while(True):
        shares = input('please enter shares >> ')
        if shares == "":
            return False
        if shares.isnumeric():
            shares = int(shares)
            break
        else:
            print("")
            print("Please enter a number")

    action = enter_trade_action("please enter [b]uy or [s]ell >> ", ActionType)
    while(True):
        price = input('please enter price >> ')
        if price == "":
            return False
        try:
            price = float(price)
            break
        except ValueError:
            print("")
            print("please enter a number")

    action = parse_action(action, ActionType)
    if transaction(conn, conf, ticker, shares, price, action):
        print("Trade Successful")
        input("[ENTER]")
        screens.clear_screen()

def deposit(conn, amount):
    sql_deposit_template = sql_t.sql_deposit_template
    sql = sql_deposit_template.replace("__TYPE__", CashEntryType.BANK)
    sql = sql.replace("__AMOUNT__", str(amount))
    sql = sql.replace("__DATE__", dt.now().strftime("%Y-%m-%d"))
    # print(sql)
    conn.execute(sql)
    conn.commit()
    return True

def deposit_screen(conn):
    while(True):
        try:
            print(" Blank and enter to exit")
            print(" How much would you like to deposit? ")
            ans =input(">> ")
            if ans == "":
                return False
            ans = float(ans)
            break
        except ValueError:
            print("")
            print("Please enter a number")
            input()
            screens.clear_screen()
    deposit(conn, ans)
    print("Amount deposited")
    input("[ENTER]")
    screens.clear_screen()

def get_cash_balance(conn):
    sql_get_cash_balance = sql_t.sql_get_cash_balance
    cursor = conn.execute(sql_get_cash_balance)
    res = cursor.fetchone()
    if res[0] is None:
        return "0"
    else:
        return res[0]

def format_activity(conn, row):
    ticker = get_ticker_from_id(conn, row[1])
    s = f"Tran Id={row[0]} Ticker={ticker} {row[2]} @ {row[4]} {row[5]}"
    print(s)


def get_transactions_by_date(conn, date=None):
    if date is None:
        sql_transactions_template = sql_t.sql_transactions_template
    else:
        raise Exception
    sql_today = sql_transactions_template.replace('__TRADE_DATE__', dt.now().strftime("%Y-%m-%d"))
    return conn.execute(sql_today).fetchall()

def cast_none_to_blank(item):
    """None to blank"""
    if item is None:
        return ""
    else:
        return item

def get_todays_activity(conn, conf):
    trans = get_transactions_by_date(conn)
    # deposits = get_deposits_by_date(conn)
    screens.clear_screen()
    screens.print_activity_banner()
    AMOUNT = 3
    ID = 0
    TYPE = 1
    DATE = 4
    TICKER = 8
    SHARES = 5
    PRICE = 6

    print("")
    header = "{:<12}{:<12}{:<12}{:<22}{:<12}{:<12}{:<12}".format("id", "type", "amount", "date", "ticker", "shares", "price")
    print(header)
    print("-" * 90)
    arr = []
    for row in trans:
        # print(row)
        if row[TYPE] == "BANK":
            _type = "DEPOSIT"
        else:
            _type = row[TYPE]
        s = "{:<12}{:<12}{:<12}{:<22}{:<12}{:<12}{:<12}".format(
                row[ID],
                _type,
                row[AMOUNT],
                row[DATE],
                cast_none_to_blank(row[TICKER]),
                cast_none_to_blank(row[SHARES]),
                cast_none_to_blank(row[PRICE]))

        arr.append({
           'id':row[ID],
           'type': _type,
           'amount':row[AMOUNT],
           'date':row[DATE],
           'ticker':cast_none_to_blank(row[TICKER]),
           'shares':cast_none_to_blank(row[SHARES]),
           'price':cast_none_to_blank(row[PRICE])})

        print(s)
        # format_activity(conn, row)
    ans = input("\r\n[M]enu [E]xport total activity >> ")
    if ans == 'E' or ans == 'e':
        import csv
        headers = ['id', 'type', 'amount', 'date', 'ticker', 'shares', 'price']
        with open(conf['report_location'], 'w') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(arr)
            if conf['is_prod'] == True:
                input(" exported ")
    screens.clear_screen()
