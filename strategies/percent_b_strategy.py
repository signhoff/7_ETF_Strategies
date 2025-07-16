# strategies/percent_b_strategy.py

"""
Implements the %b trading strategy from the book "High Probability ETF Trading"
by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Union

def check_percent_b_conditions(data: pd.DataFrame) -> Dict[str, Union[bool, str]]:
    """
    Checks the conditions for the %b trading strategy.

    This function identifies entry and exit signals for both long and short positions
    based on the Bollinger Bands %b indicator.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'Close',
                             'SMA_200', and '%b'. It must contain at least 3 rows
                             of data to check the 3-day %b trend.

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
    required_columns = ['Close', 'SMA_200', '%b']
    if len(data) < 3 or not all(col in data.columns for col in required_columns):
        signals["status"] = "Insufficient data or missing columns"
        return signals

    # Get the most recent three data points for %b trend analysis
    latest = data.iloc[-1]
    prev_1 = data.iloc[-2]
    prev_2 = data.iloc[-3]

    # --- Long Side Conditions ---
    is_uptrend = latest['Close'] > latest['SMA_200']

    # Entry: %b has been below 0.2 for three consecutive days in an uptrend.
    b_below_threshold_3_days = latest['%b'] < 0.2 and prev_1['%b'] < 0.2 and prev_2['%b'] < 0.2
    if is_uptrend and b_below_threshold_3_days:
        signals["long_entry"] = True
        signals["status"] = "Long entry signal detected"

    # Exit: %b closes above 0.8.
    if latest['%b'] > 0.8:
        signals["long_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Long exit signal detected"

    # --- Short Side Conditions ---
    is_downtrend = latest['Close'] < latest['SMA_200']

    # Entry: %b has been above 0.8 for three consecutive days in a downtrend.
    b_above_threshold_3_days = latest['%b'] > 0.8 and prev_1['%b'] > 0.8 and prev_2['%b'] > 0.8
    if is_downtrend and b_above_threshold_3_days:
        signals["short_entry"] = True
        signals["status"] = "Short entry signal detected"

    # Exit: %b closes below 0.2.
    if latest['%b'] < 0.2:
        signals["short_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Short exit signal detected"

    return signals
