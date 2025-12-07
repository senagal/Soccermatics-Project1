from mplsoccer import Sbopen
import pandas as pd

# -----------------------------
# Setup
# -----------------------------
parser = Sbopen(dataframe=True)

player_id = 5204
player_name = "Player X"
match_ids = [3942349, 3941020, 3938644, 3930174, 3930166]

# -----------------------------
# Load event data for each match
# -----------------------------
rows = []

for m_id in match_ids:
    df, related, freeze, tactics = parser.event(m_id)
    
    # Filter player's events
    player_events = df[df['player_id'] == player_id]
    passes = player_events[player_events['type_name'] == 'Pass']
    
    # Shot assists
    shot_assists = passes[passes['pass_shot_assist'] == True] \
        if 'pass_shot_assist' in passes.columns else passes.iloc[0:0]

    # Goal assists
    goal_assists = passes[passes['pass_goal_assist'] == True] \
        if 'pass_goal_assist' in passes.columns else passes.iloc[0:0]
    
    # Store results
    rows.append({
        "Match ID": m_id,
        "Passes": len(passes),
        "Shot Assists": len(shot_assists),
        "Goal Assists": len(goal_assists)
    })

# -----------------------------
# Create table
# -----------------------------
results_df = pd.DataFrame(rows)

print(results_df)
