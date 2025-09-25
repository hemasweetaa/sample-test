-- Create a new database for our application
CREATE DATABASE IF NOT EXISTS stock_pred_db;

-- Switch to the new database
USE stock_pred_db;

-- Create the table to store prediction logs
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker_symbol VARCHAR(10) NOT NULL,
    predicted_price FLOAT NOT NULL,
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);