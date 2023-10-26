import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import pickle
import matplotlib.pyplot as plt

# Load the models and data
lr_model = pickle.load(open("/mnt/data/linear_regression_model.pkl", "rb"))
lstm_model = load_model("/mnt/data/lstm_model.h5")
with open("/mnt/data/lstm_scaler.pkl", "rb") as f:
    lstm_scaler = pickle.load(f)

data_path = "path_to_your_data.csv"  # Update with your path
nft_data = pd.read_csv(data_path)
nft_data['price_in_ether'] = nft_data['total_price'] / 1e18

# Data processing functions
def create_dataset(dataset, look_back=1):
    X, Y = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

st.title("NFT Explorer and Price Predictor")

# NFT Lookup
nft_name = st.text_input("Enter NFT name:")

if nft_name:
    selected_nft = nft_data[nft_data['asset.name'] == nft_name]
    
    if not selected_nft.empty:
        # Display NFT details
        st.image(selected_nft['asset.permalink'].iloc[0])
        st.write(f"Name: {selected_nft['asset.name'].iloc[0]}")
        st.write(f"Collection: {selected_nft['asset.collection.name'].iloc[0]}")
        st.write(f"Category: {selected_nft['Category'].iloc[0]}")
        st.write(f"Number of Sales: {selected_nft['asset.num_sales'].iloc[0]}")
        st.write(f"Last Sale Price in Ether: {selected_nft['price_in_ether'].iloc[0]}")
        
        # Linear Regression Prediction
        if st.button("Predict Price with Linear Regression"):
            price = lr_model.predict([[selected_nft['feature_column'].iloc[0]]])  # Adjust based on your feature column
            st.write(f"Predicted Price in Ether (using Linear Regression): {price[0][0]}")
        
        # LSTM Prediction
        if st.button("Predict Price with LSTM"):
            selected_prices = selected_nft.sort_values(by='sales_datetime')['price_in_ether'].values
            if len(selected_prices) > 2:  # Ensure there's enough data for prediction
                selected_prices = selected_prices.reshape(-1, 1)
                selected_prices_scaled = lstm_scaler.transform(selected_prices)
                X_lstm, _ = create_dataset(selected_prices_scaled)
                X_lstm = np.reshape(X_lstm, (X_lstm.shape[0], 1, X_lstm.shape[1]))
                predicted_price_scaled = lstm_model.predict(X_lstm)
                predicted_price = lstm_scaler.inverse_transform(predicted_price_scaled)
                st.write(f"Predicted Price in Ether (using LSTM): {predicted_price[-1][0]}")
            else:
                st.write("LSTM isn't applicable for this NFT due to insufficient transaction data.")
    else:
        st.write("NFT not found in the dataset.")
