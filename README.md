# Description

Welcome and thank you for downloading Simply Trading,
This is a python project that simulates a stock trading environment.

# Dependencies

The program runs on Python3 and needs sqlite3.

# MAC

for python3 kindly do:

```
brew install python
```

Mac should have a version of sqlite3 installed. But if not:

```
brew install sqlite3
```

# Windows

You will need to install Python3 from python.org.
For sqlite3 you will need to go to:

http://

Download the executable and place the path in your PATH environment
variable.


# How to install

The only step that is involved in the setup process
is setting up the database.

Assuming you installed in a folder called simply.

```
simply>> sqlite3 db/trade.db < sql_tools/seed.sql
```

This step will setup your database with the 
appropriate tables and initial data.

# How to run

```
python simple.py
```

You will be created with the following screen:

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
Alerts
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
Alerts
-------------------------------
>> 3
 How much would you like to deposit? 
1000
```
Press Enter

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
Alerts
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
Alerts
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
Alerts
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
Alerts
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
Alerts
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




