from mplsoccer import Sbopen, Pitch
import pandas as pd
import matplotlib.pyplot as plt

parser = Sbopen(dataframe=True)

player_id = 5204
player_name = "Player X"
match_ids = [3942349, 3941020, 3938644, 3930174, 3930166]

# -----------------------------------------
# Load match info (home/away, teams)
# -----------------------------------------
matches = parser.match(55, 282)  # Euro 2024

match_info = matches[matches['match_id'].isin(match_ids)][
    ['match_id', 'home_team_name', 'away_team_name']
]

# -----------------------------------------
# Load events per match
# -----------------------------------------
all_events = {}
for m_id in match_ids:
    df, related, freeze, tactics = parser.event(m_id)
    all_events[m_id] = df

# -----------------------------------------
# Use HORIZONTAL pitch
# -----------------------------------------
pitch = Pitch(pitch_type='statsbomb', line_color='black')

# -----------------------------------------
# Loop for separate plots
# -----------------------------------------
for m_id in match_ids:

    df = all_events[m_id]

    # Basic match info
    home = match_info[match_info['match_id'] == m_id]['home_team_name'].values[0]
    away = match_info[match_info['match_id'] == m_id]['away_team_name'].values[0]

    if home == "Portugal":
        portugal_side = "Home (Left → Right)"
        opponent = away
    else:
        portugal_side = "Away (Right → Left)"
        opponent = home

    # -----------------------------
    # Filter only the player's passes
    # -----------------------------
    player_events = df[df['player_id'] == player_id]
    passes = player_events[player_events['type_name'] == 'Pass']

    # Shot assists (key passes)
    shot_assists = passes[passes['pass_shot_assist'] == True] \
        if 'pass_shot_assist' in passes.columns else passes.iloc[0:0]

    # Goal assists
    goal_assists = passes[passes['pass_goal_assist'] == True] \
        if 'pass_goal_assist' in passes.columns else passes.iloc[0:0]

    # -----------------------------
    # Create pitch figure
    # -----------------------------
    fig, ax = pitch.draw(figsize=(12, 8))

    # Normal passes (black)
    pitch.arrows(
        passes['x'], passes['y'], passes['end_x'], passes['end_y'],
        ax=ax, color='black', alpha=0.4, width=1,
        headwidth=3, headlength=3, label="Passes"
    )

    # Shot assists (green)
    pitch.arrows(
        shot_assists['x'], shot_assists['y'],
        shot_assists['end_x'], shot_assists['end_y'],
        ax=ax, color='green', alpha=1.0, width=2.5,
        headwidth=6, headlength=6, label="Shot Assists"
    )

    # Goal assists (red)
    pitch.arrows(
        goal_assists['x'], goal_assists['y'],
        goal_assists['end_x'], goal_assists['end_y'],
        ax=ax, color='red', alpha=1.0, width=3,
        headwidth=7, headlength=7, label="Goal Assists"
    )

    # -----------------------------
    # Title
    # -----------------------------
    plt.title(
        f"{player_name} – Match {m_id}\n"
        f"Portugal vs {opponent} | Portugal: {portugal_side}",
        fontsize=15
    )

    plt.legend(loc='upper right')
    plt.show()
