#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson & JakobEP

Program description: 
    
    Funtions for fitting.
    
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
# - Functions
"---------------------------------------------------------------------------" 

""" Function which takes in dataframe of shots and outputs 
    dataframes which contains information about the logistic
    regression models for the different shot-types. 

Description: 
    
    Regression model variables:

        Dependent variable: Goal
        Independent variables: Angle, Distance, Distance squared 
    
    Input:
           df_xG_model - dataframe for all shots, headers, freekicks, penalties
           and their tags (go/no goal)
        
    Output: 
            dataframes for all coefficients and fitted log models
        
"""
def xG_model(df_xG_model):
    
    #################################################
    # - Filter out headers and freekicks
    "------------------------------------------------"
    
    mask_headers = df_xG_model.header == 1
    mask_free_kicks = df_xG_model.free_kick == 1
    
    df_xG_shots = df_xG_model[(~mask_headers) & (~mask_free_kicks)]
    df_xG_headers = df_xG_model[mask_headers]
    df_xG_free_kicks = df_xG_model[mask_free_kicks]
    
    
    #################################################
    # - Split data into test and training sets, 
    #   looking at distance (dist) and angle (ang) in radians. xG-shots.
    "------------------------------------------------"
    
    df_trainSet = df_xG_shots[['goal', 'distance', 'angle_rad']].copy()
    
    # Adding distance squared to df
    squaredD = df_trainSet['distance']**2
    df_trainSet = df_trainSet.assign(distance_sq = squaredD)
    
    # y(x) where y = shot result, x1 = distance, x2 = angle
    x_train, x_test, y_train, y_test = train_test_split(df_trainSet.drop('goal', axis=1), 
                                                        df_trainSet['goal'], test_size=0.20, 
                                                        random_state=10)
    
    
    #################################################
    # - Create logistic model and fit it to data. xG-shots.
    "------------------------------------------------"
    
    # Create instance
    log_model = LogisticRegression()
    
    # Fit model with training data
    log_model.fit(x_train, y_train)
    
    # Read out coefficent(s) into df
    log_model_coef = log_model.coef_[0]
    
    # Create df of fit
    df_log_model_shots_coef = pd.DataFrame(log_model_coef, 
                 x_train.columns, 
                 columns=['coef']).sort_values(by='coef', ascending=False)
    
    # Add to df
    df_log_model_shots_coef.loc['intercept'] = log_model.intercept_[0]
    print(df_log_model_shots_coef)
    
    
    #################################################
    # - Split data into test and training sets, 
    #   looking at distance (dist) and angle (ang) in radians. xG-headers.
    "------------------------------------------------"
    
    df_trainSet_headers = df_xG_headers[['goal', 'distance', 'angle_rad']].copy()
    
    # Adding distance squared to df
    squaredD = df_trainSet_headers['distance']**2
    df_trainSet_headers = df_trainSet_headers.assign(distance_sq = squaredD)
    
    # y(x) where y = shot result, x1 = distance, x2 = angle
    x_train_h, x_test_h, y_train_h, y_test_h = train_test_split(df_trainSet_headers.drop('goal', axis=1), 
                                                        df_trainSet_headers['goal'], test_size=0.20, 
                                                        random_state=10)
    
    
    #################################################
    # - Create logistic model and fit it to data. xG-headers.
    "------------------------------------------------"
    
    # Create instance
    log_model_headers = LogisticRegression()
    
    # Fit model with training data
    log_model_headers.fit(x_train_h, y_train_h)
    
    # Read out coefficent(s) into df
    log_model_headers_coef = log_model_headers.coef_[0]
    
    # Create df of fit
    df_log_model_headers_coef = pd.DataFrame(log_model_headers_coef, 
                 x_train_h.columns, 
                 columns=['coef']).sort_values(by='coef', ascending=False)
    
    # Add to df
    df_log_model_headers_coef.loc['intercept'] = log_model_headers.intercept_[0]
    print(df_log_model_headers_coef)
    
    
    #################################################
    # - Split data into test and training sets, 
    #   looking at distance (dist) and angle (ang) in radians. xG-free-kicks.
    "------------------------------------------------"
    
    df_trainSet_free_kicks = df_xG_free_kicks[['goal', 'distance', 'angle_rad']].copy()
    
    # Adding distance squared to df
    squaredD = df_trainSet_free_kicks['distance']**2
    df_trainSet_free_kicks = df_trainSet_free_kicks.assign(distance_sq = squaredD)
    
    # y(x) where y = shot result, x1 = distance, x2 = angle
    x_train_f, x_test_f, y_train_f, y_test_f = train_test_split(df_trainSet_free_kicks.drop('goal', axis=1), 
                                                        df_trainSet_free_kicks['goal'], test_size=0.20, 
                                                        random_state=10)
    
    
    #################################################
    # - Create logistic model and fit it to data. xG-free-kicks.
    "------------------------------------------------"
    
    # Create instance
    log_model_free_kicks = LogisticRegression()
    
    # Fit model with training data
    log_model_free_kicks.fit(x_train_f, y_train_f)
    
    # Read out coefficent(s) into df
    log_model_free_kicks_coef = log_model_free_kicks.coef_[0]
    
    # Create df of fit
    df_log_model_free_kicks_coef = pd.DataFrame(log_model_free_kicks_coef, 
                 x_train_f.columns, 
                 columns=['coef']).sort_values(by='coef', ascending=False)
    
    # Add to df
    df_log_model_free_kicks_coef.loc['intercept'] = log_model_free_kicks.intercept_[0]
    print(df_log_model_free_kicks_coef)
    
    return df_log_model_shots_coef, df_log_model_headers_coef, df_log_model_free_kicks_coef, log_model, log_model_headers, log_model_free_kicks



""" Function to determine the position of a player.
    Inputs: x: average x-coordinate
            y: average y-coordinate
            position: Position taken from Wyscout "role"-column 
"""   
def decide_position(x, y, position):
    if (position == "Defender"):
        if (y < 30):
            return "LB"
        elif (y > 70):
            return "RB"
        else:
            return "CB"
    elif (position == "Midfielder"):
        if (y < 30):
            return "LM"
        elif (y > 70):
            return "RM"
        else:
            return "CM"      
    elif (position == "Forward"):
        if (y < 30):
            return "LW"
        elif (y > 70):
            return "RW"
        else:
            return "ST" 
    elif (position == "Goalkeeper"):
        return "GK"
    else:
        return "?"



""" Function which does linear regression fitting of KPI against 
    dep_var (team_xG or opponent_xG) for a given position.
    Iteratively removes one independent vaiable at a time that is
     concidered statistically insignificant (p-value > 0.05). 

    Description: 
    
    Regression model variables:

        Dependent variable: dep_var (team_xG or opponent_xG)
        Independent variables: KPI values
    
    Input:
        KPI_train - dataframe of KPIs that can be used as training data
        scaler - chosen scaler method for the normalization of KPIs
        list_kpi - list of KPIs used for training data
        dep_var -  model dependent variable
        position - position to find model for
        min_minutes - minimum minutes played for a player in a match
            to be included in the regression model training data. 
        
    Output: 
            model_coef - linear regression model coefficients 
            r_squared - resulting r-squared of the model
            list_kpi_fitting - list of statistically significant KPIs

"""
def KPI_fitting(KPI_train, scaler, list_kpi, dep_var, position, min_minutes):
    
    list_kpi_fitting = list_kpi.copy()
    
    # Append the dependent variable
    list_kpi_fitting.append(dep_var)

    ################################################
    # - Filter the training data
    "----------------------------------------------"
    df_train_filtered = pf.filter_dataframe(KPI_train, position, list_kpi_fitting, min_minutes, 1)
    
    # Normalise
    df_train_filtered[list_kpi_fitting[:-1]] = scaler.fit_transform(df_train_filtered[list_kpi_fitting[:-1]])  
    
    
    ################################################
    # - First Linear regression model for this position
    "----------------------------------------------"
    # First Linear regression model 
    X = df_train_filtered[list_kpi_fitting[:-1]] # Dep. var last
    X = sm.add_constant(X)
    y = df_train_filtered[dep_var] # Dep. var
    test_model = sm.OLS(y, X).fit()
    #print(f"Model before tuning for the position {position}: \n")
    #print(test_model.summary())        
    
    ################################################
    # - Do iterations of Linear regression model to exclude some independent variables
    "----------------------------------------------"
    model_pvalues = test_model.pvalues
    model_pvalues = model_pvalues.drop('const', axis = 0)
    pvalues_check = model_pvalues.values <= 0.05
    
    # Loop regression model and take out the highest KPI with the highest pvalue one at a time 
    while False in pvalues_check:
        
        # Find highest pvalue kpi
        highest_kpi = model_pvalues[model_pvalues == model_pvalues.values.max()].index[0]
            
        # New list of KPIs 
        list_kpi_fitting.remove(highest_kpi)
        
        # Filter the data
        df_train_filtered = pf.filter_dataframe(KPI_train, position, list_kpi_fitting, min_minutes, 1)
        
        # Normalise the new frame
        df_train_filtered[list_kpi_fitting[:-1]] = scaler.fit_transform(df_train_filtered[list_kpi_fitting[:-1]]) 
        
        # Linear regression model 
        X = df_train_filtered[list_kpi_fitting[:-1]]
        X = sm.add_constant(X)
        y = df_train_filtered[dep_var]
        test_model = sm.OLS(y, X).fit()
        
        model_pvalues = test_model.pvalues
        model_pvalues = model_pvalues.drop('const', axis = 0)
        pvalues_check = model_pvalues.values <= 0.05
    
    
    # Print model after the tuning
    print(f"Model AFTER tuning for the position {position}: \n")
    print(test_model.summary())  
    model_coef = test_model.params
    r_squared = test_model.rsquared
    
    return model_coef, r_squared, list_kpi_fitting


def compute_fitting_ratings(player, model_coef, list_kpi_fitting):
    
        result = 0
        
        for kpi in list_kpi_fitting[:-1]:
            result += (model_coef[kpi] * player[kpi])
                          
        result += model_coef['const']   
        
        return result
    
# Add position and weights
def compute_events_rating(player, position, df_KPI):
    
    dict_weights = {'plus_minus': 0.2,
                    'goals': 1,
                    'assists': 0.7,
                    'own_goals': -0.5,
                    'yellow_cards': -0.05,
                    'danger_ball_loses': -0.2,
                    'xG_tot': -0.1,
                    'red_card': -1,
                    'aerial%': 0.1,
                    'def_actions%':0.1,
                    'p_adj_succ_def_actions': 0.1,
                    'succesful_dribbles': 0.05,
                    'creative_passes': 0.1,
                    'progressive_carries': 0.05
                    }   
     
    #Set weight for the different positions
    if position == ['LB', 'RB']:
         #dict_weights['aerial%'] = 0.4
         dict_weights['def_actions%'] = 0.2
         #dict_weights['p_adj_succ_def_actions'] = 0.4
         #dict_weights['creative_passes'] = 0.4
         dict_weights['progressive_carries'] = 0.15
    elif position == ['CB']:
         dict_weights['aerial%'] = 0.3
         dict_weights['def_actions%'] = 0.8
         dict_weights['p_adj_succ_def_actions'] = 0.6
    elif position == ['LM', 'RM']:
        dict_weights['aerial%'] = 0.05
        dict_weights['def_actions%'] = 0.05
        dict_weights['creative_passes'] = 0.2
        dict_weights['progressive_carries'] = 0.1
        dict_weights['succesful_dribbles'] = 0.1
    elif position == ['CM']:
        dict_weights['creative_passes'] = 0.3
        #dict_weights['progressive_carries'] = 0.1
        dict_weights['succesful_dribbles'] = 0.1
        #dict_weights['p_adj_succ_def_actions'] = 0.3
    elif position == ['LW', 'RW']:
        dict_weights['aerial%'] = 0.05
        dict_weights['def_actions%'] = 0.05
        dict_weights['creative_passes'] = 0.6
        dict_weights['progressive_carries'] = 0.3
        dict_weights['succesful_dribbles'] = 0.4
        dict_weights['p_adj_succ_def_actions'] = 0.05
    elif position == ['ST']:
        dict_weights['def_actions%'] = 0
        #dict_weights['aerial%'] = 0.1
        #dict_weights['creative_passes'] = 0.6
        #dict_weights['progressive_carries'] = 0.5
        #dict_weights['succesful_dribbles'] = 0.4
        dict_weights['p_adj_succ_def_actions'] = 0
    else:
         print("Not a valid position")
    
    # Find the KPI dataframe
    mask_match = ((df_KPI['matchId'] == player.matchId) & (df_KPI['playerId'] == player.playerId))
    df_the_match = df_KPI.loc[mask_match]
    
    # Sum the event rating
    event_rating = 0
    for weight_name in dict_weights:
        #print(weight)
        weight = dict_weights[weight_name]
        value = df_the_match[weight_name].values[0]
        event_rating += (value * weight) 
    
    event_rating = event_rating / 20
    
    return event_rating



def create_rating_dataframe(df_ratings, df_KPI, df_KPI_test, percentiles_fit, percentiles_events, df_matches):
    for i, player in df_ratings.iterrows():
        mask_match = ((df_KPI['matchId'] == player.matchId) & (df_KPI['playerId'] == player.playerId))
        # df_the_match = df_KPI_PL.loc[mask_match]
        if df_ratings.loc[i, 'tot_fit_rating'] < percentiles_fit.values[0]:
            final_fit_rating = 0.1
        else: 
            for percentile in percentiles_fit.values:
                if df_ratings.loc[i, 'tot_fit_rating'] > percentile:
                    final_fit_rating = round(percentiles_fit[percentiles_fit == percentile].index[0] * 5, 1)
        if df_ratings.loc[i, 'match_events_rating'] < percentiles_events.values[0]:
            final_event_rating = 0.1
        else: 
            for percentile in percentiles_events.values:
                if df_ratings.loc[i, 'match_events_rating'] > percentile:
                    final_event_rating = round(percentiles_events[percentiles_events == percentile].index[0] * 5, 1)
        
        final_rating = final_fit_rating + final_event_rating
        
        # Find the match info to easier look up the rating elsewhere
        the_match = df_matches.loc[df_matches['wyId'] == player.matchId]
        match_info = the_match.label.values[0]
        gameweek = the_match.gameweek.values[0]
        
        # Add the final rating and info to both the test-df and the ratings-df
        df_ratings.loc[i, 'position'] = df_KPI.loc[mask_match, 'role'].values[0]
        df_ratings.loc[i, 'match_info'] = match_info
        df_ratings.loc[i, 'final_rating'] = final_rating
        df_ratings.loc[i, 'gameweek'] = gameweek
        
        #tot_rating = df_ratings.loc[i, 'tot_rating']
        fitting_rating_off = df_ratings.loc[i, 'fitting_rating_off']
        fitting_rating_def = df_ratings.loc[i, 'fitting_rating_def']
        tot_fit_rating = df_ratings.loc[i, 'tot_fit_rating']
        match_events_rating = df_ratings.loc[i, 'match_events_rating']
        
        #df_KPI_test.loc[mask_match, 'tot_rating'] = tot_rating
        df_KPI_test.loc[mask_match, 'fitting_rating_off'] = fitting_rating_off
        df_KPI_test.loc[mask_match, 'fitting_rating_def'] = fitting_rating_def
        df_KPI_test.loc[mask_match, 'tot_fit_rating'] = tot_fit_rating
        df_KPI_test.loc[mask_match, 'match_events_rating'] = match_events_rating
        df_KPI_test.loc[mask_match, 'final_rating'] = final_rating
        df_KPI_test.loc[mask_match, 'match_info'] = match_info
        df_KPI_test.loc[mask_match, 'gameweek'] = gameweek
        
        
        
"""

""" 
def plot_pitch_ratings(df_final_rating, home_team_lineup, home_team_bench, away_team_lineup, away_team_bench):
    pitch = Pitch(pitch_type="wyscout")
    fig, ax = pitch.draw(figsize=(7,15))
    
    match_result = df_final_rating.match_info.values[0]
    
    ax.text(50, -5, match_result, ha = "center", fontsize = 16, fontproperties = serif_bold.prop)
    
    text_size = 10
    
    alpha_scaling = 13
    
    pitch_positions = {
        'LB':  [10, 12],
        'LWB':  [17, 12],
        'LCB': [3, 30],
        'CB': [2, 50],
        'RB': [10, 88],
        'RWB': [17, 88],
        'RCB': [3, 70],
        'LM': [28, 12],
        'RM': [28, 88],
        'LCM': [20, 35],
        'CM': [17, 50],
        'RCM': [20, 65],
        'CAM': [38, 50],
        'LW': [47, 25],
        'RW': [47, 75],
        'ST': [49, 50],
        'LST': [49, 40],
        'RST': [49, 60],
        }
    
    
    # Team colors 
    team_colors = {
        'Huddersfield Town FC':  "#0E63AD",
        'Manchester United FC':  '#DA291C',
        'Tottenham Hotspur FC': '#132257',
        'Newcastle United FC': '#241F20',
        'Stoke City FC': '#E03A3E',
        'Southampton FC': '#D71920',
        'Everton FC': '#003399',
        'Leicester City FC': '#003090',
        'Crystal Palace FC':'#1B458F',
        'West Ham United FC': '#7A263A',
        'Burnley FC': '#6C1D45',
        'Swansea City AFC': '#121212',
        'West Bromwich Albion FC': '#122F67',
        'AFC Bournemouth': '#DA291C',
        'Brighton & Hove Albion FC': '#0057B8',
        'Watford FC': '#FBEE23',
        'Liverpool FC': '#C8102E',
        'Chelsea FC': '#034694',
        'Manchester City FC': '#6CABDD',
        'Arsenal FC':'#EF0107'
        }
    
    attackers = ['LW', 'CAM',
        'RW',
        'ST',
        'LST',
        'RST']
    
    # Creta list of the players in ranking dataframe
    ranked_players = df_final_rating['shortName'].tolist()
    
    # adjust for the rating box in the plot
    box_adjustment = 5
    
    # Place the home team lineup on the pitch
    for player in home_team_lineup:
        mask_player = df_final_rating.shortName == player
        position = df_final_rating.loc[mask_player, 'position'].values[0]
        rating = df_final_rating.loc[mask_player, 'final_rating'].values[0]
        team = df_final_rating.loc[mask_player, 'teamName'].values[0]
        
        # Set the team_color
        team_color = team_colors[team]
        
        # Make sure to seperate name if it is too long
        shortName = player.split()
        shortName_new = ""
        if len(shortName) == 1:
                shortName_new = player
        else:
             for i in range(2):
                shortName_new += shortName[i]
                if i == 0: 
                    shortName_new += " "
                    print("hej")
        
        x = pitch_positions[position][0]
        y = pitch_positions[position][1] + box_adjustment
        
        alignment = "left"
        box_addition = 3
        if position in attackers:
            alignment = "right"
            box_addition = -3
            
        props = dict(boxstyle='round', facecolor=team_color, alpha=rating/alpha_scaling)
        # place a text box with rating
        ax.text(x+box_addition, y-5, str(round(rating, 1)), ha = alignment, fontsize = text_size,
             fontproperties = serif_bold.prop, bbox=props)
        ax.text(x, y, shortName_new, ha = alignment, fontsize = text_size, color=team_color,
             fontproperties = serif_bold.prop) # add fonts
    
    
    # Place the home team bench
    bench_x = -2
    bench_y = 110
    for player in home_team_bench:
        
        # check if the bench player played
        if player in ranked_players:
            
            mask_player = df_final_rating.shortName == player
            rating = df_final_rating.loc[mask_player, 'final_rating'].values[0]           
            team = df_final_rating.loc[mask_player, 'teamName'].values[0]
        
            # Set the team_color
            team_color = team_colors[team]
            
            # Make sure to seperate name if it is too long
            shortName = player.split()
            shortName_new = ""
            if len(shortName) == 1:
                    shortName_new = player
            else:
                 for i in range(2):
                    shortName_new += shortName[i]
                    if i == 0: 
                        shortName_new += " "
                        print("hej")
                    
            props = dict(boxstyle='round', facecolor=team_color, alpha=rating/alpha_scaling)
            # place a text box with rating
            ax.text(bench_x+5, bench_y-5, str(round(rating, 1)), ha = "center", fontsize = text_size,
                    fontproperties = serif_bold.prop, bbox=props)
            ax.text(bench_x, bench_y, shortName_new, ha = "left", fontsize = text_size, color=team_color,
             fontproperties = serif_regular.prop) # add fonts
            bench_x += 20
    
    # Place the away team lineup
    for player in away_team_lineup:
        mask_player = df_final_rating.shortName == player
        position = df_final_rating.loc[mask_player, 'position'].values[0]
        rating = df_final_rating.loc[mask_player, 'final_rating'].values[0]
        team = df_final_rating.loc[mask_player, 'teamName'].values[0]
        
        # Set the team_color
        team_color = team_colors[team]
        
        # Make sure to seperate name if it is too long
        shortName = player.split()
        shortName_new = ""
        if len(shortName) == 1:
                shortName_new = player
        else:
             for i in range(2):
                shortName_new += shortName[i]
                if i == 0: 
                    shortName_new += " "
                    print("hej")
        
        alignment = "right"
        box_addition = -3
        if position in attackers:
            alignment = "left"
            box_addition = +3
        
        x = 100-pitch_positions[position][0]
        y = 100-pitch_positions[position][1] + box_adjustment
        
        # place a text box with rating
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor=team_color, alpha=rating/alpha_scaling)
        ax.text(x+box_addition, y-5, str(round(rating, 1)), ha = alignment, fontsize = text_size,
             fontproperties = serif_bold.prop, bbox=props)
        ax.text(x, y, shortName_new, fontsize = text_size, ha = alignment, color=team_color,
                 fontproperties = serif_bold.prop) # add fonts
    
    bench_x = 50
    bench_y = 110
    for player in away_team_bench:
        # check if the bench player played
        if player in ranked_players:
            mask_player = df_final_rating.shortName == player
            rating = df_final_rating.loc[mask_player, 'final_rating'].values[0]
            team = df_final_rating.loc[mask_player, 'teamName'].values[0]
        
            # Set the team_color
            team_color = team_colors[team]
            
            # Make sure to seperate name if it is too long
            shortName = player.split()
            shortName_new = ""
            if len(shortName) == 1:
                    shortName_new = player
            else:
                 for i in range(2):
                    shortName_new += shortName[i]
                    if i == 0: 
                        shortName_new += " "
                        print("hej")
                    
            # place a text box with rating
            props = dict(boxstyle='round', facecolor=team_color, alpha=rating/alpha_scaling)
            ax.text(bench_x+5, bench_y-5, str(round(rating, 1)), ha = "center", fontsize = text_size,
                    fontproperties = serif_bold.prop, bbox=props)
            
            # place name of the benched player
            ax.text(bench_x, bench_y, shortName_new, ha = "left", fontsize = text_size, color=team_color,
             fontproperties = serif_regular.prop) # add fonts
            bench_x += 15       
            
    
    
            