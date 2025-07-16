# strategies/rsi_25_75.py

"""
Implements the RSI 25 & RSI 75 trading strategy from the book "High Probability ETF Trading"
by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Union

def check_rsi_25_75_conditions(data: pd.DataFrame) -> Dict[str, bool]:
    """
    Checks the conditions for the RSI 25 & RSI 75 trading strategy.

    This function identifies initial entry, aggressive entry, and exit signals
    for both long and short positions.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'Close',
                             'SMA_200', and 'RSI_4' (4-period RSI).

    Returns:
        Dict[str, bool]: A dictionary containing boolean flags for each condition:
                         'long_entry': Initial condition to go long.
                         'long_aggressive_entry': Condition for a second long entry.
                         'long_exit': Condition to exit a long position.
                         'short_entry': Initial condition to go short.
                         'short_aggressive_entry': Condition for a second short entry.
                         'short_exit': Condition to exit a short position.
    """
    # Ensure the DataFrame has enough data and the required columns
    required_columns = ['Close', 'SMA_200', 'RSI_4']
    if len(data) < 1 or not all(col in data.columns for col in required_columns):
        return {
            "long_entry": False, "long_aggressive_entry": False, "long_exit": False,
            "short_entry": False, "short_aggressive_entry": False, "short_exit": False,
            "status": "Insufficient data or missing columns"
        }

    # Get the most recent data
    latest = data.iloc[-1]

    # --- Long Side Conditions ---
    is_uptrend = latest['Close'] > latest['SMA_200']
    
    # Initial Long Entry: RSI(4) closes under 25 in an uptrend.
    long_entry_condition = is_uptrend and latest['RSI_4'] < 25
    
    # Aggressive Long Entry: RSI(4) closes under 20 in an uptrend.
    long_aggressive_entry_condition = is_uptrend and latest['RSI_4'] < 20
    
    # Long Exit: RSI(4) closes above 55.
    long_exit_condition = latest['RSI_4'] > 55

    # --- Short Side Conditions ---
    is_downtrend = latest['Close'] < latest['SMA_200']

    # Initial Short Entry: RSI(4) closes above 75 in a downtrend.
    short_entry_condition = is_downtrend and latest['RSI_4'] > 75

    # Aggressive Short Entry: RSI(4) closes above 80 in a downtrend.
    short_aggressive_entry_condition = is_downtrend and latest['RSI_4'] > 80

    # Short Exit: RSI(4) closes under 45.
    short_exit_condition = latest['RSI_4'] < 45

    return {
        "long_entry": long_entry_condition,
        "long_aggressive_entry": long_aggressive_entry_condition,
        "long_exit": long_exit_condition,
        "short_entry": short_entry_condition,
        "short_aggressive_entry": short_aggressive_entry_condition,
        "short_exit": short_exit_condition,
        "status": "Checks complete"
    }
