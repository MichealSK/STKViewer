import os
import requests
import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

date_file_path = "last_date.txt"
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


def get_symbols():
    url = "https://www.mse.mk/en/stats/symbolhistory/TEL"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        dropdown = soup.find("select", {"id": "Code"})
        symbols = []

        for option in dropdown.find_all("option"):
            symbol = option.get("value")
            if not any(char.isdigit() for char in symbol): symbols.append(symbol)
        return symbols
    else:
        print("Cannot reach site.")
        return []


def get_stock_data(symbol, start_date, end_date):
    url = f"https://www.mse.mk/en/stats/symbolhistory/{symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    form_data = {"FromDate": start_date, "ToDate": end_date, "Code": symbol}
    response = requests.get(url, headers, data=form_data)

    if response.status_code == 200:
        data = []
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "resultsTable"})
        if table:
            for row in table.find_all("tr")[1:]:
                entry_data = row.find_all("td")

                entry = {"date": datetime.strptime(entry_data[0].text.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")}
                prices = ["last_price", "max", "min", "avg"]
                numbers = ["change", "volume", "best_turnover", "total_turnover"]
                for i, key in zip(range(1, 5), prices):
                    entry[key] = entry_data[i].text.strip() if entry_data[i].text.strip() else "0.00"
                for i, key in zip(range(5, 9), numbers):
                    entry[key] = float(entry_data[i].text.replace(',', '')) if entry_data[i].text.strip() else 0.0

                data.append(entry)
                print(f"{symbol}: {entry}")
    else:
        print("Cannot reach site.")

    return data


def store_data(issuer_code, cleaned_data):
    columns = ["date", "last_price", "max", "min", "avg", "change", "volume", "best_turnover", "total_turnover"]

    for record in cleaned_data:
        values = [issuer_code] + [record[column] for column in columns]
        cursor.execute(''' 
            INSERT OR IGNORE INTO stocks_history (Symbol, Date, Last_Trade_Price, Max, Min, Average_Price, Change, Volume, Best_Turnover, Total_Turnover)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', values)
    conn.commit()


def read_date_file():
    with open(date_file_path, "r") as file:
        date_string = file.read().strip()
        return datetime.strptime(date_string, "%m/%d/%Y").date()


def update_last_date():
    if not os.path.exists(date_file_path): last_date = today.replace(year=today.year-11)
    else: last_date = read_date_file()

    if (today - last_date).days < 365: last_date = today;
    else: last_date = last_date + timedelta(days=364)

    with open(date_file_path, "w") as file:
        file.write(last_date.strftime("%m/%d/%Y"))


def get_start_end_dates():
    with open(date_file_path, "r") as file:
        date_from = read_date_file()
        return date_from, date_from + timedelta(days=364)


def main_pipeline():
    if not os.path.exists(date_file_path): update_last_date()
    start_date, end_date = get_start_end_dates()
    symbols = get_symbols()

    start_time = datetime.now()
    while start_date != today:
        for symbol in symbols:
            raw_data = get_stock_data(symbol, start_date, end_date)
            if raw_data:
                store_data(symbol, raw_data)
        update_last_date()
        start_date, end_date = get_start_end_dates()

    print(f"Time needed to create/adjust database: {(datetime.now() - start_time).total_seconds()} seconds")


main_pipeline()
conn.close()
