# strategies/r3_strategy.py

"""
Implements the R3 trading strategy from the book "High Probability ETF Trading"
by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Union

def check_r3_conditions(data: pd.DataFrame) -> Dict[str, Union[bool, str]]:
    """
    Checks the conditions for the R3 trading strategy.

    This function identifies entry and exit signals for both long and short positions
    based on a 2-period RSI.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'Close',
                             'SMA_200', and 'RSI_2' (2-period RSI). It must contain at
                             least 4 rows of data to check the 3-day RSI trend.

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing boolean flags for each signal
                                     and a status message.
                                     'long_entry': True if long entry conditions are met.
                                     'long_exit': True if long exit conditions are met.
                                     'short_entry': True if short entry conditions are met.
                                     'short_exit': True if short exit conditions are met.
                                     'status': A message indicating the outcome.
    """
    # Initialize default return values
    signals = {
        "long_entry": False, "long_exit": False,
        "short_entry": False, "short_exit": False,
        "status": "No signal"
    }

    # Ensure the DataFrame has enough data and the required columns
    required_columns = ['Close', 'SMA_200', 'RSI_2']
    if len(data) < 4 or not all(col in data.columns for col in required_columns):
        signals["status"] = "Insufficient data or missing columns"
        return signals

    # Get the most recent four data points for RSI trend analysis
    latest = data.iloc[-1]
    prev_1 = data.iloc[-2]
    prev_2 = data.iloc[-3]
    prev_3 = data.iloc[-4]

    # --- Long Side Conditions ---
    is_uptrend = latest['Close'] > latest['SMA_200']

    # Entry: 3-day RSI drop from below 60, ending below 10
    rsi_dropped_3_days = latest['RSI_2'] < prev_1['RSI_2'] and prev_1['RSI_2'] < prev_2['RSI_2']
    rsi_start_was_low = prev_2['RSI_2'] < 60 # Check RSI on the first day of the 3-day period
    rsi_is_oversold = latest['RSI_2'] < 10

    if is_uptrend and rsi_dropped_3_days and rsi_start_was_low and rsi_is_oversold:
        signals["long_entry"] = True
        signals["status"] = "Long entry signal detected"

    # Exit: 2-period RSI closes above 70
    if latest['RSI_2'] > 70:
        signals["long_exit"] = True
        # Note: An exit signal can occur independently of an entry signal on a given day.
        if signals["status"] == "No signal":
             signals["status"] = "Long exit signal detected"

    # --- Short Side Conditions ---
    is_downtrend = latest['Close'] < latest['SMA_200']

    # Entry: 3-day RSI rise from above 40, ending above 90
    rsi_rose_3_days = latest['RSI_2'] > prev_1['RSI_2'] and prev_1['RSI_2'] > prev_2['RSI_2']
    rsi_start_was_high = prev_2['RSI_2'] > 40 # Check RSI on the first day of the 3-day period
    rsi_is_overbought = latest['RSI_2'] > 90

    if is_downtrend and rsi_rose_3_days and rsi_start_was_high and rsi_is_overbought:
        signals["short_entry"] = True
        signals["status"] = "Short entry signal detected"

    # Exit: 2-period RSI closes below 30
    if latest['RSI_2'] < 30:
        signals["short_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Short exit signal detected"

    return signals
