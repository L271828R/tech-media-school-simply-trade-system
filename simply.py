import sqlite3
from datetime import datetime
import os


class NoInventoryError(Exception):
    pass

class UnknownActionType(Exception):
    pass

class NotEnoughSharesException(Exception):
    pass

class ActionType:
    BUY = 'BUY'
    SELL = 'SELL'


def create_connection(conf):
    return sqlite3.connect(conf['db_location'])

def get_ticker_id(conn, ticker):
    sql_templte = "SELECT id, is_active FROM tickers where ticker = '__TICKER__'"
    sql = sql_templte.replace('__TICKER__', ticker)
    result = conn.execute(sql)
    result = result.fetchone()
    if result[1] == False:
        raise Exception("This ticker has been deactivated")
    return str(result[0])

def trade(conn, ticker, shares, price, date, action):
    sql_template = """
        INSERT INTO transactions (ticker_id, shares, action, price, trade_date) VALUES (
        '__TICKER_ID__',
        __SHARES__,
        '__ACTION__',
        __PRICE__,
        '__DATE__')
        """
    sql = sql_template.replace('__TICKER_ID__', get_ticker_id(conn, ticker))
    if action == ActionType.SELL:
        sql = sql.replace('__SHARES__', str(shares * -1))
    elif action == ActionType.BUY:
        sql = sql.replace('__SHARES__', str(shares))

    sql = sql.replace('__ACTION__', str(action)) 
    sql = sql.replace('__PRICE__', str(price))
    sql = sql.replace('__DATE__', str(date))
    print('executing sql', sql)
    conn.execute(sql)
    conn.commit()

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

def print_not_enough_cash_screen(cash_bal, tran_amount):
            print("")
            print(f"You do not have enough cash ${cash_bal:,} for this transaction ${tran_amount:,}")
            print("")
            print("[ENTER]")
            input()

def print_trade_preview(ticker, action, price, shares, tran_amount):
    s = f"\n\rTrade {ticker} {action} {shares}@{price} = " + f"${tran_amount:,}"
    print(s)

def transaction(conn, ticker, shares, price, action):
    date = datetime.now().strftime("%Y-%m-%d")
    tran_amount = round(shares * price, 2)
    print_trade_preview(ticker, action, price, shares, tran_amount)

    if action == ActionType.BUY:
        cash_bal = get_cash_balance(conn)
        if cash_bal - (shares * price) < 0:
            print_not_enough_cash_screen(cash_bal, tran_amount)
            return False

    ans = input("are you sure?")
    if 'y' in ans:
        try:
            if action == ActionType.BUY:
                trade(conn, ticker, shares, price, date, action)
                return True
            elif action == ActionType.SELL and we_have_inventory_for_sale(conn, ticker, shares):
                trade(conn, ticker, shares, price, date, action)
                return True
            else:
                raise NotEnoughSharesException
        except NotEnoughSharesException:
            print("You do not have enough shares, you only have=", get_inventory(conn, ticker))

def parse_action(action):
    if 'b' in action.lower():
        action = ActionType.BUY
    elif 's' in action.lower():
        action = ActionType.SELL
    else:
        raise UnknownActionType
    return action

def create_ticker(conn, ticker):
    sql_template = "INSERT INTO tickers (ticker) VALUES ('__TICKER__');"
    sql = sql_template.replace('__TICKER__', ticker)
    conn.execute(sql)
    conn.commit()
    return True

def does_symbol_exist(conn, ticker):
    sql_template = "select ticker from tickers where ticker = '__TICKER__'"
    sql = sql_template.replace('__TICKER__', ticker)
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    if result is None:
        return False
    else:
        return True

def trade_screen(conn):
    ticker = input('please enter symbol ').upper()
    # ticker = 'SVXY'
    if not does_symbol_exist(conn, ticker):
        ans = input('symbol ' + ticker + ' does not exist. create? y/n ')
        if 'y' in ans.lower():
            create_ticker(conn, ticker)
        else:
            exit()
    shares = int(input('please enter shares '))
    action = input('please enter buy or sell ')
    price = int(input('please enter price '))
    # shares = 200
    # action = ActionType.BUY
    # action = ActionType.SELL
    # price = 1
    action = parse_action(action)
    result = transaction(conn, ticker, shares, price, action)


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
    
def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def deposit_screen(conn):
    print(" How much would you like to deposit? ")
    ans =input()
    if ans.isnumeric():
        deposit(conn, ans)
    print("Amoutn deposited")
    input("[ENTER]")
    clear_screen()


def get_cash_balance(conn):
    sql = "SELECT SUM(amount) FROM cash_balance"
    cursor = conn.execute(sql)
    res = cursor.fetchone()
    if res[0] is None:
        return "0"
    else:
        return res[0]

def print_options_screen():
    print("Cash Balance:" + str(get_cash_balance(conn)))
    print("Cash Market Value of Securities:")
    print("")
    print(" Would you like to:")
    print("")
    print("(1) Trade ")
    print("(2) Deposit Money")
    print("(3) Get Reports")
    print("(4) Exit ")

def print_banner():
    print()
    print(" " + ("*" * 40))
    print(""" **  Welcome to simply trade v.05      **  """)
    print(" " + ("*" * 40))

if __name__ == '__main__':
    conf = {'db_location':"trade.db",
    'log_location':'logs'}
    conn = create_connection(conf)
    cash_balance = get_cash_balance(conn)

    while(True):
        print_banner()
        print_options_screen()
        ans = input()
        if ans == "1":
            trade_screen(conn)
        elif ans == "2":
            deposit_screen(conn)
        elif ans == "3":
            exit()
        elif ans == "4":
            exit()

