import yfinance as yf
import pandas as pd
import requests
import os
import datetime
import time

# Stock symbol and Pushover credentials
symbol = "SPY"
user_key = os.environ.get("USER_KEY")
api_key = os.environ.get("API_KEY")


def send_pushover_notification(message):
    """
    Function to send a notification message via Pushover API
    """
    payload = {
        "token": api_key,
        "user": user_key,
        "message": message,
    }
    requests.post("https://api.pushover.net/1/messages.json", data=payload)


def calc_stochastic(df, n=14):
    """
    Function to calculate stochastic oscillator
    """
    # Calculate the minimum and maximum prices for the past n days
    low_min = df["Low"].rolling(n).min()
    high_max = df["High"].rolling(n).max()

    # Calculate the %K and %D values
    df["%K"] = 100 * (df["Close"] - low_min) / (high_max - low_min)
    df["%D"] = df["%K"].rolling(3).mean()

    latest_data = df.tail(1)

    if (
        latest_data["%K"].values[0] < 80
        and latest_data["%D"].values[0] < 80
        and latest_data["%K"].values[0] < latest_data["%D"].values[0]
    ):
        send_pushover_notification(f"Alert: {symbol} stock price is crossing above 20!")

    elif (
        latest_data["%K"].values[0] > 20
        and latest_data["%D"].values[0] > 20
        and latest_data["%K"].values[0] > latest_data["%D"].values[0]
    ):
        send_pushover_notification(f"Alert: {symbol} stock price is crossing below 80!")
    elif latest_data["%K"].values[0] < 20 and latest_data["%D"].values[0] < 20:
        send_pushover_notification(f"Alert: {symbol} stock price is below 20!")

    return df


def calc_rsi(data, time_window=14):
    """
    Function to calculate Relative Strength Index (RSI) of stock data
    """
    diff = data.diff(1).dropna()
    positive_diff = diff.copy()
    negative_diff = diff.copy()

    positive_diff[positive_diff < 0] = 0
    negative_diff[negative_diff > 0] = 0

    avg_gain = positive_diff.rolling(window=time_window).mean().abs()
    avg_loss = negative_diff.rolling(window=time_window).mean().abs()

    rsi = 100 - (100 / (1 + avg_gain / avg_loss))

    # Check for conditions - crossing above 70 or below 30
    latest_data = rsi.tail(1)
    last_value = latest_data.values[0]
    if last_value > 70:
        message = f"Alert: {symbol} RSI at {last_value:.2f} is overbought! Potential sell signal."
        send_pushover_notification(message)

    elif last_value < 30:
        message = f"Alert: {symbol} RSI at {last_value:.2f} is oversold! Potential buy signal."
        send_pushover_notification(message)

    return rsi


print("Starting the program...")
while True:
    current_time = datetime.datetime.now()
    if current_time.hour >= 7 and current_time.hour < 15:
        spyTicker = yf.Ticker(symbol)
        df = pd.DataFrame(spyTicker.history(period="3mo", interval="1h"))

        spy_data = calc_stochastic(df)
        rsi = calc_rsi(df["Close"])

        time.sleep(1800)  # Delay for 30 minutes
    else:
        time.sleep(1800)  # Delay for 30 minutes until the next session
