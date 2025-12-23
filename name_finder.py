import soccerdata as sd
import pandas as pd

# Initialize
fbref = sd.FBref(leagues='ENG-Premier League', seasons="2324")
player_stats = fbref.read_player_match_stats(stat_type="summary")
player_stats = player_stats.reset_index()

# Flatten columns (standard cleanup)
player_stats.columns = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) else str(col) for col in player_stats.columns]

# Get all unique player names in the database
all_players = player_stats[player_stats.columns[4]].unique() # Column 4 is usually 'player'

print("\n--- NAME CHECKER ---")
# List of players who might be missing or mismatched
check_list = ["Son", "Haaland", "Salah", "Saka", "Isak", "Watkins", "Foden", "Palmer", "Solanke", "Bowen"]

for check in check_list:
    # Find names that look similar
    matches = [p for p in all_players if check.lower() in str(p).lower()]
    print(f"Searching for '{check}': Found -> {matches}")