import soccerdata as sd
import pandas as pd
import warnings

# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 1. Setup scraper
print("Initializing Scraper...")
fbref = sd.FBref(leagues='ENG-Premier League', seasons="2324")

# 2. Define Players
top10_players = [
    "Cole Palmer", "Erling Haaland", "Ollie Watkins", "Mohamed Salah",
    "Phil Foden", "Son Heung-min", "Bukayo Saka", "Alexander Isak",
    "Dominic Solanke", "Jarrod Bowen"
]

# --- LOAD DATA ---
print("Step 1: Fetching Team Schedule (Dates & xG)...")
team_stats = fbref.read_team_match_stats(stat_type="schedule")
team_stats = team_stats.reset_index()

print("Step 2: Fetching Player Match Logs...")
player_stats = fbref.read_player_match_stats(stat_type="summary")
player_stats = player_stats.reset_index()

# --- AGGRESSIVE COLUMN CLEANING ---
def standardize_cols(df):
    new_cols = []
    # Flatten MultiIndex
    flat_cols = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) else str(col) for col in df.columns]
    
    for col in flat_cols:
        c_lower = col.lower()
        # Map common keywords to standard names
        if 'date' in c_lower:
            new_cols.append('date')
        elif 'player' in c_lower:
            new_cols.append('player')
        elif 'game' in c_lower: # This is the KEY LINK
            new_cols.append('match_id')
        elif 'min' in c_lower and 'ex' not in c_lower: 
            new_cols.append('minutes')
        elif 'team' in c_lower and 'opponent' not in c_lower:
            new_cols.append('team')
        elif 'opponent' in c_lower:
            new_cols.append('opponent')
        elif 'result' in c_lower:
            new_cols.append('result')
        elif 'xg' in c_lower and 'conceded' not in c_lower and 'expected' in c_lower:
            new_cols.append('xG')
        elif 'xg' in c_lower and 'conceded' in c_lower:
            new_cols.append('xg_conceded')
        else:
            new_cols.append(col)
            
    df.columns = new_cols
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    return df

print("Standardizing column names...")
team_stats = standardize_cols(team_stats)
player_stats = standardize_cols(player_stats)

print(f"Debug - Team Keys: {team_stats.columns.tolist()[:5]}")
print(f"Debug - Player Keys: {player_stats.columns.tolist()[:5]}")

# --- PROCESSING ---
final_data = []

for player in top10_players:
    print(f"Processing data for {player}...")
    
    # 1. Get Player Logs
    if 'player' not in player_stats.columns:
        print("CRITICAL: Player column missing.")
        break

    p_log = player_stats[player_stats['player'] == player].copy()
    
    if p_log.empty:
        print(f"  -> No data found for {player}")
        continue
    
    # 2. MERGE STRATEGY CHANGE
    # We do NOT try to convert p_log['date'] because it doesn't exist.
    # We merge p_log with team_stats using 'team' and 'match_id'.
    # This brings the 'date' FROM team_stats INTO p_log.
    
    # Ensure keys exist
    if 'match_id' not in p_log.columns or 'match_id' not in team_stats.columns:
        print("CRITICAL: 'match_id' (game) column missing in one of the dataframes.")
        break
        
    merged_data = pd.merge(
        team_stats, 
        p_log[['match_id', 'minutes']], # We only need the Link (ID) and the Stats (Minutes)
        on='match_id', 
        how='left'
    )
    
    # Filter for the specific team the player belongs to
    # (Get the player's most recent team to filter the schedule)
    current_team = p_log['team'].iloc[-1]
    merged_data = merged_data[merged_data['team'] == current_team].copy()

    # 3. Logic
    merged_data['minutes_played'] = merged_data['minutes'].fillna(0)
    
    merged_data['Status'] = merged_data['minutes_played'].apply(
        lambda x: "Starter" if x >= 45 else ("Sub" if x > 0 else "Absent")
    )
    merged_data['player_name'] = player
    
    # 4. Clean & Select
    # Now 'date' exists because we pulled it from team_stats
    clean_df = pd.DataFrame()
    clean_df['date'] = pd.to_datetime(merged_data['date'])
    clean_df['player_name'] = merged_data['player_name']
    clean_df['team'] = merged_data['team']
    clean_df['opponent'] = merged_data['opponent']
    clean_df['result'] = merged_data['result']
    
    # Handle xG safely
    clean_df['xG'] = merged_data['xG'] if 'xG' in merged_data.columns else 0
    clean_df['xg_conceded'] = merged_data['xg_conceded'] if 'xg_conceded' in merged_data.columns else 0
    
    clean_df['Status'] = merged_data['Status']
    clean_df['minutes_played'] = merged_data['minutes_played']

    final_data.append(clean_df)

# --- SAVE ---
if final_data:
    full_dataset = pd.concat(final_data)
    full_dataset = full_dataset.sort_values(by=['player_name', 'date'])
    full_dataset.to_csv("top10_players_team_performance.csv", index=False)
    print("\n✅ Success! Data saved to 'top10_players_team_performance.csv'")
    print(full_dataset.head())
else:
    print("No data to save.")