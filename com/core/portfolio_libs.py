from com.sql_templates import sql as sql_t
from com.print_screens import screens


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