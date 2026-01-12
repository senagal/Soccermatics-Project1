from mplsoccer import Sbopen, Pitch
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

parser = Sbopen(dataframe=True)

player_id = 5204
player_name = "Player X"
match_ids = [3942349, 3941020, 3938644, 3930174, 3930166]

# Load match info (home/away, teams)
matches = parser.match(55, 282)
match_info = matches[matches['match_id'].isin(match_ids)][
    ['match_id', 'home_team_name', 'away_team_name']
]

# Horizontal StatsBomb pitch
pitch = Pitch(pitch_type='statsbomb', line_color='black')

# Get pitch dimensions correctly
pitch_length = pitch.dim.length   # usually 120 for StatsBomb
pitch_width = pitch.dim.width     # usually 80 for StatsBomb

# Define zones: 3 vertical thirds × 2 horizontal halves = 6 zones
x_bins = [0, pitch_length/3, 2*pitch_length/3, pitch_length]
y_bins = [0, pitch_width/2, pitch_width]

# Loop for each match
for m_id in match_ids:

    df, _, _, _ = parser.event(m_id)

    # Match info
    home = match_info[match_info['match_id'] == m_id]['home_team_name'].values[0]
    away = match_info[match_info['match_id'] == m_id]['away_team_name'].values[0]

    if home == "Portugal":
        portugal_side = "Home (Left → Right)"
        opponent = away
    else:
        portugal_side = "Away (Right → Left)"
        opponent = home

    # Player passes
    passes = df[(df['player_id'] == player_id) & (df['type_name'] == 'Pass')].copy()
    if passes.empty:
        continue

    # Assign zones safely
    passes['x_zone'] = pd.cut(passes['x'], bins=x_bins, labels=False, include_lowest=True)
    passes['y_zone'] = pd.cut(passes['y'], bins=y_bins, labels=False, include_lowest=True)

    # Drop rows with NaN zones (outside pitch or missing coords)
    passes = passes.dropna(subset=['x_zone','y_zone'])

    # Convert to int for indexing
    passes['x_zone'] = passes['x_zone'].astype(int)
    passes['y_zone'] = passes['y_zone'].astype(int)

    # -------------------------------
    # Plot
    # -------------------------------
    fig, ax = pitch.draw(figsize=(12, 8))

    # Draw broken lines for zones (stop at pitch boundaries)
    for xb in x_bins[1:-1]:
        ax.plot([xb, xb], [0, pitch_width], linestyle='--', color='gray')
    for yb in y_bins[1:-1]:
        ax.plot([0, pitch_length], [yb, yb], linestyle='--', color='gray')

    # For each zone: count passes + average arrow
    grouped = passes.groupby(['x_zone', 'y_zone'])
    for (xz, yz), group in grouped:
        if group.empty:
            continue

        # Zone boundaries
        x0, x1 = x_bins[xz], x_bins[xz+1]
        y0, y1 = y_bins[yz], y_bins[yz+1]
        xc, yc = (x0 + x1) / 2, (y0 + y1) / 2

        # Count
        count = len(group)
        ax.text(xc, yc, count, ha='center', va='center',
                fontsize=14, fontweight='bold', color='blue')

        # Average arrow for this zone
        avg_dx = (group['end_x'] - group['x']).mean()
        avg_dy = (group['end_y'] - group['y']).mean()
        avg_start_x = group['x'].mean()
        avg_start_y = group['y'].mean()

        pitch.arrows(avg_start_x, avg_start_y,
                     avg_start_x + avg_dx, avg_start_y + avg_dy,
                     ax=ax, color='red', width=2, headwidth=5, headlength=5)

    # Title
    plt.title(
        f"{player_name} – Match {m_id}\n"
        f"Portugal vs {opponent} | Portugal: {portugal_side}",
        fontsize=15
    )
    plt.show()
