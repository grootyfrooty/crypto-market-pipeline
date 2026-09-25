CREATE TABLE crypto_snap_shots (
    id SERIAL PRIMARY KEY,
    coin_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    current_price NUMERIC NOT NULL,
    market_cap NUMERIC NOT NULL,
    market_cap_rank INT NOT NULL,
    total_volume NUMERIC NOT NULL,
    price_change_percentage_24h NUMERIC,
    last_updated TIMESTAMP,
    fetched_at TIMESTAMP
);