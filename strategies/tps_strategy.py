# strategies/tps_strategy.py

"""
Implements the TPS (Time-Price-Scale-in) trading strategy from the book
"High Probability ETF Trading" by Larry Connors and Cesar Alvarez.
"""

import pandas as pd
from typing import Dict, Any, Union

def check_tps_conditions(
    data: pd.DataFrame,
    position_state: Dict[str, Any]
) -> Dict[str, Union[bool, str, int]]:
    """
    Checks the conditions for the TPS trading strategy.

    This function requires the current position state to manage the multi-tranche
    scaling-in logic.

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, including 'Close',
                             'SMA_200', and 'RSI_2' (2-period RSI). It must contain
                             at least 2 rows of data.
        position_state (Dict[str, Any]): A dictionary describing the current position.
            Expected keys:
            'is_open' (bool): Whether a position is currently open.
            'side' (str): 'long' or 'short' if a position is open.
            'tranches_filled' (int): The number of tranches already executed.
            'last_entry_price' (float): The closing price of the last tranche entry.

    Returns:
        Dict[str, Union[bool, str, int]]: A dictionary with trading signals.
            'signal' (str): 'BUY', 'SELL_SHORT', 'EXIT_LONG', 'EXIT_SHORT', or 'HOLD'.
            'tranche_to_execute' (int): The tranche number to execute (1-4).
            'status' (str): A descriptive message of the condition met.
    """
    # Initialize default return values
    signals = {
        "signal": "HOLD",
        "tranche_to_execute": 0,
        "status": "No new signal"
    }

    # Ensure the DataFrame has enough data and the required columns
    required_columns = ['Close', 'SMA_200', 'RSI_2']
    if len(data) < 2 or not all(col in data.columns for col in required_columns):
        signals["status"] = "Insufficient data or missing columns"
        return signals

    latest = data.iloc[-1]
    prev_1 = data.iloc[-2]

    # --- Exit Conditions (checked first) ---
    if position_state.get('is_open'):
        if position_state.get('side') == 'long' and latest['RSI_2'] > 70:
            signals['signal'] = 'EXIT_LONG'
            signals['status'] = 'Long exit signal: RSI > 70'
            return signals
        if position_state.get('side') == 'short' and latest['RSI_2'] < 30:
            signals['signal'] = 'EXIT_SHORT'
            signals['status'] = 'Short exit signal: RSI < 30'
            return signals

    # --- Entry and Scale-in Conditions ---
    is_uptrend = latest['Close'] > latest['SMA_200']
    is_downtrend = latest['Close'] < latest['SMA_200']

    # --- Long Side Logic ---
    if is_uptrend:
        # Tranche 1 (Initial Entry)
        if not position_state.get('is_open'):
            rsi_below_25_2_days = latest['RSI_2'] < 25 and prev_1['RSI_2'] < 25
            if rsi_below_25_2_days:
                signals['signal'] = 'BUY'
                signals['tranche_to_execute'] = 1
                signals['status'] = 'TPS Long Tranche 1: RSI < 25 for 2 days'
                return signals
        # Scale-in Logic (Tranches 2, 3, 4)
        elif position_state.get('side') == 'long' and position_state['tranches_filled'] < 4:
            if latest['Close'] < position_state['last_entry_price']:
                next_tranche = position_state['tranches_filled'] + 1
                signals['signal'] = 'BUY'
                signals['tranche_to_execute'] = next_tranche
                signals['status'] = f"TPS Long Tranche {next_tranche}: Price below last entry"
                return signals

    # --- Short Side Logic ---
    if is_downtrend:
        # Tranche 1 (Initial Entry)
        if not position_state.get('is_open'):
            rsi_above_75_2_days = latest['RSI_2'] > 75 and prev_1['RSI_2'] > 75
            if rsi_above_75_2_days:
                signals['signal'] = 'SELL_SHORT'
                signals['tranche_to_execute'] = 1
                signals['status'] = 'TPS Short Tranche 1: RSI > 75 for 2 days'
                return signals
        # Scale-in Logic (Tranches 2, 3, 4)
        elif position_state.get('side') == 'short' and position_state['tranches_filled'] < 4:
            if latest['Close'] > position_state['last_entry_price']:
                next_tranche = position_state['tranches_filled'] + 1
                signals['signal'] = 'SELL_SHORT'
                signals['tranche_to_execute'] = next_tranche
                signals['status'] = f"TPS Short Tranche {next_tranche}: Price above last entry"
                return signals

    return signals
