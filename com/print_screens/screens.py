import os

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def print_not_enough_cash_screen(cash_bal, tran_amount):
            print("")
            print(f"You do not have enough cash ${float(cash_bal):,} for this transaction ${tran_amount:,}")
            print("")
            print("[ENTER]")
            input()
            clear_screen()

def print_trade_preview(ticker, action, price, shares, tran_amount):
    s = f"\n\rTrade {ticker} {action} {shares}@{price} = " + f"${tran_amount:,}"
    print(s)


def print_options_screen(cash_bal, port_value):
    cash_bal = int(cash_bal)
    s_port_value = f"${port_value:,}"
    s_cash_bal = f"${cash_bal:,}"
    market_value_of_securities = "{:<30}{:>10}".format(
        " Market Value of Securities",
        s_port_value
    )
    cash_balance = "{:<30}{:>10}".format(
        " Cash Balance",
        s_cash_bal
    )
    print(market_value_of_securities)
    print(cash_balance)
    print("")
    print(" Would you like to:")
    print("")
    print("(1) Trade ")
    print("(2) Activity ")
    print("(3) Deposit Money")
    print("(4) Portfolio")
    print("(5) Enter Prices")
    print("(6) Run EOD")
    print("(7) Exit ")


def print_banner():
    print()
    print(" " + ("*" * 40))
    print(""" **  Welcome to simply trade v.05      **  """)
    print(" " + ("*" * 40))

def print_not_enough_shares_screen(share_bal, shares, ticker):
    print(f"You do not have enough shares {share_bal} to sell {shares} for {ticker}")
    print()
    print("[ENTER]")
    print()
    input()

def print_activity_banner():
    print()
    print(" " + ("*" * 40))
    print(""" **           Acivity Screen .        **  """)
    print(" " + ("*" * 40))

def print_portfolio_screen(portfolio):
    columns = "{:<12}{:<12}{:<12}{:<12}".format("TICKER", "SHARES", "PRICE", "MARKET VALUE")
    clear_screen()
    print("\r\n")
    print(columns)
    print("-" * 60)
    mv = 0

    # sort by MV
    portfolio = sorted(portfolio, key=lambda x: x['market_value'], reverse=True)


    for item in portfolio:
        mv += item['market_value']
        s = "{:<12}{:<12}${:<11,}${:,}".format(
            item['ticker'],
            item['shares'],
            item['price'],
            item['market_value']
            )
        print(s)
    print("-" * 60)
    s = "{:>30}{:>7}{:,}".format("portfolio value","$", mv)
    print(s)

    print("")
    input("[ENTER]")
    clear_screen()
