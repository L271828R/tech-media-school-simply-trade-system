import sqlite3
from datetime import datetime as dt
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
from com.sql_templates import sql as sql_t



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
                trade_screen(conn, conf)
            elif ans == "2":
                get_todays_activity(conn)
            elif ans == "3":
                deposit_screen(conn)
            elif ans == "4":
                portfolio_screen(conn)
            elif ans == "5":
                enter_prices(conn)
            elif ans == "6":
                run_eod(conn, conf)
            elif ans == "7":
                exit()

def get_highest_date_from_open_prices(arr):
    dt_hightest = None
    for i, item in enumerate(arr):
        if i == 0:
            dt_hightest = dt.strptime(item['date'], "%Y-%m-%d")
        dt_temp = dt.strptime(item['date'], "%Y-%m-%d")
        if dt_temp > dt_hightest:
            dt_hightest = dt_temp
    return dt_hightest

def eod_date_validation(open_prices, date_for_eod, ans):
    dt_highest_date = get_highest_date_from_open_prices(open_prices)
    str_highest_date = dt_highest_date.strftime('%Y-%m-%d')
    date_for_eod = dt.strptime(ans, "%Y-%m-%d")
    dt_diff = date_for_eod - dt_highest_date 
    if not dt_diff.days > 0:
        raise Exception(f"{ans} needs to be bigger than {str_highest_date}")
    return True



def run_eod(conn, conf):
    print_banner("EOD Screen")
    open_prices = print_open_prices(conn)
    print("Enter a future date for EOD in YYYY-MM-DD format or E[x]it")
    print("All open positions will have the entered date as EOD")
    date_for_eod = None
    while(True):
        try:
            if conf['is_prod'] == True:
                ans = input(">>")
            else:
                ans = conf['ans']
            date_for_eod = dt.strptime(ans, "%Y-%m-%d")
            if ans == 'x' or ans == 'X':
                return False
            eod_date_validation(open_prices, date_for_eod, ans)
            break
        except KeyboardInterrupt as err:
            exit()
        except Exception as err:
            print(err)
            print("please enter a valid date")
    print(date_for_eod)
    # TODO get open positions and make all dates and prices eod.
    arr = get_list_of_open_positions_for_eod(conn)
    for item in arr:
        print(item)
        ticker =item['ticker']
        price, _type, _, _id = get_last_price_type_date_id_by_ticker(conn, ticker)
        set_eod_for_ticker(conn, ticker, price, date_for_eod)
    if conf['is_prod'] == True:
        input()
    return True

def set_eod_for_ticker(conn, ticker, price,  date):
    sdate = date.strftime('%Y-%m-%d')
    # TAG
    EOD_TYPE_ID = 3
    ticker_id = get_ticker_id(conn, ticker)
    sql_template = """ INSERT INTO prices (ticker_id, price, price_date, price_type_id) VALUES (__TICKER_ID__, __PRICE__, '__PRICE_DATE__', __PRICE_TYPE_ID__);"""
    sql = sql_template.replace('__TICKER_ID__', ticker_id)
    sql = sql.replace('__PRICE__', str(price))
    sql = sql.replace('__PRICE_DATE__', sdate)
    sql = sql.replace('__PRICE_TYPE_ID__', str(EOD_TYPE_ID))
    print(sql)
    conn.execute(sql)
    conn.commit()


def run_alerts(conn):
    print('Alerts')

def get_last_price_type_date_id_by_ticker(conn, ticker):
    sql_template = sql_t.get_last_price_type_date_id_by_ticker
    sql = sql_template.replace('__TICKER__', ticker)
    # print(' get last price =', sql)
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    return result 

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



def print_banner(title="None"):
    screens.clear_screen()
    _padding = (20 - len(title))
    padding = ""
    if _padding > 0: 
        padding = " " * _padding
    print("*" * 55)
    print(f"***               {title}{padding}              ***")
    print("*" * 55)
    print("")


def get_list_of_open_positions_for_eod(conn):
    portfolio = get_portfolio(conn)
    arr = []
    for i, row in enumerate(portfolio):
        ticker = row['ticker']
        last_price, price_type, date, _ = get_last_price_type_date_id_by_ticker(conn, ticker)
        arr.append({'ticker': ticker, 'type':price_type, 'date': date})
    return arr

def print_open_prices(conn):
    portfolio = get_portfolio(conn)
    s = "{:<5}{:<10}{:<15}{:<10}{:<10}".format("#", "ticker", "last price", "source", "date")
    print(s)
    arr = []
    for i, row in enumerate(portfolio):
        ticker = row['ticker']
        last_price, price_type, date, id = get_last_price_type_date_id_by_ticker(conn, ticker)
        arr.append({'ticker':ticker,
         'last_price':last_price,
         'price_type':price_type,
         'id':id,
         'date': date})
        print(f"{i:<5}{ticker:<10}{last_price:<15}{price_type:<10}{date:<10}")
    print("")
    print("----------------------")
    return arr

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

# class NoInventoryError(Exception):
#     pass


# class NotEnoughSharesException(Exception):
#     pass

class ActionType:
    BUY = 'BUY'
    SELL = 'SELL'

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

def get_pricing_type(conn, action):
    sql_select_price_types_template = sql_t.sql_select_price_types_template
    sql = ""
    if action == ActionType.BUY:
        sql = sql_select_price_types_template.replace('__NAME__', "FROM_BUY")
    elif action == ActionType.SELL:
        sql = sql_select_price_types_template.replace('__NAME__', "FROM_SALE")

    cursor = conn.execute(sql)
    result = cursor.fetchone()
    return result[0]

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
        date = dt.now().strftime("%Y-%m-%d")

    transaction_id = insert_transaction(conn, ticker, shares, price, date, action)
    add_to_pricing_table(conn, action, price, ticker, transaction_id, date) 
    amount = shares * price
    move_cash(conn, amount, action, transaction_id)
    return True

def transaction(conn, conf, ticker, shares, price, action, date=dt.now().strftime("%Y-%m-%d")):
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
        ticker = input('please enter symbol ').upper()
        if ticker.isalpha():
            break
        else:
            print("")
            print("please enter letters only")
    shares = int(input('please enter shares '))
    action = enter_trade_action("please enter [b]uy or [s]ell ", ActionType)
    price = float(input('please enter price '))
    action = parse_action(action, ActionType)
    if transaction(conn, conf, ticker, shares, price, action):
        print("Trade Successful")
        input("[ENTER]")
        screens.clear_screen()

class CashEntryType:
    BANK = "BANK"
    SALE = "SALE"
    PURCHASE = "PURCHASE"

def deposit(conn, amount):
    sql_deposit_template = sql_t.sql_deposit_template
    sql = sql_deposit_template.replace("__TYPE__", CashEntryType.BANK)
    sql = sql.replace("__AMOUNT__", amount)
    sql = sql.replace("__DATE__", dt.now().strftime("%Y-%m-%d"))
    # print(sql)
    conn.execute(sql)
    conn.commit()
    return True

def deposit_screen(conn):
    print(" How much would you like to deposit? ")
    ans =input()
    if ans.isnumeric():
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

def ntb(item):
    """None to blank"""
    if item is None:
        return ""
    else:
        return item

def get_todays_activity(conn):
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
    for row in trans:
        # print(row)
        if row[TYPE] == "BANK":
            _type = "DEPOSIT"
        else:
            _type = row[TYPE]
        s ="{:<12}{:<12}{:<12}{:<22}{:<12}{:<12}{:<12}".format(row[ID], _type, row[AMOUNT], row[DATE], ntb(row[TICKER]), ntb(row[SHARES]), ntb(row[PRICE]))
        print(s)
        # format_activity(conn, row)
    input("\r\n[M]enu [E]xport total activity")
    screens.clear_screen()

def get_portfolio(conn):
    sql_open_positions = sql_t.sql_open_positions
    sql_last_prices = sql_t.sql_last_prices
    sql_get_second_last_prices_template = sql_t.sql_get_second_last_prices_template
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
