import requests
import psycopg2
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# --- Set up logging ---
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Pipeline run started")

# --- Step 1: Fetch data from CoinGecko ---
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    logging.info(f"Fetched {len(data)} coins from CoinGecko")
except requests.exceptions.RequestException as e:
    logging.error(f"API request failed: {e}")
    raise SystemExit("Failed to fetch data from CoinGecko — stopping pipeline.")

if not data:
    logging.error("API returned an empty response")
    raise SystemExit("No data received — stopping pipeline.")

# --- Step 2: Connect to Supabase ---
conn = None
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()

    # --- Step 3: Insert each coin's data (with validation) ---
    fetched_at = datetime.now(timezone.utc)

    required_fields = ["id", "symbol", "name", "current_price", "market_cap",
                        "market_cap_rank", "total_volume", "price_change_percentage_24h", "last_updated"]

    inserted_count = 0
    skipped_count = 0

    for coin in data:
        # Check 1: are any required fields missing?
        missing = [field for field in required_fields if coin.get(field) is None]
        if missing:
            logging.warning(f"Skipping {coin.get('id', 'unknown')} — missing fields: {missing}")
            skipped_count += 1
            continue

        # Check 2: is the price a sensible positive number?
        if coin["current_price"] <= 0:
            logging.warning(f"Skipping {coin['id']} — suspicious price: {coin['current_price']}")
            skipped_count += 1
            continue

        # Passed validation — insert it
        cur.execute("""
            INSERT INTO crypto_snap_shots
            (coin_id, symbol, name, current_price, market_cap, market_cap_rank,
             total_volume, price_change_percentage_24h, last_updated, fetched_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            coin["id"], coin["symbol"], coin["name"], coin["current_price"],
            coin["market_cap"], coin["market_cap_rank"], coin["total_volume"],
            coin["price_change_percentage_24h"], coin["last_updated"], fetched_at
        ))
        inserted_count += 1

    conn.commit()
    cur.close()
    conn.close()

    logging.info(f"Pipeline run complete — inserted {inserted_count}, skipped {skipped_count}")
    print(f"Done. Inserted {inserted_count} rows, skipped {skipped_count}.")
except psycopg2.Error as e:
    logging.error(f"Database error: {e}")
    if conn:
        conn.rollback()
    raise SystemExit("Database operation failed — stopping pipeline.")
