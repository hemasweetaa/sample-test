import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('');
    const [prediction, setPrediction] = useState(null);
    const [historicalData, setHistoricalData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handlePredict = async () => {
        if (!ticker) {
            setError('Please enter a stock ticker.');
            return;
        }
        setLoading(true);
        setError('');
        setPrediction(null);
        setHistoricalData([]);

        try {
            const response = await axios.post('http://127.0.0.1:5000/predict', { ticker });
            setPrediction(response.data.prediction);
            setHistoricalData(response.data.historical_data);
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while fetching the prediction.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <h1>StockPred 📈</h1>
            <div className="input-form">
                <input
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                    placeholder="Enter Stock Ticker (e.g., AAPL)"
                />
                <button onClick={handlePredict} disabled={loading}>
                    {loading ? 'Predicting...' : 'Predict'}
                </button>
            </div>

            {error && <p className="error">{error}</p>}

            {prediction !== null && (
                <div className="result">
                    <h2>Predicted Next Day's Close Price for {ticker}:</h2>
                    <p className="prediction-value">${prediction.toFixed(2)}</p>
                </div>
            )}

            {historicalData.length > 0 && (
                 <div style={{ width: '100%', height: 400, marginTop: '30px' }}>
                     <ResponsiveContainer>
                         <LineChart data={historicalData}>
                             <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                             <XAxis dataKey="Date" stroke="#ccc" />
                             <YAxis stroke="#ccc" domain={['dataMin - 10', 'dataMax + 10']} />
                             <Tooltip contentStyle={{ backgroundColor: '#222', border: '1px solid #444' }} />
                             <Legend />
                             <Line type="monotone" dataKey="Close" stroke="#03dac5" strokeWidth={2} dot={false} />
                         </LineChart>
                     </ResponsiveContainer>
                 </div>
            )}
        </div>
    );
}

export default App;