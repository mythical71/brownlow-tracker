import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

WEIGHTS = {
    'disposals': 0.25,
    'contested_possessions': 0.15,
    'clearances': 0.12,
    'tackles': 0.10,
    'goals': 0.08,
    'marks': 0.05,
    'contested_marks': 0.05,
    'rebound_50s': 0.04,      # strong proxy for intercept work
    'goal_assists': 0.02,
    'hitouts': 0.02,
    'kicks': 0.01,
    'handballs': 0.01,
    'behinds': 0.01
}

URL = "https://afltables.com/afl/stats/2026.html"

def fetch_latest_stats():
    print(f"[{datetime.now()}] Downloading 2026 stats from AFL Tables...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    
    all_dfs = []
    for table in tables:
        try:
            df = pd.read_html(str(table))[0]
            if len(df) > 5 and 'Player' in str(df.columns):
                df.columns = [str(col).strip() for col in df.columns]
                
                # Actual 2026 column mapping
                rename_map = {
                    'K': 'kicks',
                    'H': 'handballs',
                    'D': 'disposals',
                    'M': 'marks',
                    'CM': 'contested_marks',
                    'T': 'tackles',
                    'G': 'goals',
                    'B': 'behinds',
                    'HO': 'hitouts',
                    'C': 'clearances',
                    'CP': 'contested_possessions',
                    'GA': 'goal_assists',
                    'R': 'rebound_50s'
                }
                df = df.rename(columns=rename_map)
                
                if 'Player' in df.columns:
                    df = df.rename(columns={'Player': 'player_name'})
                
                # Calculate disposals if missing
                if 'disposals' not in df.columns and 'kicks' in df.columns and 'handballs' in df.columns:
                    df['disposals'] = df['kicks'].fillna(0) + df['handballs'].fillna(0)
                
                for col in WEIGHTS.keys():
                    if col not in df.columns:
                        df[col] = 0
                
                all_dfs.append(df)
        except:
            continue
    
    if all_dfs:
        full_df = pd.concat(all_dfs, ignore_index=True)
        full_df = full_df.dropna(subset=['player_name'])
        full_df['player_name'] = full_df['player_name'].astype(str).str.replace(r'\[.*?\]', '', regex=True).str.strip()
        print(f"✅ Loaded {len(full_df)} player records.")
        return full_df
    else:
        raise ValueError("No stats tables found.")

def main():
    stats = fetch_latest_stats()
    df = stats.copy()
    df['score'] = 0.0
    for stat, w in WEIGHTS.items():
        if stat in df.columns:
            df['score'] += df[stat].fillna(0) * w
    
    df = df.sort_values('score', ascending=False).reset_index(drop=True)
    
    df['predicted_votes'] = 0
    if len(df) >= 1: df.loc[0, 'predicted_votes'] = 3
    if len(df) >= 2: df.loc[1, 'predicted_votes'] = 2
    if len(df) >= 3: df.loc[2, 'predicted_votes'] = 1
    df['predicted_points'] = df['predicted_votes']
    
    json_data = df[['player_name', 'predicted_points', 'score']].to_dict(orient='records')
    with open('brownlow_leaderboard.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print("\n=== TOP 15 PREDICTED BROWNLOW LEADERBOARD ===\n")
    print(df[['player_name', 'predicted_points']].head(15).to_string(index=False))
    print("\n✅ brownlow_leaderboard.json updated successfully.")

if __name__ == "__main__":
    main()
