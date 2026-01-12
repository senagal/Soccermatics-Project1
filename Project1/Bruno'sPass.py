from mplsoccer import Sbopen, Pitch
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

parser = Sbopen(dataframe=True)

player_id = 5204
player_name = "Bruno's"
match_ids = [3942349, 3941020, 3930174, 3930166]

# Colors for each match
match_colors = {
    3942349: 'darkgreen',
    3941020: 'darkred',
    3930174: 'darkblue',
    3930166: 'purple'
}

# Load match info (home/away, teams)
matches = parser.match(55, 282)
match_info = matches[matches['match_id'].isin(match_ids)][
    ['match_id', 'home_team_name', 'away_team_name']
]


# Map match_id to name for legend
match_names = {
    m_id: f"{row['home_team_name']} vs {row['away_team_name']}"
    for m_id, row in match_info.set_index('match_id').iterrows()
}

# Horizontal StatsBomb pitch
pitch = Pitch(pitch_type='statsbomb', line_color='black')
pitch_length = pitch.dim.length
pitch_width = pitch.dim.width

# Define zones: 3 vertical thirds × 2 horizontal halves = 6 zones
x_bins = [0, pitch_length/3, 2*pitch_length/3, pitch_length]
y_bins = [0, pitch_width/2, pitch_width]

# Prepare a figure
fig, ax = pitch.draw(figsize=(14, 10))

# Draw zone lines
for xb in x_bins[1:-1]:
    ax.plot([xb, xb], [0, pitch_width], linestyle='--', color='gray')
for yb in y_bins[1:-1]:
    ax.plot([0, pitch_length], [yb, yb], linestyle='--', color='gray')

# Dictionary to hold counts and arrow info for all matches per zone
zone_data = {(xz, yz): {} for xz in range(3) for yz in range(2)}

# Dictionary to store summary table
summary_table = {m_id: [0]*6 for m_id in match_ids}  # 6 zones

# Process each match
for m_id in match_ids:
    df, _, _, _ = parser.event(m_id)

    # Match info
    home = match_info[match_info['match_id'] == m_id]['home_team_name'].values[0]
    away = match_info[match_info['match_id'] == m_id]['away_team_name'].values[0]

    # Player passes
    passes = df[(df['player_id'] == player_id) & (df['type_name'] == 'Pass')].copy()
    if passes.empty:
        continue

    # Assign zones
    passes['x_zone'] = pd.cut(passes['x'], bins=x_bins, labels=False, include_lowest=True)
    passes['y_zone'] = pd.cut(passes['y'], bins=y_bins, labels=False, include_lowest=True)
    passes = passes.dropna(subset=['x_zone','y_zone'])
    passes['x_zone'] = passes['x_zone'].astype(int)
    passes['y_zone'] = passes['y_zone'].astype(int)

    # Color for this match
    color = match_colors[m_id]

    # Group by zone
    grouped = passes.groupby(['x_zone', 'y_zone'])
    for (xz, yz), group in grouped:
        if group.empty:
            continue

        # Save data for this zone and match
        count = len(group)
        avg_dx = (group['end_x'] - group['x']).mean()
        avg_dy = (group['end_y'] - group['y']).mean()
        avg_start_x = group['x'].mean()
        avg_start_y = group['y'].mean()

        zone_data[(xz, yz)][m_id] = {
            'count': count,
            'start_x': avg_start_x,
            'start_y': avg_start_y,
            'dx': avg_dx,
            'dy': avg_dy
        }

        # Map zone to 1-6 for summary: top-left=1, top-middle=2, ..., bottom-right=6
        zone_index = yz * 3 + xz  # yz=0(top), 1(bottom); xz=0(left),1,2(right)
        summary_table[m_id][zone_index] = count

# Plot counts and arrows for each zone and match
for (xz, yz), matches_info in zone_data.items():
    x0, x1 = x_bins[xz], x_bins[xz+1]
    y0, y1 = y_bins[yz], y_bins[yz+1]
    xc, yc = (x0 + x1)/2, (y0 + y1)/2

    # Offset for text to avoid overlap
    offsets = np.linspace(-8, 8, len(matches_info))
    for i, (m_id, data) in enumerate(matches_info.items()):
        ax.text(xc + offsets[i], yc, str(data['count']),
                ha='center', va='center', fontsize=12, fontweight='bold',
                color=match_colors[m_id])
        pitch.arrows(data['start_x'], data['start_y'],
                     data['start_x'] + data['dx'], data['start_y'] + data['dy'],
                     ax=ax, color=match_colors[m_id], width=2, headwidth=5, headlength=5)

import matplotlib.lines as mlines

# Create legend using match names with proxy lines
legend_handles = []
for m_id, color in match_colors.items():
    handle = mlines.Line2D([], [], color=color, marker='o', linestyle='None',
                           markersize=8, label=match_names[m_id])
    legend_handles.append(handle)

ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.05),
          ncol=2, fontsize=12)

# Title
plt.title(f"{player_name} – Merged pass Pitch Map for EURO 2024\nCounts and Average Pass Directions per Zone",
          fontsize=16)
plt.show()

# Output summary
for m_id, counts in summary_table.items():
    print(f"{match_names[m_id]}: Zones 1–6 counts -> {counts}")
