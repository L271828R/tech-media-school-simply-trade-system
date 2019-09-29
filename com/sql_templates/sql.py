
get_last_price_type_date_id_by_ticker = """
        SELECT price, price_types.name, price_date, MAX(p.id) FROM 
        prices p, 
        price_types, 
        tickers 
        where 
        p.ticker_id = tickers.id 
        and 
        price_type_id = price_types.id
        and 
        tickers.ticker = '__TICKER__'
"""

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

sql_transaction_id_template = """
     SELECT max(id) FROM transactions WHERE 
        ticker_id = '__TICKER_ID__' and
        shares = __SHARES__ and
        action = '__ACTION__' and
        price = __PRICE__ and
        date(trade_date) = '__DATE__'
    """

sql_insert_transaction_template = """
        INSERT INTO transactions (ticker_id, shares, action, trade_date, price) VALUES (
        '__TICKER_ID__',
        __SHARES__,
        '__ACTION__',
        '__TRADE_DATE__',
        __PRICE__)
        """

sql_we_have_inventory_for_sale_template = """
        SELECT SUM(shares) from transactions where ticker_id = '__TICKER_ID__'
        GROUP BY shares;
        """