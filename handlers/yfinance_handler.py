# handlers/yfinance_handler.py

"""
A handler to interact with the yfinance library for fetching historical market data.
"""

import pandas as pd
import yfinance as yf
import logging
from typing import Optional, Dict, Any, List

class YFinanceHandler:
    """
    A wrapper class for the yfinance library to standardize data fetching.
    """
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initializes the YFinanceHandler.

        Args:
            logger (Optional[logging.Logger]): An optional logger instance.
                                               If None, a default logger is created.
        """
        self.logger = logger or logging.getLogger(__name__)

    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical data for a given symbol from Yahoo Finance.

        Args:
            symbol (str): The ticker symbol to fetch data for.
            period (str): The period of data to fetch (e.g., "1d", "5d", "1mo", "1y", "max").
            interval (str): The data interval (e.g., "1m", "2m", "1h", "1d").

        Returns:
            pd.DataFrame: A DataFrame containing the historical data, or an empty
                          DataFrame if an error occurs.
        """
        self.logger.info(f"Fetching {period} of {interval} data for {symbol} from yfinance.")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            if data.empty:
                self.logger.warning(f"No data found for symbol {symbol} with period {period}.")
            return data
        except Exception as e:
            self.logger.error(f"An error occurred while fetching data for {symbol}: {e}")
            return pd.DataFrame()

    async def get_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously fetches ticker information.
        Note: This async method is part of the template but not used by the synchronous e2e test.
        """
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return info
        except Exception as e:
            self.logger.error(f"Error fetching info for {ticker}: {e}")
            return None

    async def _fetch_and_cache_ticker(self, ticker: str, end_date: str) -> bool:
        """
        Fetches a long history for a single ticker and saves it to a Parquet file.
        Uses a semaphore and a retry mechanism to handle network errors.
        """
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            # Use a tighter semaphore for downloads as they are more intensive
            async with asyncio.Semaphore(1):
                try:
                    ticker_data = await asyncio.to_thread(
                        yf.download,
                        ticker,
                        start=CACHE_START_DATE,
                        end=end_date,
                        auto_adjust=True,
                        progress=False,
                    )

                    if ticker_data.empty:
                        return False

                    if not ticker_data.index.is_unique:
                        logger.warning(f"Duplicate dates found for {ticker}. Keeping last.")
                        ticker_data = ticker_data[~ticker_data.index.duplicated(keep='last')]

                    file_path = os.path.join(self.cache_dir, f"{ticker}.parquet")
                    await asyncio.to_thread(ticker_data.to_parquet, file_path)
                    return True

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Could not fetch data for {ticker} after {max_retries} attempts.")
                        return False
        return False

    async def get_historical_closes(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Asynchronously fetches historical adjusted close prices for a list of tickers,
        utilizing a robust Parquet-based cache.
        """
        all_series = []
        tickers_to_fetch = [
            t for t in tickers if not os.path.exists(os.path.join(self.cache_dir, f"{t}.parquet"))
        ]
        
        if tickers_to_fetch:
            logger.info(f"Cache miss for {len(tickers_to_fetch)} tickers. Fetching now...")
            for i, ticker in enumerate(tickers_to_fetch):
                status_msg = f"--> Fetching {i + 1}/{len(tickers_to_fetch)}: {ticker.ljust(10)}"
                sys.stdout.write(f"\r{status_msg}")
                sys.stdout.flush()
                await self._fetch_and_cache_ticker(ticker, end_date)
            sys.stdout.write("\n")

        logger.info("Loading data from cache and slicing to requested date range...")
        for i, ticker in enumerate(tickers):
            status_msg = f"--> Loading ticker data {i + 1}/{len(tickers)}: {ticker.ljust(10)}"
            sys.stdout.write(f"\r{status_msg}")
            sys.stdout.flush()

            file_path = os.path.join(self.cache_dir, f"{ticker}.parquet")
            if os.path.exists(file_path):
                try:
                    data = await asyncio.to_thread(pd.read_parquet, file_path)
                    series = data["Close"].loc[start_date:end_date]
                    series.name = ticker
                    all_series.append(series)
                except Exception as e:
                    logger.error(f"Failed to read or slice cache for {ticker}: {e}")
        
        sys.stdout.write("\n")
        
        if not all_series:
            return None

        return pd.concat(all_series, axis=1)
