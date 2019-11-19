# Description

Welcome and thank you for downloading Simply Trading,
This is a python project that simulates a stock trading environment.

# Dependencies

The program runs on Python3 and needs sqlite3.
To run tests, pytest is needed.

# MAC

for python3 kindly do:

```
brew install python
```

Mac should have a version of sqlite3 installed. But if not:

```
brew install sqlite3
```

For pytest you can run:

```
pip install pytest
```

# Windows

You will need to install Python3 from python.org.
For sqlite3 you will need to go to:

https://www.sqlite.org/download.html

Download the executable and place the path in your PATH environment
variable.


# How to install simply trading

The only step that is involved in the setup process
is setting up the database.

Assuming you installed in a folder called simply.

```
simply>> sqlite3 db/trade.db < sql_tools/seed.sql
```

This step will setup your database with the 
appropriate tables and initial data.

# Configuration

If you open simply.py in your favorite text editor
you will see the below code:

```
conf = {
        'db_location':"db/trade.db",
        'report_location':'reports/report.csv',
        'cash_validation':False,
        'is_prod':True
}
```

conf is a Python dictionary which has the locations for
the database and reports, A boolean called 'cash_validation'
is used for turning on margin trading. A boolean used to help 
testing called 'is_prod'. The 'is_prod' boolean is to bypass
manual input for automating tests.

If 'cash_validation' is set to False, then you will 
be allowed to trade any amount regardless of amount 
deposited. It should be normally set to True.


# How to run

```
python simple.py
```

You will be greeted with the following screen:

```
 ****************************************
 **  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities           $0
 Cash Balance                         $0

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 

-------------------------------
>> 
```







# How to Deposit money

Like a regular trading account. You will need to add funds
to the account.


```
 ****************************************
 **  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities           $0
 Cash Balance                         $0

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 
-------------------------------
>> 3
 How much would you like to deposit? 
1000
Amount deposited
[ENTER]
```

You are now ready for your first trade.

```

 ****************************************
 **  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities           $0
 Cash Balance                     $1,000

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 

-------------------------------
>> 
```

# First Trade

```
 ****************************************
 **  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities           $0
 Cash Balance                     $1,000

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 

-------------------------------
>> 1
please enter symbol MSFT
please enter shares 2
please enter [b]uy or [s]ell b
please enter price 33

Trade MSFT BUY 2@33.0 = $66.0
are you sure? y
```


# Activity Screen

All deposit and trades will show up here.

```
**  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities          $66
 Cash Balance                       $934

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 

-------------------------------
>> 2
```

```
 ****************************************
 **           Acivity Screen .        **  
 ****************************************

id          type        amount      date                  ticker      shares      price       
------------------------------------------------------------------------------------------
2           BUY         -66         2019-11-16 14:31:13   MSFT        2           33          
1           DEPOSIT     1000        2019-11-16                                                

[M]enu [E]xport total activity
```

# Portfolio Screen


If you enter option 4 from the main menu you will see the below.

```
TICKER      SHARES      PRICE       MARKET VALUE       CHANGE      PERCENT CHANGE
--------------------------------------------------------------------------------
MSFT        2           $33         $66                 $0           0.0%
--------------------------------------------------------------------------------
               portfolio value      $66

[ENTER]

```


# Entering prices

If you would like to update your position with current prices. 
This is the screen to do that.

In the below screens with will update the price of MSFT
from 33 to 44.

```
 ****************************************
 **  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities          $66
 Cash Balance                       $934

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 

-------------------------------
>> 5
```

```
*******************************************************
***               Price Entry                       ***
*******************************************************

#    ticker    last price     source    date      
0    MSFT      33             FROM_BUY  2019-11-16

----------------------
Enter number for ticker you want to enter prices for. [M]enu
0
Ticker Chosen MSFT
enter price
44
Enter Price Type: [E]OD [I]ntra-day
I

    For which day?
    [1] 2019-11-16
    [2] 2019-11-15

    1
[ENTER]
```

```
*******************************************************
***               Price Entry                       ***
*******************************************************

#    ticker    last price     source    date      
0    MSFT      44             INTRA_DAY 2019-11-16 14:51:01

----------------------
Enter number for ticker you want to enter prices for. [M]enu
```

# Selling shares

Just as you are able to buy shares you can sell what you have in inventory.

See the below screen:

```
****************************************
 **  Welcome to simply trade v, 1      **  
 ****************************************
 Market Value of Securities          $88
 Cash Balance                       $934

 Would you like to:

(1) Trade 
(2) Activity 
(3) Deposit Money
(4) Portfolio
(5) Enter Prices
(6) Run EOD
(7) Exit 

-------------------------------
>> 1

please enter symbol MSFT
please enter shares 1
please enter [b]uy or [s]ell s
please enter price 55

Trade MSFT SELL 1@55.0 = $55.0
are you sure? 
```

# Running EOD

EOD is a process that every trading floor and bank or any organization that does accounting
for trades needs to do.

EOD is a price you set at the end of your day. This allows you to do percentage differences
from a standard price to a standard pric which is : The price at the end of the day.


```
*******************************************************
***               EOD Screen                        ***
*******************************************************

#    ticker    last price     source    date      
0    A         3              EOD       2019-11-24
1    MSFT      44             EOD       2019-11-24

----------------------

Please enter a date that is higher than the latest date for your open positions
If you are unsure enter tomorrow's date. 'x' to exit.
Dates need to be entered in YYYY-MM-DD format.
>> 2019-11-25
```

# Sqlite3

# Database tables

if you run sqlite3 and point to the database you will be able to 
inspect the tables.

```
sqlite3 db/trade.db 
```

```
bash-3.2$ sqlite3 db/trade.db 
SQLite version 3.30.0 2019-10-04 15:03:17
Enter ".help" for usage hints.
sqlite> 
```

To inspect tables you will need to run the following command:

```
sqlite> .tables
cash_balance  price_types   tickers     
eod           prices        transactions
sqlite> 
```

it will produce the following tables:

cash_balance : This keeps a running balance of your cash position.
price_types :  A small table that defines the types of prices you place on securities.
transactions : this tracks your buys and sells
prices : this tracks the prices you lock down for securities.
eod : this table is in development. Please ignore
tickers : this defines tickers and ticker ids.


# Running a select statement on sqlite3

if you run :

```
select * from transactions;
```

you will get the follwoing:

```
sqlite> select * from transactions;
1|1|100|BUY|1|2019-11-17 15:14:14
2|1|20|BUY|3|2019-11-18 22:41:57
```

This by default is not easy to read. To have a better output do the following:

```
sqlite> .mode column
sqlite> .header on
sqlite> select * from transactions;
id          ticker_id   shares      action      price       trade_date         
----------  ----------  ----------  ----------  ----------  -------------------
1           1           100         BUY         1           2019-11-17 15:14:14
2           1           20          BUY         3           2019-11-18 22:41:57
sqlite> 
```

From above you will need to enter .mode column and .header on to get a more
detailed view.


# Running tests

From root if you run 

```
pytest
```

You will get the following output

```
bash-3.2$ pytest
================================================================= test session starts =====================================
platform darwin -- Python 3.6.9, pytest-5.2.2, py-1.8.0, pluggy-0.13.0
rootdir: /Users/luisrueda/Dropbox/scripts/simple_trading_system
plugins: xdist-1.29.0, forked-1.0.2
collected 16 items                                                                                                                                                                  

tests/test_core.py ...........                                                                                                                                                
tests/test_tooling.py .....                                                                                                                                               

================================================================== 16 passed in 1.61s =====================================
bash-3.2$ 
```

This in essence runs all the unit tests and integration tests for the system.



# please send any bugs to :

luminai@gmail.com

