#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson

Program description: 
   Find ratings of all players in the last round
   
Algorithm: 
    
"""


# The basics
import pandas as pd
import numpy as np
import json

# Plotting
import matplotlib.pyplot as plt
from mplsoccer import FontManager
from mplsoccer import Pitch, VerticalPitch


# Import other functions
import percentile_functions as pf
import fitting_functions as ff
import KPI_functions as kpi

# Statistical fitting of models
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# For tables
from tabulate import tabulate

# Ignore Future Warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#%%
# - Load Fonts
"---------------------------------------------------------------------------"

URL1 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/'
        'fonts/SourceSerifPro-Regular.ttf?raw=true')
serif_regular = FontManager(URL1)
URL2 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/'
        'fonts/SourceSerifPro-ExtraLight.ttf?raw=true')
serif_extra_light = FontManager(URL2)
URL3 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/fonts/'
        'SourceSerifPro-Bold.ttf?raw=true')
serif_bold = FontManager(URL3)


#%%
# - Read in data KPI data
"---------------------------------------------------------------------------"

# Test to load in and store as dataframe per_90 dont have all collumns yet
# with open('Json_files/KPI_per_90_All.json') as f:
#     data_kpi = json.load(f)
    
with open('Json_files/KPI_tot_All_v2.json') as f:
    data_kpi = json.load(f)
    
df_KPI = pd.DataFrame(data_kpi)


# Create match dataframes
df_England_matches = pd.read_json('../Wyscout/matches/matches_England.json', encoding="unicode_escape")


#%%
# - Read in minutes played data
"---------------------------------------------------------------------------"

with open('Json_files/minutes_played_All.json') as f:
    data_minutes = json.load(f)
    
df_minutes = pd.DataFrame(data_minutes)


#%%
# - Read PL events data, players and teams
"---------------------------------------------------------------------------"

# Create event dataframe for PL
df_events = pd.read_json('Json_files/events_All.json', encoding="unicode_escape")

# Create players and teams dataframes
df_players = pd.read_json("../Wyscout/players.json", encoding="unicode_escape")
df_teams = pd.read_json("../Wyscout/teams.json", encoding="unicode_escape")


#%%
# - Read in data for xG-model and get the coeficients dataframes
"---------------------------------------------------------------------------"  

with open('Json_files/xG_model_v2_All_except_Eng.json') as f:
    data_xG_model = json.load(f)

# Create dataframes
df_xG_model = pd.DataFrame(data_xG_model)  

# Call xG-m
df_log_model_shots_coef, df_log_model_headers_coef, df_log_model_free_kicks_coef = ff.xG_model(df_xG_model)


#%%
# - Set filter and scaler varables
"---------------------------------------------------------------------------"

# Now we want to filter out those who have not played at least 
# 10 matches with 20 minutes in each match (can change)
min_minutes = 20

# Choose method for normalizaion
scaler = MinMaxScaler()
#scaler = preprocessing.QuantileTransformer(random_state=0)
#scaler = RobustScaler()


#%%
# - Create test and train dataset and preprocess data
"---------------------------------------------------------------------------"

# Seperate df_KPI beteween PL and the rest of the legaues
mask_PL = df_KPI.league == "England"
df_KPI_PL = df_KPI.loc[mask_PL]
df_KPI_EU_train = df_KPI.loc[~mask_PL]

test_gameweek = 38
df_PL_gameweek_38 = df_England_matches.loc[df_England_matches.gameweek == test_gameweek]
list_gameweek_38_matchId = df_PL_gameweek_38['wyId'].unique().tolist()
mask_last_gameweeks = df_KPI_PL.matchId.isin(list_gameweek_38_matchId)

# KPIs GW 1-37
df_KPI_PL = df_KPI_PL.loc[~mask_last_gameweeks]


#%%
# - Let User choose a match to get ratings from
"---------------------------------------------------------------------------"

print("Choose match Id to get rankings from:\n")
for i, match in df_PL_gameweek_38.iterrows():
    print(match.label)
    print(f"matchId: {match.wyId}\n")
    
print("Enter the match Id to look at: ")

the_matchId = int(input())
#the_matchId = 2500098

# Find the match events 
df_the_match_events = df_events.loc[df_events.matchId == the_matchId]

# Df with all own goals
df_own_goals = kpi.own_goals(df_the_match_events)


# COULD LOOP OVER MATCHES HERE IF WANTED

#%%
# - Create the KPI-dataframe from that match
"---------------------------------------------------------------------------"
# Initiate the dataframe
# Prepare the dataframe with the columns we need
df_the_match_KPI = pd.DataFrame(columns=['matchId',
                               'league',          
                               'teamName',
                               'playerId',
                               'shortName',
                               'role',
                               'minutesPlayed',
                               'team_goals',
                               'team_conceded_goals',
                               'red_card',
                               # KPI's from here
                               'goals',
                               'assists',
                               'passing%',
                               'completed_passes',
                               'fouls',
                               'aerial%',
                               'aerial_wins',
                               'shots',
                               'dribbles%',
                               'succesful_dribbles',
                               'key_passes',
                               'succesful_through_passes',
                               'plus_minus',
                               'events_in_box',
                               'passes_to_box',
                               'creative_passes',
                               'succesful_def_actions',
                               'progressive_carries',
                               'xG_tot',
                               'xG_shots',
                               'xG_headers',
                               'xG_free_kicks',
                               'xG_penalties',
                               'own_goals',
                               'yellow_cards',
                               'danger_ball_loses',
                               'def_actions%'])


#%%
# - Find home and away score
"----------------------------------------------"

# Find teamIds in the match
teams_match_list = df_the_match_events['teamId'].unique().tolist()

# Find the match data from df_matches
mask_score = df_England_matches.wyId == the_matchId
df_the_match_info = df_England_matches.loc[mask_score]
team_data = df_the_match_info.teamsData.values[0]

# Get the list of players from events file
players_the_match = df_the_match_events['playerId'].unique().tolist()

# Shortrname lists
home_team_lineup = []
away_team_lineup = []
home_team_bench = []
away_team_bench = []

# playerIds list
home_team_list = []
away_team_list = []
for i in range(2):
    team_data_i = team_data[str(teams_match_list[i])]
    team_lineup = team_data_i['formation']['lineup']
    team_bench = team_data_i['formation']['bench']

    # HERE COULD WE GET THE LINEUP POSITIONS
    
    # Get the lineup players
    for player in team_lineup:
        if player['playerId'] in players_the_match:
            if team_data_i['side'] == "home":
                home_team_list.append(player['playerId'])
                shortName = df_players.loc[df_players.wyId == player['playerId']].shortName.values[0]
                home_team_lineup.append(shortName)
            elif team_data_i['side'] == "away":
                away_team_list.append(player['playerId'])
                shortName = df_players.loc[df_players.wyId == player['playerId']].shortName.values[0]
                away_team_lineup.append(shortName)
            else:
                print("Error: " + team_data_i['side'])
    
    # Get the bench players
    for player in team_bench:
        if player['playerId'] in players_the_match:
            if team_data_i['side'] == "home":
                home_team_list.append(player['playerId'])
                shortName = df_players.loc[df_players.wyId == player['playerId']].shortName.values[0]
                home_team_bench.append(shortName)
            elif team_data_i['side'] == "away":
                away_team_list.append(player['playerId'])
                shortName = df_players.loc[df_players.wyId == player['playerId']].shortName.values[0]
                away_team_bench.append(shortName)
            else:
                print("Error: " + team_data_i['side'])
        
        # Set home and away score
        if team_data_i['side'] == "home":
            home_team_score = team_data_i['score']
        elif team_data_i['side'] == "away":
            away_team_score = team_data_i['score']
        else:
            print("Error: " + team_data_i['score'])
        
#%%
# Compute the KPIs from the chosen match
"----------------------------------------------"

# Loop trough all players and get their average position and compute KPI's
for player in players_the_match:
    
    # Find the minutes played, team and red card
    mask_minutes = (df_minutes.playerId == player)
    df_player_minutes = df_minutes.loc[mask_minutes]
    
    # Some players are not registered the subbed in but their events are registerd
    # If they are not subbed in correctly in Wyscout matches "df_player_minutes"
    # will be empty. Thus we check this here. 
    if len(df_player_minutes != 0):
        player_minutes = df_player_minutes['minutesPlayed'][0]
        player_in_min = df_player_minutes['player_in_min'][0]
        player_out_min = df_player_minutes['player_out_min'][0]
        player_team = df_player_minutes['teamId'][0]
        player_team_name = df_player_minutes['teamName'][0]
        red_card_bool = df_player_minutes['red_card'][0]
        
        # New dataframe with all events from 'player' in match
        df_events_player = df_the_match_events.loc[df_the_match_events.playerId == player]
        
        # Get the position of the player
        position = df_events_player['Position'].values[0]
        
        # Get the league
        league = df_events_player["league"].values[0]
        
        # Get the shortName
        name = df_events_player['shortName'].values[0]
        
        # Get the team goal and goals conceded
        if (player in home_team_list):
            team_goals = home_team_score
            team_conceded_goals = away_team_score
        elif (player in away_team_list):
            team_goals = away_team_score
            team_conceded_goals = home_team_score
        else:
            print("Error: cant find player in list")
            
        ################################################
        # - Check after own goals from player in match
        "----------------------------------------------"
        
        # Initiate temp variable
        own_goals = 0
        
        # Read out any eventual own goals 
        df_own_goals_player = df_own_goals.loc[df_own_goals.playerId == player]
        
        # Check there were any own goals
        if len(df_own_goals_player) != 0:
            own_goals = len(df_own_goals_player)
            
        
        ################################################
        # - All function calls to compute kpi's
        "----------------------------------------------"
        
        # goals
        goals, goals_info = kpi.nr_goals(df_events_player, player_minutes)
        
        # assists
        assists, assists_info = kpi.nr_assists(df_events_player, player_minutes)
        
        # passing%
        pass_percent, pass_percent_info = kpi.percent_passes_completed(df_events_player, player_minutes)
        
        # passes_completed
        pass_comp, pass_comp_p90, pass_comp_info = kpi.passes_completed(df_events_player, player_minutes)
        
        # fouls
        fouls, fouls_p90, fouls_info = kpi.fouls(df_events_player, player_minutes)
        
        # aerials%
        aerials_percent, aerials_percent_info = kpi.percent_aerial_wins(df_events_player, player_minutes)
        
        # aerials_won
        aerial_wins, aerial_wins_p90, aerial_wins_info = kpi.aerials_won(df_events_player, player_minutes)
        
        # shots
        shots, shots_p90, shots_info = kpi.shots(df_events_player, player_minutes)
        
        # dribbles%
        dribbles_percent, dribbles_percent_info = kpi.percent_succesful_dribbles(df_events_player, player_minutes)
        
        # succesful_dribbles
        succesful_dribbles, succesful_dribbles_p90, succesful_dribbles_info = kpi.succesful_dribbles(df_events_player, player_minutes)
        
        # key_passes
        key_passes, key_passes_p90, key_passes_info = kpi.key_passes(df_events_player, player_minutes)
        
        # succesful_through_passes
        succesful_through_passes, succesful_through_passes_p90, succesful_through_passes_info = kpi.succesful_through_passes(df_events_player, player_minutes)
        
        # plus-minus
        plus_minus, plus_minus_info = kpi.plus_minus(df_the_match_events, player_team, player_minutes, player_in_min, player_out_min)
        
        # events_in_box
        events_in_box, events_in_box_p90, event_in_box_info = kpi.events_in_box(df_events_player, player_minutes)
        
        # passes_to_box
        passes_to_box, passes_to_box_p90, passes_to_box_info = kpi.passes_to_box(df_events_player, player_minutes)
        
        # creative_passes
        creative_passes, creative_passes_p90, creative_passes_info = kpi.creative_passes(df_events_player, player_minutes)
        
        # defensive_actions
        succesful_def_actions, succesful_def_actions_p90, succesful_def_actions_info = kpi.succesful_def_actions(df_events_player, player_minutes)
        
        # progressive_carries 
        progressive_carries, progressive_carries_p90, progressive_carries_info = kpi.progressive_carries(df_events_player, player_minutes) 
        
        # xG
        xG_tot, xG_tot_p90, xG_info, xG_shots, xG_headers, xG_free_kicks, xG_penalties = kpi.xG(df_events_player, player_minutes, df_log_model_shots_coef, df_log_model_headers_coef, df_log_model_free_kicks_coef)
        
        # danger_ball_loses
        danger_ball_loses, danger_ball_loses_p90, danger_ball_loses_info = kpi.danger_ball_loses(df_events_player, player_minutes)
        
        # yellow_cards
        yellow_cards, yellow_cards_info = kpi.yellow_cards(df_events_player)
        
        # percent_def_actions
        percent_def_actions, percent_def_actions_info = kpi.percent_def_actions(df_events_player, player_minutes)
            
        
        ########################################################
        # - Add rows to df_the_match_KPI
        "------------------------------------------------------"
        # df_KPI_tot
        df_the_match_KPI.loc[df_the_match_KPI.shape[0]] = [the_matchId, league, player_team_name, player, name,
                                       position, player_minutes, team_goals, 
                                       team_conceded_goals, red_card_bool,
                                       goals,
                                       assists,
                                       pass_percent,
                                       pass_comp,
                                       fouls,
                                       aerials_percent,
                                       aerial_wins,
                                       shots,
                                       dribbles_percent,
                                       succesful_dribbles,
                                       key_passes,
                                       succesful_through_passes,
                                       plus_minus,
                                       events_in_box,
                                       passes_to_box,
                                       creative_passes,
                                       succesful_def_actions,
                                       progressive_carries,
                                       xG_tot,
                                       xG_shots,
                                       xG_headers,
                                       xG_free_kicks,
                                       xG_penalties,
                                       own_goals,
                                       yellow_cards,
                                       danger_ball_loses,
                                       percent_def_actions
                                       ]
    
#%%
# - Create the new columns team_xG, opponents_xG, possesion
"---------------------------------------------------------------------------"
# List of the team names
list_teams = df_the_match_KPI["teamName"].unique().tolist()

for team in list_teams:
    
    # Find the team KPI
    mask_team = df_the_match_KPI.teamName == team
    df_team = df_the_match_KPI.loc[mask_team]
    df_opponent = df_the_match_KPI.loc[~mask_team]
    
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
        mask_player =  (df_the_match_KPI.playerId == player.playerId)
        df_player = df_the_match_KPI.loc[mask_player]
        def_actions = df_player.succesful_def_actions.values[0]
        p_adj_def_actions = def_actions / opponent_possesion
        df_the_match_KPI.loc[mask_player, 'p_adj_succ_def_actions'] = p_adj_def_actions
    
    # Add to the KPI dataframe
    mask_add_xG = (df_the_match_KPI.teamName == team)
    df_the_match_KPI.loc[mask_add_xG, 'team_xG'] = team_xG
    df_the_match_KPI.loc[mask_add_xG, 'opponent_xG'] = opponent_xG
    df_the_match_KPI.loc[mask_add_xG, 'team_possesion'] = team_possesion
    df_the_match_KPI.loc[mask_add_xG, 'opponent_possesion'] = opponent_possesion
    # df_the_match_KPI.loc[mask_add_xG, 'team_shots'] = team_shots
    # df_the_match_KPI.loc[mask_add_xG, 'opponent_shots'] = opponent_shots

#%%
# - Rank the players 
"---------------------------------------------------------------------------"

# Merge the KPIs from the chosen match with the KPIS from 1-37
df_KPI_PL = df_KPI_PL.append(df_the_match_KPI, ignore_index = True)

# Positions to fit for
positions_fitting = [['LB', 'RB'], ['CB'], ['LM', 'RM'], ['CM'], ['LW', 'RW'], ['ST']]

# Initiate rating and info dataframe
df_final_rating = pd.DataFrame(columns = ['matchId', 'teamName', 'playerId',
                                          'shortName', 'position', 'tot_rating',
                                          'match_events_rating', 'fitting_rating_off',
                                          'fitting_rating_def',
                                          'final_rating', 'match_info',
                                          'gameweek'])

# Do fitting for all the positins
for position in positions_fitting:
    # print(position)

    ################################################
    # - Kpis to fit for
    "----------------------------------------------"
    
    list_kpi_all = ['passing%', 
            'completed_passes',
            'fouls',
            'aerial%',
            'aerial_wins',
            'shots',
            'dribbles%',
            'succesful_dribbles',
            'key_passes',
            'succesful_through_passes',
            'events_in_box',
            'passes_to_box',
            'creative_passes',
            'succesful_def_actions',
            'progressive_carries',
            'red_card',
            'own_goals',
            'yellow_cards',
            'danger_ball_loses',
            'def_actions%',
            'p_adj_succ_def_actions'
            ] 
        
    # KPIs when using KPI_tot_All
    list_kpi_off = ['passing%', 
                'completed_passes',
                'fouls',
                #'aerial%',
                #'aerial_wins',
                'shots',
                'dribbles%',
                #'succesful_dribbles',
                'key_passes',
                #'succesful_through_passes',
                'events_in_box',
                'passes_to_box',
                #'creative_passes',
                #'succesful_def_actions', 
                #'progressive_carries',
                'red_card',
                'own_goals',
                'yellow_cards',
                'danger_ball_loses',
                #'def_actions%',
                'p_adj_succ_def_actions'
                ] 
    
    list_kpi_def = ['passing%', 
                'completed_passes',
                'fouls',
                #'aerial%',
                #'aerial_wins',
                #'shots',
                'dribbles%',
                #'succesful_dribbles',
                #'key_passes',
                #'succesful_through_passes',
                #'events_in_box',
                #'passes_to_box',
                #'creative_passes',
                #'succesful_def_actions',
                #'progressive_carries',
                'red_card',
                'own_goals',
                'yellow_cards',
                'danger_ball_loses',
                #'def_actions%',
                'p_adj_succ_def_actions'
                ] 
    
    # # KPIs when using per_90_All
    # list_kpi_p90 = ['passing%',
    #             'completed_passes_p90',
    #             'fouls_p90',
    #             'aerial%',
    #             'aerial_wins_p90',
    #             'shots_p90',
    #             'dribbles%',
    #             'succesful_dribbles_p90',
    #             'key_passes_p90',
    #             'succesful_through_passes_p90',
    #             'events_in_box_p90',
    #             'passes_to_box_p90',
    #             'creative_passes_p90',
    #             'succesful_def_actions_p90',
    #             'progressive_carries_p90',
    #             'red_card',
    #             'own_goals',
    #             'yellow_cards',
    #             'danger_ball_loses',
    #             'def_actions%'
    #             ]
    
    # Copy the KPI dataframe to add offensive and defensive

    ################################################
    # - Filter the training data
    "----------------------------------------------"
    # Call to fitting function to find coeficient and independent variables
    dep_var_off = 'team_xG'
    model_coef_off, r_squared_off, list_kpi_off_fitting = ff.KPI_fitting(df_KPI_EU_train, scaler,
                                                  list_kpi_off, dep_var_off,
                                                  position, min_minutes)
    
    # Call to fitting function to find coeficient and independent variables
    dep_var_def = 'opponent_xG'
    model_coef_def, r_squared_def, list_kpi_def_fitting = ff.KPI_fitting(df_KPI_EU_train, scaler,
                                                  list_kpi_def, dep_var_def,
                                                  position, min_minutes)
    
    
    ################################################
    # - Use the coeficient from EU to compute percentiles
    #   in the PL gameweek 1-37, filtered PL training data
    "----------------------------------------------"
    
    # Merge the KPIs from the chosen match with the KPIS from 1-37
    
    # Filter and normalise the PL data (including the chosen match)
    df_filtered_PL = pf.filter_dataframe(df_KPI_PL, position, list_kpi_all, min_minutes, 1)
    df_filtered_PL[list_kpi_all] = scaler.fit_transform(df_filtered_PL[list_kpi_all]) 
    
    # KPIs GW 1-37
    df_KPI_PL_train = df_filtered_PL.loc[~(df_filtered_PL.matchId == the_matchId)]
    
    # Initiate rating dataframe for GW 1-37
    df_ratings = pd.DataFrame()
    
    # Loop through players in gameweek 1-37
    for i, player in df_KPI_PL_train.iterrows():
        
        # Add some info to dataframe
        df_ratings.loc[i, 'matchId'] = player['matchId']
        df_ratings.loc[i, 'teamName'] = player['teamName']
        df_ratings.loc[i, 'playerId'] = player['playerId']
        df_ratings.loc[i, 'shortName'] = player['shortName']
        
        ################################################
        # - xG-Fit
        "----------------------------------------------"
    
        # Find the fitted xG 
        xG_fitting_rating_off = ff.compute_fitting_ratings(player, model_coef_off, list_kpi_off_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xG_fitting_rating_off = xG_fitting_rating_off * r_squared_off
        
        # Add to df
        df_ratings.loc[i, 'fitting_rating_off'] = xG_fitting_rating_off
        
        ################################################
        # - opponent_xG-Fit (xGC)
        "----------------------------------------------"
        # Find the fitted opponent xG (xGC)
        xGC_fitting_rating_def = ff.compute_fitting_ratings(player, model_coef_def, list_kpi_def_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xGC_fitting_rating_def = xGC_fitting_rating_def * r_squared_def
        
        # Add to df
        df_ratings.loc[i, 'fitting_rating_def'] = xGC_fitting_rating_def
        
        ################################################
        # - Match event-rating
        "----------------------------------------------"
        
        # Find the event rating and add to dataframe
        match_event_rating = ff.compute_events_rating(player, position, df_KPI)
        df_ratings.loc[i, 'match_events_rating'] = match_event_rating
        
        # Sum fitting rating and add to dataframe
        tot_fit_rating = xG_fitting_rating_off - xGC_fitting_rating_def
        df_ratings.loc[i, 'tot_fit_rating'] = tot_fit_rating
        
        

    # Find percentiles from the rankings in gameweek 1-37 PL 
    percentiles = np.arange(0.01, 1, 0.01)
    percentiles_fit = df_ratings['tot_fit_rating'].quantile(percentiles)
    percentiles_events = df_ratings['match_events_rating'].quantile(percentiles)
    
    ################################################
    # - Compute the rankings of the chosen match gameweek 38 for the position
    "----------------------------------------------"
    # KPIs GW 38
    df_the_match_KPI_players = df_filtered_PL.loc[df_filtered_PL.matchId == the_matchId] 
    
    # Initiate rating dataframe for GW 38
    df_ratings_test = pd.DataFrame()
    
    # Loop through players in gameweek 38
    for i, player in df_the_match_KPI_players.iterrows():
        
        # Add some info to dataframe
        df_ratings_test.loc[i, 'matchId'] = player['matchId']
        df_ratings_test.loc[i, 'teamName'] = player['teamName']
        df_ratings_test.loc[i, 'playerId'] = player['playerId']
        df_ratings_test.loc[i, 'shortName'] = player['shortName']
        
        ################################################
        # - xG-Fit
        "----------------------------------------------"
        
        # Find the fitted xG 
        xG_fitting_rating_off = ff.compute_fitting_ratings(player, model_coef_off, list_kpi_off_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xG_fitting_rating_off = xG_fitting_rating_off * r_squared_off
        
        # Add to df
        df_ratings_test.loc[i, 'fitting_rating_off'] = xG_fitting_rating_off
        
        ################################################
        # - opponent_xG-Fit (xGC)
        "----------------------------------------------"

        # Find the fitted opponent xG (xGC)
        xGC_fitting_rating_def = ff.compute_fitting_ratings(player, model_coef_def, list_kpi_def_fitting)
        
        # Multiply the fitted value with r_squared, how good the fit was
        xGC_fitting_rating_def = xGC_fitting_rating_def * r_squared_def
        
        # Add to df
        df_ratings_test.loc[i, 'fitting_rating_def'] = xGC_fitting_rating_def
        
        ################################################
        # - Match event-rating
        "----------------------------------------------"
        
        # Find the event rating and add to dataframe
        match_event_rating = ff.compute_events_rating(player, position, df_KPI)
        df_ratings_test.loc[i, 'match_events_rating'] = match_event_rating
        
        # Sum fitting rating and add to dataframe
        tot_fit_rating = xG_fitting_rating_off - xGC_fitting_rating_def
        df_ratings_test.loc[i, 'tot_fit_rating'] = tot_fit_rating
    
    # Modify the df_rating_test dataframe and the gameweek 38 dataframe
    ff.create_rating_dataframe(df_ratings_test, df_KPI_PL, df_the_match_KPI_players,
                               percentiles_fit, percentiles_events, df_England_matches)

    # Merge to the raw rating dataframe
    frames = [df_final_rating, df_ratings_test]
    df_final_rating = pd.concat(frames) 


#%%
# - Print the ratings
"---------------------------------------------------------------------------"
print(df_final_rating.match_info.values[0])
table = df_final_rating[['teamName', 'shortName', 'position', 'final_rating']]
print(tabulate(table))



#%%
# - Plot the pitch
"---------------------------------------------------------------------------"

"""
Idea: 
    Find the formation of each team in that game and use as input
    
    Find posistion of each player and add to the final dataframe rating
    
    Find if the player started that game came in
    
"""
positions = ['GK', 'CB', 'LCB', 'RCB', 'LB', 'RB', 'LWB', 'RWB', 'CM', 
             'LCM', 'RCM', 'CAM', 'LM',
             'RM', 'LW', 'RW', 'ST', 'LST', 'RST']

print("Here is the home team lineup:")
# Print home team players 
for player in home_team_lineup:
    print(player)

print("Here is the away team lineup:")
for player in away_team_lineup:
    print(player)

print("Now enter the position for each player in that game.")
print(f"The positions to choose from are the following: \n{positions}")
print("HOME TEAM:")
for player in home_team_lineup:
    print(f"Write the position for: {player}")
    position = input()
    while position not in positions:
        print("NOT A VALID POSITION!")
        print(f"Write the position for: {player}")
        position = input()
    mask_player = df_final_rating.shortName == player
    df_final_rating.loc[mask_player, 'position'] = position
    
print("AWAY TEAM:")
for player in away_team_lineup:
    print(f"Write the position for: {player}")
    position = input()
    while position not in positions:
        print("NOT A VALID POSITION!")
        print(f"Write the position for: {player}")
        position = input()
    mask_player = df_final_rating.shortName == player
    df_final_rating.loc[mask_player, 'position'] = position
    
#%%

df_plot_ratings = df_final_rating.copy()
ff.plot_pitch_ratings(df_plot_ratings, home_team_lineup, home_team_bench, away_team_lineup, away_team_bench)

