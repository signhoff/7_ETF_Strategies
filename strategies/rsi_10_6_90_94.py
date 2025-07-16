# strategies/rsi_10_6_90_94.py

"""
Implements the RSI 10/6 & RSI 90/94 trading strategy from the book
"High Probability ETF Trading" by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Union

def check_rsi_10_6_90_94_conditions(data: pd.DataFrame) -> Dict[str, Union[bool, str]]:
    """
    Checks the conditions for the RSI 10/6 & RSI 90/94 trading strategy.

    This function identifies initial entry, a second-tier entry, and exit signals
    for both long and short positions based on extreme readings of a 2-period RSI.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'Close',
                             'SMA_200', 'SMA_5', and 'RSI_2' (2-period RSI).

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing boolean flags for each
                                     potential trading signal and a status message.
    """
    # Initialize default return values
    signals = {
        "long_initial_entry": False,
        "long_second_entry": False,
        "long_exit": False,
        "short_initial_entry": False,
        "short_second_entry": False,
        "short_exit": False,
        "status": "No signal"
    }

    # Ensure the DataFrame has enough data and the required columns
    required_columns = ['Close', 'SMA_200', 'SMA_5', 'RSI_2']
    if len(data) < 1 or not all(col in data.columns for col in required_columns):
        signals["status"] = "Insufficient data or missing columns"
        return signals

    # Get the most recent data point
    latest = data.iloc[-1]

    # --- Long Side Conditions (RSI 10/6) ---
    is_uptrend = latest['Close'] > latest['SMA_200']

    if is_uptrend:
        # Initial Entry: 2-period RSI closes under 10
        if latest['RSI_2'] < 10:
            signals["long_initial_entry"] = True
            signals["status"] = "Long initial entry signal detected"

        # Second Entry: 2-period RSI closes under 6
        if latest['RSI_2'] < 6:
            signals["long_second_entry"] = True
            signals["status"] = "Long second entry signal detected"

    # Exit for Longs: ETF closes above its 5-day SMA
    if latest['Close'] > latest['SMA_5']:
        signals["long_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Long exit signal detected"


    # --- Short Side Conditions (RSI 90/94) ---
    is_downtrend = latest['Close'] < latest['SMA_200']

    if is_downtrend:
        # Initial Entry: 2-period RSI closes above 90
        if latest['RSI_2'] > 90:
            signals["short_initial_entry"] = True
            signals["status"] = "Short initial entry signal detected"

        # Second Entry: 2-period RSI closes above 94
        if latest['RSI_2'] > 94:
            signals["short_second_entry"] = True
            signals["status"] = "Short second entry signal detected"

    # Exit for Shorts: ETF closes below its 5-day SMA
    if latest['Close'] < latest['SMA_5']:
        signals["short_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Short exit signal detected"

    return signals
