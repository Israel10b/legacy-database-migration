USE energy_trading;

-- 1. Things being traded
CREATE TABLE commodities (
	commodity_id	INT AUTO_INCREMENT PRIMARY KEY,
    name			VARCHAR(50)   NOT NULL,
    unit			VARCHAR(20)   NOT NULL,
    created_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Employees who trade
CREATE TABLE traders (
	trader_id		INT AUTO_INCREMENT PRIMARY KEY,
    full_name		VARCHAR(100) NOT NULL,
    email			VARCHAR(100) NOT NULL UNIQUE,
    desk			VARCHAR(50)	 NOT NULL,
    created_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at		TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Companies on the other side of a trade
CREATE TABLE counterparties (
    counterparty_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name    VARCHAR(100) NOT NULL,
    country         VARCHAR(50)  NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. Each buy or sell
CREATE TABLE trades (
    trade_id        INT AUTO_INCREMENT PRIMARY KEY,
    trader_id       INT NOT NULL,
    commodity_id    INT NOT NULL,
    counterparty_id INT NOT NULL,
    side            ENUM('BUY', 'SELL') NOT NULL,
    quantity        DECIMAL(12,2) NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    trade_date      DATE NOT NULL,
    status          VARCHAR(20) DEFAULT 'CONFIRMED',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (trader_id)       REFERENCES traders(trader_id),
    FOREIGN KEY (commodity_id)    REFERENCES commodities(commodity_id),
    FOREIGN KEY (counterparty_id) REFERENCES counterparties(counterparty_id)
);

-- 5. Daily price of each commodity
CREATE TABLE market_prices (
    price_id       INT AUTO_INCREMENT PRIMARY KEY,
    commodity_id   INT NOT NULL,
    price_date     DATE NOT NULL,
    close_price    DECIMAL(10,2) NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (commodity_id) REFERENCES commodities(commodity_id),
    UNIQUE (commodity_id, price_date)
);