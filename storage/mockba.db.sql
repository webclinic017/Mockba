BEGIN TRANSACTION;
DROP TABLE IF EXISTS "t_login";
CREATE TABLE IF NOT EXISTS "t_login" (
	"id"	INTEGER NOT NULL,
	"token"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "t_signal";
CREATE TABLE IF NOT EXISTS "t_signal" (
	"status"	INTEGER NOT NULL
);
DROP TABLE IF EXISTS "parameters";
CREATE TABLE IF NOT EXISTS "parameters" (
	"trend"	TEXT NOT NULL,
	"margingsell"	NUMERIC NOT NULL,
	"margingbuy"	NUMERIC NOT NULL,
	"forcesell"	INTEGER NOT NULL,
	"stoploss"	INTEGER NOT NULL,
	"id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "trend";
CREATE TABLE IF NOT EXISTS "trend" (
	"id"	INTEGER NOT NULL,
	"trend"	INTEGER NOT NULL,
	"downtrend"	INTEGER NOT NULL DEFAULT 0,
	"uptrend"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "trader";
CREATE TABLE IF NOT EXISTS "trader" (
	"qty"	REAL NOT NULL,
	"nextOpsVal"	REAL NOT NULL,
	"nextOps"	REAL NOT NULL,
	"sellFlag"	INTEGER NOT NULL,
	"counterBuy"	INTEGER NOT NULL,
	"ops"	TEXT NOT NULL,
	"close_time"	INTEGER NOT NULL,
	"trend"	TEXT
);
DROP TABLE IF EXISTS "trader_history";
CREATE TABLE IF NOT EXISTS "trader_history" (
	"id"	INTEGER NOT NULL,
	"qty"	REAL NOT NULL,
	"nextOpsVal"	REAL NOT NULL,
	"nextOps"	REAL NOT NULL,
	"sellFlag"	INTEGER NOT NULL,
	"ops"	TEXT NOT NULL,
	"price"	REAL NOT NULL,
	"margin"	REAL NOT NULL,
	"close_time"	INTEGER NOT NULL,
	"trend"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TRIGGER IF EXISTS "trg_parameters";
CREATE TRIGGER trg_parameters
BEFORE insert on parameters
BEGIN
delete from parameters where trend = new.trend;
end;
DROP TRIGGER IF EXISTS "trg_trend";
CREATE TRIGGER trg_trend
BEFORE insert on trend
BEGIN
delete from trend;
end;
DROP TRIGGER IF EXISTS "trg_trader";
CREATE TRIGGER trg_trader BEFORE insert on trader BEGIN delete from trader; end;
COMMIT;
