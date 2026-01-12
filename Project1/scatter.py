# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 09:52:59 2026

@author: senaa
"""

# -*- coding: utf-8 -*-
"""
Scatter plot of Bruno Fernandes vs Kevin De Bruyne vs other midfielders
for passes per 90, shot assists per 90, and goal assists per 90.
"""

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Load the data
# ---------------------------
# Replace with your CSV path
CSV_PATH = "euro2024_midfielders_summary_360plus.csv"
full_stats = pd.read_csv(CSV_PATH)

# ---------------------------
# Constants
# ---------------------------
BRUNO_ID = 5204
DEBRUYNE_ID = 3089

# ---------------------------
# Define colors
# ---------------------------
def get_color(pid):
    if pid == BRUNO_ID:
        return 'red'
    elif pid == DEBRUYNE_ID:
        return 'yellow'
    else:
        return 'blue'

full_stats['color'] = full_stats['player_id'].apply(get_color)

# ---------------------------
# Metrics
# ---------------------------
metrics = ['passes_per90', 'shot_assists_per90', 'goal_assists_per90']
labels = ['Passes per 90', 'Shot Assists per 90', 'Goal Assists per 90']

# ---------------------------
# Scatter plots
# ---------------------------
plt.figure(figsize=(18, 5))

for i, metric in enumerate(metrics):
    plt.subplot(1, 3, i+1)
    plt.scatter(
        full_stats[metric],
        [0]*len(full_stats),  # all points on same horizontal line
        c=full_stats['color'],
        s=100,  # size of dots
        alpha=0.8,
        edgecolors='k'
    )
    
    # Annotate Bruno and De Bruyne
    for _, row in full_stats[full_stats['player_id'].isin([BRUNO_ID, DEBRUYNE_ID])].iterrows():
        plt.text(row[metric], 0.02, row['player_name'], ha='center', va='bottom', fontsize=9)
    
    plt.xlabel(labels[i])
    plt.yticks([])  # hide y-axis
    plt.title(labels[i])
    plt.grid(axis='x', linestyle='--', alpha=0.5)

# Legend
plt.scatter([], [], c='red', s=100, label='Bruno Fernandes', edgecolors='k')
plt.scatter([], [], c='yellow', s=100, label='Kevin De Bruyne', edgecolors='k')
plt.scatter([], [], c='blue', s=100, label='Other Midfielders', edgecolors='k')
plt.legend(loc='upper right')

plt.suptitle("Bruno vs De Bruyne vs Other Midfielders (EURO 2024 per 90 stats)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
