import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

URL = "https://afltables.com/afl/stats/2026.html"

def fetch_latest_stats():
    print(f"[{datetime.now()}] Downloading page...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    print("✅ Page downloaded successfully")

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page")

    all_dfs = []
    for i, table in enumerate(tables):
        try:
            df = pd.read_html(str(table))[0]
            print(f"Table {i}: {len(df)} rows, columns = {list(df.columns)}")
            
            if len(df) > 5 and 'Player' in str(df.columns):
                df.columns = [str(col).strip() for col in df.columns]
                all_dfs.append(df)
        except:
            pass

    if all_dfs:
        full_df = pd.concat(all_dfs, ignore_index=True)
        print(f"\n✅ Successfully combined {len(full_df)} player rows")
        print("First few columns:", list(full_df.columns)[:15])
        return full_df
    else:
        raise ValueError("No valid player tables found")

def main():
    try:
        stats = fetch_latest_stats()
        print("\n=== DEBUG COMPLETE - Script is working but needs final column mapping ===")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
