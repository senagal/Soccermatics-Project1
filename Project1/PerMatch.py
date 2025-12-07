from mplsoccer import Sbopen
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
# -----------------------------
# Setup
# -----------------------------
parser = Sbopen(dataframe=True)
competition_id = 55   # Euro 2024
season_id = 282
player_id_focus = 5204
target_positions = [9, 11, 19]

# -----------------------------
# Load all matches
# -----------------------------
matches = parser.match(competition_id=competition_id, season_id=season_id)
match_ids = matches['match_id'].tolist()

# -----------------------------
# Collect assists for target positions in each match
# -----------------------------
all_assists = []

for match_id in match_ids:
    df, related, freeze, tactics = parser.event(match_id)
    
    # Filter passes of players in target positions
    position_passes = df[(df['type_name'] == 'Pass') & (df['position_id'].isin(target_positions))]
    
    # Shot assists: any pass that assisted a shot
    shot_assists = position_passes[position_passes['pass_assisted_shot_id'].notna()].copy()
    shot_assists['outcome'] = 'Shot Assist'
    
    # Goal assists: same pass, but the shot resulted in a goal
    goal_assists = position_passes[
        (position_passes['pass_assisted_shot_id'].notna()) &
        (position_passes['outcome_name'] == 'Goal')
    ].copy()
    goal_assists['outcome'] = 'Goal Assist'
        
    # Combine
    assists = pd.concat([shot_assists, goal_assists], ignore_index=True)
    assists['match_id'] = match_id
    all_assists.append(assists[['player_id', 'player_name', 'position_id', 'outcome', 'match_id']])

# Combine all matches
assists_df = pd.concat(all_assists, ignore_index=True)

# -----------------------------
# Count assists per player per match
# -----------------------------
player_matches = assists_df.groupby(['player_id', 'player_name', 'match_id']).size().reset_index(name='assists')

# Compute per-match normalization
player_totals = player_matches.groupby(['player_id', 'player_name'])['assists'].mean().reset_index()
player_totals = player_totals.sort_values('assists', ascending=True).reset_index(drop=True)
# -----------------------------
# Plotting
# -----------------------------
fig, ax = plt.subplots(figsize=(12, len(player_totals)*0.5))  # wider and taller

bars = ax.barh(player_totals['player_name'], player_totals['assists'], color='skyblue')

# Highlight player 5204
focus_idx = player_totals[player_totals['player_id'] == player_id_focus].index[0]
bars[focus_idx].set_color('red')

# Labels and title
ax.set_xlabel('Average Assists per Match')
ax.set_ylabel('Players (Positions 9, 11, 19)')
ax.set_title('Normalized Assists per Match - Player 5204 vs Other Forwards/Attacking Midfielders (Euro 2024)')

# Make x-axis sequential integers starting at 1
max_assists = int(player_totals['assists'].max())
ax.set_xticks(range(0, max_assists+1))  # 0,1,2,... up to max
ax.set_xticklabels(range(0, max_assists+1))

plt.tight_layout()
plt.show()
