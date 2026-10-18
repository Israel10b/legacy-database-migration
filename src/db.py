import os

import pymysql
from dotenv import load_dotenv

#Read the settings from .env file into the environment
load_dotenv()

def get_connection():
    """Open a connection to the MySQL database using settings from .env."""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )

if __name__ == "__main__":
    # Quick test: connect and list the tables
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        print(cursor.fetchall())
    conn.close()