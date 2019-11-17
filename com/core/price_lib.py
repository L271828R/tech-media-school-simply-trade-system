import com.sql_templates.sql as sql_t
from com.core.simply_constants import ActionType
from com.core.portfolio_libs import get_portfolio


def get_last_price_type_date_id_by_ticker(conn, ticker):
    sql_template = sql_t.get_last_price_type_date_id_by_ticker
    sql = sql_template.replace('__TICKER__', ticker)
    cursor = conn.execute(sql)
    result = cursor.fetchone()
    return result 

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