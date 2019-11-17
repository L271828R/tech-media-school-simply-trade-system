
get_last_price_type_date_id_by_ticker = """
        SELECT price, price_types.name, MAX(price_date) as price_date, p.id FROM
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
        trade_date = '__DATE__'
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

sql_get_second_last_prices_template = """
    SELECT
    price,
    tickers.ticker,
    MAX(p.price_date)
    FROM prices p,
    tickers
    WHERE p.ticker_id = tickers.id
    AND
    tickers.ticker = '__TICKER__'
    AND
    p.price_date < (
        SELECT MAX(p.price_date)
        FROM prices p,
        tickers
        WHERE p.ticker_id = tickers.id
        AND
        tickers.ticker = '__TICKER__');
    """

sql_last_prices = """
    SELECT
    ticker,
    price,
    MAX(p.price_date)
    FROM prices p,
    tickers
    WHERE
    p.ticker_id = tickers.id
    GROUP BY p.ticker_id;
    """
#     SELECT ticker, price, MAX(p.price_date) FROM prices p, tickers WHERE p.ticker_id = tickers.id GROUP BY p.ticker_id;
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

sql_transactions_template = """
        SELECT
         cb.id,
         cb.type,
         cb.transaction_id,
         cb.amount,
         cb.date,
         sub.shares,
         sub.price,
         sub.trade_date,
         sub.ticker
         FROM
         cash_balance cb
         LEFT JOIN
            (
                SELECT trs.id as trans_id, *
                FROM transactions trs, tickers tks
                WHERE trs.ticker_id = tks.id
            ) sub
        ON trans_id=transaction_id
        ORDER BY cb.id DESC"""

sql_get_cash_balance = "SELECT SUM(amount) FROM cash_balance"

sql_move_cash_template = """
        INSERT INTO cash_balance
        (type, transaction_id, amount)
        VALUES
        (
            '__TYPE__',
            __TRANSACTION_ID__,
            __AMOUNT__
        )
    """

sql_deposit_template = "INSERT INTO cash_balance (type, amount, date) VALUES ('__TYPE__', __AMOUNT__, '__DATE__')"

sql_insert_into_prices_template_no_date = """
    INSERT INTO prices
    (ticker_id, price_type_id, price, transaction_id)
    values (
    __TICKER_ID__,
    __PRICE_TYPE_ID__,
    __PRICE__,
    __TRANSACTION_ID__ )
    """

sql_insert_into_prices_template_with_date = """
    INSERT INTO prices
    (ticker_id, price_type_id, price, transaction_id, price_date)
    values (
    __TICKER_ID__,
    __PRICE_TYPE_ID__,
    __PRICE__,
    __TRANSACTION_ID__,
    '__PRICE_DATE__'
     )
    """


sql_select_price_types_template = "SELECT id from price_types where name = '__NAME__'"

sql_get_shares_balance_template = "SELECT SUM(shares) FROM transactions WHERE ticker_id = '__TICKER_ID__'"

sql_get_inventory_template = """
        SELECT SUM(shares) from transactions where ticker_id = '__TICKER_ID__'
        GROUP BY shares;
        """
