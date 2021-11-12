#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 16:54:33 2021

@author: emildanielsson & JakobEP

Program description: 
    1. Read in data
    2. Creates two dataframes; 
        df_KPI      - Dataframe of all the player's KPI's from each game
        df_KPI_info - Dataframe with info of player's KPI's 
    (3.) Create and store the two dataframes as json-files in working directory
    
"""

# The basics
import pandas as pd
import numpy as np
import json

# Import KPI-funcion
import KPI_functions as kpi


#%%
# - Create dataframes from the Wyscout data
"---------------------------------------------------------------------------"

# Create event dataframe
#df_Europe_events = pd.read_json('Json_files/events_All.json', encoding="unicode_escape") #SLOWER
with open('../Json_files/events_All.json') as f:
    data_Europe = json.load(f)
    
df_Europe_events = pd.DataFrame(data_Europe)

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
# - Merge matches dataframes from all leagues 
"---------------------------------------------------------------------------"

frames_matches = [df_England_matches, df_France_matches, df_Germany_matches, 
                  df_Italy_matches, df_Spain_matches]

df_Europe_matches = pd.concat(frames_matches, keys = ["England", "France",
                                                      "Germany", "Italy", "Spain"])


#%%
# - Read in minutes played data
"---------------------------------------------------------------------------"

with open('../Json_files/minutes_played_All.json') as f:
    data_minutes = json.load(f)
    
df_minutes = pd.DataFrame(data_minutes)


#%%
# - Read in dataframes of all KPI's to edit
"---------------------------------------------------------------------------"

with open('../Json_files/new_KPI_tot_All.json') as f:
    data_kpi_tot = json.load(f)
    
with open('../Json_files/new_KPI_per_90_All.json') as f:
    data_kpi_p90 = json.load(f)
    
# with open('Json_files/KPI_info_All.json') as f:
#     data_kpi_info = json.load(f)
    
df_KPI_tot = pd.DataFrame(data_kpi_tot)
    
df_KPI_p90 = pd.DataFrame(data_kpi_p90)

#df_KPI_info = pd.DataFrame(data_kpi_info)


#%%
# - Find number of own goals
"---------------------------------------------------------------------------"

# Df with all own goals
df_own_goals = kpi.own_goals(df_Europe_events)

    
#%%
# - Loop to add additional KPIs
"---------------------------------------------------------------------------"

# Match id checkpoints
loop_checkpoints = np.arange(0, 2100, 5)
j = 0

# Loop through all matches
for i, match in df_Europe_matches.iterrows():
    
    # Find the events from match_i
    mask_match = df_Europe_events.matchId == match.wyId
    df_events_match = df_Europe_events.loc[mask_match]
    
    # List of all the players involved in match_i
    player_match_list = df_events_match['playerId'].unique().tolist()
    
    # Loop trough all players and get their average position and compute KPI's
    for player in player_match_list:
        
        # Find the minutes played, team and red card
        mask_minutes = (df_minutes.playerId == player) & (df_minutes.matchId == match.wyId)
        df_player_minutes = df_minutes.loc[mask_minutes]
        
        # Some players are not registered the subbed in but their events are registerd
        # If they are not subbed in correctly in Wyscout matches "df_player_minutes"
        # will be empty. Thus we check this here. 
        if len(df_player_minutes != 0):
            player_minutes = df_player_minutes['minutesPlayed'][0]
            
            # mask to find the given player-events
            mask_player = df_events_match.playerId == player
            
            # New dataframe with all events from 'player' in match
            df_events_player = df_events_match.loc[mask_player]
            
            
            ################################################
            # - Check after own goals from player in match
            "----------------------------------------------"
            
            # Initiate temp variable
            # own_goals_player = 0
            
            # # Read out any eventual own goals 
            # mask_own_goals = (df_own_goals.playerId == player) & (df_own_goals.matchId == match.wyId)
            # df_own_goals_player = df_own_goals.loc[mask_own_goals]
            
            # # Check there were any own goals
            # if len(df_own_goals_player) != 0:
            #     own_goals_player = len(df_own_goals_player)
            
            
            ################################################
            # - All function calls to compute kpi's
            "----------------------------------------------"
            
            # danger_ball_loses
            #danger_ball_loses, danger_ball_loses_p90, danger_ball_loses_info = kpi.danger_ball_loses(df_events_player, player_minutes)
            
            # yellow_cards
            #yellow_cards, yellow_cards_info = kpi.yellow_cards(df_events_player)
            
            # percent_def_actions
            percent_def_actions, percent_def_actions_info = kpi.percent_def_actions(df_events_player, player_minutes)
            
            ########################################################
            # - Add rows to df_KPI_p90, df_KPI_tot and df_KPI_info
            "------------------------------------------------------"
            
            # df_KPI_p90
            mask_insert1 = (df_KPI_p90.matchId == match.wyId) & (df_KPI_p90.playerId == player)
            #df_KPI_p90.loc[mask_insert1, 'own_goals'] = own_goals_player
            #df_KPI_p90.loc[mask_insert1, 'yellow_cards'] = yellow_cards
            #df_KPI_p90.loc[mask_insert1, 'danger_ball_loses'] = danger_ball_loses_p90
            df_KPI_p90.loc[mask_insert1, 'def_actions%'] = percent_def_actions
            
            # df_KPI_tot
            mask_insert2 = (df_KPI_tot.matchId == match.wyId) & (df_KPI_tot.playerId == player)
            #df_KPI_tot.loc[mask_insert2, 'own_goals'] = own_goals_player
            #df_KPI_tot.loc[mask_insert2, 'yellow_cards'] = yellow_cards
            #df_KPI_tot.loc[mask_insert2, 'danger_ball_loses'] = danger_ball_loses
            df_KPI_tot.loc[mask_insert2, 'def_actions%'] = percent_def_actions
            
            # df_KPI_info
            # mask_insert3 = (df_KPI_info.matchId) == match.wyId & (df_KPI_info.playerId == player)
            # df_KPI_info.loc[mask_insert3, 'yellow_cards'] = yellow_cards_info
            # df_KPI_info.loc[mask_insert3, 'danger_ball_loses'] = danger_ball_loses_info
            #df_KPI_info.loc[mask_insert3, 'def_actions%'] = percent_def_actions_info
        
        
    if (j in loop_checkpoints):
        print(f"Number of matches with computed KPI's': {j}\n")

    j+=1


#%%
# - Create the new columns team_xG_p90, opponents_xG, possesion, etc
"---------------------------------------------------------------------------"
# Find all unique matches 
list_matches = df_KPI_tot["matchId"].unique().tolist()

for match in list_matches:
    
    # mask for the match to add team_xG 
    mask_match = df_KPI_tot.matchId == match
    df_match = df_KPI_tot.loc[mask_match]
    
    # List of the team names
    list_teams = df_match["teamName"].unique().tolist()
    
    for team in list_teams:
        
        # Find the team KPI
        mask_team = df_match.teamName == team
        df_team = df_match.loc[mask_team]
        df_opponent = df_match.loc[~mask_team]
        
        # Find xG and shots
        # team_shots = df_team['shots'].sum()
        # opponent_shots = df_opponent['shots'].sum()
        team_xG = df_team["xG_tot"].sum()
        opponent_xG = df_opponent["xG_tot"].sum()
        team_passes = df_team['completed_passes'].sum()
        opponent_passes = df_opponent['completed_passes'].sum()
        
        tot_game_passes = team_passes + opponent_passes
        
        # Find approximate possesion
        team_possesion = team_passes / tot_game_passes
        opponent_possesion = opponent_passes / tot_game_passes
        
        # Find PossAdj defnesive actions
        for i, player in df_team.iterrows():
            mask_player =  ((df_KPI_tot.matchId == match) & (df_KPI_tot.playerId == player.playerId))
            df_player = df_KPI_tot.loc[mask_player]
            def_actions = df_player.succesful_def_actions.values[0]
            p_adj_def_actions = def_actions / opponent_possesion
            df_KPI_tot.loc[mask_player, 'p_adj_succ_def_actions'] = p_adj_def_actions
        
        # Add to the KPI dataframe
        mask_add_xG = ((df_KPI_tot.matchId == match) & (df_KPI_tot.teamName == team))
        df_KPI_tot.loc[mask_add_xG, 'team_xG'] = team_xG
        df_KPI_tot.loc[mask_add_xG, 'opponent_xG'] = opponent_xG
        df_KPI_tot.loc[mask_add_xG, 'team_possesion'] = team_possesion
        df_KPI_tot.loc[mask_add_xG, 'opponent_possesion'] = opponent_possesion
        # df_KPI_tot.loc[mask_add_xG, 'team_shots'] = team_shots
        # df_KPI_tot.loc[mask_add_xG, 'opponent_shots'] = opponent_shots


#%%
# - Save dataframes to json-files, uncomment which to save
"---------------------------------------------------------------------------" 

df_KPI_p90.to_json("Json_files/KPI_per_90_All.json")
df_KPI_tot.to_json("Json_files/KPI_tot_All.json")
#df_KPI_info.to_json("Json_files/new_KPI_info_All.json")

        