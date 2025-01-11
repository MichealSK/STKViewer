from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import sqlite3
date_file_path = "last_date.txt"


def read_date_file():
    with open(date_file_path, "r") as file:
        date_string = file.read().strip()
        return datetime.strptime(date_string, "%m/%d/%Y").date()


def get_start_end_dates():
    with open(date_file_path, "r") as file:
        date_from = read_date_file()
        return date_from, date_from + timedelta(days=364)


def get_rows_columns():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '1d')  # Default to 1 day if not provided

    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    try:
        conn = sqlite3.connect('stocks_history.db')
        cursor = conn.cursor()
        query = "SELECT * FROM stocks_history WHERE Symbol = ? ORDER BY Date DESC"
        cursor.execute(query, (symbol,))
        rows = cursor.fetchall()
        conn.close()
        columns = ["Symbol", "Date", "Last_Trade_Price", "Max", "Min", "Average_Price", "Change", "Volume", "Best_Turnover",
                   "Total_Turnover"]
        return rows, columns
    except Exception as e:
        return jsonify({"error": str(e)}), 500