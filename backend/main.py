import sqlite3
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from data_scraper import get_symbols
from data_retriever import get_rows_columns
from database_main_pipeline import main_pipeline
from natural_language_analysis import get_news_sentiment
from stock_price_predictor import predict_prices
from technical_analysis import get_signal_dataframe

# RETRIEVE DATA
main_pipeline()

# FRONTEND
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/symbols', methods=['GET'])
def fetch_symbols():
    symbols = get_symbols()
    return jsonify(symbols), 200

@app.route('/stocks', methods=['GET'])
def fetch_stock_data():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    try:
        rows, columns = get_rows_columns()
        print("Rows and Columns received successfully.")
        data = [dict(zip(columns, row)) for row in rows]
        print("Created Dataframe.")
        df = get_signal_dataframe(data)
        print("Created signal dataframe.")
        sentiment = get_news_sentiment(symbol)
        print("Received Sentiment.")
        prediction = predict_prices(df)
        print("Predicted Prices.")
        df = df.fillna(0)
        print("Replaced Nulls.")
        df = df.replace([np.inf, -np.inf], 0)
        print("Replaced Nulls.")
        return jsonify(
            {"dataframe": df.to_dict(orient='records'), "sentiment": sentiment, "prediction": prediction}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chart', methods=['GET'])
def fetch_chart_data():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '7')

    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    try:
        rows, columns = get_rows_columns()
        df = pd.DataFrame(rows, columns=columns)
        df = df.fillna(0)
        df = df.replace([np.inf, -np.inf], 0)
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values(by='Date', ascending=False, inplace=True)
        if interval == '7':
            filtered_df = df.head(7)
        elif interval == '30':
            filtered_df = df.head(30)
        elif interval == '60':
            filtered_df = df.head(60)
        else:
            return jsonify({"error": "Invalid interval parameter"}), 400
        filtered_data = filtered_df.to_dict(orient='records')
        return jsonify({"dataframe": filtered_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
