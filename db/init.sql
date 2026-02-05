-- ZenJP MVP Database Initialization
-- テーブル1: stocks (銘柄マスタ)
CREATE TABLE IF NOT EXISTS stocks (
    stock_code VARCHAR(4) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    sector_name VARCHAR(50),
    market VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- テーブル2: stock_prices (株価データ)
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    price_date DATE NOT NULL,
    open_price NUMERIC(10,2),
    high_price NUMERIC(10,2),
    low_price NUMERIC(10,2),
    close_price NUMERIC(10,2) NOT NULL,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code),
    UNIQUE (stock_code, price_date)
);

CREATE INDEX IF NOT EXISTS idx_prices_stock_date ON stock_prices(stock_code, price_date DESC);

-- テーブル3: stock_financials (財務データ)
CREATE TABLE IF NOT EXISTS stock_financials (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    fiscal_period DATE NOT NULL,
    revenue BIGINT,
    eps NUMERIC(10,2),
    bps NUMERIC(10,2),
    dividend NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code),
    UNIQUE (stock_code, fiscal_period)
);

CREATE INDEX IF NOT EXISTS idx_financials_stock ON stock_financials(stock_code, fiscal_period DESC);

-- テーブル4: daily_scores (日次スコア)
CREATE TABLE IF NOT EXISTS daily_scores (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    score_date DATE NOT NULL,
    total_score NUMERIC(5,2) NOT NULL,
    rank VARCHAR(2) NOT NULL,
    value_score NUMERIC(5,2),
    growth_score NUMERIC(5,2),
    momentum_score NUMERIC(5,2),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code),
    UNIQUE (stock_code, score_date),
    CHECK (total_score >= 0 AND total_score <= 100)
);

CREATE INDEX IF NOT EXISTS idx_scores_stock_date ON daily_scores(stock_code, score_date DESC);
CREATE INDEX IF NOT EXISTS idx_scores_date ON daily_scores(score_date DESC);

-- 初期データ投入
INSERT INTO stocks (stock_code, stock_name, sector_name, market)
VALUES 
    ('7203', 'トヨタ自動車', '輸送用機器', 'プライム'),
    ('6758', 'ソニーグループ', '電気機器', 'プライム'),
    ('9984', 'ソフトバンクグループ', '情報・通信業', 'プライム')
ON CONFLICT DO NOTHING;
