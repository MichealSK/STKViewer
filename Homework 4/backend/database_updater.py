import sqlite3
import os
from datetime import datetime, timedelta
from data_scraper import get_stock_data
from data_retriever import date_file_path, read_date_file


def store_data(issuer_code, cleaned_data):
    conn_store = sqlite3.connect('stocks_history.db')
    cursor_store = conn_store.cursor()
    columns = ["date", "last_price", "max", "min", "avg", "change", "volume", "best_turnover", "total_turnover"]

    for record in cleaned_data:
        values = [issuer_code] + [record[column] for column in columns]
        cursor_store.execute(''' 
                INSERT OR IGNORE INTO stocks_history (Symbol, Date, Last_Trade_Price, Max, Min, Average_Price, Change, Volume, Best_Turnover, Total_Turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', values)
    conn_store.commit()


def update_last_date():
    today = datetime.now().date()
    if not os.path.exists(date_file_path): last_date = today.replace(year=today.year-11)
    else: last_date = read_date_file()

    if (today - last_date).days < 365: last_date = today;
    else: last_date = last_date + timedelta(days=364)

    with open(date_file_path, "w") as file:
        file.write(last_date.strftime("%m/%d/%Y"))


def get_and_store_data(start_date, end_date, symbols):
    for symbol in symbols:
        raw_data = get_stock_data(symbol, start_date, end_date)
        if raw_data:
            store_data(symbol, raw_data)
        print(f"CONTINUE: {start_date} for {symbol}")