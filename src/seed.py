"""Fill the energy_trading database with realistic fake data."""
import random

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

def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            reset_tables(cursor)
            seed_commodities(cursor)
            seed_traders(cursor)
            seed_counterparties(cursor)
        conn.commit()
        print("Seeded commodities, traders and counterparties.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()