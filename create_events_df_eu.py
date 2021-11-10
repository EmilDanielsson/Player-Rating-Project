#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 12:04:25 2021

@author: emildanielsson

Program description:
    1. Read in Wyscout data, Events, Players, Matches and Teams
    2. Filtering of the event and player data
        - get rid of gk's from players data
        - get rid of gk-events from event data
        - get rid of events with unknown playerId
    3. Merge all the legaue event files to one datafram
    4. Creates and stores a new events.json file in the working directory
        - Added column "Position" with the detected position
        - Added column "shortName" with the shortName from Wyscout
        

"""

# The basics
import pandas as pd
import numpy as np
import json

import fitting_functions as ff
 
#%%
# - Create dataframes from the Wyscout data
"---------------------------------------------------------------------------"

# Create event dataframes
df_England_events = pd.read_json('../../Wyscout/events/events_England.json', encoding="unicode_escape")

df_France_events = pd.read_json('../../Wyscout/events/events_France.json', encoding="unicode_escape")

df_Germany_events = pd.read_json('../../Wyscout/events/events_Germany.json', encoding="unicode_escape")

df_Italy_events = pd.read_json('../../Wyscout/events/events_Italy.json', encoding="unicode_escape")

df_Spain_events = pd.read_json('../../Wyscout/events/events_Spain.json', encoding="unicode_escape")


# Create match dataframes
df_England_matches = pd.read_json('../../Wyscout/matches/matches_England.json', encoding="unicode_escape")

df_France_matches = pd.read_json('../../Wyscout/matches/matches_France.json', encoding="unicode_escape")

df_Germany_matches = pd.read_json('../../Wyscout/matches/matches_Germany.json', encoding="unicode_escape")

df_Italy_matches = pd.read_json('../../Wyscout/matches/matches_Italy.json', encoding="unicode_escape")

df_Spain_matches = pd.read_json('../../Wyscout/matches/matches_Spain.json', encoding="unicode_escape")


# Create players and teams dataframes
df_players = pd.read_json("../../Wyscout/players.json", encoding="unicode_escape")
df_teams = pd.read_json("../../Wyscout/teams.json", encoding="unicode_escape")



#%%
# - Merge dataframes from all leagues but England
"---------------------------------------------------------------------------"

frames_events = [df_England_events, df_France_events, df_Germany_events,
          df_Italy_events, df_Spain_events]

df_Europe_events = pd.concat(frames_events, keys = ["England", "France", "Germany", "Italy", "Spain"])
df_Europe_events = df_Europe_events.reset_index(level=[0])
df_Europe_events = df_Europe_events.rename(columns ={'level_0': "league"})


frames_matches = [df_England_matches, df_France_matches, df_Germany_matches, 
                  df_Italy_matches, df_Spain_matches]

df_Europe_matches = pd.concat(frames_matches, keys = ["England", "France", "Germany", "Italy", "Spain"])
df_Europe_matches = df_Europe_matches.reset_index(level=[0])
df_Europe_matches = df_Europe_matches.rename(columns ={'level_0': "league"})

#%%
# - Add shortName and position to df_Europe
"---------------------------------------------------------------------------"

# Filter out events with no playerId (0) 
mask_filter = df_Europe_events.playerId != 0
df_Europe_events = df_Europe_events[mask_filter]

# Find unique player ids
eu_players = df_Europe_events["playerId"].unique().tolist()

# Player id checkpoints
loop_checkpoints = np.arange(0,2080,50)
j = 0

# Loop through player list and add new column for name
for player in eu_players:
    
    # Find player short name
    mask_player = df_players.wyId == player
    shortName = df_players.loc[mask_player, 'shortName'].values[0]
    
    # Mask player
    mask_events_player = df_Europe_events.playerId == player
    df_Europe_events.loc[mask_events_player, 'shortName'] = shortName
    
    if (j in loop_checkpoints):
        print(f"shortName added: {j}\n")
    
    j+=1
    
# Find all unique matches played
matchId_list = df_Europe_events['matchId'].unique().tolist()    

# Match id checkpoints
loop_checkpoints = np.arange(0,2080,50)
j = 0

# Loop through all matches 
for match_i in matchId_list:
    
    # Find the event from match_i
    mask_match = df_Europe_events.matchId == match_i
    df_match = df_Europe_events.loc[mask_match]
    
    # List of all the players involved in match_i
    player_match_list = df_match['playerId'].unique().tolist()
    
    # Loop trough all players and get their average position
    for player in player_match_list:
        
        # mask to find the given player-events
        mask_player = df_match.playerId == player
        
        # mask to find player from df_players
        mask_player2 = df_players.wyId == player
        
        # New dataframe with all events from 'player' in match 'match_i'
        player_df = df_match.loc[mask_player]

        # Inititae lists to be filled with x and y coordinates
        x_list = []
        y_list = []
        
        # Get list of all starting coordinates from each event of the player
        for i, event in player_df.iterrows():
            x_list.append(event['positions'][0]['x'])
            y_list.append(event['positions'][0]['y'])
            
        # Get the mean positions
        y_mean = sum(y_list) / len(y_list)
        x_mean = sum(x_list) / len(x_list)
        
        # Get the Wyscout-determined role of the player
        position_wyscout = df_players.loc[mask_player2]['role'].values[0]['name']
        
        # Call to function
        position = ff.decide_position(x_mean, y_mean, position_wyscout)
        
        # Add the position to the dataframe
        mask_add_position = (df_Europe_events.matchId == match_i) & (df_Europe_events.playerId == player)
        df_Europe_events.loc[mask_add_position, 'Position'] = position
        
    if (j in loop_checkpoints):
        print(f"Number of event-modified matches: {j}\n")
    
    j+=1



# Filter out events with goalkeepers
mask_gk = df_Europe_events.Position == "GK"
df_Europe_events = df_Europe_events[~mask_gk]


#%%
# - Save dataframe of Europe events to working directory
"---------------------------------------------------------------------------"
df_Europe_events.reset_index(inplace=True)
df_Europe_events.to_json("Json_files/events_All.json")

# Test to load in and store as dataframe
with open('Json_files/events_All.json') as f:
    data_Europe_new = json.load(f)
    
df_Europe_new = pd.DataFrame(data_Europe_new)



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    