BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "t_login" (
	"id"	INTEGER NOT NULL,
	"token"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "trader" (
	"qty"	REAL NOT NULL,
	"nextOps"	REAL NOT NULL,
	"sellFlag"	INTEGER NOT NULL,
	"counterStopLoss"	INTEGER NOT NULL,
	"counterForceSell"	INTEGER NOT NULL,
	"counterBuy"	INTEGER NOT NULL,
	"ops"	TEXT NOT NULL,
	"close_time"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "t_signal" (
	"status"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "trader_history" (
	"id"	INTEGER NOT NULL,
	"qty"	REAL NOT NULL,
	"nextOps"	REAL NOT NULL,
	"ops"	TEXT NOT NULL,
	"close_time"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "parameters" (
	"margingsell"	NUMERIC,
	"margingbuy"	NUMERIC,
	"forcesell"	INTEGER,
	"stoploss"	INTEGER
);
CREATE TABLE IF NOT EXISTS "historical_ETHUSDT" (
	"timestamp"	TEXT,
	"open"	REAL,
	"high"	REAL,
	"low"	REAL,
	"close"	REAL,
	"volume"	REAL,
	"close_time"	INTEGER,
	"quote_av"	REAL,
	"trades"	INTEGER,
	"tb_base_av"	REAL,
	"tb_quote_av"	REAL,
	"ignore"	REAL
);
CREATE INDEX IF NOT EXISTS "ix_historical_ETHUSDT_timestamp" ON "historical_ETHUSDT" (
	"timestamp"
);
CREATE TRIGGER trg_trader 
BEFORE insert on trader
BEGIN
delete from trader;
end;
CREATE TRIGGER trg_trader_history after insert on trader 
BEGIN 
 insert into trader_history
  (qty,nextOps,ops,close_time)
  VALUES
  (new.qty,new.nextOps,new.ops,new.close_time);
end;
CREATE TRIGGER trg_paramters
BEFORE insert on parameters
BEGIN
delete from parameters;
end;
COMMIT;
