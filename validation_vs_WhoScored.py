#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson & JakobEP

Program description: 
   Finds ratings of all players in the last round and compares them with 
   read in ratings from WhoScored (for the same matches in last round).
    
"""

# The basics
import pandas as pd
import numpy as np
import json


#%%
# - Read Excels
"---------------------------------------------------------------------------"

# Specify the path to the xlsx-file
excel_path = "Gameweek_38.xlsx"

df_WhoScored = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='WhoScored')  

df_MinMax = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='testing_MinMax_new') 

df_Quantile = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='testing_Quantile_new') 

df_Robust = pd.read_excel(open(excel_path, 'rb'),
              sheet_name='testing_Robust_new') 


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
    
    # MinMax frame sorted
    df_MinMax_team = df_MinMax.loc[df_MinMax.teamName == team]
    df_MinMax_team = df_MinMax_team.sort_values(by='final_rating', ascending=False)
    MinMax_players = df_MinMax_team.shortName.values.tolist()
    
    # Quantile frame sorted
    df_Quantile_team = df_Quantile.loc[df_Quantile.teamName == team]
    df_Quantile_team = df_Quantile_team.sort_values(by='final_rating', ascending=False)
    Quantile_players = df_Quantile_team.shortName.values.tolist()
    
    # Robust frame sorted
    df_Robust_team = df_Robust.loc[df_Robust.teamName == team]
    df_Robust_team = df_Robust_team.sort_values(by='final_rating', ascending=False)
    Robust_players = df_Robust_team.shortName.values.tolist()
    
    for i, player in df_WhoScored_team.iterrows():
        playerName = player.shortName
        df_validation.loc[i, 'shortName'] = playerName
        df_validation.loc[i, 'Position'] = player.position
        df_validation.loc[i, 'teamName'] = player.teamName
        df_validation.loc[i, 'WhoScored'] = WhoScored_players.index(playerName) + 1
        df_validation.loc[i, 'MinMax'] = MinMax_players.index(playerName) + 1
        df_validation.loc[i, 'Quantile'] = Quantile_players.index(playerName) + 1 
        df_validation.loc[i, 'Robust'] = Robust_players.index(playerName) + 1
        

#%%
# - Validate all players 
"---------------------------------------------------------------------------"

score_MinMax = 0
score_Quantile = 0
score_Robust = 0
nr_of_players = len(df_validation)
for i, player in df_validation.iterrows():
    score_MinMax += abs(player.WhoScored - player.MinMax) 
    score_Quantile += abs(player.WhoScored - player.Quantile) 
    score_Robust += abs(player.WhoScored - player.Robust) 
    
# Divide by the number of players (average "false" in comparison to WhoScored)
score_MinMax = score_MinMax / nr_of_players
score_Quantile = score_Quantile / nr_of_players
score_Robust = score_Robust / nr_of_players 
    
# Print Validation for all players
print("All Players validation:")
print(f"MinMax score = {score_MinMax}")
print(f"Quantile score = {score_Quantile}")
print(f"Robust score = {score_Robust}\n")


#%%
# - Validate Positions
"---------------------------------------------------------------------------"

# Positions to fit for
positions = [['LB', 'RB'], ['CB'], ['LM', 'RM'], ['CM'], ['LW', 'RW'], ['ST']]

for position in positions:
    df_validate = df_validation.loc[df_validation.Position.isin(position)]
    score_MinMax = 0
    score_Quantile = 0
    score_Robust = 0
    nr_of_players = len(df_validate)
    for i, player in df_validate.iterrows():
        score_MinMax += abs(player.WhoScored - player.MinMax) 
        score_Quantile += abs(player.WhoScored - player.Quantile) 
        score_Robust += abs(player.WhoScored - player.Robust) 
        
    # Divide by the number of players (average "false" in comparison to WhoScored)
    score_MinMax = score_MinMax / nr_of_players
    score_Quantile = score_Quantile / nr_of_players
    score_Robust = score_Robust / nr_of_players 
        
    # Print Validation for the position
    print(f"Validation: {position}")
    print(f"MinMax score = {score_MinMax}")
    print(f"Quantile score = {score_Quantile}")
    print(f"Robust score = {score_Robust}\n")
        

#%%
# - Write validation results to Excel document
"---------------------------------------------------------------------------"

with pd.ExcelWriter("Gameweek_38.xlsx", mode="a", engine="openpyxl", if_sheet_exists = "new") as writer:
    df_validation.to_excel(writer, sheet_name="Validation222",
                            columns=['shortName', 'Position', 'teamName', 'WhoScored', 'MinMax'],
                    header=True, index=False)