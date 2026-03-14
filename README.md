# Simplified Trading Bot - Binance Futures Testnet

A small Python CLI app to place `MARKET` and `LIMIT` orders on Binance USDT-M Futures Testnet.

## Features

- Python 3.x CLI (`argparse`)
- Places `MARKET` and `LIMIT` orders
- Supports both sides: `BUY` and `SELL`
- Clear stdout output:
  - order request summary
  - order response details (`orderId`, `status`, `executedQty`, `avgPrice`)
  - success/failure message
- Structured design:
  - `bot/client.py`: Binance API client wrapper
  - `bot/orders.py`: order service and formatters
  - `bot/validators.py`: input validation
  - `bot/logging_config.py`: log configuration
  - `cli.py`: command entry point
- Logs API requests, responses, and errors to file
- Exception handling for validation, API, and network errors

## Project Structure

```text
.
├── bot
│   ├── __init__.py
│   ├── client.py
│   ├── logging_config.py
│   ├── orders.py
│   └── validators.py
├── logs
│   ├── limit_order.log
│   └── market_order.log
├── cli.py
├── README.md
└── requirements.txt
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create Binance Futures Testnet API credentials.
4. Set env vars (optional):

```bash
set BINANCE_API_KEY=your_key
set BINANCE_API_SECRET=your_secret
```

PowerShell:

```powershell
$env:BINANCE_API_KEY="your_key"
$env:BINANCE_API_SECRET="your_secret"
```

## Usage

Base URL used by default:

```text
https://testnet.binancefuture.com
```

### MARKET order

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### LIMIT order

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 80000
```

### Dry run mode (no real API call)

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001 --dry-run
```

## Example output

```text
Order Request Summary: symbol=BTCUSDT, side=BUY, type=MARKET, quantity=0.001
Order Response Details: orderId=123456789, status=FILLED, executedQty=0.001, avgPrice=0.0
Success: order submitted successfully.
```

## Log Files

Sample logs are included in `logs/`:

- `logs/market_order.log`
- `logs/limit_order.log`

You can generate your own by setting `--log-file` in commands.

## Assumptions

- Uses Binance Futures USDT-M endpoint (`/fapi/v1/order`)
- LIMIT orders use `timeInForce=GTC`
- `avgPrice` may be unavailable depending on order state
- A `--dry-run` mode is available for local validation without credentials
