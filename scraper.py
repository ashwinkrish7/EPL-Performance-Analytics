import soccerdata as sd
import pandas as pd
import time
import warnings

# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 1. Setup
print("Initializing Scraper...")
fbref = sd.FBref(leagues='ENG-Premier League', seasons="2324")

# 2. Define Players (Using the correct names we found)
top10_players = [
    "Cole Palmer", "Erling Haaland", "Ollie Watkins", "Mohamed Salah",
    "Phil Foden", "Son Heung-min", "Bukayo Saka", "Alexander Isak",
    "Dominic Solanke", "Jarrod Bowen"
]

# --- LOAD DATA ---
print("Step 1: Fetching Team Schedule...")
team_stats = fbref.read_team_match_stats(stat_type="schedule").reset_index()

print("Step 2: Fetching Player Logs...")
player_stats = fbref.read_player_match_stats(stat_type="summary").reset_index()

# --- STANDARDIZE COLUMNS ---
# (Keeps column names consistent across different data updates)
def standardize_cols(df):
    new_cols = []
    flat_cols = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) else str(col) for col in df.columns]
    
    for col in flat_cols:
        c_lower = col.lower()
        if 'date' in c_lower: new_cols.append('date')
        elif 'player' in c_lower: new_cols.append('player')
        elif 'game' in c_lower: new_cols.append('match_id') 
        elif 'min' in c_lower and 'ex' not in c_lower: new_cols.append('minutes')
        elif 'team' in c_lower and 'opponent' not in c_lower: new_cols.append('team')
        elif 'opponent' in c_lower: new_cols.append('opponent')
        elif 'result' in c_lower: new_cols.append('result')
        elif 'xg' in c_lower and 'conceded' not in c_lower and 'expected' in c_lower: new_cols.append('xG')
        elif 'xg' in c_lower and 'conceded' in c_lower: new_cols.append('xg_conceded')
        else: new_cols.append(col)
    
    df.columns = new_cols
    return df.loc[:, ~df.columns.duplicated()]

team_stats = standardize_cols(team_stats)
player_stats = standardize_cols(player_stats)

# --- PROCESSING LOOP ---
final_data = []

# *** FIX: TEAM NAME TRANSLATOR ***
# This dictionary maps the Player Log name -> Team Schedule name
team_name_map = {
    "Tottenham Hotspur": "Tottenham",
    "Newcastle United": "Newcastle Utd",
    "West Ham United": "West Ham"
}

print("\n--- STARTING MERGE ---")
for player in top10_players:
    print(f"Processing {player}...")
    
    # 1. Filter Player
    p_log = player_stats[player_stats['player'] == player].copy()
    if p_log.empty:
        print(f"Skipping {player} (Not found)")
        continue
    
    # 2. Identify Team
    raw_team_name = p_log['team'].mode()[0]
    
    # *** APPLY FIX HERE ***
    # If the name is in our map, use the mapped version. Otherwise, use the original.
    team_name = team_name_map.get(raw_team_name, raw_team_name)
    
    # 3. Merge
    merged_data = pd.merge(
        team_stats, 
        p_log[['match_id', 'minutes']], 
        on='match_id', 
        how='left'
    )
    
    # 4. Filter for Specific Team
    merged_data = merged_data[merged_data['team'] == team_name].copy()
    
    if merged_data.empty:
        print(f"Warning: No data found for {player} (Check team mapping for '{team_name}')")
        continue

    # 5. Add Status Logic
    merged_data['minutes_played'] = merged_data['minutes'].fillna(0)
    merged_data['Status'] = merged_data['minutes_played'].apply(
        lambda x: "Starter" if x >= 45 else ("Sub" if x > 0 else "Absent")
    )
    merged_data['player_name'] = player
    
    # Select Clean Columns
    clean_df = pd.DataFrame()
    clean_df['date'] = pd.to_datetime(merged_data['date'])
    clean_df['player_name'] = merged_data['player_name']
    clean_df['team'] = merged_data['team']
    clean_df['result'] = merged_data['result']
    clean_df['xG'] = merged_data['xG'] if 'xG' in merged_data.columns else 0
    clean_df['xg_conceded'] = merged_data['xg_conceded'] if 'xg_conceded' in merged_data.columns else 0
    clean_df['Status'] = merged_data['Status']
    
    final_data.append(clean_df)

# --- SAVE TO CSV ---
if final_data:
    full_dataset = pd.concat(final_data)
    full_dataset = full_dataset.sort_values(by=['player_name', 'date'])
    full_dataset.to_csv("top10_players_team_performance.csv", index=False)
    print(f"\n✅ SUCCESS! Saved {len(full_dataset)} rows for {len(final_data)}/10 players.")
else:
    print("❌ No data saved.")
