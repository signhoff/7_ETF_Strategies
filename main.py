# main.py

"""
Main application file for the High-Probability ETF Trading Bot.

This script initializes the connection to Interactive Brokers, manages data,
runs the selected trading strategy, and executes paper trades.
"""

import time
import logging
from typing import Dict, Any

from ibapi.contract import Contract
from ibapi.order import Order

from handlers.ibkr_api_wrapper import IbkrApiWrapper
from data_manager import DataManager
from utils.financial_calculations import calculate_indicators
from configs.ibkr_config import a_list_of_etfs, a_strategy_to_run

# --- Import all strategy functions ---
from strategies.three_day_hl import check_three_day_hl_conditions
from strategies.rsi_25_75 import check_rsi_25_75_conditions
from strategies.r3_strategy import check_r3_conditions
from strategies.percent_b_strategy import check_percent_b_conditions
from strategies.mdd_mdu import check_mdd_mdu_conditions
from strategies.rsi_10_6_90_94 import check_rsi_10_6_90_94_conditions
from strategies.tps_strategy import check_tps_conditions


# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Strategy Mapping ---
STRATEGY_MAP = {
    "3_day_hl": check_three_day_hl_conditions,
    "rsi_25_75": check_rsi_25_75_conditions,
    "r3": check_r3_conditions,
    "percent_b": check_percent_b_conditions,
    "mdd_mdu": check_mdd_mdu_conditions,
    "rsi_10_6_90_94": check_rsi_10_6_90_94_conditions,
    "tps": check_tps_conditions,
}

class TradingApp:
    """
    The main application class that orchestrates the trading bot.
    """
    def __init__(self, symbols: list[str], strategy_name: str):
        self.symbols = symbols
        self.strategy_name = strategy_name
        self.strategy_func = STRATEGY_MAP.get(strategy_name)
        if not self.strategy_func:
            raise ValueError(f"Strategy '{strategy_name}' not found.")

        self.ibkr_wrapper = IbkrApiWrapper()
        self.data_manager = DataManager()
        self.position_states: Dict[str, Dict[str, Any]] = {
            symbol: {"is_open": False, "side": None, "tranches_filled": 0, "last_entry_price": 0.0}
            for symbol in self.symbols
        }

    def run(self):
        """
        The main execution loop of the trading application.
        """
        logging.info("Starting Trading Application...")
        self.ibkr_wrapper.connect("127.0.0.1", 7497, clientId=1) # Use 7497 for TWS, 4002 for IB Gateway

        # Allow time for connection to establish
        time.sleep(2)

        try:
            while True:
                for symbol in self.symbols:
                    self.process_symbol(symbol)
                # Wait for the next market data update (e.g., every 5 minutes)
                logging.info("Waiting for next cycle...")
                time.sleep(300)
        except KeyboardInterrupt:
            logging.info("Application stopped by user.")
        finally:
            self.ibkr_wrapper.disconnect()
            logging.info("Disconnected from IBKR and shut down.")

    def process_symbol(self, symbol: str):
        """
        Processes a single symbol: fetches data, checks strategy, and places orders.
        """
        logging.info(f"Processing symbol: {symbol}")

        # 1. Fetch and prepare data
        historical_data = self.data_manager.get_historical_data(symbol)
        if historical_data.empty:
            logging.warning(f"Could not retrieve historical data for {symbol}.")
            return

        data_with_indicators = calculate_indicators(historical_data)
        if data_with_indicators.empty or data_with_indicators.isnull().values.any():
            logging.warning(f"Could not calculate indicators for {symbol}. Check data integrity.")
            return

        # 2. Check strategy conditions
        position_state = self.position_states[symbol]
        
        # The TPS strategy requires the position state, others do not.
        if self.strategy_name == 'tps':
            signals = self.strategy_func(data_with_indicators, position_state)
        else:
            signals = self.strategy_func(data_with_indicators)
        
        logging.info(f"Signals for {symbol}: {signals}")

        # 3. Act on signals
        self.act_on_signals(symbol, signals)


    def act_on_signals(self, symbol: str, signals: Dict[str, Any]):
        """
        Interprets the signals from a strategy and places orders if necessary.
        """
        # This is a simplified logic handler. A real-world application would need
        # more sophisticated state management and order handling.
        
        # Example for a simple strategy (e.g., 3_day_hl)
        if signals.get("long_signal") and not self.position_states[symbol]["is_open"]:
            self.place_order(symbol, "BUY", 100) # Example quantity
            self.position_states[symbol].update({"is_open": True, "side": "long"})
        
        elif signals.get("short_signal") and not self.position_states[symbol]["is_open"]:
            self.place_order(symbol, "SELL", 100) # Example quantity
            self.position_states[symbol].update({"is_open": True, "side": "short"})

        # Logic to handle exits would be added here
        # ...

    def place_order(self, symbol: str, action: str, quantity: int):
        """
        Creates and places a market-on-close (MOC) order with IBKR.
        """
        logging.info(f"Placing {action} order for {quantity} shares of {symbol}.")

        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        order = Order()
        order.action = action
        order.orderType = "MOC" # Market-on-Close
        order.totalQuantity = quantity

        self.ibkr_wrapper.place_order(self.ibkr_wrapper.next_order_id(), contract, order)


if __name__ == "__main__":
    # --- Configuration ---
    # These would ideally be loaded from a more robust config file or environment variables
    etf_symbols_to_trade = a_list_of_etfs
    strategy_to_run = a_strategy_to_run

    app = TradingApp(symbols=etf_symbols_to_trade, strategy_name=strategy_to_run)
    app.run()
