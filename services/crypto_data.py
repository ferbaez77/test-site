import requests
import json # For potential error logging or if needed later

# Base URL for CoinGecko API
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

def get_top_crypto_data(limit: int = 20):
    """
    Fetches market data for the top N cryptocurrencies from CoinGecko.
    Data includes price, market cap, volume, 24h change, etc.
    """
    endpoint = f"{COINGECKO_API_URL}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': 'false', # We don't need sparkline data for now
        'price_change_percentage': '24h' # Include 24h price change
    }
    headers = {
        'Accept': 'application/json'
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        
        data = response.json()
        
        # We can simplify the data returned if needed, or return as is
        # For now, let's return the relevant fields CoinGecko provides
        # Example fields: id, symbol, name, image, current_price, market_cap, 
        # market_cap_rank, total_volume, price_change_percentage_24h
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CoinGecko: {e}")
        # In a real app, you might log this error and handle it more gracefully
        return [] # Return empty list on error
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from CoinGecko: {e}")
        return []

if __name__ == '__main__':
    # For testing the function directly
    top_cryptos = get_top_crypto_data(5)
    if top_cryptos:
        print(f"Successfully fetched top {len(top_cryptos)} cryptocurrencies:")
        for crypto in top_cryptos:
            print(f"- {crypto.get('name')} ({crypto.get('symbol').upper()}): ${crypto.get('current_price'):,.2f}, 24h Change: {crypto.get('price_change_percentage_24h_in_currency', crypto.get('price_change_percentage_24h', 0)):.2f}%") # Adjusted key for 24h change
    else:
        print("Failed to fetch cryptocurrency data.")

def get_coin_details(crypto_id: str):
    endpoint = f"{COINGECKO_API_URL}/coins/{crypto_id}"
    params = {
        'localization': 'false',
        'tickers': 'false',
        'market_data': 'true', # Need market_data for current_price
        'community_data': 'false',
        'developer_data': 'false',
        'sparkline': 'false'
    }
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Sanitize description by removing HTML tags
        description_html = data.get("description", {}).get("en", "No description available.")
        import re
        description_text = re.sub(r'<a href="[^"]*">([^<]*)</a>', r'\1', description_html) # Keep link text
        description_text = re.sub(r'<[^>]+>', '', description_text) # Remove all other tags
        description_text = description_text.strip() if description_text else "No description available."

        return {
            "id": data.get("id"),
            "name": data.get("name", crypto_id.capitalize()),
            "symbol": data.get("symbol", "").upper(),
            "image": data.get("image", {}).get("thumb"), # thumb or small
            "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
            "description": description_text # Use sanitized description
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coin details for {crypto_id} from CoinGecko: {e}")
        return {"id": crypto_id, "name": crypto_id.capitalize(), "error": "Could not load details from CoinGecko."}
    except Exception as e: # Catch any other error
        print(f"Unexpected error fetching coin details for {crypto_id}: {e}")
        return {"id": crypto_id, "name": crypto_id.capitalize(), "error": "Could not load details due to an unexpected error."}

def get_ohlcv_data(crypto_id: str, days: int = 30):
    endpoint = f"{COINGECKO_API_URL}/coins/{crypto_id}/ohlc"
    params = {'vs_currency': 'usd', 'days': str(days)}
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        # Data is typically: [[timestamp, open, high, low, close], ...]
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching OHLCV data for {crypto_id} from CoinGecko: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching OHLCV data for {crypto_id}: {e}")
        return []
