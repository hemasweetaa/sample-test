import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# --- 1. Settings and Data Collection ---
TICKER = 'GOOGL'
START_DATE = '2015-01-01'
END_DATE = '2024-12-31'
TIME_STEPS = 60 # How many past days of data the model will look at

print(f"Fetching data for {TICKER}...")
data = yf.download(TICKER, start=START_DATE, end=END_DATE)
close_data = data['Close'].values.reshape(-1, 1)

# --- 2. Data Preprocessing ---
print("Preprocessing data...")
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(close_data)

X_train = []
y_train = []
for i in range(TIME_STEPS, len(scaled_data)):
    X_train.append(scaled_data[i-TIME_STEPS:i, 0])
    y_train.append(scaled_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# --- 3. Build the LSTM Model ---
print("Building the LSTM model...")
model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(units=50, return_sequences=True),
    Dropout(0.2),
    LSTM(units=50),
    Dropout(0.2),
    Dense(units=1)
])
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# --- 4. Train the Model ---
print("Training the model... (This may take a while)")
model.fit(X_train, y_train, epochs=25, batch_size=32)

# --- 5. Save the Model ---
MODEL_PATH = 'stock_predictor.h5'
model.save(MODEL_PATH)
print(f"Model saved successfully to {MODEL_PATH}")