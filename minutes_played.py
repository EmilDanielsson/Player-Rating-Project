#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 12:44:56 2021

@author: emildanielsson
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 11:51:54 2021

@author: emildanielsson

Program description: 
    Computes how many minutes each player have played for each game 
    from the given event and matches data set  
    
    Creates and saves a dataframe with the following columns:
        playerId - playerId from Wyscout 
        shortName - shortName from Wyscout
        matchId - matchId from Wyscout data
        teamId - teamId from Wyscout data
        teamName - Official teamname frrom Wyscout data
        player_in_min - the minute of the match the playerr started playing
        player_out_min - the minute of the match the player stopped playing
        minutesPlayed - Minutes played in the given game
        red_card - boolean to show if the player got a red card that game  
                    (1 = red card,  = no red card)
        
"""

# The basics
import pandas as pd
import numpy as np
import json


#############################################################################
# - Create dataframes from the Wyscout data
"---------------------------------------------------------------------------"

# Create event dataframe
#df_Europe_events = pd.read_json('Json_files/events_All.json', encoding="unicode_escape") #SLOWER
with open('Json_files/events_All.json') as f:
    data_Europe= json.load(f)
    
df_Europe_events = pd.DataFrame(data_Europe)

# Create match dataframes
df_England_matches = pd.read_json('../Wyscout/matches/matches_England.json', encoding="unicode_escape")

df_France_matches = pd.read_json('../Wyscout/matches/matches_France.json', encoding="unicode_escape")

df_Germany_matches = pd.read_json('../Wyscout/matches/matches_Germany.json', encoding="unicode_escape")

df_Italy_matches = pd.read_json('../Wyscout/matches/matches_Italy.json', encoding="unicode_escape")

df_Spain_matches = pd.read_json('../Wyscout/matches/matches_Spain.json', encoding="unicode_escape")


# Create players and teams dataframes
df_players = pd.read_json("../Wyscout/players.json", encoding="unicode_escape")
df_teams = pd.read_json("../Wyscout/teams.json", encoding="unicode_escape")



#############################################################################
# - Merge matches dataframes from all leagues 
"---------------------------------------------------------------------------"

frames_matches = [df_England_matches, df_France_matches, df_Germany_matches, 
                  df_Italy_matches, df_Spain_matches]

df_Europe_matches = pd.concat(frames_matches, keys = ["England", "France",
                                                      "Germany", "Italy", "Spain"])


#############################################################################
# - Creating the dataframe of full playing time for each match
"---------------------------------------------------------------------------"

# Prepares the dataframe with the columns we need
df_matches_fulltime=pd.DataFrame(columns=['matchId','matchDuration'])

# Match id checkpoints
loop_checkpoints = np.arange(0,2080,50)
j = 0

# Loop trough all matches
for i, match in df_Europe_matches.iterrows():
    
    # Find the events from match
    mask_match = (df_Europe_events.matchId == match['wyId']) & (df_Europe_events.matchPeriod == "2H")
    df_match = df_Europe_events.loc[mask_match]
    
    # time ofsecond half in seconds
    fulltime_sec = df_match['eventSec'].max()
    
    # Convert to minutes
    fulltime_min = 45 + round(fulltime_sec / 60)
    
    # Add match and full time (minutes) to dataframe
    df_matches_fulltime.loc[df_matches_fulltime.shape[0]] = [match.wyId, fulltime_min]
    
    if (j in loop_checkpoints):
        print(f"Number of matches checked for fulltimes: {j}\n")
    
    j+=1

#############################################################################
# - Creating the dataframe of minutes played for each player in each game
"---------------------------------------------------------------------------"

# Prepares the dataframe with the columns we need
df_minutes_played=pd.DataFrame(columns=['playerId', 'shortName',
                                        'matchId', 'teamId', 'teamName',
                                        'player_in_min', 'player_out_min',
                                        'minutesPlayed', 'red_card'])

# Match id checkpoints
loop_checkpoints = np.arange(0,2080,50)
j = 0

# Loop trough all matches
for i, match in df_Europe_matches.iterrows():
    
    # Lineups and substitutions are nested in teamsData
    team_data = match['teamsData']
    
    # Get match Id
    matchId = match['wyId']   
    
    # Get full match length
    fulltime_min = df_matches_fulltime.loc[df_matches_fulltime['matchId'] == matchId]['matchDuration'].values[0]
    
    # Loop through both teams in the match
    for teamId in team_data: 
        # loop like this gets the teamId as String, not the team object apperantly
        
        # Fetches the team to look at
        team = team_data[teamId]
        
        # list of the lineup
        lineup = team['formation']['lineup']
        
        # list of the substitutions
        substitutions = team['formation']['substitutions']
        
        # Get the team id
        teamId = team['teamId']
        
        # Get the team name
        mask_team_name = df_teams.wyId == teamId
        df_team = df_teams.loc[mask_team_name]
        teamName = df_team.officialName.values[0] # Could change officialName -> name ??
        
        # list of the players that came in during the match
        sub_ins = []
        sub_outs = []
        if (substitutions != "null"):
            for sub in substitutions:
                # "Handle" the case when the sub is badly registered
                if ((sub['playerIn'] != 0) & (sub['playerOut'] != 0)):
                    sub_ins.append(sub['playerIn'])
                    sub_outs.append(sub['playerOut']) 
                # With this solution some players will have played more minutes
                # than they actually played. But it is not that many matches 
                # so I think we are fine with it.
        
        # Loop through all players in the lineup and get their minutes played
        for player in lineup:
            
            # Get the current playerId
            playerId = player['playerId']
            
            # Get the current player shortName
            shortName = df_players.loc[df_players.wyId == playerId].shortName.values[0]
            
            # If the player have been subbed out set minutes played for the sub and the player
            if (playerId in sub_outs):
                
                # Find index of the substitution from the lists
                sub_index = sub_outs.index(playerId)
                
                # Find the mninute when sub took place
                sub_minute = substitutions[sub_index]['minute']
                
                # Find the name of the subbed in player
                shortName_sub = df_players.loc[df_players.wyId == sub_ins[sub_index]].shortName.values[0]
                
                # Add minutes played by the subed out player to the dataframe
                df_minutes_played.loc[df_minutes_played.shape[0]] = [sub_outs[sub_index], shortName, matchId, teamId, teamName, 0, sub_minute, sub_minute, 0]
                    
                
                # Handle the case if the subbed in player also is subbed out (injury for example)
                if (sub_ins[sub_index] in sub_outs):

                    # Find index of the substitution from the lists
                    sub_index2 = sub_outs.index(sub_ins[sub_index])
                    
                    # Find the mninute when sub took place
                    sub_minute2 = substitutions[sub_index2]['minute']
                    
                    # Find the name of the subbed in player
                    shortName_sub2 = df_players.loc[df_players.wyId == sub_ins[sub_index2]].shortName.values[0]
                    
                    # Make sure the subbed in and then out player at least played 1 min
                    if (sub_minute2 - sub_minute <= 0):
                       sub_playing_minutes2 = 1
                    else:
                        sub_playing_minutes2 = sub_minute2 - sub_minute
                    
                    # Add minutes played by the subed in and out player to the dataframe
                    df_minutes_played.loc[df_minutes_played.shape[0]] = [sub_outs[sub_index2], shortName_sub, matchId, teamId, teamName, sub_minute, sub_minute2, sub_playing_minutes2, 0]
                    
                    # Make sure the subbed in player at least played 1 min
                    if (fulltime_min - sub_minute2 <= 0):
                       sub_playing_minutes3 = 1
                    else:
                        sub_playing_minutes3 = fulltime_min - sub_minute2
                
                        
                    # Add minutes played by the subed in player to the dataframe    
                    df_minutes_played.loc[df_minutes_played.shape[0]] = [sub_ins[sub_index2], shortName_sub2, matchId, teamId, teamName, sub_minute2, fulltime_min, sub_playing_minutes3, 0]
                
                # Normal substitution
                else: 
                    # Make sure the subbed in player at least played 1 min
                    if (fulltime_min - sub_minute <= 0):
                       sub_playing_minutes = 1
                    else:
                        sub_playing_minutes = fulltime_min - sub_minute
                        
                    # Add minutes played by the subed in player to the dataframe    
                    df_minutes_played.loc[df_minutes_played.shape[0]] = [sub_ins[sub_index], shortName_sub, matchId, teamId, teamName, sub_minute, fulltime_min, sub_playing_minutes, 0]
                
            # The player played for the whole game   
            else:
                df_minutes_played.loc[df_minutes_played.shape[0]] = [playerId, shortName, matchId, teamId, teamName, 0, fulltime_min, fulltime_min, 0]
                
                
    if (j in loop_checkpoints):
        print(f"Number of matches checked for minutes: {j}\n")
    
    j+=1



#############################################################################
# - Adjust for red cards
"---------------------------------------------------------------------------"

# Filter out the fouls, assumed that red cards only exists as Foul-event
mask_fouls = df_Europe_events.eventName == "Foul"
df_fouls = df_Europe_events.loc[mask_fouls]

# Initiate variables 
match_list_reds = []
player_list_reds = []

# Loop through events to find matcghes and players with red cards
for i, foul_i in df_fouls.iterrows():
    
    # List to save the tags in
    foul_tags = []

    # Loop through fouls to find red cards
    for foultag in foul_i['tags']:
        foul_tags.append(foultag['id'])

    # tag 1701 == red card, tag 1703 == second yellow card
    if ((1701 in foul_tags) or (1703 in foul_tags)):
        
        # Fet the redcarded playerId and matchId
        red_carded_player = foul_i.playerId
        red_carded_match = foul_i.matchId
        
        # Find minute of the red card
        if foul_i.matchPeriod == "1H":
            red_card_minute = round(foul_i.eventSec / 60)
        elif foul_i.matchPeriod == "2H":
            red_card_minute = 45 + round(foul_i.eventSec / 60)
        else:
            print("Error" + str(foul_i.matchPeriod))

        # Find the minute the red carded player got in 
        mask_red_card_player_min = ((df_minutes_played.playerId == red_carded_player) & (df_minutes_played.matchId == red_carded_match))
        df_red_card = df_minutes_played.loc[mask_red_card_player_min]
        if len(df_red_card) != 0:
            red_card_player_in = df_red_card.player_in_min.values[0]
            
            # Adjust the dataframe "df_minutes_played" to add the red card info 
            df_minutes_played.loc[mask_red_card_player_min, 'player_out_min'] = red_card_minute
            df_minutes_played.loc[mask_red_card_player_min, 'minutesPlayed'] = red_card_minute - red_card_player_in
            df_minutes_played.loc[mask_red_card_player_min, 'red_card'] = 1



#############################################################################
# - Save df_minutes to dataframe "minutes_played_All.json"
"---------------------------------------------------------------------------"


df_minutes_played.to_json("Json_files/minutes_played_All.json")

# Test to load in and store as dataframe
with open('Json_files/minutes_played_All.json') as f:
    data_minutes_new = json.load(f)
    
df_test_new = pd.DataFrame(data_minutes_new)




























