import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://afltables.com/afl/stats/2026.html"

def main():
    print(f"[{datetime.now()}] Downloading 2026 stats...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    print("✅ Page downloaded successfully")

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page\n")

    for i, table in enumerate(tables):
        try:
            df = pd.read_html(str(table))[0]
            print(f"Table {i}: {len(df)} rows | Columns: {list(df.columns)}")
            
            # Print first row to help debugging
            if len(df) > 0:
                print("   First row example:", df.iloc[0].to_dict())
                print("-" * 60)
        except Exception as e:
            print(f"Table {i} failed to parse: {e}")
    
    print("\nDebug complete. Copy the output above and send it to me.")

if __name__ == "__main__":
    main()
