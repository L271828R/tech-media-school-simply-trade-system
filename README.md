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








