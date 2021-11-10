#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 16:41:04 2021

@author: emildanielsson

Program description: 
    
    Funtions which creates a nice looking bar plot that can be used instead 
    player radars.
    
"""


# The basics
import pandas as pd
import numpy as np

# Plotting
import matplotlib.pyplot as plt
from mplsoccer import FontManager

# For images 
from PIL import Image

# other imports 
from pathlib import Path



################################################
# - Load Fonts
"----------------------------------------------"

URL1 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/'
        'fonts/SourceSerifPro-Regular.ttf?raw=true')
serif_regular = FontManager(URL1)
URL2 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/'
        'fonts/SourceSerifPro-ExtraLight.ttf?raw=true')
serif_extra_light = FontManager(URL2)
URL3 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/main/fonts/'
        'SourceSerifPro-Bold.ttf?raw=true')
serif_bold = FontManager(URL3)



""" Function which returns a nice percentile bar plot 

Description: 
    
    Input: dict_player_info, dict_filter, df_KPI, list_param_labels, list_kpi
    
    
        dict_player_info - Dictionary with information about the player that 
        we want plot for. "shortName" must be the same shortName as in the 
        Wyscout dataset and is the player we plot for. "kpi_position" must 
        also be a position that exists in "df_KPI" .The rest of the 
        parameters are just for plotting. The images are optional. 
        Example:
        dict_player_Pogba = {
            "shortName": "P. Pogba",                            # Wyscout shortName 
            "age": 25,                                          # Manual input                     
            "marketValue": "€60.0m",                            # Manual input      
            "teamImg": "Images/manchester_united_logo.png",     # Optional
            "playerImg": "Images/Pogba.png",                    # Optional
            "title_league": "Premier League",                   # For plotting
            "kpi_position": "MID",                              # For filtering
            "title_position": "Midfielders",                    # For plotting
            "team_color": "#DA291C"                             # For plotting
            }        


        dict_filter - Dictionary with information about how to filter "df_KPI"
        Will be inputs to funcion filter_dataframe().
        Example:    
        dict_filter = {
            "min_minutes": 20,
            "min_matches": 10
            }
        
        
        df_KPI - Dataframe with information about player´s KPI´s from x number 
        of games.
        
        
        list_param_labels - List of the labels for the y-axis bars in the hbar.
        Example: 
        list_param_labels = ["Passing%", "Aerial%", 'Dribble%',
            'Events In Box', 'Passes To Box',
            'Creative Passes', 'Successful Def Actions', 'Progressive Carries']
        
        
        list_kpi - List of the KPI´s we want percetiles of. Need to be columns
        that exists in df_KPI
        Example: 
        list_kpi = ['passing%', 'aerial%', 'dribbles%', 'events_in_box',
            'passes_to_box', 'creative_passes', 'succesful_def_actions',
            'progressive_carries']
        
        
    Output: ax, fig
        Returns a nice percentile horizontal bar plot 
        
"""
def barplot_percentiles(dict_player_info, dict_filter, df_KPI, list_param_labels, list_kpi):

 
    ################################################
    # - Set variables
    "----------------------------------------------"
    
    # Set player variables
    player_name = dict_player_info["shortName"]
    player_age = dict_player_info["age"]
    player_market_value = dict_player_info["marketValue"]
    player_posistion = dict_player_info["kpi_position"]
    
    # Find player image if there were any as input
    if dict_player_info["playerImg"]:
        print("Image player path entered")
        player_file = Path(dict_player_info["playerImg"])
        if player_file.is_file():
            # file exists
            player_img = Image.open(dict_player_info["playerImg"])  
        else: 
            print("Image player path not found")
            player_img = None
    else: 
        print("No image player path entered")
        player_img = None
        
    # Find team image if there were any as input
    if dict_player_info["teamImg"]:
        print("Image team path entered")
        team_file = Path(dict_player_info["teamImg"])
        if team_file.is_file():
            # file exists
            team_img = Image.open(dict_player_info["teamImg"])  
        else:
            print("Image team path not found")
            team_img = None
    else: 
        print("No image team path entered")
        team_img = None
    
    # Plot variables
    title_position = dict_player_info["title_position"]
    title_league = dict_player_info["title_league"]
    bar_color = dict_player_info["team_color"]
    
    # Filter df_KPI variables
    min_minutes = dict_filter["min_minutes"]
    min_matches = dict_filter["min_matches"]
    
    
    ################################################
    # - Prepare/filter dataframe and find minutes played
    "----------------------------------------------"
    
    # Sum mids to find minutes played
    df_KPI_sum = df_KPI.groupby(['playerId', 'shortName'], as_index = False).sum()
    
    # Find the player minutes and team name
    mask_player = df_KPI_sum.shortName == player_name
    df_player = df_KPI_sum.loc[mask_player]
    player_minutes = df_player.minutesPlayed.values[0]
    player_team = df_player.teamName.values[0]
    # player_team = "Villareal CF"
    
    # Filter the data
    df_filtered = filter_dataframe(df_KPI, player_posistion, list_kpi, min_minutes, min_matches)


    ################################################
    # - Get the percentiles anhd sort frame labels
    "----------------------------------------------"
    player_percentiles = find_percentiles(df_filtered, player_name, list_kpi)
    list_param_labels = sorted(list_param_labels)
        

    ################################################
    # - Create the Bar plot
    "----------------------------------------------"
    
    # Create the data frame to plot
    df = pd.DataFrame ({
            'Group':  list_param_labels,
            'Value': player_percentiles
    })
    
    
    # Inititate the plot and set facecolor
    fig, ax = plt.subplots(figsize=(16,8)) 
    fig.set_facecolor("white")
    
    # Set a grid
    ax.xaxis.grid(lw=0.3, alpha=0.5, color="k", zorder=1)
    
    # Create horizontal bars
    ax.barh(y=df.Group, width=df.Value, color = bar_color);
    
    # Adding title and subtitle
    fig.text(0.05,1, player_name + ", " +player_team + " 2017-18 \n", fontsize = 20,
             fontproperties = serif_bold.prop)
    fig.text(0.05,1,"Minutes played: " + str(player_minutes), fontsize = 16,
             fontproperties = serif_regular.prop)
    fig.text(0.05,0.96,f"Market Value: {player_market_value}", fontsize = 16,
             fontproperties = serif_regular.prop)
    fig.text(0.05,0.92,"Age: " + str(player_age), fontsize = 16,
             fontproperties = serif_regular.prop)
    
    # Adding Percentile inforamtion
    fig.text(0.95,1, "Percentile Ranks\n", fontsize = 20,
             fontproperties = serif_bold.prop, ha="right")
    fig.text(0.95,1,f"{title_league} {title_position}", fontsize = 16,
             fontproperties = serif_regular.prop, ha="right")
    
    # x label, Thought it looked nicer without the label
    # ax.set_xlabel("Percentile Rank", fontproperties = serif_bold.prop, fontsize = 16)
    
    # Rotate y labels slithly 
    plt.yticks(rotation = 10)
    
    # Set x-ticks to be 0, 10, ... , 100 
    plt.xticks(ticks = np.linspace(0, 100, num=11))
    ax.set_xlim(0, 105)
    
    # Write out reference to Statsbomb
    fig.text(0.05,-0.025, 'Data provided by Wyscout', fontsize = 12, 
             fontproperties = serif_regular.prop, color = '#414141')
    
    # remove pips
    ax.tick_params(axis="both", length = 0)
    
    # remove top, right and left spines
    ax.spines["top"].set_visible(False) 
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False) 
    
    # Set ticklabels setting y axis
    ticklabels = [t for t in plt.gca().get_yticklabels()]
    for l in list_param_labels:
        i = list_param_labels.index(l)
        # ticklabels[i].set_color("red")
        ticklabels[i].set_fontproperties(serif_bold.prop)
        ticklabels[i].set_fontsize(14)
        
    # Set ticklabels setting x axis
    for label in ax.get_xticklabels():
        label.set_fontproperties(serif_regular.prop)
        label.set_fontsize(12)
        
    # # Adding team logo, Optional
    if team_img:
        ax2 = fig.add_axes([0.15, 0.83, 0.15, 0.15])
        ax2.axis("off")
        ax2.imshow(team_img)    
    
    # Adding player image, Optional
    if player_img:
        ax3 = fig.add_axes([0.42, 0.83, 0.20, 0.25])
        ax3.axis("off")
        ax3.imshow(player_img)
    
    # The tight_layout() function in pyplot module of matplotlib library is used 
    # to automatically adjust subplot parameters to give specified padding.
    plt.tight_layout()
    
    # Make some more room for the images
    if (player_img or team_img):
        fig.subplots_adjust(top=0.83)
    else:
        fig.subplots_adjust(top=0.95)
        
    return ax, fig


# - End function
##############################################################################



""" Function which filters the dataframe 

Description: 
    
    Input:  df_KPI, position, list_kpi, min_minutes, min_matches
    
            df_KPI - Dataframe with information about player´s KPI´s 
            from x number of games.
            
            position - postion to filter for
            
            list_kpi - selected kpi column´s to include in the returne dataframe
            
            min_minutes - minutes to filter for
            
            min_matches - total number of matches to filter for
        
    Output: df_pos_final
            df_pos_final - Filtered dataframe
            
        
"""
def filter_dataframe(df_KPI, positions, list_kpi, min_minutes, min_matches):
    
    # Create a dataframe with all the players from chosen position
    mask_pos = df_KPI.role.isin(positions)
    df_pos = df_KPI.loc[mask_pos]
    
    # Find the matches were the players have played more than "min_minutes" 
    mask_tot_min = df_pos.minutesPlayed > min_minutes
    df_pos = df_pos.loc[mask_tot_min] 
    
    # Find the unique player Id´s
    player_list = df_pos['playerId'].unique().tolist()
    
    # Loop through and add the players with more than "min_matches" 
    # matches to the dataframe
    player_list_high_minutes = []
    for player in player_list:
        mask_player = df_pos.playerId == player
        df_player = df_pos.loc[mask_player]
        nr_of_matches = len(df_player)
        
        # Add player to the list
        if (nr_of_matches >= min_matches):
            player_list_high_minutes.append(player)
            
    # Create the final dataframe with matches
    mask_tot_matches = df_pos.playerId.isin(player_list_high_minutes)
    df_pos_final = df_pos.loc[mask_tot_matches]
    
    # Only return the relevant columns
    list_columns = list_kpi.copy()
    list_columns.extend(['playerId', 'shortName', 'teamName', 'matchId']) 
    df_pos_final = df_pos_final[df_pos.columns.intersection(list_columns)]

    return df_pos_final

# - End function
#############################################################################




"""  Function to find the player percentiles for "player_name" given the kpi´s 
    in list_kpi.

Description: 
     
    Input: df_KPI, player_name, list_kpi
    
        df_KPI - Dataframe with information about player´s KPI´s 
        from x number of games. Should probably be filtered before use.
        
        player_name - player to find percentiles for
        
        list_kpi - list of the kpi´s we want the percetiles for
        
    Output: player_percentiles
        player_percentiles - returns list with player percentiles ordered 
        as list_kpi alpabetical ordered
        
"""
def find_percentiles(df_KPI, player_name, list_kpi):
    
    # Find the mean dataframe
    df_data_mean = df_KPI.groupby(['playerId', 'shortName'], as_index = False).mean()
    
       
    ################################################
    # - Get the player stats
    "----------------------------------------------"
    
    # Get the Stats from chosen player
    mask_player = df_data_mean.shortName == player_name
    df_player = df_data_mean.loc[mask_player]
    
    # Drop the player info so we can sort kpi correctly
    df_data_mean = df_data_mean.drop(['playerId', 'shortName'], axis = 1)
    
    # Sort columns and list_param_labels alpabetically to make sure order gets right
    df_data_mean = df_data_mean.reindex(sorted(df_data_mean.columns), axis=1)
    list_kpi = sorted(list_kpi)
    # list_param_labels = sorted(list_param_labels)
    
    # Drop here to easy find the relevant values to a list
    df_stats_player = df_player.drop(['playerId', 'shortName'], axis = 1)
    df_stats_player = df_stats_player.reindex(sorted(df_stats_player.columns), axis=1)
    
    
    ################################################
    # - Get the percentiles
    "----------------------------------------------"
    percentiles = np.arange(0.05, 1, .05)
    df_percentiles = df_data_mean.quantile(percentiles)
         
        
    ################################################
    # - Find the player percentiles
    "----------------------------------------------"
    
    player_percentiles = []
    # Loop through all the kpi´s to find which percentile the values belong to
    for kpi_i in list_kpi:
        # print(kpi_i)
        value = df_stats_player[kpi_i].values[0]
        for i, percentile in df_percentiles.iterrows():
            if (value < percentile[kpi_i]):
                # print(kpi_i + ": " + str(i))
                player_percentiles.append(round(i, 2) * 100)
                break
        if (value > percentile[kpi_i]):
            # print(kpi_i + ": " + str(1))
            player_percentiles.append(100)

    return player_percentiles


# - End function
#############################################################################