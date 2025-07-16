# daily_scanner.py

"""
Daily ETF Strategy Scanner

This script runs once a day to scan the ETF universe against all seven trading
strategies. It identifies new entry signals and checks the status of existing
positions for exit or scale-in opportunities.

The output is a comprehensive CSV report detailing all findings for the day.
V4: Reads a two-column (Ticker, Strategy) live portfolio CSV.
"""

import pandas as pd
import json
import logging
import os
from datetime import datetime
from tqdm import tqdm

from data_manager import DataManager
from utils.financial_calculations import calculate_indicators

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
LIVE_PORTFOLIO_PATH = "data/live_portfolio.csv"

STRATEGY_MAP = {
    "3_day_hl": {
        "func": check_three_day_hl_conditions,
        "indicators": ["SMA_5"],
        "entry_desc": "3 consecutive lower highs/lows (long) or higher highs/lows (short)"
    },
    "rsi_25_75": {
        "func": check_rsi_25_75_conditions,
        "indicators": ["RSI_4"],
        "entry_desc": "RSI(4) < 25 (long) or > 75 (short)"
    },
    "r3": {
        "func": check_r3_conditions,
        "indicators": ["RSI_2"],
        "entry_desc": "RSI(2) drops 3 days & < 10 (long) or rises 3 days & > 90 (short)"
    },
    "percent_b": {
        "func": check_percent_b_conditions,
        "indicators": ["%b"],
        "entry_desc": "%b < 0.2 for 3 days (long) or > 0.8 for 3 days (short)"
    },
    "mdd_mdu": {
        "func": check_mdd_mdu_conditions,
        "indicators": ["SMA_5"],
        "entry_desc": "4 of 5 last days close lower (long) or higher (short)"
    },
    "rsi_10_6_90_94": {
        "func": check_rsi_10_6_90_94_conditions,
        "indicators": ["RSI_2", "SMA_5"],
        "entry_desc": "RSI(2) < 10 (long) or > 90 (short)"
    },
    "tps": {
        "func": check_tps_conditions,
        "indicators": ["RSI_2"],
        "entry_desc": "RSI(2) < 25 for 2 days (long) or > 75 for 2 days (short)"
    },
}

# --- Helper Functions ---

def load_etf_universe(filepath: str) -> list[str]:
    """Loads the list of ETF symbols from a CSV file."""
    if not os.path.exists(filepath):
        logging.error(f"ETF universe file not found at {filepath}.")
        return []
    return pd.read_csv(filepath)['Symbol'].tolist()

def load_live_portfolio_from_csv(filepath: str) -> dict:
    """
    Loads the live portfolio state from a CSV file and converts it to a dictionary.
    """
    if not os.path.exists(filepath):
        pd.DataFrame(columns=[
            "Ticker", "Strategy", "Side", "EntryDate", "EntryPrice", "TranchesFilled"
        ]).to_csv(filepath, index=False)
        return {}
    
    try:
        df = pd.read_csv(filepath)
        portfolio_dict = {}
        for index, row in df.iterrows():
            # Create the composite key that the rest of the script uses
            key = f"{row['Ticker']}_{row['Strategy']}"
            # Store the rest of the row's data as the value
            portfolio_dict[key] = row.to_dict()
        return portfolio_dict
    except Exception as e:
        logging.error(f"Error loading portfolio from {filepath}: {e}")
        return {}


def run_daily_scanner():
    """Main function to run the daily strategy scanner."""
    logging.info("Starting Daily ETF Scanner...")
    
    etf_symbols = load_etf_universe(ETF_UNIVERSE_PATH)
    if not etf_symbols:
        logging.critical("No ETFs to scan. Exiting.")
        return

    live_portfolio = load_live_portfolio_from_csv(LIVE_PORTFOLIO_PATH)
    data_manager = DataManager()
    scan_results = []

    for symbol in tqdm(etf_symbols, desc="Scanning ETFs"):
        historical_data = data_manager.get_historical_data(symbol, period="1y")
        if len(historical_data) < 200:
            logging.warning(f"Insufficient data for {symbol} (need 200 days). Skipping.")
            continue

        data_with_indicators = calculate_indicators(historical_data)
        latest_data = data_with_indicators.iloc[-1]
        
        for strategy_name, strategy_info in STRATEGY_MAP.items():
            strategy_func = strategy_info["func"]
            portfolio_key = f"{symbol}_{strategy_name}"
            position = live_portfolio.get(portfolio_key, {})

            # The TPS strategy is stateful and requires the position dictionary
            if strategy_name == 'tps':
                # Reformat the position dictionary slightly for the TPS function
                tps_position_state = {
                    'is_open': bool(position),
                    'side': position.get('Side'),
                    'tranches_filled': position.get('TranchesFilled', 0),
                    'last_entry_price': position.get('EntryPrice', 0.0)
                }
                signals = strategy_func(data_with_indicators, tps_position_state)
            else:
                signals = strategy_func(data_with_indicators)

            result_row = {
                "Date": datetime.now().strftime('%Y-%m-%d'),
                "Symbol": symbol,
                "Strategy": strategy_name,
                "Current Price": round(latest_data['Close'], 2),
                "Signal Type": "None",
                "Status": "No Signal",
                "Entry Price": "N/A",
                "Entry Condition": strategy_info["entry_desc"],
                "Exit Condition/Value": "N/A",
                "Key Indicator Value": "N/A"
            }

            primary_indicator = strategy_info["indicators"][0]
            if primary_indicator in latest_data:
                result_row["Key Indicator Value"] = f"{primary_indicator}: {round(latest_data[primary_indicator], 2)}"

            if not position: # If position is an empty dictionary, no trade is open
                if signals.get('long_entry') or signals.get('long_signal') or signals.get('long_initial_entry'):
                    result_row["Status"] = "TRIGGERED"
                    result_row["Signal Type"] = "Long Entry"
                    result_row["Entry Price"] = round(latest_data['Close'], 2)
                elif signals.get('short_entry') or signals.get('short_signal') or signals.get('short_initial_entry'):
                    result_row["Status"] = "TRIGGERED"
                    result_row["Signal Type"] = "Short Entry"
                    result_row["Entry Price"] = round(latest_data['Close'], 2)
            
            else: # A position exists for this key
                result_row["Status"] = "HOLDING"
                result_row["Signal Type"] = f"Holding {position['Side'].upper()}"
                result_row["Entry Price"] = position['EntryPrice']
                
                if (position['Side'] == 'long' and signals.get('long_exit')) or \
                   (position['Side'] == 'short' and signals.get('short_exit')):
                    result_row["Status"] = "EXIT SIGNAL"
                    result_row["Signal Type"] = f"Exit {position['Side'].upper()}"
                
                elif (position['Side'] == 'long' and signals.get('long_aggressive_entry')) or \
                     (position['Side'] == 'short' and signals.get('short_aggressive_entry')):
                    result_row["Status"] = "AGGRESSIVE ENTRY"
                    result_row["Signal Type"] = f"Scale-In {position['Side'].upper()}"

            if "SMA_5" in strategy_info["indicators"]:
                result_row["Exit Condition/Value"] = f"Close vs SMA_5: {round(latest_data['SMA_5'], 2)}"
            elif "RSI_4" in strategy_info["indicators"]:
                result_row["Exit Condition/Value"] = "RSI(4) > 55 (long) or < 45 (short)"
            elif "RSI_2" in strategy_info["indicators"]:
                 result_row["Exit Condition/Value"] = "RSI(2) > 70 (long) or < 30 (short)"
            elif "%b" in strategy_info["indicators"]:
                 result_row["Exit Condition/Value"] = "%b > 0.8 (long) or < 0.2 (short)"
            
            scan_results.append(result_row)

    results_df = pd.DataFrame(scan_results)
    today_str = datetime.now().strftime('%Y-%m-%d')
    output_path = f"data/daily_scan_results_{today_str}.csv"
    results_df.to_csv(output_path, index=False)

    logging.info(f"Daily scan complete. Results saved to {output_path}")

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    run_daily_scanner()