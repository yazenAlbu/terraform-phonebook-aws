import os
import time

import pymysql
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "autocommit": True,
}


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS phonebook (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    number VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_person_name (name)
);
"""


SEED_DATA = [
    ("ahmed ali", "0301234567"),
    ("sara hassan", "017612345678"),
    ("john smith", "015212345678"),
]


for attempt in range(1, 31):
    try:
        connection = pymysql.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)

            cursor.executemany(
                """
                INSERT IGNORE INTO phonebook (name, number)
                VALUES (%s, %s);
                """,
                SEED_DATA,
            )

        connection.close()
        print("Database initialized successfully.")
        break

    except pymysql.MySQLError as error:
        print(f"Database attempt {attempt} failed: {error}")
        time.sleep(5)

else:
    raise SystemExit("Database initialization failed.")