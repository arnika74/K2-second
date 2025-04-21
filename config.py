import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.environ.get("DB_PASSWORD", "arnikajain1174"),  # Use environment variable for security
    "database": "user_db"
}