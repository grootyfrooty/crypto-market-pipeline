# Crypto Market Pipeline

An automated ETL pipeline that pulls live cryptocurrency market data from the [CoinGecko API](https://www.coingecko.com/en/api), loads it into a PostgreSQL database hosted on Neon, and runs on a schedule using GitHub Actions. A Power BI dashboard on top of the data is in progress.

## Tech Stack

Python (`requests`, `psycopg2`) · PostgreSQL (Neon) · GitHub Actions · Power BI (coming soon)

## How It Works

```
CoinGecko API  →  Python script  →  PostgreSQL (Neon)  →  Power BI (coming soon)
   (extract)       (transform)          (load)              (visualize)
                        ↑
                 GitHub Actions
                 (scheduled runs)
```

1. **Extract**: `scripts/fetch_crypto_data.py` calls the CoinGecko API and fetches market data for 50 coins.
2. **Transform**: the raw response is cleaned and shaped into rows that match the database table.
3. **Load**: rows are inserted into PostgreSQL on Neon. Rows that already exist are skipped, so re-running the script doesn't create duplicates.
4. **Automate**: a GitHub Actions workflow runs the script on a schedule, so the database keeps growing without any manual work.

If CoinGecko can't be reached, the script stops with a clear error message and a non-zero exit code, so the failed run shows up in the Actions tab.

## Project Structure

```
crypto-market-pipeline/
├── .github/workflows/   # GitHub Actions workflow that runs the pipeline
├── scripts/
│   └── fetch_crypto_data.py   # extract, transform and load script
├── sql/                 # SQL for creating tables and querying the data
├── requirements.txt     # Python dependencies
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.9+
- A PostgreSQL database (this project uses a free [Neon](https://neon.tech) database)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/grootyfrooty/crypto-market-pipeline.git
   cd crypto-market-pipeline
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create the table(s) in your database by running the SQL files in the `sql/` folder.

4. Create a `.env` file in the project root with your database connection string:

   ```
   DATABASE_URL=postgresql://user:password@host/dbname
   ```

   The `.env` file is listed in `.gitignore` so your credentials are never committed.

5. Run the pipeline:

   ```bash
   python scripts/fetch_crypto_data.py
   ```

   A successful run ends with a message like `Done. Inserted 50 rows, skipped 0`.

## Automation (GitHub Actions)

The workflow in `.github/workflows/` runs the script automatically on a schedule. To use it in your own fork:

1. Go to **Settings → Secrets and variables → Actions** in your repository.
2. Add a repository secret named `DATABASE_URL` with your Neon connection string.
3. Enable GitHub Actions. You can also trigger a run manually from the **Actions** tab.

## Dependencies

| Package | Purpose |
| --- | --- |
| `requests` | Calls the CoinGecko API |
| `psycopg2-binary` | Connects to PostgreSQL |
| `python-dotenv` | Loads credentials from the `.env` file locally |

## Roadmap

- [x] Fetch market data from CoinGecko
- [x] Load data into PostgreSQL (Neon)
- [x] Schedule automatic runs with GitHub Actions
- [ ] Build a live Power BI dashboard on top of the Neon data

## Author

Built by [@grootyfrooty](https://github.com/grootyfrooty) as a data analyst/engineering portfolio project.
