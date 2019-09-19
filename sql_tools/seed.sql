drop table if exists tickers;
drop table if exists transactions;
drop table if exists inventory;
drop table if exists cash_balance;


create table tickers (
    id integer primary key AUTOINCREMENT,
    ticker VARCHAR,
    is_active BOOLEAN
);

create table transactions (
    id integer not null primary key AUTOINCREMENT,
    ticker_id NUMBER,
    shares NUMBER,
    action VARCHAR(30),
    price NUMBER,
    trade_date DATE
);

create table inventory (
    id NUMBER not null primary key,
    ticker_id NUMBER,
    shares NUMBER
);

create table cash_balance (
    id integer not null primary key AUTOINCREMENT,
    type VARCHAR(30),
    transaction_id NUMBER,
    amount NUMBER,
    date Date
)


