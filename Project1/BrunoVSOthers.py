from mplsoccer import Sbopen
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# Setup
# -------------------------------------------------------------
parser = Sbopen(dataframe=True)
competition_id = 55     # Euro 2024
season_id = 282
player_id_focus = 5204
target_positions = [9, 11, 19]

# -------------------------------------------------------------
# Load matches
# -------------------------------------------------------------
matches = parser.match(competition_id=competition_id, season_id=season_id)
match_ids = matches['match_id'].tolist()

all_assists = []

# -------------------------------------------------------------
# Helper: compute minutes played from event times
# -------------------------------------------------------------
def compute_minutes(df, player_id):
    pdf = df[df['player_id'] == player_id]

    if pdf.empty:
        return 0

    return pdf['minute'].max() - pdf['minute'].min()

# -------------------------------------------------------------
# Loop over matches
# -------------------------------------------------------------
for match_id in match_ids:

    df, related, freeze, tactics = parser.event(match_id)

    # Compute minutes for each player in the match
    unique_players = df['player_id'].dropna().unique()
    minutes = {pid: compute_minutes(df, pid) for pid in unique_players}

    # Filter passes by target positions
    position_passes = df[
        (df['type_name'] == 'Pass') &
        (df['position_id'].isin(target_positions))
    ]

    # Shot assists
    shot_assists = position_passes[position_passes['pass_assisted_shot_id'].notna()].copy()
    shot_assists['outcome'] = 'Shot Assist'

    # Goal assists
    goal_assists = position_passes[
        (position_passes['pass_assisted_shot_id'].notna()) &
        (position_passes['outcome_name'] == 'Goal')
    ].copy()
    goal_assists['outcome'] = 'Goal Assist'

    # Combine assists
    assists = pd.concat([shot_assists, goal_assists], ignore_index=True)
    assists['match_id'] = match_id
    assists['minutes_played'] = assists['player_id'].map(minutes)

    all_assists.append(
        assists[['player_id', 'player_name', 'position_id', 'outcome',
                 'match_id', 'minutes_played']]
    )

# -------------------------------------------------------------
# Combine all matches
# -------------------------------------------------------------
assists_df = pd.concat(all_assists, ignore_index=True)

# Group by match + minutes
player_matches = assists_df.groupby(
    ['player_id', 'player_name', 'match_id', 'minutes_played']
).size().reset_index(name='assists')

# -------------------------------------------------------------
# Normalize: assists per 90 minutes
# -------------------------------------------------------------
player_matches['assists_per_90'] = (
    player_matches['assists'] / player_matches['minutes_played'] * 90
)

# Average across all matches
player_totals = player_matches.groupby(['player_id', 'player_name'])[
    'assists_per_90'
].mean().reset_index()

# -------------------------------------------------------------
# Fix: sort and reset index to highlight the correct player
# -------------------------------------------------------------
player_totals = player_totals.sort_values('assists_per_90').reset_index(drop=True)

# -------------------------------------------------------------
# Plot
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, len(player_totals) * 0.5))

bars = ax.barh(player_totals['player_name'], player_totals['assists_per_90'])

# Highlight target player correctly
focus_idx = player_totals[player_totals['player_id'] == player_id_focus].index[0]
bars[focus_idx].set_color('red')

ax.set_xlabel("Assists per 90 minutes")
ax.set_ylabel("Players (Positions 9, 11, 19)")
ax.set_title("Assists Normalized Per 90 Minutes – Euro 2024")

plt.tight_layout()
plt.show()
