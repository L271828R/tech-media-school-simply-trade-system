drop table if exists tickers;
drop table if exists transactions;
drop table if exists cash_balance;
drop table if exists price_types;
drop table if exists prices;
drop table if exists eod;


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
    trade_date DATE DEFAULT (DATETIME('now', 'localtime'))
);

create table eod (
    id integer not null primary key AUTOINCREMENT,
    eod_date DATE,
    market_value_of_securities NUMBER,
    cash_balance NUMBER,
    modified_date DATE DEFAULT (DATETIME('now', 'localtime'))
);

INSERT INTO eod (eod_date, market_value_of_securities, cash_balance) 
VALUES (
    DATE('now', 'localtime'),
    NULL, 
    NULL);

create table cash_balance (
    id integer not null primary key AUTOINCREMENT,
    type VARCHAR(30),
    transaction_id NUMBER,
    amount NUMBER,
    date DATE DEFAULT (DATETIME('now', 'localtime'))
);

create table price_types(
    id integer not null primary key AUTOINCREMENT,
    name varchar(30)
);

INSERT INTO price_types (name) VALUES ('FROM_SALE');
INSERT INTO price_types (name) VALUES ('FROM_BUY');
INSERT INTO price_types (name) VALUES ('EOD');
INSERT INTO price_types (name) VALUES ('INTRA_DAY');

create table prices (
    id integer not null primary key AUTOINCREMENT,
    ticker_id NUMBER,
    price NUMBER,
    price_date DATE DEFAULT (DATETIME('now', 'localtime')),
    price_type_id integer,
    transaction_id NUMBER,
    modified_date DATE DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (price_type_id) REFERENCES price_types(id)
);

