import pandas as pd

# 1. Load your clean data
df = pd.read_csv("top10_players_team_performance.csv")

# 2. Define a helper to calculate points/win rate
def calculate_metrics(group):
    games = len(group)
    if games == 0: return pd.Series({'Win Rate': 0, 'Avg xG Diff': 0, 'Games': 0})
    
    # Calculate Wins (assuming 'W' is the result string for Win)
    wins = len(group[group['result'] == 'W'])
    win_rate = (wins / games) * 100
    
    # Calculate Average xG Differential
    avg_xg_diff = (group['xG'] - group['xg_conceded']).mean()
    
    return pd.Series({
        'Win Rate': round(win_rate, 1), 
        'Avg xG Diff': round(avg_xg_diff, 2),
        'Games': games
    })

# 3. Group by Player and Status
print("\n--- PLAYER IMPACT REPORT (2023-2024) ---")
print(f"{'Player':<20} | {'Status':<8} | {'Win %':<6} | {'xG Diff':<8} | {'Games'}")
print("-" * 65)

impact_data = []
unique_players = df['player_name'].unique()

for player in unique_players:
    p_data = df[df['player_name'] == player]
    
    # Compare "Starter" vs "Absent"
    starter = p_data[p_data['Status'] == 'Starter']
    absent = p_data[p_data['Status'] == 'Absent']
    
    s_metrics = calculate_metrics(starter)
    a_metrics = calculate_metrics(absent)
    
    # Print Starter Stats
    print(f"{player:<20} | Start    | {s_metrics['Win Rate']}%  | {s_metrics['Avg xG Diff']}     | {int(s_metrics['Games'])}")

    # Check if they have absent games to compare
    if a_metrics['Games'] > 0:
        print(f"{'':<20} | Absent   | {a_metrics['Win Rate']}%  | {a_metrics['Avg xG Diff']}     | {int(a_metrics['Games'])}")
        
        # Calculate Impact
        win_impact = s_metrics['Win Rate'] - a_metrics['Win Rate']
        xg_impact = s_metrics['Avg xG Diff'] - a_metrics['Avg xG Diff']
        print(f"{'':<20} | IMPACT   | {win_impact:+.1f}% | {xg_impact:+.2f}    |")
        
        impact_data.append({
            'Player': player,
            'Win Rate Impact': win_impact,
            'xG Impact': xg_impact,
            'Games Missed': a_metrics['Games']
        })
    else:
        # Player never missed a game
        print(f"{'':<20} | Absent   | N/A     | N/A          | 0")
        print(f"{'':<20} | IMPACT   | N/A     | N/A          |")

    print("-" * 65)

# Save summary
if impact_data:
    summary_df = pd.DataFrame(impact_data)
    summary_df.to_csv("player_impact_summary.csv", index=False)
    print("\n✅ Impact analysis saved (for players with absent games).")