# strategies/three_day_hl.py

"""
Implements the 3-Day High/Low trading strategy from the book "High Probability ETF Trading"
by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Union

def check_three_day_hl_conditions(data: pd.DataFrame) -> Dict[str, Union[bool, str]]:
    """
    Checks the conditions for the 3-Day High/Low trading strategy.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'High', 'Low', 'Close',
                             'SMA_200', and 'SMA_5'.

    Returns:
        Dict[str, Union[bool, str]]: A dictionary containing the results of the condition checks.
                                     'long_signal': True if long conditions are met, False otherwise.
                                     'short_signal': True if short conditions are met, False otherwise.
                                     'status': A message indicating the outcome of the checks.
    """
    # Ensure the DataFrame has enough data
    if len(data) < 4:
        return {"long_signal": False, "short_signal": False, "status": "Insufficient data"}

    # Get the most recent data
    latest = data.iloc[-1]
    prev_1 = data.iloc[-2]
    prev_2 = data.iloc[-3]
    prev_3 = data.iloc[-4]

    # Long side rules
    long_trend = latest['Close'] > latest['SMA_200']
    long_pullback = latest['Close'] < latest['SMA_5']
    lower_highs = latest['High'] < prev_1['High'] and prev_1['High'] < prev_2['High'] and prev_2['High'] < prev_3['High']
    lower_lows = latest['Low'] < prev_1['Low'] and prev_1['Low'] < prev_2['Low'] and prev_2['Low'] < prev_3['Low']

    if long_trend and long_pullback and lower_highs and lower_lows:
        return {"long_signal": True, "short_signal": False, "status": "Long signal detected"}

    # Short side rules
    short_trend = latest['Close'] < latest['SMA_200']
    short_rally = latest['Close'] > latest['SMA_5']
    higher_highs = latest['High'] > prev_1['High'] and prev_1['High'] > prev_2['High'] and prev_2['High'] > prev_3['High']
    higher_lows = latest['Low'] > prev_1['Low'] and prev_1['Low'] > prev_2['Low'] and prev_2['Low'] > prev_3['Low']

    if short_trend and short_rally and higher_highs and higher_lows:
        return {"short_signal": True, "long_signal": False, "status": "Short signal detected"}

    return {"long_signal": False, "short_signal": False, "status": "No signal"}
