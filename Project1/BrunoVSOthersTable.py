from mplsoccer import Sbopen
import pandas as pd

# -------------------------------
# Settings
# -------------------------------
COMPETITION_ID = 55   # Euro 2024
SEASON_ID = 282
POSITION_IDS = [9, 11, 19]  # Target positions

parser = Sbopen(dataframe=True)

# -------------------------------
# Load matches
# -------------------------------
matches = parser.match(competition_id=COMPETITION_ID, season_id=SEASON_ID)
match_ids = matches['match_id'].tolist()

# -------------------------------
# Helper function
# -------------------------------
def timestamp_to_min(ts):
    if pd.isna(ts):
        return 0
    if hasattr(ts, "hour"):
        return ts.hour*60 + ts.minute + ts.second/60
    return float(ts)

# -------------------------------
# Dictionary to store stats per player
# -------------------------------
player_stats = {}

# -------------------------------
# Loop over matches
# -------------------------------
for match_id in match_ids:
    df, related, freeze, tactics = parser.event(match_id)
    
    # Filter only relevant positions
    players_in_match = df[df['position_id'].isin(POSITION_IDS)]['player_id'].unique()
    
    for pid in players_in_match:
        player_events = df[df['player_id'] == pid].copy()
        if player_events.empty:
            continue

        # Compute match end times
        p1_end = timestamp_to_min(df[(df.type_name=="Half End") & (df.period==1)].iloc[0].timestamp)
        p2_end = timestamp_to_min(df[(df.type_name=="Half End") & (df.period==2)].iloc[0].timestamp)
        total_match_min = p1_end + p2_end
        half2_offset = p1_end

        # Determine minute in match
        player_events['minute'] = player_events.apply(
            lambda row: timestamp_to_min(row.timestamp) + (half2_offset if row.period==2 else 0),
            axis=1
        )

        # Starting XI check
        started = False
        if isinstance(tactics, list):
            for t in tactics:
                if "lineup" in t:
                    for p in t["lineup"]:
                        if p["player"]["id"] == pid:
                            started = True
                            break

        enter_min = 0 if started else None
        exit_min = total_match_min

        sub_in = player_events[(player_events.type_name=="Substitution") & (player_events.substitution_replacement_id==pid)]
        sub_out = player_events[(player_events.type_name=="Substitution") & (player_events.player_id==pid)]

        if not sub_in.empty:
            enter_min = sub_in['minute'].iloc[0]
        if not sub_out.empty:
            exit_min = sub_out['minute'].iloc[0]

        red_card_min = None
        if 'foul_committed_card' in player_events.columns:
            red = player_events[(player_events.type_name=="Foul Committed") & (player_events.foul_committed_card=="Red Card")]
            if not red.empty:
                red_card_min = red['minute'].iloc[0]
                exit_min = min(exit_min, red_card_min)

        # Minutes played
        if enter_min is None:
            enter_min = 0
        minutes_played = exit_min - enter_min

        # Passes & assists
        passes = player_events[player_events.type_name=="Pass"]
        shot_assists = passes[passes.pass_assisted_shot_id.notna()]
        goal_assists = shot_assists[shot_assists.outcome_name=="Goal"]

        # Aggregate stats
        if pid not in player_stats:
            player_stats[pid] = {
                'player_name': player_events['player_name'].iloc[0],
                'matches_played': 0,
                'total_minutes': 0,
                'total_passes': 0,
                'total_shot_assists': 0,
                'total_goal_assists': 0
            }
        
        player_stats[pid]['matches_played'] += 1
        player_stats[pid]['total_minutes'] += minutes_played
        player_stats[pid]['total_passes'] += len(passes)
        player_stats[pid]['total_shot_assists'] += len(shot_assists)
        player_stats[pid]['total_goal_assists'] += len(goal_assists)

# -------------------------------
# Build summary dataframe
# -------------------------------
summary_df = pd.DataFrame([
    {
        'player_id': pid,
        'player_name': stats['player_name'],
        'matches_played': stats['matches_played'],
        'total_minutes_played': round(stats['total_minutes'],2),
        'total_passes': stats['total_passes'],
        'total_shot_assists': stats['total_shot_assists'],
        'total_goal_assists': stats['total_goal_assists'],
        'shot_assists_per90': round(stats['total_shot_assists']/stats['total_minutes']*90,2) if stats['total_minutes']>0 else 0,
        'goal_assists_per90': round(stats['total_goal_assists']/stats['total_minutes']*90,2) if stats['total_minutes']>0 else 0
    }
    for pid, stats in player_stats.items() if stats['total_minutes'] > 150
])

# -------------------------------
# Save to CSV
# -------------------------------
summary_df.to_csv("euro2024_midfielders_summary.csv", index=False)
print("Data saved to euro2024_midfielders_summary.csv")
