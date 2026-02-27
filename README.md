# PrimeTrade AI – Binance Futures Testnet Trading Bot

A simplified Python trading bot that places **Market**, **Limit**, and **Stop-type** orders on the **Binance Futures Testnet (USDT-M)**.  
Built with a clean, reusable architecture, structured logging, and full input validation.

---

## Features

- **Market & Limit orders** on Binance Futures Testnet
- **Bonus: Stop-Limit / Stop-Market / Take-Profit orders**
- **Interactive menu** with guided prompts (runs with no arguments)
- **Direct CLI** for scripted / one-shot usage
- Structured logging to both console and rotating log file
- Comprehensive input validation with clear error messages
- Separate client / orders / validators / CLI layers

---

## Project Structure

```
primetrade ai/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance REST client (auth, signing, HTTP)
│   ├── orders.py            # Order placement + response formatting
│   ├── validators.py        # Input validation helpers
│   └── logging_config.py    # Dual console + file logging setup
├── cli.py                   # CLI entry-point (Click)
├── logs/                    # Log files (auto-created)
│   └── trading_bot.log
├── .env                     # API credentials (not committed)
├── .env.example             # Template for .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Prerequisites

- **Python 3.9+** (tested on 3.11)
- A **Binance Futures Testnet** account  
  → Register at <https://testnet.binancefuture.com>

### 2. Clone & create virtual environment

```bash
git clone <repo-url>
cd "primetrade ai"

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Copy the example env file and fill in your testnet keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

> **Note:** `.env` is git-ignored and will not be committed.

---

## Usage

### Interactive Mode (guided menu)

```bash
python cli.py
```

This launches a menu with options to:
1. Place an order (with step-by-step prompts)
2. Check a symbol's current price
3. View testnet account balances
4. Exit

### Direct CLI Commands

#### Place a Market order

```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

#### Place a Limit order

```bash
python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 100000
```

#### Place a Stop-Market order (bonus)

```bash
python cli.py order --symbol ETHUSDT --side SELL --type STOP_MARKET --quantity 0.1 --stop-price 2000
```

#### Place a Stop-Limit order (bonus)

```bash
python cli.py order --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --price 90000 --stop-price 91000
```

#### Check price

```bash
python cli.py price --symbol BTCUSDT
```

#### View account balances

```bash
python cli.py account
```

---

## Example Output

### Market Order

```
────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────
  Symbol      : BTCUSDT
  Side        : BUY
  Type        : MARKET
  Quantity    : 0.01
  Price       : MARKET
  Stop Price  : N/A
────────────────────────────────────────────

╔══════════════════════════════════════════╗
║           ORDER RESPONSE                 ║
╠══════════════════════════════════════════╣
  Order ID    : 123456789
  Symbol      : BTCUSDT
  Side        : BUY
  Type        : MARKET
  Status      : FILLED
  Quantity    : 0.01
  Executed    : 0.01
  Price       : 0
  Avg Price   : 84523.50
  Stop Price  : 0
  Time        : 1740700000000
╚══════════════════════════════════════════╝
✔ Order placed successfully!
```

---

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.  
Console output shows INFO-level messages; the log file captures DEBUG-level detail.

Log format:
```
2026-02-27 10:30:00 | INFO     | bot.orders | Placing BUY MARKET order: 0.01 BTCUSDT @ MARKET (stop=N/A)
2026-02-27 10:30:01 | INFO     | bot.orders | Order response – orderId=123456789 status=FILLED executedQty=0.01 avgPrice=84523.50
```

---

## Assumptions

1. **Testnet only** – the bot targets `https://testnet.binancefuture.com`. Never point it at the production API unless you understand the risks.
2. **USDT-M Futures** – all endpoints use the `/fapi/` namespace.
3. **No position management** – this bot places orders but does not track or close positions automatically.
4. **Default Time-in-Force** – Limit orders use `GTC` (Good-Til-Cancelled) by default.
5. **Decimal precision** – the bot does not auto-adjust quantity/price to symbol step sizes. Use values that comply with the symbol's filters on the exchange.

---

## Dependencies

| Package        | Purpose                          |
| -------------- | -------------------------------- |
| requests       | HTTP client for REST API calls   |
| python-dotenv  | Load `.env` credentials          |
| click          | CLI framework                    |
| colorama       | Coloured terminal output         |

---

## License

MIT
