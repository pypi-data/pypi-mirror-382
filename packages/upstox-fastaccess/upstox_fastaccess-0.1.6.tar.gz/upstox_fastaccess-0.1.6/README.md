# Upstox Auto Login

A **Python package** to **automate the Upstox API v2 login flow**  handling the complete **OAuth2** process to retrieve an `access_token`.
---

## Security Disclaimer

This package handles **sensitive credentials** (API keys, PIN, TOTP secret).

> **Storing credentials as plaintext is a major security risk.**
> It is **highly recommended** to:

* Use **environment variables** or a **secret manager**.
* Avoid sharing your credentials in public repositories.
  This tool is intended for **personal use in secure environments only.**

---

##  How It Works

The tool:

1. Launches a **headless Chrome browser**.
2. Automates the login by entering your **User ID**, **TOTP**, and **PIN**.
3. Captures the **authorization code** after successful login.
4. Exchanges it for an **access_token** via the Upstox OAuth2 flow.
5. Closes the browser automatically.

You can then use the returned `access_token` in your Upstox API client.

---

##  Prerequisites

Before using this package, make sure you have:

* **Python 3.10+**
*  **Google Chrome** (latest version)
*  An **Upstox Developer App** with:

  * `API_KEY`
  * `SECRET_KEY`
  * Configured `redirect_url`

---

## Installation

```bash
pip install upstox-fastaccess
```

---

## Usage

The main function provided is `auto_login()` — it automates the entire login flow.

### **Function Parameters**

| Parameter      | Type  | Description                                                                              |
| -------------- | ----- | ---------------------------------------------------------------------------------------- |
| `API_KEY`      | `str` | Your Upstox API Key                                                                      |
| `SECRET_KEY`   | `str` | Your Upstox Secret Key                                                                   |
| `USER_ID`      | `str` | Your 10-digit Upstox mobile number                                                       |
| `PIN`          | `str` | Your 6-digit Upstox trading PIN                                                          |
| `TOTP_SECRET`  | `str` | Your **authentication secret** (TOTP secret key) from the authenticator app used for 2FA |
| `redirect_url` | `str` | *(Optional)* Redirect URI (default: `https://127.0.0.1:5000/`)                           |

---

## Example

```python
from upstox_auto_login import auto_login
import os
import logging

# Recommended: Load credentials from environment variables
# API_KEY = os.getenv("UPSTOX_API_KEY")

# Configure logging to track the login process
logging.basicConfig(level=logging.INFO)

try:
    # Call the auto_login function
    access_token = auto_login(
        API_KEY="your_api_key",
        SECRET_KEY="your_secret_key",
        USER_ID="your_10_digit_mobile_number",
        PIN="your_6_digit_pin",
        TOTP_SECRET="your_totp_secret_key",
        redirect_url = "https://127.0.0.1:5000/"
    )

    if access_token:
        print(f"Success! Access Token: {access_token}")
        # Use this token with your Upstox API client or other SDK functions
    else:
        print("Login failed. Check logs for details.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
```
# Retrive All orders
```python
access_token = access_token

url = "https://api.upstox.com/v2/order/retrieve-all"
url = "https://api-sandbox.upstox.com/v2/order/retrieve-all"   # for Sandbox api use this urls

orders = get_all_orders(access_token, url)
print(orders)

```

# Exit All orders
```python
access_token = access_token

url = 'https://api.upstox.com/v2/order/positions/exit'
url = "https://api-sandbox.upstox.com/v2order/positions/exit"   # for Sandbox api use this urls

res = exit_orders(access_token)
print(res)

```


---

## Using Upstox SDK After Auto Login

You can now use the Upstox SDK to access trading, market data, and portfolio features.

### Install Upstox SDK

```bash
pip install upstox-python-sdk
# You may need root permission:
sudo pip install upstox-python-sdk
```

### Import and Set Up SDK

```python
import upstox_client

# Configuration for sandbox mode
configuration = upstox_client.Configuration(sandbox=True)
configuration.access_token = '<SANDBOX_ACCESS_TOKEN>'

api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))
```

### Place an Order Example

```python
body = upstox_client.PlaceOrderV3Request(
    quantity=1, product="D", validity="DAY", price=9.12, tag="string",
    instrument_token="NSE_EQ|INE669E01016", order_type="LIMIT",
    transaction_type="BUY", disclosed_quantity=0, trigger_price=0.0, is_amo=True, slice=True
)

try:
    api_response = api_instance.place_order(body)
    print(api_response)
except upstox_client.rest.ApiException as e:
    print("Exception when calling OrderApi->place_order: %s\n" % e)
```

### Algo ID Support

```python
api_response = api_instance.place_order(body, algo_id="your-algo-id")
```

Other order methods (modify, cancel, etc.) accept an optional `algo_id`.

### Websocket Market & Portfolio Data

* `MarketDataStreamerV3` → Real-time market updates
* `PortfolioDataStreamer` → Real-time order, position, holding, and GTT updates

Example:

```python
import upstox_client

configuration = upstox_client.Configuration()
configuration.access_token = '<ACCESS_TOKEN>'

streamer = upstox_client.MarketDataStreamerV3(upstox_client.ApiClient(configuration), ["NSE_INDEX|Nifty 50"], "full")

def on_message(msg):
    print(msg)

streamer.on("message", on_message)
streamer.connect()
```

Refer to the SDK docs for full WebSocket methods: `subscribe`, `unsubscribe`, `change_mode`, `auto_reconnect`, etc.

---

## Error Handling

The function is designed to handle failures gracefully.

* Logs detailed errors during execution.
* Returns `None` if the login or token exchange fails.

---


---

## Contributing

Contributions are welcome!
If you’d like to:

* Report a bug 
* Request a feature 
* Submit a pull request 

Please open an issue or PR on the **GitHub repository**.

---

## License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for more details.

---

## Author

**Uttam Kumar**
Python Developer • Automation & Trading Systems

---
