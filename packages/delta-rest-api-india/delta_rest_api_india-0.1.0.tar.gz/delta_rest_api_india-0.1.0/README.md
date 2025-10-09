# delta_rest_api_india

A simple Python wrapper for **Delta Exchange (India)** REST API — allows trading on both **Testnet** and **Production** environments.

---

## 🌐 Create an Account
👉 [Testnet (India)](https://testnet.delta.exchange)

---

## 📦 Installation
```bash
pip install delta-rest-api-india
```

---

## 🚀 Quick Start

```python
import delta-rest-api-india as delta_algo

# --- API Configuration ---
api_key = ""          # Your API key
api_secret = ""       # Your API secret
price = ""            # Needed for LIMIT orders (default is MARKET)
SL = ""               # Stop Loss (for bracket orders)
TP = ""               # Take Profit (for bracket orders)
LOT = ""              # Quantity
side = ""             # BUY / SELL
product_symbol = ""   # Example: BTCUSD / ETHUSD
product_id = ""       # Example: BTCUSD = 27, ETHUSD = 3136
base_url = ""         # Use either PROD or TESTNET URL
timeframe = ""        # Chart timeframe
```

---

## 🌍 Base URLs

| Environment | URL |
|--------------|-----|
| **Production (India)** | `https://api.india.delta.exchange` |
| **Testnet (India)** | `https://cdn-ind.testnet.deltaex.org` |

---

## 🧩 API Methods

### ➕ Place a Bracket Order
```python
delta_algo.PLACE_BRACKET_ORDER(
    api_key, api_secret, price, SL, TP, LOT, side,
    product_symbol, product_id, base_url
)
```

### 💰 Place a Normal Order
```python
delta_algo.PLACE_ORDER(
    api_key, api_secret, price, LOT, side, product_id, base_url
)
```

### 💵 Check Balance
```python
delta_algo.BALANCE_CHECK(api_key, api_secret, base_url)
```

### 📈 Get Current Price
```python
delta_algo.CURRENT_PRICE(product_symbol)
```

---

## 🧠 Upcoming Features (Next Version)
- EMA (Exponential Moving Average)
- Moving Average (SMA)
- RSI (Relative Strength Index)
- Support & Resistance Detection
- EMA/SMA Crossover Detection

---

## 📬 Contact
📧 **shashankjoshi61@yahoo.com**
