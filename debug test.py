import soccerdata as sd
import pandas as pd
import warnings

# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 1. Setup scraper
print("Initializing Scraper...")
fbref = sd.FBref(leagues='ENG-Premier League', seasons="2324")

# 2. Define Players (Double check these exact spellings from your previous test)
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
def standardize_cols(df):
    new_cols = []
    flat_cols = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) else str(col) for col in df.columns]
    
    for col in flat_cols:
        c_lower = col.lower()
        if 'date' in c_lower: new_cols.append('date')
        elif 'player' in c_lower: new_cols.append('player')
        elif 'game' in c_lower: new_cols.append('match_id') # KEY LINK
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

print(f"Debug: Unique Teams in Schedule: {team_stats['team'].unique()[:5]}")

# --- PROCESSING WITH DEBUG PRINTS ---
final_data = []

print("\n--- STARTING PROCESSING LOOP ---")
for player in top10_players:
    print(f"\n> Processing: {player}...")
    
    # 1. Filter Player
    p_log = player_stats[player_stats['player'] == player].copy()
    if p_log.empty:
        print(f"  ❌ FAILURE: Player not found in player_stats.")
        continue
    
    # 2. Identify Team
    # We take the most frequent team to avoid issues with transfers/national teams if present
    team_name = p_log['team'].mode()[0] 
    print(f"  -> Identified Team: '{team_name}'")
    
    # CHECK: Does this team exist in team_stats?
    if team_name not in team_stats['team'].values:
        print(f"  ❌ FAILURE: Team '{team_name}' NOT found in Team Schedule. (Check spelling?)")
        continue

    # 3. Merge Strategy (Link by match_id)
    # Check if we have match_ids
    if 'match_id' not in p_log.columns or 'match_id' not in team_stats.columns:
        print("  ❌ FAILURE: 'match_id' column missing. Cannot merge.")
        break
        
    merged_data = pd.merge(
        team_stats, 
        p_log[['match_id', 'minutes']], 
        on='match_id', 
        how='left'
    )
    
    # 4. Filter for Specific Team
    # This removes matches from other teams (if the dataset has multiple leagues mixed in)
    before_len = len(merged_data)
    merged_data = merged_data[merged_data['team'] == team_name].copy()
    
    if merged_data.empty:
        print(f"  ❌ FAILURE: Merge resulted in 0 rows. (Team filter '{team_name}' removed everything?)")
        continue

    # 5. Success Logic
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
    print(f"  ✅ SUCCESS: Added {len(clean_df)} games for {player}.")

# --- SAVE ---
if final_data:
    full_dataset = pd.concat(final_data)
    full_dataset = full_dataset.sort_values(by=['player_name', 'date'])
    full_dataset.to_csv("top10_players_team_performance.csv", index=False)
    print(f"\n✅ DONE. Saved {len(full_dataset)} total rows. ({len(final_data)}/10 players processed)")
else:
    print("\n❌ CRITICAL: No data collected.")