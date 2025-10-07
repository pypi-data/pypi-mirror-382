# Schwab SDK (Python)

Lightweight client for the Schwab API: OAuth, REST (Trader/Market Data), and WebSocket Streaming.

* Focus: thin wrappers, no heavy validation; robust token handling, refresh, and retries.
* Coverage: Accounts, Orders, Market Data, and Streaming (Level One, Book, Chart, Screener, Account Activity).

## Installation

Unofficial PyPI package (distribution name):

```bash
pip install schwab_sdk_unofficial
```

Import in code (module):

```python
from schwab_sdk import Client, AsyncClient
```

⚠️ Note: The package name on PyPI is `schwab_sdk_unofficial`, but the import remains `schwab_sdk` for a clean API.

## Table of Contents

* [Requirements](#requirements)
* [Configuration](#configuration)
* [Quick Start](#quick-start)
* [Authentication (OAuth)](#authentication-oauth)
* [Request & Error Handling (REST)](#request--error-handling-rest)
* [Accounts (`accounts.py`)](#accounts-accountspy)
* [Orders (`orders.py`)](#orders-orderspy)
* [Market Data (`market.py`)](#market-data-marketpy)
* [WebSocket Streaming (`streaming.py`)](#websocket-streaming-streamingpy)

  * [Key Formats (quick table)](#key-formats-quick-table)
  * [Service-by-Service Examples](#service-by-service-examples)
  * [Utilities](#utilities)
  * [Recommended Fields](#recommended-fields)
  * [Quick Field Guide (IDs → meaning)](#quick-field-guide-ids--meaning)
  * [Frame Structure](#frame-structure)
* [Advanced Troubleshooting](#advanced-troubleshooting)
* [Contributions](#contributions)
* [Disclaimer](#disclaimer)
* [License](#license)

## Requirements

* Python 3.9+
* Install dependencies:

```bash
pip install requests websocket-client flask
```

## Configuration

Create `.env` (or export environment variables):

```env
SCHWAB_CLIENT_ID=your_client_id
SCHWAB_CLIENT_SECRET=your_client_secret
SCHWAB_REDIRECT_URI=https://127.0.0.1:8080/callback
```

### Token storage modes

- `save_token` controla la persistencia de tokens en los clientes (Sync/Async).
- `save_token=True` (default): guarda tokens en archivo JSON (`schwab_tokens.json`) y rota automáticamente (access ~29 min; aviso de re-login cuando el refresh expira ~7 d).
- `save_token=False`: mantiene tokens solo en memoria; puedes inicializar con `token_data` y consultar el estado con `client.token_handler.get_token_payload()`.

## Quick Start

```python
from schwab_sdk import Client
import os

client = Client(
    os.environ['SCHWAB_CLIENT_ID'],
    os.environ['SCHWAB_CLIENT_SECRET'],
    os.environ.get('SCHWAB_REDIRECT_URI','https://127.0.0.1:8080/callback'),
    save_token=True,  # True: guarda en archivo JSON, False: solo en memoria
    # Opcional: inicializar tokens desde un dict (refresh/boot)
    token_data={
        # Minimal example: provide current tokens
        # 'access_token': '...',
        # 'refresh_token': '...',
        # either expires_in (seconds) OR access_token_expires_at (ISO)
        # 'expires_in': 1800,
        # 'access_token_expires_at': '2025-10-01T12:00:00',
        # optional refresh token expiration (ISO)
        # 'refresh_token_expires_at': '2025-10-07T11:00:00'
    }
)

# First use: OAuth login (opens the browser)
success, tokens = client.login()
if success:
    print("Login successful!")
    print("Token data:", tokens)
else:
    print("Login failed")

# REST
quotes = client.market.get_quotes(["AAPL","MSFT"])  # Market Data
accounts = client.account.get_accounts()               # Accounts

# Streaming (Level One equities)
ws = client.streaming
ws.on_data(lambda f: print("DATA", f))
ws.connect(); ws.login()
ws.equities_subscribe(["AAPL"])
```

## Async Support

The SDK also provides async versions of all endpoints using `AsyncClient`:

```python
import asyncio
from schwab_sdk import AsyncClient

async def main():
    # Initialize async client
    async with AsyncClient(
        os.environ['SCHWAB_CLIENT_ID'],
        os.environ['SCHWAB_CLIENT_SECRET'],
        save_token=True  # True: guarda en archivo JSON, False: solo en memoria
    ) as client:
        # Login (async wrapper)
        success, tokens = await client.login()
        if success:
            print("Async login successful!")
            print("Token data:", tokens)
        
        # Async REST calls
        quotes = await client.market.get_quotes(["AAPL", "MSFT"])
        accounts = await client.account.get_accounts()
        orders = await client.orders.get_all_orders()
        
        # Async streaming
        await client.streaming.connect()
        await client.streaming.login()
        await client.streaming.equities_subscribe(["AAPL"])
        
        # Set up callbacks
        client.streaming.on_data(lambda data: print("DATA:", data))
        client.streaming.on_response(lambda resp: print("RESPONSE:", resp))
        
        # Keep running to receive data
        await asyncio.sleep(10)  # Example: run for 10 seconds
        await client.streaming.disconnect()

# Run async function
asyncio.run(main())
```

### Async Benefits

- **Non-blocking**: Multiple API calls can run concurrently
- **Better performance**: Especially for multiple simultaneous requests
- **Context manager**: Automatic session cleanup with `async with`
- **Same API**: All methods have async equivalents with `await`

### Async vs Sync

| Feature | Sync | Async |
|---------|------|-------|
| **Import** | `from schwab_sdk import Client` | `from schwab_sdk import AsyncClient` |
| **Usage** | `client.method()` | `await client.method()` |
| **Context** | `client = Client(...)` | `async with AsyncClient(...)` |
| **Performance** | Sequential | Concurrent |
| **Dependencies** | `requests`, `websocket-client` | `aiohttp`, `websockets` |

### Async Streaming

The async streaming client provides non-blocking WebSocket connections:

```python
import asyncio
from schwab_sdk import AsyncClient

async def streaming_example():
    async with AsyncClient(client_id, client_secret, save_token=False) as client:
        await client.login()
        
        # Connect to streaming
        await client.streaming.connect()
        await client.streaming.login()
        
        # Set up callbacks
        client.streaming.on_data(lambda data: print("Market data:", data))
        client.streaming.on_response(lambda resp: print("Response:", resp))
        client.streaming.on_notify(lambda notify: print("Notification:", notify))
        
        # Subscribe to data streams
        await client.streaming.equities_subscribe(["AAPL", "MSFT"])
        await client.streaming.options_subscribe([
            client.streaming.create_option_symbol("AAPL", "2025-12-19", "C", 200.0)
        ])
        await client.streaming.account_activity_subscribe("your_account_hash")
        
        # Keep running
        await asyncio.sleep(30)  # Run for 30 seconds
        
        # Cleanup
        await client.streaming.disconnect()

asyncio.run(streaming_example())
```

### Streaming Services Available

| Service | Method | Description |
|---------|--------|-------------|
| **Equities** | `equities_subscribe(symbols)` | Stock quotes |
| **Options** | `options_subscribe(option_symbols)` | Option quotes |
| **Futures** | `futures_subscribe(symbols)` | Futures quotes |
| **Forex** | `forex_subscribe(pairs)` | Currency pairs |
| **Account** | `account_activity_subscribe(account_hash)` | Account activity |

## Async Accounts Module

Async version of account and transaction endpoints:

### Methods

* `get_accounts(fields=None)` - Get all accounts
* `get_account_by_id(account_hash, fields=None)` - Get specific account
* `get_transactions(account_hash, from_date=None, to_date=None, symbol=None, types=None)` - Get transactions
* `get_transaction(account_hash, transaction_id)` - Get specific transaction
* `get_preferences(account_hash)` - Get account preferences

### Example

```python
async with AsyncClient(client_id, client_secret) as client:
    await client.login()
    
    # Get all accounts
    accounts = await client.account.get_accounts()
    
    # Get account with positions
    account = await client.account.get_account_by_id("123456789", fields="positions")
    
    # Get transactions for date range
    transactions = await client.account.get_transactions(
        "123456789", 
        from_date="2025-01-01", 
        to_date="2025-01-31"
    )
```

## Async Orders Module

Async version of order management endpoints:

### Methods

* `get_orders(account_hash, max_results=None, from_entered_time=None, to_entered_time=None, status=None)` - Get orders
* `get_all_orders(max_results=None, from_entered_time=None, to_entered_time=None, status=None)` - Get all orders
* `place_order(account_hash, order_data)` - Place new order
* `get_order(account_hash, order_id)` - Get specific order
* `cancel_order(account_hash, order_id)` - Cancel order
* `replace_order(account_hash, order_id, order_data)` - Replace order
* `preview_order(account_hash, order_data)` - Preview order

### Example

```python
async with AsyncClient(client_id, client_secret) as client:
    await client.login()
    
    # Get orders for account (various date formats)
    orders = await client.orders.get_orders("123456789", status="FILLED")
    
    # Get orders with date range (YYYY-MM-DD format)
    orders = await client.orders.get_orders(
        "123456789", 
        from_entered_time="2025-01-01", 
        to_entered_time="2025-01-31"
    )
    
    # Get orders with full ISO format (passed through as-is)
    orders = await client.orders.get_orders(
        "123456789",
        from_entered_time="2025-01-01T09:00:00.000Z",
        to_entered_time="2025-01-01T17:00:00.000Z"
    )
    
    # Mixed formats also work
    orders = await client.orders.get_orders(
        "123456789",
        from_entered_time="2025-01-01",  # YYYY-MM-DD (auto-converted)
        to_entered_time="2025-01-31T23:59:59.000Z"  # Full ISO (passed through)
    )
    
    # Place a market order
    order_data = {
        "orderType": "MARKET",
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [{
            "instruction": "BUY",
            "quantity": 100,
            "instrument": {"symbol": "AAPL", "assetType": "EQUITY"}
        }]
    }
    result = await client.orders.place_order("123456789", order_data)
```

## Async Market Module

Async version of market data endpoints:

### Methods

* `get_quote(symbol)` - Get single quote
* `get_quotes(symbols)` - Get multiple quotes
* `get_movers(symbol_id, sort=None, frequency=None, params=None)` - Get market movers
* `get_option_chain(symbol, contract_type=None, ...)` - Get option chain
* `get_expiration_chain(symbol, params=None)` - Get expiration dates
* `get_markets(date=None)` - Get market hours
* `get_market_hours(date=None)` - Get market hours for date

### Example

```python
async with AsyncClient(client_id, client_secret) as client:
    await client.login()
    
    # Get quotes
    quotes = await client.market.get_quotes(["AAPL", "MSFT", "GOOGL"])
    
    # Get option chain
    options = await client.market.get_option_chain(
        "AAPL",
        contract_type="CALL",
        strike_count=5,
        from_date="2025-01-01",
        to_date="2025-12-31"
    )
    
    # Get market movers
    movers = await client.market.get_movers("$SPX.X", sort="PERCENT_CHANGE")
```

## Authentication (OAuth)

* `client.login(timeout=300, auto_open_browser=True)`
* Handy: `client.has_valid_token()`, `client.refresh_token_now()`, `client.logout()`
* Internals: adhoc HTTPS callback server (dev), code-for-token exchange, auto-refresh and notice when refresh expires.

## Request & Error Handling (REST)

All REST calls use `Client._request()` with:

* Automatic Authorization headers
* Refresh retry on 401 (once) and immediate resend
* Retries with backoff for 429/5xx (exponential with factor 0.5)

---

## Accounts (`accounts.py`)

### get_account_numbers() -> List[dict]

* GET `/accounts/accountNumbers`
* Returns `accountNumber` and `hashValue` pairs.
* Example response:

```json
[
  {"accountNumber":"12345678","hashValue":"827C...AC12"}
]
```

### get_accounts(params: dict|None=None) -> dict

* GET `/accounts`
* Query parameters:

  * `fields` (optional): the API currently accepts `positions` to return positions. E.g.: `fields=positions`.

### get_account_by_id(account_hash: str, params: dict|None=None) -> dict

* GET `/accounts/{accountNumber}`
* `account_hash`: encrypted account identifier (`hashValue`).
* Query parameters:

  * `fields` (optional): `positions` to include positions. E.g.: `fields=positions`.

### find_account(last_4_digits: str) -> dict|None

* Helper that uses `get_account_numbers()` and filters by the last 4 digits, then calls `get_account_by_id`.

### get_transactions(account_hash: str, from_date: str|None, to_date: str|None, filters: dict|None=None) -> dict

* GET `/accounts/{accountHash}/transactions`
* **ONE DATE REQUIRED**: you may pass only `from_date` or only `to_date`. If you pass a single date, the SDK fills in the other for the same day:

  * Short format `YYYY-MM-DD`: start → `YYYY-MM-DDT00:00:00.000Z`, end → `YYYY-MM-DDT23:59:59.000Z`
  * Full ISO UTC `YYYY-MM-DDTHH:MM:SS.ffffffZ`: used as-is; if the other date is missing, it is derived with `00:00:00.000Z` or `23:59:59.000Z` of the same day.
* Params:

  * `startDate`: ISO UTC - `YYYY-MM-DDTHH:MM:SS.ffffffZ` (or short `YYYY-MM-DD`)
  * `endDate`: ISO UTC - `YYYY-MM-DDTHH:MM:SS.ffffffZ` (or short `YYYY-MM-DD`)
  * `filters`: optional dict:

    * `types`: string with valid types: `TRADE`, `RECEIVE_AND_DELIVER`, `DIVIDEND_OR_INTEREST`, `ACH_RECEIPT`, `ACH_DISBURSEMENT`, `CASH_RECEIPT`, `CASH_DISBURSEMENT`, `ELECTRONIC_FUND`, `WIRE_OUT`, `WIRE_IN`, `JOURNAL`
    * `symbol`: specific symbol
    * `status`: transaction status

  Note: In some API configurations, `types` may be considered mandatory. The SDK does not require it and treats it as an optional filter.

**Correct example**:

```python
from datetime import datetime, timezone, timedelta

# Get hashValue
hash_value = client.account.get_account_numbers()[0]['hashValue']

# Create UTC dates
start = datetime.now(timezone.utc) - timedelta(days=7)
start = start.replace(hour=0, minute=0, second=0, microsecond=0)
end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)

# Proper call
transactions = client.account.get_transactions(
    account_hash=hash_value,  # Use hashValue!
    from_date=start.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    to_date=end.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    filters={"types": "TRADE,DIVIDEND_OR_INTEREST"}  # Optional
)
```

### get_transaction(account_hash: str, transaction_id: str) -> dict

* GET `/accounts/{accountHash}/transactions/{transactionId}`
* Path parameters:

  * `account_hash` (required)
  * `transaction_id` (required): numeric transaction ID
* Returns details of a specific transaction.

### get_user_preferences() -> dict

* GET `/userPreference`
* Returns user preferences and, when applicable, streamer information needed for WebSocket:

  * `streamerSocketUrl`
  * `schwabClientCustomerId`
  * `schwabClientCorrelId`
  * `SchwabClientChannel`
  * `SchwabClientFunctionId`
* Useful to initialize `client.streaming` (LOGIN and subscriptions).

---

## Orders (`orders.py`)

All responses include HTTP metadata and the native data:

```json
{
  "status_code": 200,
  "success": true,
  "headers": {"...": "..."},
  "url": "https://...",
  "elapsed_seconds": 0.42,
  "method": "GET|POST|PUT|DELETE",
  "params": {"...": "..."},
  "data": {},
  "order_id": "..."   
}
```

### get_orders(account_hash, from_entered_time=None, to_entered_time=None, status=None, max_results=None) -> dict

* GET `/accounts/{accountNumber}/orders`
* **Date format**: Accepts both `YYYY-MM-DD` (auto-converted to ISO) or full ISO-8601 format. If omitted, defaults to "last 60 days".
* `status` (case-insensitive): normalized to uppercase. Values accepted by the API:
  `AWAITING_PARENT_ORDER`, `AWAITING_CONDITION`, `AWAITING_STOP_CONDITION`, `AWAITING_MANUAL_REVIEW`, `ACCEPTED`, `AWAITING_UR_OUT`, `PENDING_ACTIVATION`, `QUEUED`, `WORKING`, `REJECTED`, `PENDING_CANCEL`, `CANCELED`, `PENDING_REPLACE`, `REPLACED`, `FILLED`, `EXPIRED`, `NEW`, `AWAITING_RELEASE_TIME`, `PENDING_ACKNOWLEDGEMENT`, `PENDING_RECALL`, `UNKNOWN`.
* `maxResults` (optional): record limit (API default 3000).
* **Date conversion**: `YYYY-MM-DD` → `YYYY-MM-DDT00:00:00.000Z` (start) or `YYYY-MM-DDT23:59:59.000Z` (end)

### get_all_orders(from_entered_time=None, to_entered_time=None, status=None, max_results=None) -> dict

* GET `/orders`
* **Date format**: Accepts both `YYYY-MM-DD` (auto-converted to ISO) or full ISO-8601 format. If omitted, defaults to "last 60 days".
* Filters identical to `get_orders` (including `status` normalization).
* `maxResults` (optional): record limit (API default 3000).
* **Date conversion**: `YYYY-MM-DD` → `YYYY-MM-DDT00:00:00.000Z` (start) or `YYYY-MM-DDT23:59:59.000Z` (end)

### place_order(account_hash: str, order_data: dict) -> dict

* POST `/accounts/{accountNumber}/orders`
* Extracts `order_id` from the `Location` header when present.

### get_order(account_hash: str, order_id: str) -> dict

* GET `/accounts/{accountNumber}/orders/{orderId}`

### cancel_order(account_hash: str, order_id: str) -> dict

* DELETE `/accounts/{accountNumber}/orders/{orderId}`
* Tries to extract `order_id` from `Location` if the server returns it.

### replace_order(account_hash: str, order_id: str, new_order_data: dict) -> dict

* PUT `/accounts/{accountNumber}/orders/{orderId}`
* Returns new `order_id` (from `Location`) when applicable.

### preview_order(account_hash: str, order_data: dict) -> dict

* POST `/accounts/{accountNumber}/previewOrder`
* Tries to extract `order_id` from `Location` if the server returns it.

### Payload helpers

* `build_limit_order(symbol, quantity, price, instruction="BUY")`
* `build_market_order(symbol, quantity, instruction="BUY")`
* `build_bracket_order(symbol, quantity, entry_price, take_profit_price, stop_loss_price)`

Example (preview):

```python
acc = client.account.get_account_numbers()[0]['hashValue']
order = client.orders.build_limit_order("AAPL", 1, 100.00)
preview = client.orders.preview_order(acc, order)
```

---

## Market Data (`market.py`)

### get_quotes(symbols: str|List[str], params: dict|None=None) -> dict

* GET `/quotes?symbols=...`
* Parameters:

  * `symbols` (required): str or list of symbols separated by commas. E.g.: `AAPL,AMZN,$DJI,/ESH23`.
  * `params` (optional):

    * `fields`: subset of data. Values: `quote`, `fundamental`, `extended`, `reference`, `regular`. Default: all.
    * `indicative`: boolean (`true|false`) to include indicative quotes (e.g., ETFs). Example: `indicative=false`.

### get_quote(symbol: str, params: dict|None=None) -> dict

* GET `/{symbol}/quotes`
* Parameters:

  * `symbol` (required): single symbol (e.g., `TSLA`).
  * `params` (optional):

    * `fields`: same as in `get_quotes`.

### get_option_chain(symbol: str, contract_type: str|None=None, strike_count: int|None=None, include_underlying_quote: bool|None=None, strategy: str|None=None, interval: float|None=None, strike: float|None=None, range_type: str|None=None, from_date: str|None=None, to_date: str|None=None, volatility: float|None=None, underlying_price: float|None=None, interest_rate: float|None=None, days_to_expiration: int|None=None, exp_month: str|None=None, option_type: str|None=None, entitlement: str|None=None, params: dict|None=None) -> dict

* GET `/chains`

* Parameters:

  * `symbol` (required): Underlying asset symbol
  * `contract_type` (optional): Contract Type. Available values: `CALL`, `PUT`, `ALL`
  * `strike_count` (optional): The Number of strikes to return above or below the at-the-money price
  * `include_underlying_quote` (optional): Underlying quotes to be included (boolean)
  * `strategy` (optional): OptionChain strategy. Default is SINGLE. Available values: `SINGLE`, `ANALYTICAL`, `COVERED`, `VERTICAL`, `CALENDAR`, `STRANGLE`, `STRADDLE`, `BUTTERFLY`, `CONDOR`, `DIAGONAL`, `COLLAR`, `ROLL`
  * `interval` (optional): Strike interval for spread strategy chains (see strategy param)
  * `strike` (optional): Strike Price
  * `range_type` (optional): Range(ITM/NTM/OTM etc.)
  * `from_date` (optional): From date (pattern: yyyy-MM-dd)
  * `to_date` (optional): To date (pattern: yyyy-MM-dd)
  * `volatility` (optional): Volatility to use in calculations. Applies only to ANALYTICAL strategy chains
  * `underlying_price` (optional): Underlying price to use in calculations. Applies only to ANALYTICAL strategy chains
  * `interest_rate` (optional): Interest rate to use in calculations. Applies only to ANALYTICAL strategy chains
  * `days_to_expiration` (optional): Days to expiration to use in calculations. Applies only to ANALYTICAL strategy chains
  * `exp_month` (optional): Expiration month. Available values: `JAN`, `FEB`, `MAR`, `APR`, `MAY`, `JUN`, `JUL`, `AUG`, `SEP`, `OCT`, `NOV`, `DEC`, `ALL`
  * `option_type` (optional): Option Type
  * `entitlement` (optional): Applicable only if its retail token, entitlement of client PP-PayingPro, NP-NonPro and PN-NonPayingPro. Available values: `PN`, `NP`, `PP`
  * `params` (optional): Additional query parameters

### get_expiration_chain(symbol: str, params: dict|None=None) -> dict

* GET `/expirationchain`

* Parameters:

  * `symbol` (required): Underlying asset symbol
  * `params` (optional): Additional query parameters

* Returns: JSON response with option expiration dates for the symbol

### get_price_history(symbol, periodType="month", period=1, frequencyType="daily", frequency=1, startDate=None, endDate=None, params=None) -> dict

* GET `/pricehistory`
* Parameters:

  * `periodType`: `day|month|year|ytd`
  * `period`: int
  * `frequencyType`: `minute|daily|weekly|monthly`
  * `frequency`: int
  * `startDate`/`endDate` (ms since epoch)
  * Additional optionals (`needExtendedHoursData`, etc., depending on entitlements)

### get_movers(symbol_id: str, sort: str|None=None, frequency: int|None=None, params: dict|None=None) -> dict

* GET `/movers/{symbol_id}` (e.g., `$DJI`, `$SPX`, `NASDAQ`)
* Parameters:

  * `symbol_id` (required): Index Symbol. Available values: `$DJI`, `$COMPX`, `$SPX`, `NYSE`, `NASDAQ`, `OTCBB`, `INDEX_ALL`, `EQUITY_ALL`, `OPTION_ALL`, `OPTION_PUT`, `OPTION_CALL`
  * `sort` (optional): Sort by a particular attribute. Available values: `VOLUME`, `TRADES`, `PERCENT_CHANGE_UP`, `PERCENT_CHANGE_DOWN`
  * `frequency` (optional): To return movers with the specified directions of up or down. Available values: `0,1,5,10,30,60` (min). Default `0`
  * `params` (optional): Additional query parameters

### get_markets(params: dict|None=None) -> dict

* GET `/markets`
* Query parameters:

  * `markets` (required by API): array of `equity`, `option`, `bond`, `future`, `forex` (the SDK accepts `params={"markets": ...}`)
  * `date` (optional): `YYYY-MM-DD` (if you send ISO, the SDK trims to date)

### get_market_hours(market_id: str, params: dict|None=None) -> dict

* GET `/markets/{market_id}` (`equity`, `option`, `bond`, `forex`)
* Query parameters:

  * `date` (optional): `YYYY-MM-DD` (if you send ISO, the SDK trims to date)

### get_instruments(symbols: str|List[str], projection: str, extra_params: dict|None=None) -> dict

* GET `/instruments`
* Parameters:

  * `symbols` (required): single symbol or comma-separated list
  * `projection` (required by API): `symbol-search`, `symbol-regex`, `desc-search`, `desc-regex`, `search`, `fundamental`
    Note: the SDK does not require it in the signature, but it is recommended to provide it.

### get_instrument_by_cusip(cusip_id: str, params: dict|None=None) -> dict

* GET `/instruments/{cusip_id}`

---

## WebSocket Streaming (`streaming.py`)

### Callbacks

* `on_data(fn)`  (data frames)
* `on_response(fn)`  (command confirmations/errors)
* `on_notify(fn)`  (heartbeats/notices)

### Basic flow

```python
ws = client.streaming
ws.on_data(lambda f: print("DATA", f))
ws.on_response(lambda f: print("RESP", f))
ws.on_notify(lambda f: print("NOTIFY", f))
ws.connect(); ws.login()  # Authorization = access token without "Bearer"
ws.equities_subscribe(["AAPL","MSFT"])             # LEVELONE_EQUITIES
ws.options_subscribe(["AAPL  250926C00257500"])      # LEVELONE_OPTIONS
ws.nasdaq_book(["MSFT"])                             # NASDAQ_BOOK
ws.chart_equity(["AAPL"])                            # CHART_EQUITY
ws.screener_equity(["NYSE_VOLUME_5"])                # SCREENER_EQUITY
```

### Key Formats (quick table)

| Type           | Format                               | Example                 | Notes                                      |
| -------------- | ------------------------------------ | ----------------------- | ------------------------------------------ |
| Equities       | Ticker                               | `AAPL`, `MSFT`          | Uppercase                                  |
| Options        | `RRRRRRYYMMDDsWWWWWddd`              | `AAPL  251219C00200000` | 6-char symbol, YYMMDD, C/P, 5+3 strike    |
| Futures        | `/<root><month><yy>`                 | `/ESZ25`                | Root/month/year in uppercase               |
| FuturesOptions | `./<root><month><year><C/P><strike>` | `./OZCZ23C565`          | Depends on the feed                        |
| Forex          | `PAIR`                               | `EUR/USD`, `USD/JPY`    | `/` separator                              |
| Screener       | `PREFIX_SORTFIELD_FREQUENCY`         | `NYSE_VOLUME_5`         | Prefix/criterion/frequency                 |

### Service-by-Service Examples

#### Level One Options

```python
ws.options_subscribe(["AAPL  250926C00257500"])  # standard option string
# Default fields: 0,2,3,4,8,16,17,18,20,28,29,30,31,37,44
```

#### Level One Futures

```python
ws.futures_subscribe(["/ESZ25"])  # E-mini S&P 500 Dec 2025
# Default fields: 0,1,2,3,4,5,8,12,13,18,19,20,24,33
```

#### Level One Forex

```python
ws.forex_subscribe(["EUR/USD","USD/JPY"])  
# Default fields: 0,1,2,3,4,5,6,7,8,9,10,11,15,16,17,20,21,27,28,29
```

#### Book (Level II)

```python
ws.nasdaq_book(["MSFT"])  # Also: ws.nyse_book, ws.options_book
# Default fields: 0 (Symbol), 1 (BookTime), 2 (Bids), 3 (Asks)
```

#### Chart (Series)

```python
ws.chart_equity(["AAPL"])      # 0..7: key, open, high, low, close, volume, sequence, chartTime
ws.chart_futures(["/ESZ25"])   # 0..5
```

#### Screener

```python
ws.screener_equity(["NYSE_VOLUME_5"])   
ws.screener_options(["CBOE_VOLUME_5"])
```

#### Account Activity

```python
ws.account_activity()  # Gets accountHash and subscribes
```

### Utilities

* `subscribe(service, keys, fields=None)`
* `add(service, keys)`
* `unsubscribe(service, keys)` / `unsubscribe_service(service, keys)`
* `view(service, fields)`

### Option Symbol Helper

* `create_option_symbol(symbol, expiration, option_type, strike_price)` - Creates Schwab option symbol from components

**Example:**
```python
# Create option symbol from components
option_symbol = ws.create_option_symbol("AAPL", "2025-12-19", "C", 200.0)
# Returns: "AAPL  251219C00200000"

# Use in subscription
ws.options_subscribe([option_symbol])
```

**Parameters:**
* `symbol`: Underlying symbol (e.g., "AAPL")
* `expiration`: Expiration date in "YYYY-MM-DD" format (e.g., "2025-10-03")
* `option_type`: "C" for Call or "P" for Put
* `strike_price`: Strike price (e.g., 257.5)

### Recommended Fields

* LEVELONE_EQUITIES: `0,1,2,3,4,5,8,10,18,42,33,34,35`
* LEVELONE_OPTIONS: `0,2,3,4,8,16,17,18,20,28,29,30,31,37,44`
* LEVELONE_FUTURES: `0,1,2,3,4,5,8,12,13,18,19,20,24,33`
* CHART_EQUITY: `0,1,2,3,4,5,6,7`

#### Quick fields table (copy/paste)

| Service                  | Fields CSV                                        |
| ------------------------ | ------------------------------------------------- |
| LEVELONE_EQUITIES        | 0,1,2,3,4,5,8,10,18,42,33,34,35                   |
| LEVELONE_OPTIONS         | 0,2,3,4,8,16,17,18,20,28,29,30,31,37,44           |
| LEVELONE_FUTURES         | 0,1,2,3,4,5,8,12,13,18,19,20,24,33                |
| LEVELONE_FUTURES_OPTIONS | 0,1,2,3,4,5,8,12,13,18,19,20,24,33                |
| LEVELONE_FOREX           | 0,1,2,3,4,5,6,7,8,9,10,11,15,16,17,20,21,27,28,29 |
| NASDAQ_BOOK              | 0,1,2,3                                           |
| NYSE_BOOK                | 0,1,2,3                                           |
| OPTIONS_BOOK             | 0,1,2,3                                           |
| CHART_EQUITY             | 0,1,2,3,4,5,6,7                                   |
| CHART_FUTURES            | 0,1,2,3,4,5                                       |
| SCREENER_EQUITY          | 0,1,2,3,4                                         |
| SCREENER_OPTION          | 0,1,2,3,4                                         |
| ACCT_ACTIVITY            | 0,1,2                                             |

### SUBS / ADD / VIEW / UNSUBS examples by service

```python
ws = client.streaming
ws.on_data(lambda f: print("DATA", f))
ws.on_response(lambda f: print("RESP", f))
ws.connect(); ws.login()

# LEVELONE_EQUITIES
ws.equities_subscribe(["AAPL","TSLA"], fields=[0,1,2,3,4,5,8,10,18,42,33,34,35])
ws.equities_add(["MSFT"])                          # adds without replacing
ws.equities_view([0,1,2,3,5,8,18])                  # changes fields
ws.equities_unsubscribe(["TSLA"])                  # removes symbols

# LEVELONE_OPTIONS
ws.options_subscribe(["AAPL  250926C00257500"], fields=[0,2,3,4,8,16,17,18,20,28,29,30,31,37,44])
ws.options_add(["AAPL  250926P00257500"])          
ws.options_view([0,2,3,4,8,16,17,20,28,29,30,31,37,44])
ws.options_unsubscribe(["AAPL  250926C00257500"])  

# LEVELONE_FUTURES
ws.futures_subscribe(["/ESZ25"], fields=[0,1,2,3,4,5,8,12,13,18,19,20,24,33])
ws.futures_add(["/NQZ25"])
ws.futures_view([0,1,2,3,4,5,8,12,13,18,19,20,24,33])
ws.futures_unsubscribe(["/ESZ25"])  

# BOOK (Level II)
ws.nasdaq_book(["MSFT"], fields=[0,1,2,3])
ws.add("NASDAQ_BOOK", ["AAPL"])                    # generic ADD
ws.view("NASDAQ_BOOK", [0,1,2,3])                   # generic VIEW
ws.unsubscribe_service("NASDAQ_BOOK", ["MSFT"])    # generic UNSUBS

# CHART (Series)
ws.chart_equity(["AAPL"], fields=[0,1,2,3,4,5,6,7])
ws.add("CHART_EQUITY", ["MSFT"])                  # generic ADD
ws.view("CHART_EQUITY", [0,1,2,3,4,5,6,7])          # generic VIEW
ws.unsubscribe("CHART_EQUITY", ["AAPL"])           # generic UNSUBS

# SCREENER
ws.screener_equity(["EQUITY_ALL_VOLUME_5"], fields=[0,1,2,3,4])
ws.add("SCREENER_EQUITY", ["NYSE_TRADES_1"])      
ws.view("SCREENER_EQUITY", [0,1,2,3,4])
ws.unsubscribe("SCREENER_EQUITY", ["EQUITY_ALL_VOLUME_5"])

# ACCT_ACTIVITY
ws.account_activity(fields=[0,1,2])                  # subscribe account activity
# For UNSUBS you need the same key used in SUBS (account_hash)
account_hash = getattr(client, "_account_hash", None)
if account_hash:
    ws.unsubscribe_service("ACCT_ACTIVITY", [account_hash])
```

### Quick Field Guide (IDs → meaning)

> Note: exact mappings may vary depending on entitlements/version. Below are practical equivalences observed in frames.

#### LEVELONE_EQUITIES

| ID | Field                      |
| -- | -------------------------- |
| 0  | symbol/key                 |
| 1  | bidPrice                   |
| 2  | askPrice                   |
| 3  | lastPrice                  |
| 4  | bidSize                    |
| 5  | askSize                    |
| 8  | totalVolume                |
| 10 | referencePrice (open/mark) |
| 18 | netChange                  |
| 42 | percentChange              |

#### LEVELONE_OPTIONS

| ID | Field                           |
| -- | ------------------------------- |
| 0  | symbol/key                      |
| 2  | bidPrice                        |
| 3  | askPrice                        |
| 4  | lastPrice                       |
| 8  | totalVolume                     |
| 16 | openInterest                    |
| 17 | daysToExpiration                |
| 20 | strikePrice                     |
| 28 | delta                           |
| 29 | gamma                           |
| 30 | theta                           |
| 31 | vega                            |
| 44 | impliedVolatility (if provided) |

#### LEVELONE_FUTURES

| ID | Field                                      |
| -- | ------------------------------------------ |
| 0  | symbol/key                                 |
| 1  | bidPrice                                   |
| 2  | askPrice                                   |
| 3  | lastPrice                                  |
| 4  | bidSize                                    |
| 5  | askSize                                    |
| 8  | totalVolume                                |
| 12 | openInterest                               |
| 13 | contractDepth/series info (per feed)       |
| 18 | netChange                                  |
| 19 | sessionChange (or days/indicator per feed) |
| 20 | percentChange/ratio (per feed)             |
| 24 | lastSettlement/mark                        |
| 33 | priorSettle                                |

### Frame Structure

* Confirmations (`response`): `{ "response": [ { "service":"ADMIN","command":"LOGIN","content":{"code":0,"msg":"..."}} ] }`
* Data (`data`): `{ "service":"LEVELONE_EQUITIES","timestamp":...,"command":"SUBS","content":[{"key":"AAPL",...}] }`
* Notifications (`notify`): `{ "notify": [ { "heartbeat": "..." } ] }`

### Streamer API Cheat Sheet (parameters and commands)

1. Connection and prerequisites

* **Auth**: use the Access Token from the OAuth flow.
* **Session IDs** (from `GET /userPreference`): `schwabClientCustomerId`, `schwabClientCorrelId`, `SchwabClientChannel`, `SchwabClientFunctionId`.
* **Transport**: JSON WebSocket. One stream per user (if you open more: code 12 CLOSE_CONNECTION).

2. Envelope of each command

* **Common fields**:

  * `service` (req.): `ADMIN`, `LEVELONE_EQUITIES`, `LEVELONE_OPTIONS`, `LEVELONE_FUTURES`, `LEVELONE_FUTURES_OPTIONS`, `LEVELONE_FOREX`, `NYSE_BOOK`, `NASDAQ_BOOK`, `OPTIONS_BOOK`, `CHART_EQUITY`, `CHART_FUTURES`, `SCREENER_EQUITY`, `SCREENER_OPTION`, `ACCT_ACTIVITY`.
  * `command` (req.): `LOGIN`, `SUBS`, `ADD`, `UNSUBS`, `VIEW`, `LOGOUT`.
  * `requestid` (req.): unique request identifier.
  * `SchwabClientCustomerId` and `SchwabClientCorrelId` (recommended): from `userPreference`.
  * `parameters` (optional): depends on service/command.
* **Notes**: `SUBS` overwrites list; `ADD` appends; `UNSUBS` removes; `VIEW` changes `fields`.

3. ADMIN (session)

* `LOGIN` (`service=ADMIN`, `command=LOGIN`)

  * parameters: `Authorization` (token without "Bearer"), `SchwabClientChannel`, `SchwabClientFunctionId`.
* `LOGOUT` (`service=ADMIN`, `command=LOGOUT`)

  * parameters: empty.

4. LEVEL ONE (L1 quotes)

* Common parameters: `keys` (req., CSV list), `fields` (optional, indexes).
* `LEVELONE_EQUITIES`: `keys` uppercase tickers (e.g., `AAPL,TSLA`).
* `LEVELONE_OPTIONS`: `keys` Schwab option format `RRRRRR  YYMMDD[C/P]STRIKE`.
* `LEVELONE_FUTURES`: `keys` `/<root><monthCode><yearCode>` (month codes: F,G,H,J,K,M,N,Q,U,V,X,Z; year two digits), e.g., `/ESZ25`.
* `LEVELONE_FUTURES_OPTIONS`: `keys` `./<root><month><yy><C|P><strike>`, e.g., `./OZCZ23C565`.
* `LEVELONE_FOREX`: `keys` `BASE/QUOTE` pairs CSV (e.g., `EUR/USD,USD/JPY`).

5. BOOK (Level II)

* Services: `NYSE_BOOK`, `NASDAQ_BOOK`, `OPTIONS_BOOK`.
* Parameters: `keys` (req., tickers), `fields` (optional, level indexes).

6. CHART (streaming series)

* `CHART_EQUITY`: `keys` equities; `fields` indexes (OHLCV, time, seq).
* `CHART_FUTURES`: `keys` futures (same format as L1 futures); `fields` indexes.

7. SCREENER (gainers/losers/actives)

* Services: `SCREENER_EQUITY`, `SCREENER_OPTION`.
* `keys` pattern `PREFIX_SORTFIELD_FREQUENCY`, e.g., `EQUITY_ALL_VOLUME_5`.

  * `PREFIX` examples: `$COMPX`, `$DJI`, `$SPX`, `INDEX_ALL`, `NYSE`, `NASDAQ`, `OTCBB`, `EQUITY_ALL`, `OPTION_PUT`, `OPTION_CALL`, `OPTION_ALL`.
  * `SORTFIELD`: `VOLUME`, `TRADES`, `PERCENT_CHANGE_UP`, `PERCENT_CHANGE_DOWN`, `AVERAGE_PERCENT_VOLUME`.
  * `FREQUENCY`: `0,1,5,10,30,60` (min; `0` = full day).
* `fields` (optional): screener field indexes.

8. ACCOUNT (account activity)

* Service: `ACCT_ACTIVITY` (`SUBS`/`UNSUBS`).
* `keys` (req.): arbitrary identifier for your sub; if you send multiple, the first is used.
* `fields` (recommended): `0` (or `0,1,2,3` per example/need).

9. Server responses

* Types: `response` (to your requests), `notify` (heartbeats), `data` (market flow).
* Key codes: `0` SUCCESS, `3` LOGIN_DENIED, `11` SERVICE_NOT_AVAILABLE, `12` CLOSE_CONNECTION, `19` REACHED_SYMBOL_LIMIT, `20` STREAM_CONN_NOT_FOUND, `21` BAD_COMMAND_FORMAT, `26/27/28/29` successes for `SUBS/UNSUBS/ADD/VIEW`.

10. Delivery Types

* `All Sequence`: everything with sequence number.
* `Change`: only changed fields (conflated).
* `Whole`: full messages with throttling.

11. Best practices

* Do `LOGIN` and wait for `code=0` before `SUBS/ADD`.
* To add symbols without losing existing ones, use `ADD` (not `SUBS`).
* Change `fields` with `VIEW` for performance.
* Handle `notify` (heartbeats) and reconnect if they are lost.
* Reuse your `SchwabClientCorrelId` during the session.
* If you see `19` (symbol limit), shard loads by service/session.

---

## Advanced Troubleshooting

* `notify.code=12` (Only one connection): close other active WebSocket sessions.
* `response.content.code=3` (Login denied): invalid/expired token → `client.login()`.
* `response.content.code=21` (Bad command formatting): check `Authorization` format (without `Bearer`) and keys (spacing for options, uppercase).
* Persistent REST 401: delete `schwab_tokens.json` and re-run `client.login()`.
* High latency/lost frames: avoid parallel reconnects; use the SDK's auto-resubscription.

---

## Contributions

Your contributions are welcome! Ideas, issues, and PRs help improve the SDK:

* Open an issue with clear details (environment, steps, expected/actual error).
* Propose endpoint coverage improvements and examples.
* Follow a clear style and add tests or minimal examples when possible.

If you want to hold working sessions or discuss the roadmap, open an issue labeled `discussion`.

## Disclaimer

This project is unofficial and is not affiliated with, sponsored by, or endorsed by Charles Schwab & Co., Inc. “Schwab” and other trademarks are the property of their respective owners. Use of this SDK is subject to the terms and conditions of Schwab APIs and applicable regulations. Use at your own discretion and responsibility.

---

## License

MIT ([LICENSE](LICENSE))
