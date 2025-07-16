# tests/test_e2e_strategies.py

"""
End-to-end test script for evaluating all trading strategies across the ETF universe.

This script simulates the behavior of each strategy over historical data, tracks a
hypothetical portfolio with dynamic P&L, and logs all trades and their performance.
V3: Adds a tqdm progress bar for better status tracking.
"""

import pandas as pd
import json
import logging
import os
from datetime import datetime
from typing import Dict
from tqdm import tqdm

# Adjust path to import from the root directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_manager import DataManager
from utils.financial_calculations import calculate_indicators
from configs.ibkr_config import PORTFOLIO_VALUE_USD, RISK_PER_TRADE_PERCENT

# --- Import all strategy functions ---
from strategies.three_day_hl import check_three_day_hl_conditions
from strategies.rsi_25_75 import check_rsi_25_75_conditions
from strategies.r3_strategy import check_r3_conditions
from strategies.percent_b_strategy import check_percent_b_conditions
from strategies.mdd_mdu import check_mdd_mdu_conditions
from strategies.rsi_10_6_90_94 import check_rsi_10_6_90_94_conditions
from strategies.tps_strategy import check_tps_conditions

# --- Configure Logging ---
logger = logging.getLogger(__name__)

# --- Constants ---
ETF_UNIVERSE_PATH = "configs/etf_universe.csv"
PORTFOLIO_STATE_PATH = "data/test_portfolio.json"
SIGNAL_LOG_PATH = "data/test_results.csv"
TRADE_LOG_PATH = "data/trade_log.csv"
EQUITY_CURVE_LOG_PATH = "data/equity_curve.csv"

STRATEGY_MAP = {
    "3_day_hl": check_three_day_hl_conditions,
    "rsi_25_75": check_rsi_25_75_conditions,
    "r3": check_r3_conditions,
    "percent_b": check_percent_b_conditions,
    "mdd_mdu": check_mdd_mdu_conditions,
    "rsi_10_6_90_94": check_rsi_10_6_90_94_conditions,
    "tps": check_tps_conditions,
}

# --- Helper Functions ---

def load_etf_universe(filepath: str) -> list[str]:
    """Loads the list of ETF symbols from a CSV file."""
    if not os.path.exists(filepath):
        logging.error(f"ETF universe file not found at {filepath}.")
        return []
    df = pd.read_csv(filepath)
    return df['Symbol'].tolist()

def load_portfolio_state(filepath: str) -> dict:
    """Loads the portfolio state from a JSON file."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def save_portfolio_state(filepath: str, state: dict):
    """Saves the portfolio state to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(state, f, indent=4)

def initialize_log_files():
    """Creates the header for the CSV log files if they don't exist."""
    if not os.path.exists(SIGNAL_LOG_PATH):
        pd.DataFrame(columns=[
            "Timestamp", "Symbol", "Strategy", "Signal", "Price", "Details"
        ]).to_csv(SIGNAL_LOG_PATH, index=False)

    if not os.path.exists(TRADE_LOG_PATH):
        pd.DataFrame(columns=[
            "Symbol", "Strategy", "Side", "EntryDate", "EntryPrice",
            "ExitDate", "ExitPrice", "Quantity", "P&L"
        ]).to_csv(TRADE_LOG_PATH, index=False)
        
    if not os.path.exists(EQUITY_CURVE_LOG_PATH):
        pd.DataFrame(columns=[
            "Date", "Strategy", "PortfolioValue"
        ]).to_csv(EQUITY_CURVE_LOG_PATH, index=False)

def log_signal(symbol: str, strategy: str, price: float, signals: dict):
    """Logs generated signals to the results CSV file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    true_signals = {k: v for k, v in signals.items() if isinstance(v, bool) and v}
    if true_signals:
        details = json.dumps(true_signals)
        new_log = pd.DataFrame([[timestamp, symbol, strategy, "Signal Found", price, details]],
                               columns=["Timestamp", "Symbol", "Strategy", "Signal", "Price", "Details"])
        new_log.to_csv(SIGNAL_LOG_PATH, mode='a', header=False, index=False)

def log_trade(trade_details: dict) -> float:
    """Logs a completed trade and returns the P&L."""
    pnl = 0
    if trade_details['Side'] == 'long':
        pnl = (trade_details['ExitPrice'] - trade_details['EntryPrice']) * trade_details['Quantity']
    else: # short
        pnl = (trade_details['EntryPrice'] - trade_details['ExitPrice']) * trade_details['Quantity']

    trade_details['P&L'] = round(pnl, 2)
    new_log = pd.DataFrame([trade_details])
    new_log.to_csv(TRADE_LOG_PATH, mode='a', header=False, index=False)
    return pnl

def log_equity_curve(date: str, strategy: str, portfolio_value: float):
    """Logs the portfolio value for a given strategy on a specific date."""
    new_log = pd.DataFrame([[date, strategy, portfolio_value]],
                           columns=["Date", "Strategy", "PortfolioValue"])
    new_log.to_csv(EQUITY_CURVE_LOG_PATH, mode='a', header=False, index=False)

def calculate_position_size(price: float, portfolio_value: float) -> int:
    """Calculates share quantity based on the CURRENT portfolio value."""
    if price <= 0:
        return 0
    trade_unit_value = portfolio_value * (RISK_PER_TRADE_PERCENT / 100)
    return int(trade_unit_value / price)

# --- Main Test Runner ---

def run_e2e_test():
    """Main function to run the end-to-end strategy test."""
    logging.info("Starting E2E Strategy Test with Dynamic P&L...")
    initialize_log_files()

    etf_symbols = load_etf_universe(ETF_UNIVERSE_PATH)
    if not etf_symbols:
        logging.critical("No ETFs to test. Exiting.")
        return

    portfolio_state = load_portfolio_state(PORTFOLIO_STATE_PATH)
    data_manager = DataManager()
    
    portfolio_values = {strategy: PORTFOLIO_VALUE_USD for strategy in STRATEGY_MAP}

    # --- Main Progress Bar for ETFs ---
    for symbol in tqdm(etf_symbols, desc="Processing ETFs"):
        historical_data = data_manager.get_historical_data(symbol, period="5y")
        if historical_data.empty:
            logging.warning(f"Could not get data for {symbol}. Skipping.")
            continue
        data_with_indicators = calculate_indicators(historical_data)

        # --- Nested Progress Bar for Strategies ---
        for strategy_name in tqdm(STRATEGY_MAP.keys(), desc=f"Testing {symbol} Strategies", leave=False):
            strategy_func = STRATEGY_MAP[strategy_name]
            
            for i in range(1, len(data_with_indicators)):
                daily_data_slice = data_with_indicators.iloc[:i+1]
                current_day = daily_data_slice.iloc[-1]
                current_price = current_day['Close']
                current_date = current_day.name.strftime('%Y-%m-%d')

                portfolio_key = f"{symbol}_{strategy_name}"
                position = portfolio_state.get(portfolio_key, {})

                if strategy_name == 'tps':
                    signals = strategy_func(daily_data_slice, position)
                else:
                    signals = strategy_func(daily_data_slice)

                log_signal(symbol, strategy_name, current_price, signals)

                if position.get('is_open'):
                    exit_signal = (position['side'] == 'long' and signals.get('long_exit')) or \
                                  (position['side'] == 'short' and signals.get('short_exit'))

                    if exit_signal:
                        trade = {
                            "Symbol": symbol, "Strategy": strategy_name,
                            "Side": position['side'], "EntryDate": position['entry_date'],
                            "EntryPrice": position['entry_price'], "ExitDate": current_date,
                            "ExitPrice": current_price, "Quantity": position['quantity']
                        }
                        pnl = log_trade(trade)
                        portfolio_values[strategy_name] += pnl
                        log_equity_curve(current_date, strategy_name, portfolio_values[strategy_name])
                        del portfolio_state[portfolio_key]

                elif not position.get('is_open'):
                    side = None
                    if signals.get('long_entry') or signals.get('long_signal') or signals.get('long_initial_entry'):
                        side = 'long'
                    elif signals.get('short_entry') or signals.get('short_signal') or signals.get('short_initial_entry'):
                        side = 'short'

                    if side:
                        quantity = calculate_position_size(current_price, portfolio_values[strategy_name])
                        if quantity > 0:
                            portfolio_state[portfolio_key] = {
                                "is_open": True, "side": side, "entry_date": current_date,
                                "entry_price": current_price, "quantity": quantity,
                                "tranches_filled": 1
                            }
    
    save_portfolio_state(PORTFOLIO_STATE_PATH, portfolio_state)
    logging.info("E2E Strategy Test Finished.")
    logging.info(f"Final Portfolio Values: {json.dumps(portfolio_values, indent=4)}")
    logging.info(f"Portfolio state saved to {PORTFOLIO_STATE_PATH}")
    logging.info(f"Trade logs saved to {TRADE_LOG_PATH}")
    logging.info(f"Equity curve logs saved to {EQUITY_CURVE_LOG_PATH}")

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    run_e2e_test()

