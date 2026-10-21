"""Fill the energy_trading database with realistic fake data."""
import random
from datetime import date, timedelta
from faker import Faker

from db import get_connection

# Fixed seeds = the same "random" data every run (reproducible)
Faker.seed(42)
random.seed(42)
fake = Faker("en_GB")

COMMODITIES = [
    ("Natural Gas", "MWh"),
    ("Power", "MWh"),
    ("Brent Crude", "bbl"),
    ("Coal", "tonne"),
    ("Carbon (EUA)", "tonne"),
]
DESKS = ["Gas", "Power", "Oil", "Coal", "Carbon"]
COUNTRIES = ["Ireland", "United Kingdom", "Germany", "France",
             "Netherlands", "Norway", "Spain", "Italy"]

NUM_TRADERS = 20
NUM_COUNTERPARTIES = 30

START_DATE = date(2025, 1, 1)
NUM_DAYS = 365
NUM_TRADES = 5000

BASE_PRICES = {
    "Natural Gas": 35.0,
    "Power": 80.0,
    "Brent Crude": 75.0,
    "Coal": 110.0,
    "Carbon (EUA)": 70.0,
}

DESK_FOR_COMMODITY = {
    "Natural Gas": "Gas",
    "Power": "Power",
    "Brent Crude": "Oil",
    "Coal": "Coal",
    "Carbon (EUA)": "Carbon",
}

def reset_tables(cursor):
    """Empty every table so the script can be re-run from scratch."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in ["trades", "market_prices", "traders",
                  "counterparties", "commodities"]:
        cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def seed_commodities(cursor):
    cursor.executemany(
        "INSERT INTO commodities (name, unit) VALUES (%s, %s)",
        COMMODITIES,
    )


def seed_traders(cursor):
    rows = []
    for i in range(NUM_TRADERS):
        first, last = fake.first_name(), fake.last_name()
        email = f"{first}.{last}{i}@energyco.example".lower().replace("'", "")
        rows.append((f"{first} {last}", email, random.choice(DESKS)))
    cursor.executemany(
        "INSERT INTO traders (full_name, email, desk) VALUES (%s, %s, %s)",
        rows,
    )


def seed_counterparties(cursor):
    rows = [(fake.unique.company(), random.choice(COUNTRIES))
            for _ in range(NUM_COUNTERPARTIES)]
    cursor.executemany(
        "INSERT INTO counterparties (company_name, country) VALUES (%s, %s)",
        rows,
    )


def seed_market_prices(cursor, commodity_ids):
    prices = {}
    rows = []

    for name, commodity_id in commodity_ids.items():
        price = BASE_PRICES[name]
        for i in range(NUM_DAYS):
            day = START_DATE +timedelta(days=i)
            if day.weekday() >= 5:
                continue
            price = max(1.0, price *(1+ random.gauss(0, 0.02)))
            prices[(commodity_id, day)] = round(price, 2)
            rows.append((commodity_id, day, round(price, 2)))

    cursor.executemany(
        "INSERT INTO market_prices (commodity_id, price_date, close_price) "
        "VALUES (%s, %s, %s)",
        rows,
    )
    return prices


def seed_trades(cursor, commodity_ids, prices):
    """Create trades priced close to that day's market price."""

    # 1. Group trader IDs by desk, e.g. {"Gas": [1, 4, 9], "Oil": [7], ...}
    cursor.execute("SELECT trader_id, desk FROM traders")
    traders_by_desk = {}
    for trader_id, desk in cursor.fetchall():
        traders_by_desk.setdefault(desk, []).append(trader_id)
    # Backup list of every trader, in case a desk has nobody
    all_traders = [t for ids in traders_by_desk.values() for t in ids]

    # 2. Every counterparty ID, e.g. [1, 2, ... 30]
    cursor.execute("SELECT counterparty_id FROM counterparties")
    counterparty_ids = [row[0] for row in cursor.fetchall()]

    # 3. Every day that has a market price (weekdays only), in order
    trading_days = sorted({day for (_, day) in prices})

    # 4. Build NUM_TRADES rows
    rows = []
    for _ in range(NUM_TRADES):
        name = random.choice(list(commodity_ids))
        commodity_id = commodity_ids[name]
        desk_traders = traders_by_desk.get(DESK_FOR_COMMODITY[name]) or all_traders
        day = random.choice(trading_days)
        trade_price = round(prices[(commodity_id, day)] * random.uniform(0.98, 1.02), 2)

        rows.append((
            random.choice(desk_traders),                       # trader_id
            commodity_id,                                      # commodity_id
            random.choice(counterparty_ids),                   # counterparty_id
            random.choice(["BUY", "SELL"]),                    # side
            random.choice([100, 250, 500, 1000, 2500, 5000]),  # quantity
            trade_price,                                       # price
            day,                                               # trade_date
            random.choices(["CONFIRMED", "PENDING", "CANCELLED"],
                           weights=[90, 7, 3])[0],             # status
        ))

    # 5. Insert them all at once
    cursor.executemany(
        "INSERT INTO trades (trader_id, commodity_id, counterparty_id, side, "
        "quantity, price, trade_date, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        rows,
    )


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            reset_tables(cursor)
            seed_commodities(cursor)
            seed_traders(cursor)
            seed_counterparties(cursor)

            # Get {"Natural Gas": 1, "Power": 2, ...} from the database
            cursor.execute("SELECT name, commodity_id FROM commodities")
            commodity_ids = dict(cursor.fetchall())

            # Prices first, because trades need them
            prices = seed_market_prices(cursor, commodity_ids)
            seed_trades(cursor, commodity_ids, prices)
        conn.commit()
        print("Seeded all tables.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
