import pandas as pd
import numpy as np
import os

# --- PART 1: ROBUST FILE LOADING ---
filename = "top10_players_team_performance.csv"

# Check if file exists in the current directory
if os.path.exists(filename):
    print(f"✅ Found '{filename}' successfully.")
    df = pd.read_csv(filename)
else:
    # Try to find it in the same folder as the script (helps with VS Code/PyCharm)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    if os.path.exists(file_path):
        print(f"✅ Found '{filename}' using script path.")
        df = pd.read_csv(file_path)
    else:
        print("\n❌ CRITICAL ERROR: File not found.")
        print(f"   I looked for: '{filename}'")
        print(f"   I also looked in: '{script_dir}'")
        print("   Make sure 'scraper.py' ran successfully and the CSV is in this folder.")
        exit()

# --- PART 2: METRIC CALCULATOR ---
def calculate_metrics(group):
    games = len(group)
    if games == 0:
        return pd.Series({'Win Rate': 0.0, 'Avg xG Diff': 0.0, 'Games': 0})
    
    wins = len(group[group['result'] == 'W'])
    win_rate = (wins / games) * 100
    avg_xg_diff = (group['xG'] - group['xg_conceded']).mean()
    
    return pd.Series({
        'Win Rate': win_rate, 
        'Avg xG Diff': avg_xg_diff,
        'Games': games
    })

# --- PART 3: ANALYSIS LOOP ---
print("\n" + "="*80)
print(f"{'PLAYER IMPACT REPORT (2023-2024)':^80}")
print("="*80)
print(f"{'Player':<20} | {'Status':<8} | {'Win %':<6} | {'Games'}")
print("-" * 80)

impact_data = []
unique_players = df['player_name'].unique()

for player in unique_players:
    p_data = df[df['player_name'] == player]
    
    # Define Groups
    starter = p_data[p_data['Status'] == 'Starter']
    absent = p_data[p_data['Status'] == 'Absent']
    
    s_metrics = calculate_metrics(starter)
    a_metrics = calculate_metrics(absent)
    
    # Print Starter Stats (Always exists)
    print(f"{player:<20} | Start    | {s_metrics['Win Rate']:.1f}%  | {int(s_metrics['Games'])}")

    # Initialize impact variables
    win_impact = 0.0
    xg_impact = 0.0
    note = ""

    # Check if they have absent games to compare
    if a_metrics['Games'] > 0:
        print(f"{'':<20} | Absent   | {a_metrics['Win Rate']:.1f}%  | {int(a_metrics['Games'])}")
        
        # Calculate Impact
        win_impact = s_metrics['Win Rate'] - a_metrics['Win Rate']
        xg_impact = s_metrics['Avg xG Diff'] - a_metrics['Avg xG Diff']
        
        sign = "+" if win_impact > 0 else ""
        print(f"{'':<20} | IMPACT   | {sign}{win_impact:.1f}% |")
    else:
        # Player NEVER missed a game
        note = "Never missed a game"
        print(f"{'':<20} | Absent   | N/A     | 0")
        print(f"{'':<20} | IMPACT   | N/A     | ({note})")
        # We set impact to NaN or 0 so it appears in CSV
        win_impact = np.nan 
        xg_impact = np.nan

    print("-" * 80)

    # Append to list
    impact_data.append({
        'Player': player,
        'Team': p_data['team'].iloc[0],
        'Win Rate Impact': win_impact,
        'xG Impact': xg_impact,
        'Games Started': s_metrics['Games'],
        'Games Missed': a_metrics['Games'],
        'Note': note
    })

# --- PART 4: SAVE RESULTS ---
if impact_data:
    summary_df = pd.DataFrame(impact_data)
    # Sort: Put valid impacts first, then N/A
    summary_df = summary_df.sort_values(by='Win Rate Impact', ascending=False, na_position='last')
    
    summary_df.to_csv("player_impact_summary.csv", index=False)
    print(f"\n✅ SUCCESS: Processed {len(summary_df)} players.")
    print("   Data saved to 'player_impact_summary.csv'.")
else:
    print("\n⚠️  No data processed.")
