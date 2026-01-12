from mplsoccer import Sbopen, Pitch
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.lines as mlines
import plotly.express as px

st.set_page_config(page_title="Bruno vs Other midfielders in the EURO 2024", layout="wide")

# ---------------------------
# Load Data from CSV
# ---------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(__file__)
    CSV_PATH = os.path.join(BASE_DIR, "euro2024_midfielders_summary_360plus.csv")
    return pd.read_csv(CSV_PATH)

full_stats = load_data()

# ---------------------------
# Constants
# ---------------------------
BRUNO_ID = 5204
DEBRUYNE_ID = 3089
PLAYER_ID = BRUNO_ID
PLAYER_NAME = "Bruno Fernandes"

st.title("Bruno's passes in the matches he played in EURO 2024")

# ---------------------------
# StatsBomb parser
# ---------------------------
parser = Sbopen(dataframe=True)

# ---------------------------
# Match list
# ---------------------------
all_match_ids = [3942349, 3941020, 3930174, 3930166]

# Load match info
matches = parser.match(55, 282)
match_info = matches[matches['match_id'].isin(all_match_ids)][
    ['match_id', 'home_team_name', 'away_team_name']
]

# Map match_id to name
match_names = {
    m_id: f"{row['home_team_name']} vs {row['away_team_name']}"
    for m_id, row in match_info.set_index('match_id').iterrows()
}

# Colors for each match
match_colors = {
    3942349: 'darkgreen',
    3941020: 'darkred',
    3930174: 'darkblue',
    3930166: 'purple'
}

# ---------------------------
# UI: match selector
# ---------------------------
selected_match_ids = st.multiselect(
    "Select matches to display",
    options=all_match_ids,
    format_func=lambda x: match_names[x],
    default=all_match_ids
)

# ---------------------------
# Load events
# ---------------------------
@st.cache_data
def load_events(match_ids):
    all_events = []
    for m_id in match_ids:
        df, _, _, _ = parser.event(m_id)
        df["match_id"] = m_id
        all_events.append(df)
    return pd.concat(all_events, ignore_index=True)

if selected_match_ids:
    events = load_events(selected_match_ids)

    # Player passes
    player_events = events[events["player_id"] == PLAYER_ID].copy()
    passes = player_events[player_events["type_name"] == "Pass"].copy()

    # ---------------------------
    # Zone-based pitch map
    # ---------------------------
    pitch = Pitch(pitch_type='statsbomb', line_color='black')
    pitch_length = pitch.dim.length
    pitch_width = pitch.dim.width

    # Define zones: 3 vertical thirds × 2 horizontal halves
    x_bins = [0, pitch_length/3, 2*pitch_length/3, pitch_length]
    y_bins = [0, pitch_width/2, pitch_width]

    # Prepare figure
    fig, ax = pitch.draw(figsize=(14, 10))

    # Draw zone lines
    for xb in x_bins[1:-1]:
        ax.plot([xb, xb], [0, pitch_width], linestyle='--', color='gray')
    for yb in y_bins[1:-1]:
        ax.plot([0, pitch_length], [yb, yb], linestyle='--', color='gray')

    # Zone data dictionary
    zone_data = {(xz, yz): {} for xz in range(3) for yz in range(2)}
    summary_table = {m_id: [0]*6 for m_id in selected_match_ids}

    # Process each selected match
    for m_id in selected_match_ids:
        match_passes = passes[passes["match_id"] == m_id].copy()
        if match_passes.empty:
            continue

        # Assign zones
        match_passes['x_zone'] = pd.cut(match_passes['x'], bins=x_bins, labels=False, include_lowest=True)
        match_passes['y_zone'] = pd.cut(match_passes['y'], bins=y_bins, labels=False, include_lowest=True)
        match_passes.dropna(subset=['x_zone', 'y_zone'], inplace=True)
        match_passes['x_zone'] = match_passes['x_zone'].astype(int)
        match_passes['y_zone'] = match_passes['y_zone'].astype(int)

        # Group by zone
        grouped = match_passes.groupby(['x_zone', 'y_zone'])
        for (xz, yz), group in grouped:
            if group.empty:
                continue

            # Count and average arrow
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

            # Update summary table (zones 1–6)
            zone_index = yz * 3 + xz
            summary_table[m_id][zone_index] = count

    # Plot counts and arrows
    for (xz, yz), matches_info in zone_data.items():
        x0, x1 = x_bins[xz], x_bins[xz+1]
        y0, y1 = y_bins[yz], y_bins[yz+1]
        xc, yc = (x0 + x1)/2, (y0 + y1)/2

        offsets = np.linspace(-8, 8, len(matches_info))
        for i, (m_id, data) in enumerate(matches_info.items()):
            ax.text(xc + offsets[i], yc, str(data['count']),
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color=match_colors[m_id])
            pitch.arrows(data['start_x'], data['start_y'],
                         data['start_x'] + data['dx'], data['start_y'] + data['dy'],
                         ax=ax, color=match_colors[m_id], width=2, headwidth=5, headlength=5)

    # Legend
    legend_handles = [mlines.Line2D([], [], color=match_colors[m_id], marker='o',
                                    linestyle='None', markersize=8, label=match_names[m_id])
                      for m_id in selected_match_ids]
    ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.05),
              ncol=2, fontsize=12)

    # Title
    plt.title(f"{PLAYER_NAME} – Pass Map with Zones (EURO 2024)", fontsize=16)
    st.pyplot(fig, use_container_width=True)

    # ---------------------------
    # Metric selection for the bar chart (below pitch map)
    # ---------------------------
    metric = st.selectbox(
        "Choose metric to compare for bar chart",
        ["total_passes", "passes_per90", "total_shot_assists", "total_goal_assists", 
         "shot_assists_per90", "goal_assists_per90", "total_minutes_played", "matches_played"]
    )

    # ---------------------------
    # Horizontal Bar Chart
    # ---------------------------
    st.subheader("Bruno Fernandes vs Kevin De Bruyne vs Other midfielders in the EURO 2024")
    st.write("This comparison only includes players with above 360 total minutes played")

    # Highlight Bruno and De Bruyne
    def highlight_players(pid):
        if pid == BRUNO_ID:
            return "Bruno"
        elif pid == DEBRUYNE_ID:
            return "De Bruyne"
        else:
            return "Peer"

    full_stats["highlight"] = full_stats["player_id"].apply(highlight_players)

    hover_cols = [
        "matches_played", "total_minutes_played",
        "total_passes", "passes_per90",
        "total_shot_assists", "total_goal_assists",
        "shot_assists_per90", "goal_assists_per90"
    ]
    hover_cols = [col for col in hover_cols if col in full_stats.columns]

    fig_bar = px.bar(
        full_stats,
        x=metric,
        y='player_name',
        orientation='h',
        color="highlight",
        color_discrete_map={"Bruno": "red", "De Bruyne": "orange", "Peer": "blue"},
        hover_data=hover_cols
    )

    fig_bar.update_yaxes(tickfont=dict(size=14, family='Arial Black'))

    fig_bar.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title=metric.replace('_', ' ').title(),
        yaxis_title="Players",
        showlegend=True,
        height=max(600, len(full_stats) * 25)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------------------
    # Player Table
    # ---------------------------
    st.subheader("Full Player Comparison Table (Highlighted Bruno & De Bruyne)")

    df_table = full_stats.sort_values(metric, ascending=False)
    df_table = df_table.iloc[:, :-1]  # Drop last column if needed
    st.dataframe(df_table, hide_index=True)

    # ---------------------------
    # Generate summary for report
    # ---------------------------
    summary_stats = full_stats[full_stats["player_id"].isin([BRUNO_ID, DEBRUYNE_ID])]
    st.subheader("Summary of Bruno Fernandes & Kevin De Bruyne")
    st.dataframe(summary_stats)

else:
    st.warning("Please select at least one match.")
