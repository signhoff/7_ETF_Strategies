# config/ibkr_config.py
import logging

# No need for local logger setup anymore
logger = logging.getLogger(__name__)

# --- IBKR Connection Parameters ---
HOST = '127.0.0.1'
PORT = 7497 # 7497 for TWS Paper Trading, 7496 for TWS Live, 4002 for Gateway Paper, 4001 for Gateway Live

# --- API Call Delays & Timeouts ---
IBKR_API_DELAY_SECONDS = 0.05
IBKR_CONNECTION_TIMEOUT_SECONDS = 15
IBKR_REQUEST_TIMEOUT_SECONDS = 45

# Client IDs for main application components (e.g., GUI)
# Ensure these are unique for each concurrent connection to IBKR.
CLIENT_ID_GUI_STOCK = 101
CLIENT_ID_GUI_OPTION = 102
CLIENT_ID_GUI_GENERAL = 103  # If GUI needs another general purpose connection

# --- Logging Configuration ---
LOG_LEVEL = 'INFO'

# --- Strategy Selection ---
# Choose the strategy to run from the available keys in STRATEGY_MAP in main.py
# Options: "3_day_hl", "rsi_25_75", "r3", "percent_b", "mdd_mdu", "rsi_10_6_90_94", "tps"
a_strategy_to_run = "r3"

# --- DEPRECATED: ETF List ---
# The list of ETFs is now loaded from configs/etf_universe.csv
a_list_of_etfs = ["SPY", "QQQ", "IWM"] # This list is no longer used by main.py

# --- Portfolio and Risk Management ---
# The total value of the portfolio in USD.
PORTFOLIO_VALUE_USD = 25000.00

# The percentage of the portfolio to risk on a single "unit" of a trade.
# For example, 0.25 means 0.25% of the portfolio value.
RISK_PER_TRADE_PERCENT = 0.25