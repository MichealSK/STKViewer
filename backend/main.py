from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from data_scraper import get_symbols
from database_main_pipeline import main_pipeline
from natural_language_analysis import get_news_sentiment
from stock_price_predictor import predict_prices
from technical_analysis import get_signal_dataframe
from data_retriever import get_rows_columns


# RETRIEVE DATA
main_pipeline()


# FRONTEND
app = Flask(__name__)
CORS(app)


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
        data = [dict(zip(columns, row)) for row in rows]
        df = get_signal_dataframe(data)
        sentiment = get_news_sentiment(symbol)
        prediction = predict_prices(df)
        df = df.fillna(0)
        df = df.replace([np.inf, -np.inf], 0)
        return jsonify({"dataframe": df.to_dict(orient='records'), "sentiment": sentiment, "prediction": prediction}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chart', methods=['GET'])
def fetch_chart_data():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '1d')  # Default to 1 day if not provided

    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    try:
        rows, columns = get_rows_columns()
        df = pd.DataFrame(rows, columns=columns)
        df = df.fillna(0)
        df = df.replace([np.inf, -np.inf], 0)
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values(by='Date', ascending=False, inplace=True)
        if interval == '1d':
            filtered_df = df.head(1)
        elif interval == '1w':
            last_week = datetime.now() - timedelta(days=7)
            filtered_df = df[df['Date'] >= last_week]
        elif interval == '1m':
            last_month = datetime.now() - timedelta(days=30)
            filtered_df = df[df['Date'] >= last_month]
        else:
            return jsonify({"error": "Invalid interval parameter"}), 400
        filtered_data = filtered_df.to_dict(orient='records')
        return jsonify({"dataframe": filtered_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
