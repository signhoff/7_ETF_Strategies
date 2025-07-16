# strategies/mdd_mdu.py

"""
Implements the Multiple Days Down (MDD) & Multiple Days Up (MDU) trading strategy
from the book "High Probability ETF Trading" by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Union

def check_mdd_mdu_conditions(data: pd.DataFrame) -> Dict[str, Union[bool, str]]:
    """
    Checks the conditions for the MDD/MDU trading strategy.

    This function identifies entry and exit signals for both long and short positions.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'Close',
                             'SMA_200', and 'SMA_5'. It must contain at least 6 rows
                             of data to check the 5-day closing trend.

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

    # Data validation: Need 5 prior days + current day = 6 rows
    required_columns = ['Close', 'SMA_200', 'SMA_5']
    if len(data) < 6 or not all(col in data.columns for col in required_columns):
        signals["status"] = "Insufficient data or missing columns"
        return signals

    # Get the most recent data point
    latest = data.iloc[-1]

    # --- Long Side Conditions (MDD) ---
    is_uptrend = latest['Close'] > latest['SMA_200']
    is_below_sma5 = latest['Close'] < latest['SMA_5']

    # Entry: Check for at least 4 down closes in the last 5 days
    if is_uptrend and is_below_sma5:
        # Calculate daily changes for the last 5 periods
        closes_last_5_days = data['Close'].iloc[-5:]
        down_days = (closes_last_5_days.diff().dropna() < 0).sum()
        if down_days >= 4:
            signals["long_entry"] = True
            signals["status"] = "Long entry signal detected (MDD)"

    # Exit: Close above the 5-day SMA
    if latest['Close'] > latest['SMA_5']:
        signals["long_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Long exit signal detected"


    # --- Short Side Conditions (MDU) ---
    is_downtrend = latest['Close'] < latest['SMA_200']
    is_above_sma5 = latest['Close'] > latest['SMA_5']

    # Entry: Check for at least 4 up closes in the last 5 days
    if is_downtrend and is_above_sma5:
        closes_last_5_days = data['Close'].iloc[-5:]
        up_days = (closes_last_5_days.diff().dropna() > 0).sum()
        if up_days >= 4:
            signals["short_entry"] = True
            signals["status"] = "Short entry signal detected (MDU)"

    # Exit: Close below the 5-day SMA
    if latest['Close'] < latest['SMA_5']:
        signals["short_exit"] = True
        if signals["status"] == "No signal":
            signals["status"] = "Short exit signal detected"

    return signals
