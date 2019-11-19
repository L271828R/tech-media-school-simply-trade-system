import sys
import argparse
from com.print_screens import screens
from com.core.simply_core import create_connection
from com.core.simply_core import get_portfolio_value
from com.core.simply_core import get_cash_balance
from com.core.simply_core import deposit_screen
from com.core.simply_core import enter_prices
from com.core.simply_core import get_todays_activity
from com.core.simply_core import trade_screen
from com.core.eod_lib import run_eod
from com.core.portfolio_libs import get_portfolio
from com.core.portfolio_libs import portfolio_screen

def run(conf):
    conn = create_connection(conf)
    with conn:
        while(True):
            screens.clear_screen()
            portfolio_value = get_portfolio_value(conn)
            cash_balance = get_cash_balance(conn)
            screens.print_banner("Simply Trade v.1")
            screens.print_options_screen(cash_balance, portfolio_value)
            print("")
            print("-------------------------------")
            ans = input(">> ")
            if ans == "1":
                trade_screen(conn, conf)
            elif ans == "2":
                get_todays_activity(conn, conf)
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


if __name__ == '__main__':
    conf = {
            'db_location':"db/trade.db",
            'report_location':'reports/report.csv',
            'cash_validation':True,
            'is_prod':True
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--cash_validation")
    parser.add_argument("--is_prod")
    args = vars(parser.parse_args(sys.argv[1:]))
    if args['cash_validation'] is not None:
        conf['cash_validation'] = args['cash_validation']
    if args['is_prod'] is not None:
        conf['is_prod'] = args['is_prod']
    run(conf)



