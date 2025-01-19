import os
import threading
import sqlite3
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, wait

from data_retriever import date_file_path, get_start_end_dates
from data_scraper import get_symbols
from database_updater import get_and_store_data, update_last_date


def main_pipeline():
    write_lock = threading.Lock()
    today = datetime.now().date()
    conn = sqlite3.connect('stocks_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks_history (
            Symbol TEXT,
            Date TEXT,
            Last_Trade_Price REAL,
            Max REAL,
            Min REAL,
            Average_Price REAL,
            Change REAL,
            Volume REAL,
            Best_Turnover REAL,
            Total_Turnover REAL,
            PRIMARY KEY (Symbol, Date)
    )''')
    conn.commit()

    if not os.path.exists(date_file_path): update_last_date()
    start_date, end_date = get_start_end_dates()
    symbols = get_symbols()
    futures = []

    start_time = datetime.now()
    with ThreadPoolExecutor() as executor:
        while start_date < today:
            with write_lock:
                print(f"Starting thread for {start_date}")
                futures.append(executor.submit(get_and_store_data, start_date, end_date, symbols))
                update_last_date()
                start_date, end_date = get_start_end_dates()
                print(f"Current Start Date: {start_date}")

    wait(futures)
    print(f"Time needed to create/adjust database: {(datetime.now() - start_time).total_seconds()} seconds")
    conn.close()
