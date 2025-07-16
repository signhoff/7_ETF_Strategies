# High-Probability ETF Trading Strategies

This project is a Python-based application designed to systematically implement, backtest, and trade the seven high-probability ETF trading strategies described in the book "High Probability ETF Trading" by Larry Connors and Cesar Alvarez.

---

## Features

* **Strategy Implementation**: All seven mean-reversion strategies from the book are implemented in a modular and reusable way.
* **Comprehensive Backtester**: A powerful end-to-end test script (`tests/test_e2e_strategies.py`) that simulates strategy performance over 5 years of historical data, complete with dynamic P&L tracking and equity curve generation.
* **Daily Signal Scanner**: A daily scanner (`daily_scanner.py`) that checks the entire ETF universe for new trading signals and provides a detailed report for managing open positions.
* **Live Paper Trading**: A main application (`main.py`) designed to connect to the Interactive Brokers TWS API for live paper trading of the strategies.
* **Configurable & Extensible**: The application is designed to be easily configured through simple files, allowing users to change the ETF universe, risk parameters, and strategies without modifying the core code.

---

## Project Structure

 TWS Projects - Code Prompt
Custom Gem

Of course. Here is the complete README.md file in a raw Markdown format that you can easily copy and paste.
Markdown

---

# High-Probability ETF Trading Strategies

This project is a Python-based application designed to systematically implement, backtest, and trade the seven high-probability ETF trading strategies described in the book "High Probability ETF Trading" by Larry Connors and Cesar Alvarez.

---

## Features

* **Strategy Implementation**: All seven mean-reversion strategies from the book are implemented in a modular and reusable way.
* **Comprehensive Backtester**: A powerful end-to-end test script (`tests/test_e2e_strategies.py`) that simulates strategy performance over 5 years of historical data, complete with dynamic P&L tracking and equity curve generation.
* **Daily Signal Scanner**: A daily scanner (`daily_scanner.py`) that checks the entire ETF universe for new trading signals and provides a detailed report for managing open positions.
* **Live Paper Trading**: A main application (`main.py`) designed to connect to the Interactive Brokers TWS API for live paper trading of the strategies.
* **Configurable & Extensible**: The application is designed to be easily configured through simple files, allowing users to change the ETF universe, risk parameters, and strategies without modifying the core code.

---

## Project Structure
/
├── configs/
│   ├── ibkr_config.py
│   └── etf_universe.csv
├── data/
│   ├── (generated csv and json files)
├── handlers/
│   ├── ibkr_api_wrapper.py
│   └── yfinance_handler.py
├── strategies/
│   ├── three_day_hl.py
│   ├── rsi_25_75.py
│   ├── r3_strategy.py
│   ├── percent_b_strategy.py
│   ├── mdd_mdu.py
│   ├── rsi_10_6_90_94.py
│   └── tps_strategy.py
├── tests/
│   └── test_e2e_strategies.py
├── utils/
│   ├── financial_calculations.py
│   └── logging_config.py
├── .gitignore
├── daily_scanner.py
├── data_manager.py
├── main.py
└── requirements.txt

---

## Strategies Implemented

1.  **The 3-Day High/Low Method**
2.  **RSI 25 & RSI 75**
3.  **R3 Strategy**
4.  **The %b Strategy**
5.  **Multiple Days Down (MDD) & Multiple Days Up (MDU)**
6.  **RSI 10/6 & RSI 90/94**
7.  **TPS (Time-Price-Scale-in)**

## Strategy Details

Below is a detailed breakdown of the rules for each implemented strategy. The core logic for all strategies is filtered by a long-term trend indicator: long positions are only considered if the ETF is above its 200-day SMA, and short positions are only considered if it is below.

### 1. The 3-Day High/Low Method
* **Concept**: A simple price-action strategy that identifies a three-day pattern of price exhaustion.
* **Long Side Rules**:
    * **Entry**: Buy on close if the ETF has had three consecutive days of lower highs and lower lows, and today's close is below the 5-day SMA.
    * **Aggressive Entry**: If a position is open, buy a second unit if the ETF's closing price is lower than the initial entry price.
    * **Exit**: Exit the entire position on any day the ETF's closing price is above its 5-day SMA.
* **Short Side Rules**:
    * **Entry**: Sell short on close if the ETF has had three consecutive days of higher highs and higher lows, and today's close is above the 5-day SMA.
    * **Aggressive Entry**: If a position is open, sell short a second unit if the ETF's closing price is higher than the initial entry price.
    * **Exit**: Cover the entire position on any day the ETF's closing price is below its 5-day SMA.

### 2. RSI 25 & RSI 75
* **Concept**: Uses a sensitive 4-period RSI to identify short-term overbought and oversold conditions.
* **Indicator**: 4-period RSI.
* **Long Side Rules**:
    * **Entry**: Buy when the 4-period RSI closes under 25.
    * **Aggressive Entry**: If a position is open, buy a second unit if the RSI closes under 20.
    * **Exit**: Exit when the 4-period RSI closes above 55.
* **Short Side Rules**:
    * **Entry**: Sell short when the 4-period RSI closes above 75.
    * **Aggressive Entry**: If a position is open, sell short a second unit if the RSI closes above 80.
    * **Exit**: Cover when the 4-period RSI closes under 45.

### 3. R3 Strategy
* **Concept**: Combines a persistent momentum decline with an extreme oversold reading using a highly sensitive 2-period RSI.
* **Indicator**: 2-period RSI.
* **Long Side Rules**:
    * **Entry**: Buy if the 2-period RSI has dropped for three consecutive days (starting from a value below 60) and today's RSI closes under 10.
    * **Aggressive Entry**: If a position is open, buy a second unit if the ETF's closing price is lower than the initial entry price.
    * **Exit**: Exit when the 2-period RSI closes above 70.
* **Short Side Rules**:
    * **Entry**: Sell short if the 2-period RSI has risen for three consecutive days (starting from a value above 40) and today's RSI closes above 90.
    * **Aggressive Entry**: If a position is open, sell short a second unit if the ETF's closing price is higher than the initial entry price.
    * **Exit**: Cover when the 2-period RSI closes below 30.

### 4. The %b Strategy
* **Concept**: Uses Bollinger Bands %b to identify when a price is persistently "hugging" the lower or upper band.
* **Indicator**: Bollinger Bands %b (20-period SMA, 2 standard deviations).
* **Long Side Rules**:
    * **Entry**: Buy after the daily closing %b value has been below 0.2 for three consecutive days.
    * **Aggressive Entry**: If a position is open, buy a second unit if the %b closes below 0.2 on any subsequent day.
    * **Exit**: Exit when the %b closes above 0.8.
* **Short Side Rules**:
    * **Entry**: Sell short after the daily closing %b value has been above 0.8 for three consecutive days.
    * **Aggressive Entry**: If a position is open, sell short a second unit if the %b closes above 0.8 on any subsequent day.
    * **Exit**: Cover when the %b closes below 0.2.

### 5. Multiple Days Down (MDD) & Multiple Days Up (MDU)
* **Concept**: A direct quantification of a pullback, looking for a sequence of predominantly down-days or up-days.
* **Long Side Rules (MDD)**:
    * **Entry**: Buy if the ETF has had a lower close on at least 4 of the past 5 days, and today's close is below the 5-day SMA.
    * **Aggressive Entry**: If a position is open, buy a second unit if the ETF's closing price is lower than the initial entry price.
    * **Exit**: Exit when the ETF closes above its 5-day SMA.
* **Short Side Rules (MDU)**:
    * **Entry**: Sell short if the ETF has had a higher close on at least 4 of the past 5 days, and today's close is above the 5-day SMA.
    * **Aggressive Entry**: If a position is open, sell short a second unit if the ETF's closing price is higher than the initial entry price.
    * **Exit**: Cover when the ETF closes below its 5-day SMA.

### 6. RSI 10/6 & RSI 90/94
* **Concept**: An aggressive, two-tiered strategy using extreme 2-period RSI readings for both initial and scale-in entries.
* **Indicator**: 2-period RSI.
* **Long Side Rules**:
    * **Initial Entry**: Buy when the 2-period RSI closes under 10.
    * **Second Entry**: If a position is open, buy a second unit if the RSI closes under 6.
    * **Exit**: Exit when the ETF closes above its 5-day SMA.
* **Short Side Rules**:
    * **Initial Entry**: Sell short when the 2-period RSI closes above 90.
    * **Second Entry**: If a position is open, sell short a second unit if the RSI closes above 94.
    * **Exit**: Cover when the ETF closes below its 5-day SMA.

### 7. TPS (Time-Price-Scale-in)
* **Concept**: A sophisticated strategy that synthesizes time, price, and a multi-tiered, pyramid-style scaling approach.
* **Indicator**: 2-period RSI.
* **Position Sizing**: Capital is deployed in four tranches: 10%, 20%, 30%, and 40% of the total intended position size.
* **Long Side Rules**:
    * **Tranche 1 (10%)**: Buy after the 2-period RSI closes below 25 for two consecutive days.
    * **Tranches 2, 3, 4**: On any day after the previous tranche is filled, buy the next tranche if the ETF's closing price is lower than the entry price of the most recent tranche.
    * **Exit**: Exit the entire position when the 2-period RSI closes above 70.
* **Short Side Rules**:
    * **Tranche 1 (10%)**: Sell short after the 2-period RSI closes above 75 for two consecutive days.
    * **Tranches 2, 3, 4**: On any day after the previous tranche is filled, sell short the next tranche if the ETF's closing price is higher than the entry price of the most recent tranche.
    * **Exit**: Cover the entire position when the 2-period RSI closes below 30.

## Core Features

* **Asynchronous API Handling**: Built with `asyncio` for high-performance, non-blocking interactions with real-time data sources.
* **Multi-Source Data Integration**: Includes handlers for Interactive Brokers (TWS API), Polygon.io, and yfinance, designed for easy extension.
* **Intelligent Data Caching**: The `DataManager` minimizes redundant API calls by caching historical data locally in the efficient Parquet format.
* **Modular Utilities**: A rich set of utility modules for financial calculations (e.g., Black-Scholes), performance metrics (e.g., Sharpe Ratio), and plotting.
* **Secure Configuration**: Manages API keys and sensitive settings securely through environment variables using a `.env` file.
* **Centralized Logging**: A pre-configured logging setup that provides consistent and clear output across all modules.
* **Testing Framework**: Includes a `pytest` environment with existing unit tests for core utilities, promoting a test-driven development approach.

---

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # You may need to adjust your execution policy for the current process
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    .\venv\Scripts\Activate.ps1
    ```

3.  **Install the IBKR TWS API**
    This project requires the official TWS API from Interactive Brokers. You must install it from the local source file.
    *(Instructions from your `Setup_Instructions.txt`)*
    ```bash
    python -m pip install --upgrade "C:\TWS API\source\pythonclient\dist\ibapi-10.30.1-py3-none-any.whl"
    ```

4.  **Install Python Dependencies**
    Install all required packages from the `requirements.txt` file.
    ```bash
    python -m pip install -r requirements.txt
    ```

5.  **Configure VS Code Interpreter:**
    * Use `Ctrl+Shift+P` to open the command palette.
    * Search for and select **Python: Select Interpreter**.
    * Choose the Python executable from your virtual environment (e.g., `.\venv\Scripts\python.exe`).

---

## Configuration

### 1. API Keys

This project uses a `.env` file to securely store your API keys.

1.  Create a file named `.env` in the project root directory.
2.  Add your Polygon.io API key to this file:
    ```
    POLYGON_API_KEY="YOUR_POLYGON_API_KEY_HERE"
    ```

### 2. Interactive Brokers (TWS / Gateway)

For the IBKR handlers to connect, you must have either Trader Workstation (TWS) or the IBKR Gateway running.

1.  In TWS/Gateway, go to **File > Global Configuration**.
2.  Select **API > Settings** from the left pane.
3.  Ensure **"Enable ActiveX and Socket Clients"** is checked.
4.  Make note of the **"Socket port"** number. The default is `7497` for TWS paper trading, which matches the default in `configs/ibkr_config.py`.
5.  It is recommended to add `127.0.0.1` to the list of **"Trusted IP Addresses"**.

---

## Module Usage Guide

This template is designed to be used as a collection of powerful, independent modules. You would typically import and use them in a central `main.py` application script.

### `DataManager` (Primary Historical Data Access)

The `DataManager` is the main entry point for getting historical bar data. It will automatically cache data to prevent re-calling APIs.

**Note on Polygon.io Rate Limiting:** The free tier for Polygon's API is limited to 5 calls per minute. The `DataManager` is essential for managing this, as it will only call the API for dates not present in your local cache.

```python
import asyncio
from data_manager import DataManager

async def main():
    data_manager = DataManager()

    # Get 1 year of SPY data from Polygon (will be cached locally)
    spy_data_poly = await data_manager.get_daily_stock_data(
        ticker='SPY',
        start_date='2023-01-01',
        end_date='2024-01-01',
        source='polygon'  # Specify the source
    )
    if spy_data_poly is not None:
        print("--- Polygon Data for SPY ---")
        print(spy_data_poly.tail())
```

---

### Direct Handler Usage (for non-historical data)

While the `DataManager` is best for historical bars, you can use handlers directly for other types of information.

#### `yfinance_handler.py`
The `YFinanceHandler` can be used to get fundamental company information.

```python
from handlers.yfinance_handler import YFinanceHandler

def get_info():
    yf_handler = YFinanceHandler()
    
    # Get fundamental info for a ticker
    nvda_info = yf_handler.get_ticker_info("NVDA")
    
    if nvda_info:
        market_cap = nvda_info.get("marketCap")
        sector = nvda_info.get("sector")
        print(f"\n--- Ticker Info for NVDA ---")
        print(f"Market Cap: {market_cap:,}")
        print(f"Sector: {sector}")

# To run this synchronous function:
# get_info()
```

---

### Calculation Utilities

The `utils` modules contain pure functions for analysis.

#### `options_models.py`
```python
from utils.options_models import black_scholes_price

# Calculate the price of a call option
price = black_scholes_price(S=150, K=155, T=0.25, r=0.05, sigma=0.22, option_type='call')
print(f"\nCalculated Call Price: {price:.2f}")
```

#### `performance_metrics.py`
```python
from utils.performance_metrics import calculate_sharpe_ratio
# Assuming 'spy_data_poly' is a DataFrame from the DataManager
# daily_returns = spy_data_poly['close'].pct_change().dropna()
# sharpe = calculate_sharpe_ratio(daily_returns, risk_free_rate=0.05)
# print(f"SPY Sharpe Ratio: {sharpe:.2f}")
```

## Running the Test Suite

This project uses `pytest`. To run all tests and ensure the core logic is working correctly, navigate to the project root in your terminal and simply run:

```bash
pytest
```

## Git & GitHub Workflow Guide

### Here are the standard command-line steps for managing your projects with Git and GitHub:
See what remote repository your local project is currently pointing to by running:
```bash
git remote -v
````

If applicable, remove the wrong remote link:

```bash
git remote remove origin
```

Add the correct remote URL:

```bash
git remote add origin [https://github.com/signhoff/Quantitative_Momentum](https://github.com/signhoff/Quantitative_Momentum)
```

Push to the correct repository:

```bash
git push -u origin main
```

# Guide: Creating a New GitHub Project from a Template

## Prerequisites: Install and Configure the GitHub CLI

This workflow requires the GitHub CLI (`gh`). If you haven't already, you need to install and authenticate it.

### Install the GitHub CLI

Open your VS Code terminal and run the appropriate command for your operating system. For Windows, use Winget:

```bash
winget install --id GitHub.cli
````

### Authenticate with Your GitHub Account

After installation, run the following command and follow the on-screen prompts to log in.

```bash
gh auth login
```

-----

## Step-by-Step Instructions

### Step 1: Navigate to Your Projects Directory

Before creating the project, change your terminal's location to the exact folder where you want your new project to live.

```bash
cd C:\Users\17082\Documents\TWS_Projects
```

### Step 2: Create and Clone the Repository

Use the `gh repo create` command to generate a new repository on GitHub from the template. The `--clone` flag will automatically download it into your current directory (`TWS_Projects`).

```bash
gh repo create your-new-project-name --template https://github.com/signhoff/Project_Template --public --clone
```

  - Replace `your-new-project-name` with the actual name for your new repository (e.g., `Quantitative-Momentum-V2`).
  - You can change `--public` to `--private` if you wish to make the repository private.

### Step 3: Open the Project in VS Code

Once the command finishes, your new project folder will be ready.

Navigate into the new project directory:

```bash
cd your-new-project-name
```

Open it in your current VS Code window:

```bash
code . -r
```

(The `-r` flag reuses the existing VS Code window. You can omit it to open a new window.)

-----

### Step 4: Make Changes and Push to GitHub

You are now ready to work on your code. When you want to save your progress to GitHub, follow the standard Git workflow in the terminal.

#### Stage Your Changes

This command prepares all modified files for saving.

```bash
git add .
```

#### Commit Your Changes

This command saves a snapshot of your work with a descriptive message.

```bash
git commit -m "Add initial feature or describe your changes"
```

#### Push Your Commits to GitHub

This command uploads your saved changes to your remote GitHub repository.

```bash
git push
```

Your new project is now set up correctly and any future work can be pushed directly to its own repository on GitHub.

-----

### How to Upload a Brand New Project to GitHub**

  Step 1: CD into the Project Folder
    cd "C:\Users\17082\Documents\TWS_Projects\Project_Template\"

  Step 2: Initialize Git and Make Your First "Commit"
    # 1. git init
    # 2. git add .
    # 3. git commit -m "Initial commit"

  Step 3: Create the GitHub Repository and Push
    gh repo create
    ***answer any questions***

***First-Time Setup Note:** If you ever get an `Author identity unknown` error after the `git commit` command,
run these two commands one time to set up your identity, then try the `git commit` command again:***
  `git config --global user.name "YourGitHubUsername"`
  `git config --global user.email "your_email_for_github@example.com"`
Of course, here is that text formatted in markdown.

-----

### **Push Updates to an Existing Project**

#### **Step 1: CD into Your Project Folder**

```bash
cd "C:\Users\17082\Documents\TWS_Projects\Project_Template\"
```

-----

#### **Step 2: Check the Status of Your Changes**

This is the most common command you'll use. It shows you which files you have modified, added, or deleted. Files in **red** are changes that have not yet been prepared ("staged") for the next commit.

```bash
git status
```

-----

#### **Step 3: Add Your Changes to the Staging Area**

You need to tell Git exactly which changes you want to include in the next update.

To add ALL changes you've made:

```bash
git add .
```

OR, to add changes from a specific file only:

```bash
git add "C:\Users\17082\Documents\TWS_Projects\Project_Template\[folder/file name]"
```

> After running `git add`, if you run `git status` again, you'll see the files have turned **green**. This means they are "staged" and ready to be committed.

-----

#### **Step 4: Commit Your Staged Changes**

Bundle your staged changes into a "commit" with a clear message describing what you did. Write a clear, descriptive message inside the quotes.

```bash
git commit -m "Add new feature for user profiles"
```

> **Good commit messages are very helpful\!** Examples: "Fix bug on the login page", "Update documentation for API", "Add historical data for 2024".

-----

#### **Step 5: Push Your Commit to GitHub**

This sends all of your new, committed changes from your local computer up to your GitHub repository.

```bash
git push
```

-----

### **Additional Git Commands**

```bash
# Add a remote repository named "origin"
git remote add origin https://github.com/signhoff/Project_Template.git

# Rename the current branch to "main"
git branch -M main

# Push the "main" branch to the "origin" remote and set it as the upstream branch
git push -u origin main

# Force push to the "main" branch. Be very careful with this command as it will overwrite the remote history.
git push origin main --force 
```
