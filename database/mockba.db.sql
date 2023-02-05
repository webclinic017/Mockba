BEGIN TRANSACTION;
DROP TABLE IF EXISTS "t_login";
CREATE TABLE IF NOT EXISTS "t_login" (
	"id"	INTEGER NOT NULL,
	"token"	INTEGER NOT NULL,
	PRIMARY KEY("token")
);
DROP TABLE IF EXISTS "t_api";
CREATE TABLE IF NOT EXISTS "t_api" (
	"id"	INTEGER NOT NULL,
	"api_key"	TEXT NOT NULL,
	"api_secret"	TEXT NOT NULL,
	"token"	INTEGER NOT NULL,
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "t_pair_spot";
CREATE TABLE IF NOT EXISTS "t_pair_spot" (
	"id"	INTEGER NOT NULL,
	"pair"	TEXT NOT NULL,
	"token"	INTEGER NOT NULL,
	"percentage"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE
);
DROP TABLE IF EXISTS "t_signal";
CREATE TABLE IF NOT EXISTS "t_signal" (
	"status"	INTEGER NOT NULL,
	"token"	INTEGER NOT NULL,
	"pair"	TEXT,
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE,
	PRIMARY KEY("status","token")
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
	"trend"	TEXT NOT NULL,
	"token"	INTEGER NOT NULL,
	"pair"	TEXT,
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE
);
DROP TABLE IF EXISTS "t_pair";
CREATE TABLE IF NOT EXISTS "t_pair" (
	"id"	INTEGER NOT NULL,
	"pair"	TEXT NOT NULL,
	"token"	INTEGER NOT NULL,
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "trend";
CREATE TABLE IF NOT EXISTS "trend" (
	"id"	INTEGER NOT NULL,
	"trend"	INTEGER NOT NULL,
	"downtrend"	INTEGER NOT NULL DEFAULT 0,
	"uptrend"	INTEGER NOT NULL DEFAULT 0,
	"token"	INTEGER NOT NULL,
	"pair"	TEXT NOT NULL,
	"timeframe"	TEXT NOT NULL,
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "parameters";
CREATE TABLE IF NOT EXISTS "parameters" (
	"trend"	TEXT NOT NULL,
	"margingsell"	NUMERIC NOT NULL,
	"margingbuy"	NUMERIC NOT NULL,
	"takeprofit"	INTEGER NOT NULL,
	"stoploss"	INTEGER NOT NULL,
	"id"	INTEGER NOT NULL,
	"token"	TEXT NOT NULL,
	"pair"	TEXT NOT NULL,
	"timeframe"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("token") REFERENCES "t_login"("token") ON DELETE CASCADE
);
DROP TRIGGER IF EXISTS "delete_before_insert_parameters";
CREATE TRIGGER delete_before_insert_parameters
BEFORE INSERT ON parameters
BEGIN
  DELETE FROM parameters
  WHERE trend = new.trend 
  and token = new.token
  and pair = new.pair
  and timeframe = new.timeframe;
END;
COMMIT;
