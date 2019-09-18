drop table if exists tickers;
drop table if exists transactions;
drop table if exists inventory;


create table tickers (
    id NUMBER not null primary key,
    ticker VARCHAR
);

create table transactions (
    id NUMBER not null primary key,
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