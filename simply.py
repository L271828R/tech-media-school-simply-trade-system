from com.core.simply_core import get_cash_balance 
from com.core.simply_core import get_inventory 
from com.core.simply_core import get_portfolio 
from com.core.simply_core import get_portfolio_value 
from com.core.simply_core import trade_screen 
from com.core.simply_core import get_todays_activity
from com.core.simply_core import deposit_screen
from com.core.simply_core import portfolio_screen
from com.core.simply_core import create_connection
from com.print_screens import screens


if __name__ == '__main__':
    conf = {'db_location':"db/trade.db",
    'log_location':'logs'}
    conn = create_connection(conf)

    while(True):
        screens.clear_screen()
        portfolio_value = get_portfolio_value(conn)
        cash_balance = get_cash_balance(conn)
        screens.print_banner()
        screens.print_options_screen(cash_balance, portfolio_value)
        print("")
        ans = input()
        if ans == "1":
            trade_screen(conn)
        elif ans == "2":
            get_todays_activity(conn)
        elif ans == "3":
            deposit_screen(conn)
        elif ans == "4":
            portfolio_screen(conn)
        elif ans == "5":
            exit()

