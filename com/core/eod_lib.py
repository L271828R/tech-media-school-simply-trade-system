from com.core.price_lib import get_last_price_type_date_id_by_ticker 
from com.core.portfolio_libs import get_portfolio
from com.core.simply_core import get_ticker_id, print_open_prices
from com.print_screens.screens import print_banner
from datetime import datetime as dt

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
    conn.execute(sql)
    conn.commit()


def run_eod(conn, conf):
    eod_screen()
    open_prices = print_open_prices(conn)
    date_for_eod = None
    print("")
    print("Please enter a date that is higher than the latest date for your open positions")
    print("If you are unsure enter tomorrow's date. 'x' to exit.")
    print("Dates need to be entered in YYYY-MM-DD format.")
    while(True):
        try:
            if conf['is_prod'] == True:
                ans = input(">> ")
            else:
                ans = conf['ans']
            if ans == 'x' or ans == 'X' or ans == '':
                return False
            date_for_eod = dt.strptime(ans, "%Y-%m-%d")
            eod_date_validation(open_prices, date_for_eod, ans)
            break
        except KeyboardInterrupt as err:
            exit()
        except Exception as err:
            print(err)
            print("please enter a valid date")
    arr = get_list_of_open_positions_for_eod(conn)
    for item in arr:
        ticker =item['ticker']
        price, _type, _, _id = get_last_price_type_date_id_by_ticker(conn, ticker)
        set_eod_for_ticker(conn, ticker, price, date_for_eod)
    print("Success!")
    if conf['is_prod'] == True:
        input()
    return True

def get_list_of_open_positions_for_eod(conn):
    portfolio = get_portfolio(conn)
    arr = []
    for i, row in enumerate(portfolio):
        ticker = row['ticker']
        last_price, price_type, date, _ = get_last_price_type_date_id_by_ticker(conn, ticker)
        arr.append({'ticker': ticker, 'type':price_type, 'date': date})
    return arr

def eod_screen():
    print("Enter a future date for EOD in YYYY-MM-DD format or E[x]it")
    print("All open positions will have the entered date as EOD")
    print_banner("EOD Screen")

def eod_date_validation(open_prices, date_for_eod, ans):
    dt_highest_date = get_highest_date_from_open_prices(open_prices)
    str_highest_date = dt_highest_date.strftime('%Y-%m-%d')
    date_for_eod = dt.strptime(ans, "%Y-%m-%d")
    if not date_for_eod > dt_highest_date:
        raise Exception(f"{ans} needs to be bigger than {str_highest_date}")
    return True


def get_highest_date_from_open_prices(arr):
    dt_hightest = None
    dt_temp = None
    for i, item in enumerate(arr):
        if i == 0:
            if len(item['date']) > 10:
                dt_hightest = dt.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
            else:
                dt_hightest = dt.strptime(item['date'], "%Y-%m-%d")
        if len(item['date']) > 10:
            dt_temp = dt.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
        else:
            dt_temp = dt.strptime(item['date'], "%Y-%m-%d")
        if dt_temp > dt_hightest:
            dt_hightest = dt_temp
    return dt_hightest