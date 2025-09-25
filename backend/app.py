from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import os

app = Flask(__name__)
CORS(app)

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:swee090104@localhost/stock_pred_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model ---
class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    ticker_symbol = db.Column(db.String(20), nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    prediction_timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# --- Load Model ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'stock_predictor.h5')
model = load_model(MODEL_PATH)
TIME_STEPS = 60

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    ticker = data.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        # --- Fetch sufficient historical data ---
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=730)  # fetch 2 years
        stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if len(stock_data) < TIME_STEPS:
            return jsonify({'error': f'Not enough historical data ({len(stock_data)} days) to predict'}), 400

        # --- Prepare Data ---
        close_data = stock_data['Close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(close_data)
        last_60_days = scaled_data[-TIME_STEPS:]
        X_pred = np.array([last_60_days])

        # --- Predict ---
        predicted_price_scaled = model.predict(X_pred)
        predicted_price = scaler.inverse_transform(predicted_price_scaled)
        final_prediction = float(predicted_price[0][0])

        # --- Save to DB ---
        new_log = Prediction(ticker_symbol=ticker, predicted_price=final_prediction)
        db.session.add(new_log)
        db.session.commit()

        # --- Prepare Historical Data Response ---
        stock_data = stock_data.reset_index()
        stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')

        # Explicitly build JSON-safe list
        historical_data_list = []
        for _, row in stock_data.iterrows():
            historical_data_list.append({
                "Date": str(row['Date']),
                "Close": float(row['Close'])
            })

        return jsonify({
            'prediction': final_prediction,
            'historical_data': historical_data_list
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
