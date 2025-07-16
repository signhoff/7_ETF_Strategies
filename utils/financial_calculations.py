# utils/financial_calculations.py

"""
A collection of utility functions for calculating financial technical indicators.
This version calculates indicators manually using pandas, removing the dependency
on the pandas_ta library.
"""

import pandas as pd

def calculate_sma(data: pd.Series, length: int) -> pd.Series:
    """Calculates the Simple Moving Average (SMA)."""
    return data.rolling(window=length).mean()

def calculate_rsi(data: pd.Series, length: int) -> pd.Series:
    """Calculates the Relative Strength Index (RSI)."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data: pd.Series, length: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """Calculates Bollinger Bands and the %b value."""
    middle_band = calculate_sma(data, length)
    std = data.rolling(window=length).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    percent_b = (data - lower_band) / (upper_band - lower_band)
    
    bands = pd.DataFrame({
        f'BBL_{length}_{std_dev}': lower_band,
        f'BBM_{length}_{std_dev}': middle_band,
        f'BBU_{length}_{std_dev}': upper_band,
        '%b': percent_b
    })
    return bands

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates all required technical indicators for the trading strategies.

    This function manually calculates:
    - Simple Moving Averages (SMA)
    - Relative Strength Index (RSI)
    - Bollinger Bands (%b)

    Args:
        data (pd.DataFrame): A DataFrame with historical price data, must include
                             'High', 'Low', and 'Close' columns.

    Returns:
        pd.DataFrame: The original DataFrame with added columns for each indicator.
                      Returns the original DataFrame if data is insufficient.
    """
    if 'Close' not in data.columns or data.empty:
        return data

    # Calculate indicators using our own functions
    data['SMA_5'] = calculate_sma(data['Close'], 5)
    data['SMA_200'] = calculate_sma(data['Close'], 200)
    data['RSI_2'] = calculate_rsi(data['Close'], 2)
    data['RSI_4'] = calculate_rsi(data['Close'], 4)
    
    # Calculate Bollinger Bands and %b
    bbands = calculate_bollinger_bands(data['Close'], length=20, std_dev=2.0)
    data['%b'] = bbands['%b']

    return data
