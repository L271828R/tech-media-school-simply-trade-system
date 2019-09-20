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


def print_options_screen(cash_bal):
    print(f"Cash Balance: ${cash_bal:,}")
    print("Cash Market Value of Securities:")
    print("")
    print(" Would you like to:")
    print("")
    print("(1) Trade ")
    print("(2) Activity ")
    print("(3) Deposit Money")
    print("(4) Get Reports")
    print("(5) Exit ")


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

