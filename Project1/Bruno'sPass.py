from mplsoccer import Sbopen, Pitch
import pandas as pd
import matplotlib.pyplot as plt

parser = Sbopen(dataframe=True)

player_id = 5204
player_name = "Bruno Fernandez"

# Removed 3938644
match_ids = [3942349, 3941020, 3930174, 3930166]

# -----------------------------
# Load event data + store team names
# -----------------------------
all_events = []
match_team_names = {}

for idx, m_id in enumerate(match_ids):
    df, related, freeze, tactics = parser.event(m_id)
    df['match_id'] = m_id 
    all_events.append(df)

    teams = df['team_name'].dropna().unique().tolist()
    if len(teams) == 2:
        if idx == 2:
            match_team_names[m_id] = f"{teams[1]} vs {teams[0]}"
        else:
            match_team_names[m_id] = f"{teams[0]} vs {teams[1]}"
    else:
        match_team_names[m_id] = f"Match {m_id}"

events = pd.concat(all_events, ignore_index=True)

# -----------------------------
# Filter passes + assists (using StatsBomb flags)
# -----------------------------
player_events = events[events['player_id'] == player_id].copy()
passes = player_events[player_events['type_name'] == 'Pass'].copy()

# Safely handle missing columns
if 'pass_shot_assist' in passes.columns:
    shot_assists = passes[passes['pass_shot_assist'] == True]
else:
    shot_assists = passes.iloc[0:0]

if 'pass_goal_assist' in passes.columns:
    goal_assists = passes[passes['pass_goal_assist'] == True]
else:
    goal_assists = passes.iloc[0:0]

# -----------------------------
# Match color map
# -----------------------------
colors = ['#032dff', '#03ff0b', '#ee03ff', '#ff7700']
color_map = dict(zip(match_ids, colors))

# -----------------------------
# Plot on horizontal pitch
# -----------------------------
pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(14, 9))

# Normal passes (with counts in legend)
for m_id in match_ids:
    match_passes = passes[passes['match_id'] == m_id]

    pass_count = len(match_passes)

    pitch.arrows(
        match_passes['x'], match_passes['y'],
        match_passes['end_x'], match_passes['end_y'],
        ax=ax,
        width=1.2, headwidth=4, headlength=4,
        color=color_map[m_id],
        alpha=1.00,
        label=f"{match_team_names[m_id]} — Passes: {pass_count}"
    )

# Shot assists (red)
pitch.arrows(
    shot_assists['x'], shot_assists['y'],
    shot_assists['end_x'], shot_assists['end_y'],
    ax=ax,
    width=3, headwidth=7, headlength=7,
    color='red', alpha=1.0,
    label=f"Shot Assists: {len(shot_assists)}"
)

# Goal assists (yellow)
pitch.arrows(
    goal_assists['x'], goal_assists['y'],
    goal_assists['end_x'], goal_assists['end_y'],
    ax=ax,
    width=3.5, headwidth=8, headlength=8,
    color='yellow', alpha=1.0,
    label=f"Goal Assists: {len(goal_assists)}"
)

plt.title(f"{player_name}: Passes, Shot Assists and Goal Assists (Euro 2024)", fontsize=16)
plt.legend(loc='upper right', fontsize=8)
plt.tight_layout()
plt.show()
