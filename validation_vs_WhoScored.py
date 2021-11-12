#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson & JakobEP

Program description: 
   Finds ratings of all players in the last round and compares them with 
   read in ratings from WhoScored (for the same matches in last round).
   
   OBS! Make sure to run GW_38_Ratings.py firstly and then 
    
"""

# The basics
import pandas as pd
import numpy as np
import json


#%%
# - Read Excels
# - 
# - Make sure to choose the correct sheets
# - 
"---------------------------------------------------------------------------"

# Specify the path to the xlsx-file
excel_path = "../Gameweek_38.xlsx"

df_WhoScored = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='WhoScored')  

df_pre_tune = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='result_pre_tune') 

df_post_tune = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='result_post_tune') 



#%%
# - Create validation dataframe
"---------------------------------------------------------------------------"
df_validation = pd.DataFrame()

# Find all the teams
teams = df_WhoScored.teamName.unique().tolist()

# Loop through teams and add theri "team_rating"
for team in teams:
    
    # Whoscored frame sorted
    df_WhoScored_team = df_WhoScored.loc[df_WhoScored.teamName == team]
    df_WhoScored_team = df_WhoScored_team.sort_values(by='Rating', ascending=False)
    WhoScored_players = df_WhoScored_team.shortName.values.tolist()
    
    # df_pre_tune frame sorted
    df_pre_tune_team = df_pre_tune.loc[df_pre_tune.teamName == team]
    df_pre_tune_team = df_pre_tune_team.sort_values(by='final_rating', ascending=False)
    pre_tune_players = df_pre_tune_team.shortName.values.tolist()
    
    # df_ost_tune frame sorted
    df_post_tune_team = df_post_tune.loc[df_post_tune.teamName == team]
    df_post_tune_team = df_post_tune_team.sort_values(by='final_rating', ascending=False)
    post_tune_players = df_post_tune_team.shortName.values.tolist()
    
    for i, player in df_WhoScored_team.iterrows():
        playerName = player.shortName
        df_validation.loc[i, 'shortName'] = playerName
        df_validation.loc[i, 'Position'] = player.position
        df_validation.loc[i, 'teamName'] = player.teamName
        df_validation.loc[i, 'WhoScored'] = WhoScored_players.index(playerName) + 1
        df_validation.loc[i, 'pre_tune'] = pre_tune_players.index(playerName) + 1
        df_validation.loc[i, 'post_tune'] = post_tune_players.index(playerName) + 1 
        

#%%
# - Validate all players 
"---------------------------------------------------------------------------"

score_pre = 0
score_post = 0
nr_of_players = len(df_validation)
for i, player in df_validation.iterrows():
    score_pre += abs(player.WhoScored - player.pre_tune) 
    score_post += abs(player.WhoScored - player.post_tune) 
    
# Divide by the number of players (average "false" in comparison to WhoScored)
score_pre = score_pre / nr_of_players
score_post = score_post / nr_of_players
    
# Print Validation for all players
print("All Players validation:")
print(f"pre tuning score = {score_pre}")
print(f"post score = {score_post}\n")



#%%
# - Validate Positions
"---------------------------------------------------------------------------"

# Positions to fit for
positions = [['LB', 'RB'], ['CB'], ['LM', 'RM'], ['CM'], ['LW', 'RW'], ['ST']]

for position in positions:
    df_validate = df_validation.loc[df_validation.Position.isin(position)]
    score_pre = 0
    score_post = 0
    nr_of_players = len(df_validate)
    for i, player in df_validate.iterrows():
        score_pre += abs(player.WhoScored - player.pre_tune) 
        score_post += abs(player.WhoScored - player.post_tune) 
    
    # Divide by the number of players (average "false" in comparison to WhoScored)
    score_pre = score_pre / nr_of_players
    score_post = score_post / nr_of_players
        
    # Print Validation for all players
    print(f"Validation {position}")
    print(f"pre tuning score = {score_pre}")
    print(f"post score = {score_post} \n")
        

#%%
# - Write validation results to Excel document
"---------------------------------------------------------------------------"

# with pd.ExcelWriter("../Gameweek_38.xlsx", mode="a", engine="openpyxl", if_sheet_exists = "new") as writer:
#     df_validation.to_excel(writer, sheet_name="WhoScored_Validation",
#                             columns=['shortName', 'Position', 'teamName', 'WhoScored', 'pre_tune', 'pre_tune'],
#                     header=True, index=False)