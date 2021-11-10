#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 16:15:36 2021

@author: emildanielsson & JakobEP

Program description: 
    Code that contains all functions that returns the relevant KPI's.
    
"""

# The basics
import pandas as pd
import numpy as np
import json


#############################################################################
# - KPI-functions
"---------------------------------------------------------------------------"


""" Function which computes the KPI: % Passes completed.

Description: 
    
    Input:
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - % of passes completed in a match
            info - dictionary with background info of computed kpi
        
"""
def percent_passes_completed(df_events_player, player_minutes):
    
    # Initiate variable for KPI-result
    result_kpi = 0.0
     
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    df_passes = df_events_player.loc[mask_passes]
    
    # Find number of events
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variables for passing%
        nr_completed_passes = 0
        nr_incompleted_passes = 0
        
        # Loop through all the passes
        for i, pass_i in df_passes.iterrows():
            
            # Loop through all the tags from that pass
            for passtags in pass_i['tags']:
                
                # tag 1801 == Accurate
                if passtags['id'] == 1801:
                    nr_completed_passes += 1
                
                # tag 1802 == Inaccurate
                elif passtags['id'] == 1802:
                    nr_incompleted_passes += 1
            
        # Compute results, passing accuraccy
        result_kpi = round(nr_completed_passes / (nr_completed_passes + nr_incompleted_passes), 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'completed_passes': nr_completed_passes,
                'incompleted_passes': nr_incompleted_passes}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################



""" Function which computes the KPI: Passes completed tot, and per 90.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - commited fouls
            result_kpi_p90 - commited fouls per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def passes_completed(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
    
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    df_passes = df_events_player.loc[mask_passes]
    
    # Find number of events
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for passes completed
        nr_completed_passes = 0
        
        # Loop through all the passes
        for i, pass_i in df_passes.iterrows():
            
            # Loop through all the tags from that pass
            for passtags in pass_i['tags']:
                
                # tag 1801 == Accurate
                if passtags['id'] == 1801:
                    nr_completed_passes += 1
        
        # Find results
        result_kpi = nr_completed_passes
        
        # Compute results computed passes per 90 minutes played
        result_kpi_p90 = round((nr_completed_passes / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'completed_passes': nr_completed_passes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Fouls tot and per 90 minutes.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - commited fouls
            result_kpi_p90 - commited fouls per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def fouls(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
    
    # Filter out passes from events data
    mask_fouls = df_events_player.eventName == 'Foul'
    df_fouls = df_events_player.loc[mask_fouls]
    
    # Find number of events
    nr_of_events = len(df_fouls)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variables for fouls
        tot_fouls = nr_of_events
        
        # Find results
        result_kpi = tot_fouls
        
        # Compute result, fouls per 90 minutes played
        result_kpi_p90 = round((tot_fouls / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: % Aerial wins.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - % of aerial duels won in a match
            info - dictionary with background info of computed kpi
        
"""
def percent_aerial_wins(df_events_player, player_minutes):
     
    # Initiate variables for KPI-result
    result_kpi = 0
    
    # Filter out passes from events data
    mask_aerials = df_events_player.subEventName == 'Air duel'
    df_aerials = df_events_player.loc[mask_aerials]
    
    # Find number of events
    nr_of_events = len(df_aerials)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variables for aerials
        nr_won_aerials = 0
        nr_neutral_aerials = 0
        nr_lost_aerials = 0
        
        # Loop through all the passes
        for i, aerial_i in df_aerials.iterrows():
            
            # Loop through all the tags from that aerial 
            for tag in aerial_i['tags']:
                
                # tag 703 == won
                if tag['id'] == 703:
                    nr_won_aerials += 1
                
                # tag 702 == neutral
                elif tag['id'] == 702:
                    nr_neutral_aerials += 1
                    
                # tag 701 == lost
                elif tag['id'] == 701:
                    nr_lost_aerials += 1
            
        # Compute results, % aerials won
        result_kpi = round(nr_won_aerials / (nr_won_aerials + nr_neutral_aerials + nr_lost_aerials), 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'aerials_won': nr_won_aerials,
                'aerials_neutral': nr_neutral_aerials,
                'aerials_lost': nr_lost_aerials}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################



""" Function which computes the KPI: Aerials won tot and per 90.

Description: 
    
    Input:
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - aerial duels won
            result_kpi_p90 - aerial duels won per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def aerials_won(df_events_player, player_minutes):
     
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
    
    # Filter out passes from events data
    mask_aerials = df_events_player.subEventName == 'Air duel'
    df_aerials = df_events_player.loc[mask_aerials]
    
    # Find number of events
    nr_of_events = len(df_aerials)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variables for aerials
        nr_won_aerials = 0
        
        # Loop through all the passes
        for i, aerial_i in df_aerials.iterrows():
            
            # Loop through all the tags from that pass
            for tag in aerial_i['tags']:
                
                # tag 703 == won
                if tag['id'] == 703:
                    nr_won_aerials += 1
        
        # Find results
        result_kpi = nr_won_aerials
        
        # Compute results, aerials win per 90 minutes played
        result_kpi_p90 = round((nr_won_aerials / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'aerials_won': nr_won_aerials}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Shots taken tot and per 90.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - shots taken
            result_kpi_p90 - shots taken per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def shots(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out passes from events data
    mask_shots = df_events_player.eventName == 'Shot'
    df_shots = df_events_player.loc[mask_shots]
    
    # Find number of events
    nr_of_events = len(df_shots)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:

        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Find results
        result_kpi = nr_of_events
        
        # Compute results, shots taken per 90 minutes played
        result_kpi_p90 = round((nr_of_events / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: % Successful dribbles.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - % of succesful dribbles
            info - dictionary with background info of computed kpi
        
"""
def percent_succesful_dribbles(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0

    # Filter out passes from events data
    mask_dribbles = df_events_player.subEventName == 'Ground attacking duel'
    df_dribbles = df_events_player.loc[mask_dribbles]
    
    # Find number of events
    nr_of_events = len(df_dribbles)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variables for dribbles
        nr_succesful_dribbles = 0
        nr_unsuccesful_dribbles = 0
        
        # Loop through all the passes
        for i, aerial_i in df_dribbles.iterrows():
            
            # Loop through all the tags from that pass
            for tag in aerial_i['tags']:
                
                # tag 1801 == accurate
                if tag['id'] == 1801:
                    nr_succesful_dribbles += 1
                
                # tag 1802 == not accurate
                elif tag['id'] == 1802:
                    nr_unsuccesful_dribbles += 1
            
        # Compute results, % succesful dribbles
        result_kpi = round(nr_succesful_dribbles / (nr_succesful_dribbles + nr_unsuccesful_dribbles), 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'succesful_dribbles': nr_succesful_dribbles,
                'unsuccesful_dribbles': nr_unsuccesful_dribbles}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################




""" Function which computes the KPI: Succesful dribbles tot and per 90.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - number of succesful dribbles
            result_kpi_p90 - number of succesful dribbles per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def succesful_dribbles(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out passes from events data
    mask_dribbles = df_events_player.subEventName == 'Ground attacking duel'
    df_dribbles = df_events_player.loc[mask_dribbles]
    
    # Find number of events
    nr_of_events = len(df_dribbles)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variables for dribbles
        nr_succesful_dribbles = 0
        nr_unsuccesful_dribbles = 0
        
        # Loop through all the passes
        for i, aerial_i in df_dribbles.iterrows():
            
            # Loop through all the tags from that pass
            for tag in aerial_i['tags']:
                
                # tag 1801 == accurate
                if tag['id'] == 1801:
                    nr_succesful_dribbles += 1
            
        # Find results
        result_kpi = nr_succesful_dribbles
        
        # Compute results, number of succesful dribbles
        result_kpi_p90 = round((nr_succesful_dribbles / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'succesful_dribbles': nr_succesful_dribbles,
                'unsuccesful_dribbles': nr_unsuccesful_dribbles}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Key passes completed tot and per 90.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - completed key passes
            result_kpi_p90 - completed key passes per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def key_passes(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    df_passes = df_events_player.loc[mask_passes]
    
    # Find number of events
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for passes completed
        nr_key_passes = 0
        nr_incompleted_key_passes = 0
        
        # Loop through all the passes
        for i, pass_i in df_passes.iterrows():
            
            # Loop through all the tags from that pass
            tag_list = []
            for tag in pass_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 302 == key pass
            if (302 in tag_list):
                nr_key_passes += 1
        
        # Check so there were any key passes
        if nr_key_passes == 0:
            # No key passes
            result_kpi = 0
            result_kpi_p90 = 0
        else:
           # Find results
           result_kpi = nr_key_passes
            
           # Compute results, key passes per 90 minutes played
           result_kpi_p90 = round((nr_key_passes / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'key_passes': nr_key_passes,
                'incompleted_key_passes': nr_incompleted_key_passes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Through passes tot and completed per 90.

Description: 
    
    Input:
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - completed through passes
            result_kpi_p90 - completed through passes per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def succesful_through_passes(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    df_passes = df_events_player.loc[mask_passes]
    
    # Find number of events
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for passes completed
        nr_completed_through_passes = 0
        nr_incompleted_through_passes = 0
        
        # Loop through all the passes
        for i, pass_i in df_passes.iterrows():
            
            # Loop through all the tags from that pass
            tag_list = []
            for tag in pass_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 901 == through pass
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (901 in tag_list) and (1801 in tag_list):
                nr_completed_through_passes += 1
            elif (901 in tag_list) and (1802 in tag_list):
                nr_incompleted_through_passes += 1
        
        # Check so there were any succesful through passes
        if nr_completed_through_passes == 0:
            # No key passes
            result_kpi = 0
            result_kpi_p90 = 0.0
        else:
            # Find results
            result_kpi = nr_completed_through_passes
            
            # Compute results, succesful through passes per 90 minutes played
            result_kpi_p90 = round((nr_completed_through_passes / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'completed_through_passes': nr_completed_through_passes,
                'incompleted_through_passes': nr_incompleted_through_passes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Plus-minus that game

Description: 
    
    Input: 
           df_events_match - dataframe for the events in a match
           player_team - the teamId (wyId) of the team of the player
           player_minutes- number of minutes played in that match
           player_in_min - the minute the player came in that game
           player_out_min - the minute the player was sent out/game ended 
        
    Output: 
            result_kpi - plus-minus goals for that game
            info - dictionary with background info of computed kpi
        
"""
def plus_minus(df_events_match, player_team, player_minutes, player_in_min, player_out_min):
    
    # Initiate variable for KPI-result
    result_kpi = 0
    
    # Numer of events counter
    nr_of_events = 0 
    
    # Loop through all the events and look for goals and own-goals
    for i, event in df_events_match.iterrows():
        
        # Loop through all the tags from that event
        for eventtag in event['tags']:
            
            # tag 101 == Goal, 102 == Own goal
            if ((eventtag['id'] == 101) | (eventtag['id'] == 102)):
                
                # Add 1 to numer of events
                nr_of_events += 1 
                
                # Get the minute of the event 
                # event is in first half
                if (event['matchPeriod'] == '1H'): 
                    event_minute = event['eventSec'] / 60
                
                # event is in second half
                elif(event['matchPeriod'] == '2H'):
                    event_minute = 45 + event['eventSec'] / 60
                    
                # Something unexpected happened    
                else:
                    print(event['matchPeriod'])
                    
                # check if the player was on the pitch when the goal was scored    
                if ((player_in_min <= event_minute) & (player_out_min >= event_minute)):
                    
                    # player team scored a goal
                    if ((eventtag['id'] == 101) & (player_team == event['teamId'])):
                        result_kpi += 1
                        
                    # the opponents scored an own goal
                    elif ((eventtag['id'] == 102) & (player_team != event['teamId'])):
                        result_kpi += 1
                        
                    # The opponents scored a goal
                    else:
                        result_kpi -= 1
    
        
    # Dictionary with info 
    info = {'result': result_kpi,
            'nr_of_events': nr_of_events,
            'minutes_played': player_minutes}

    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################



""" Function which computes the KPI: Number of events in offensive box tot and per 90 minutes.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - events in offensive box
            result_kpi_p90 - events in offensive box per 90 minutes
            info - dictionary with background info of computed kpi
        
"""
def events_in_box(df_events_player, player_minutes):
    
    # Variable for number of events
    nr_of_events = len(df_events_player)
    in_box = 0
    
    # Loop through all the events from the player 
    for i, event in df_events_player.iterrows():
        
        # Get x and y coordinate for the starting position of the event
        x = event['positions'][0]['x']
        y = event['positions'][0]['y']
        
        # Check if the coorrdinates are in the opposing box
        if ((x >= 84) & (y >= 19) & (y <= 81)):
            in_box += 1
            
    # Find results
    result_kpi = in_box
    
    # Compute result, events per 90 minutes played
    result_kpi_p90 = round((in_box / player_minutes) * 90, 2)
    
    # Dictionary with info 
    info = {'result': result_kpi,
            'nr_of_events': nr_of_events,
            'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Number of passes into the offensive box tot and per 90 minutes.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - passes to offensive box
            result_kpi_p90 - passes to offensive box per 90 minutes
            info - dictionary with background info of computed kpi
        
"""
def passes_to_box(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
    
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    df_passes = df_events_player.loc[mask_passes]
    
    # Find number of events
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for passes to box
        to_box = 0
        
        # Loop through all the events from the player 
        for i, pass_i in df_passes.iterrows():
            
            # Get x and y coordinate for the nding position of the pass
            x = pass_i['positions'][1]['x']
            y = pass_i['positions'][1]['y']
            
            # Check if the coorrdinates are in the opposing box
            if ((x >= 84) & (y >= 19) & (y <= 81)):
                to_box += 1
            
        # Find results
        result_kpi = to_box
        
        # Compute results, computed passes per 90 minutes played
        result_kpi_p90 = round((to_box / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Creative passes tot and per 90.

Description: 
    
    Creative pass is here defined by the following passing types:
        
        Event:       Subevent:        Tags
        
        Pass         Cross            -
        Pass         Smart pass       -
        Pass         -                {901, 301, 302}
        
        901 == through pass
        301 == assist
        302 == key pass
    
    Important here in the loop to dont count crosses and Smart passes two times
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - creative passes
            result_kpi_p90 - creative passes per 90
            info - dictionary with background info of computed kpi
        
"""
def creative_passes(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    df_passes = df_events_player.loc[mask_passes]
    
    # Find number of events/passes
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type (passes) exists
    else:
        
        # Get the dataframe from passes with subevents as 'Cross' or 'Smart pass'
        mask_crosses = df_passes.subEventName == 'Cross'
        mask_smart_passes = df_passes.subEventName == 'Smart pass'
        df_crosses = df_passes.loc[mask_crosses]
        df_smart_passes = df_passes.loc[mask_smart_passes]
        
        # Variables for creative passes
        nr_creative_passes = len(df_crosses) + len(df_smart_passes)
        
        # Create a new dataframe without Crosses and Smart passes
        df_passes_new = df_passes.loc[(~mask_crosses) & (~mask_smart_passes)]
        
        # Loop through all the passes
        for i, pass_i in df_passes_new.iterrows():
            
            # Loop through all the tags from that pass
            tag_list = []
            for tag in pass_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 901 == through pass, tag 301 == assist, tag 302 == keypass
            if ((901 in tag_list) or (301 in tag_list) or (302 in tag_list)):
                nr_creative_passes += 1
            
        # Find results
        result_kpi = nr_creative_passes
        
        # Compute results, creative passes per 90 minutes played
        result_kpi_p90 = round((nr_creative_passes / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_passes': nr_of_events,
                'nr_of_creative_passes': nr_creative_passes,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes the KPI: Succesful defensive actions tot and per 90.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - succesful defensive actions
            result_kpi_p90 - succesful defensive actions per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def succesful_def_actions(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out defensive actions from events data
    mask_def_duel = df_events_player.subEventName == 'Ground defending duel'
    mask_def_loose_ball = df_events_player.subEventName == 'Ground loose ball duel'
    mask_def_touch = df_events_player.subEventName == 'Touch'
    mask_def_clearance = df_events_player.subEventName == 'Clearance'
    mask_def_aerial = df_events_player.subEventName == 'Air duel'
    
    # Create df's of defensive actions
    df_def_duel = df_events_player.loc[mask_def_duel]
    df_def_loose_ball = df_events_player.loc[mask_def_loose_ball]
    df_def_touch = df_events_player.loc[mask_def_touch]
    df_def_clearance = df_events_player.loc[mask_def_clearance]
    df_def_aerial = df_events_player.loc[mask_def_aerial]
    
    # Find number of events
    nr_of_events = len(df_def_duel) + len(df_def_loose_ball) + len(df_def_touch) + len(df_def_clearance) + len(df_def_aerial)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for defensive actions
        nr_completed_def_actions = 0
        nr_incompleted_def_actions = 0
        
        # Loop through Ground defending duels
        for i, g_duel_i in df_def_duel.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in g_duel_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (1801 in tag_list):
                nr_completed_def_actions += 1
            elif (1802 in tag_list):
                nr_incompleted_def_actions += 1
        
        # Loop through Ground loose ball duels
        for i, lb_duel_i in df_def_loose_ball.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in lb_duel_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (1801 in tag_list):
                nr_completed_def_actions += 1
            elif (1802 in tag_list):
                nr_incompleted_def_actions += 1
                
        # Loop through all touches and find defensive ones (interceptions)
        for i, touch_i in df_def_touch.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in touch_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1401 == Interception
            if (1401 in tag_list):
                nr_completed_def_actions += 1
        
        # Loop through Clearances
        for i, clearance_i in df_def_clearance.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in clearance_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (1801 in tag_list):
                nr_completed_def_actions += 1
            elif (1802 in tag_list):
                nr_incompleted_def_actions += 1
        
        # Loop through Aerial duels
        for i, aerial_i in df_def_aerial.iterrows():
            
            # Get x coordinate for event
            x = aerial_i['positions'][0]['x']
            
            # Filter to only include def aerial duels (x-limited)
            if x < 50:
                
                # Aerial happened on defensive pitch
                # Loop through all tags
                tag_list = []
                for tag in aerial_i['tags']:
                    tag_list.append(tag['id'])
                
                # tag 1801 == Accurate, tag 1802 == Inaccurate
                if (1801 in tag_list):
                    nr_completed_def_actions += 1
                elif (1802 in tag_list):
                    nr_incompleted_def_actions += 1
        
        
        # Check so there were any succesful defensive actions
        if nr_completed_def_actions == 0:
            # No key passes
            result_kpi = 0
            result_kpi_p90 = 0
        else:
            # Find results
            result_kpi = nr_completed_def_actions
            
            # Compute results, succesful def actions per 90 minutes played
            result_kpi_p90 = round((nr_completed_def_actions / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'completed_def_actions': nr_completed_def_actions,
                'incompleted_def_actions': nr_incompleted_def_actions}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################


""" Function which computes the KPI: Succesful defensive actions %.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - succesful defensive actions %
            result_kpi_p90 - succesful defensive actions per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def percent_def_actions(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
     
    # Filter out defensive actions from events data
    mask_def_duel = df_events_player.subEventName == 'Ground defending duel'
    mask_def_loose_ball = df_events_player.subEventName == 'Ground loose ball duel'
    mask_def_touch = df_events_player.subEventName == 'Touch'
    mask_def_clearance = df_events_player.subEventName == 'Clearance'
    mask_def_aerial = df_events_player.subEventName == 'Air duel'
    
    # Create df's of defensive actions
    df_def_duel = df_events_player.loc[mask_def_duel]
    df_def_loose_ball = df_events_player.loc[mask_def_loose_ball]
    df_def_touch = df_events_player.loc[mask_def_touch]
    df_def_clearance = df_events_player.loc[mask_def_clearance]
    df_def_aerial = df_events_player.loc[mask_def_aerial]
    
    # Find number of events
    nr_of_events = len(df_def_duel) + len(df_def_loose_ball) + len(df_def_touch) + len(df_def_clearance) + len(df_def_aerial)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for defensive actions
        nr_completed_def_actions = 0
        nr_incompleted_def_actions = 0
        
        # Loop through Ground defending duels
        for i, g_duel_i in df_def_duel.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in g_duel_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (1801 in tag_list):
                nr_completed_def_actions += 1
            elif (1802 in tag_list):
                nr_incompleted_def_actions += 1
        
        # Loop through Ground loose ball duels
        for i, lb_duel_i in df_def_loose_ball.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in lb_duel_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (1801 in tag_list):
                nr_completed_def_actions += 1
            elif (1802 in tag_list):
                nr_incompleted_def_actions += 1
                
        # Loop through all touches and find defensive ones (interceptions)
        for i, touch_i in df_def_touch.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in touch_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1401 == Interception
            if (1401 in tag_list):
                nr_completed_def_actions += 1
        
        # Loop through Clearances
        for i, clearance_i in df_def_clearance.iterrows():
            
            # Loop through all tags
            tag_list = []
            for tag in clearance_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 1801 == Accurate, tag 1802 == Inaccurate
            if (1801 in tag_list):
                nr_completed_def_actions += 1
            elif (1802 in tag_list):
                nr_incompleted_def_actions += 1
        
        # Loop through Aerial duels
        for i, aerial_i in df_def_aerial.iterrows():
            
            # Get x coordinate for event
            x = aerial_i['positions'][0]['x']
            
            # Filter to only include def aerial duels (x-limited)
            if x < 50:
                
                # Aerial happened on defensive pitch
                # Loop through all tags
                tag_list = []
                for tag in aerial_i['tags']:
                    tag_list.append(tag['id'])
                
                # tag 1801 == Accurate, tag 1802 == Inaccurate
                if (1801 in tag_list):
                    nr_completed_def_actions += 1
                elif (1802 in tag_list):
                    nr_incompleted_def_actions += 1
        
        
        # Find results
        result_kpi = nr_completed_def_actions / nr_of_events
            
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'completed_def_actions': nr_completed_def_actions,
                'incompleted_def_actions': nr_incompleted_def_actions}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################




""" Function which computes the KPI: Progressive carries tot and per 90.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: 
            result_kpi - progressive carries
            result_kpi_p90 - progressive carries per 90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def progressive_carries(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out carries from events
    mask_att_duel = df_events_player.subEventName == 'Ground attacking duel'
    mask_acc = df_events_player.subEventName == 'Acceleration'
    mask_touch = df_events_player.subEventName == 'Touch'

    # Create df's of carries
    df_carries = df_events_player.loc[(mask_att_duel | mask_acc | mask_touch)]
    
    # Find number of events
    nr_of_events = len(df_carries)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for carries completed
        nr_prog_carries = 0
        
        # Loop through all the carries
        for i, carry_i in df_carries.iterrows():
            
            # Get coordinates for carry
            x_start = carry_i['positions'][0]['x']
            y_start = carry_i['positions'][0]['y']
            x_end = carry_i['positions'][1]['x']
            y_end = carry_i['positions'][1]['y']
            
            # Get start and end point 
            start_point = np.array((x_start, y_start))
            end_point = np.array((x_end, y_end))
            
            # oppent goal coordinate
            goal_point = np.array((100, 50))
            
            # carry distances
            start_distance_to_goal = np.linalg.norm(start_point - goal_point)
            end_distance_to_goal = np.linalg.norm(end_point - goal_point)
            
            # difference in distances
            diff_distance_to_goal = start_distance_to_goal - end_distance_to_goal
            
            # Find where carry happens
            # Carry is in own half
            if (x_start <= 50) and (x_end <= 50):
                # at least 30 meters closer to opponent goal
                if (diff_distance_to_goal >= 28):
                    nr_prog_carries += 1
            # Carry is between halves
            elif (x_start <= 50) and (x_end > 50):
                # at least 15 meters closer to opponent goal
                if (diff_distance_to_goal >= 13):
                    nr_prog_carries += 1
            # Carry is in offensive half
            elif (x_start > 50) and (x_end > 50):
                # at least 10 meters closer to opponent goal
                if (diff_distance_to_goal >= 9):
                    nr_prog_carries += 1
        
        # Check so there were any progressive runs
        if nr_prog_carries == 0:
            # No key passes
            result_kpi = 0
            result_kpi_p90 = 0
        else:
            # Find results
            result_kpi = nr_prog_carries
            
            # Compute results, progressive runs
            result_kpi_p90 = round((nr_prog_carries / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes,
                'nr_prog_carries': nr_prog_carries,
                }
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################


""" Function which computes the KPI: xG tot and per 90, both summed and for 
                                    open play, penalties, headers and free kicks.
                                    A penalty xG value is fixed to 0.76.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
           player_minutes - number of minutes played in that match
           df_coef_shots - coefficients from xG-model, for open play shots
           
        
    Output: 
            result_kpi - xG_tot
            result_kpi_p90 - xG_tot_per90 minutes played
            info - dictionary with background info of computed kpi
        
"""
def xG(df_events_player, player_minutes, df_coef_shots, df_coef_headers, df_coef_free_kicks):
    
    # Initiate variables for KPI-result
    result_kpi = 0.0
    result_kpi_p90 = 0.0
    xG_shots_tot = 0.0
    xG_headers_tot = 0.0
    xG_free_kicks_tot = 0.0 
    xG_penalties_tot = 0.0
     
    # Filter out shots from events data, including headers and free kicks
    mask_shots = (df_events_player.eventName == 'Shot') | (df_events_player['subEventName'] == 'Free kick shot')
    df_shots = df_events_player.loc[mask_shots]
    
    # Filter out penalties from events data
    mask_penalties = df_events_player.subEventName == 'Penalty'
    df_penalties = df_events_player.loc[mask_penalties]
    
    # Find number of events
    nr_of_events = len(df_shots) + len(df_penalties)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable list for xG(s)
        xG_shots_list = []
        xG_headers_list = []
        xG_free_kicks_list = []
        
        
        # Loop through all the carries
        for i, shot_i in df_shots.iterrows():
                
            # Find shot coordinates and convert from % to meters
            # C == center distance
            X = 100 - shot_i['positions'][0]['x']
            #Y = shot_i['positions'][0]['y']
            C = abs(shot_i['positions'][0]['y'] - 50)
                
            # Distance in metres and shot angle in radians
            # Pitch is assumed to be 105x65 meters
            x = X * 105/100
            y = C * 65/100
                
            # Compute angle for shot_i
            shot_angle = np.arctan(7.32 *x /(x**2 + y**2 - (7.32/2)**2))
            if shot_angle < 0:
                shot_angle = np.pi + shot_angle
                
            # Compute distance for shot_i
            shot_distance = np.sqrt(x**2 + y**2)
            
            # Loop through all the tags for shot_i
            tag_list = []
            for tag in shot_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 403 == header
            if (403 in tag_list):
                
                # Compute xG for shot_i as a header
                xG_header_i = 1/(1 + np.exp(-(df_coef_headers.loc['distance'].values[0]*shot_distance 
                                            + df_coef_headers.loc['distance_sq'].values[0]*shot_distance**2 
                                            + df_coef_headers.loc['angle_rad'].values[0]*shot_angle 
                                            + df_coef_headers.loc['intercept'].values[0])))
                
                # Add to list
                xG_headers_list.append(xG_header_i)
            
            # Find if shot is a free kick
            if shot_i.subEventName == 'Free kick shot':
                
                # Compute xG for shot_i as a free kick
                xG_free_kick_i = 1/(1 + np.exp(-(df_coef_free_kicks.loc['distance'].values[0]*shot_distance 
                                            + df_coef_free_kicks.loc['distance_sq'].values[0]*shot_distance**2 
                                            + df_coef_free_kicks.loc['angle_rad'].values[0]*shot_angle 
                                            + df_coef_free_kicks.loc['intercept'].values[0])))
                
                # Add to list
                xG_free_kicks_list.append(xG_free_kick_i)
            
            # Shot is from open play
            else:
                
                # Compute xG for shot_i as from open play
                xG_shot_i = 1/(1 + np.exp(-(df_coef_shots.loc['distance'].values[0]*shot_distance 
                                            + df_coef_shots.loc['distance_sq'].values[0]*shot_distance**2 
                                            + df_coef_shots.loc['angle_rad'].values[0]*shot_angle 
                                            + df_coef_shots.loc['intercept'].values[0])))
            
            
                # Add to list
                xG_shots_list.append(xG_shot_i)
        
        
        # Compute summed xG, summing over all shots xG's
        xG_shots_tot = round(sum(xG_shots_list), 2)
        xG_headers_tot = round(sum(xG_headers_list), 2)
        xG_free_kicks_tot = round(sum(xG_free_kicks_list), 2)
        
        # Compute xG for penalties
        xG_penalties_tot = round(len(df_penalties)*0.76, 2)
        
        # Compute tot xG
        xG_tot = xG_shots_tot + xG_headers_tot + xG_free_kicks_tot + xG_penalties_tot
        
        # Compute results, xG tot and per 90 minutes played
        result_kpi = round(xG_tot, 2)
        result_kpi_p90 = round((xG_tot / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info, xG_shots_tot, xG_headers_tot, xG_free_kicks_tot, xG_penalties_tot

# - End function
##############################################################################


""" Function which computes the KPI: Number of assist(s).

Description: 
    
    Input: df_events_player, player_minutes
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: result_kpi, info
            result_kpi - nr of assist(s)
            info - dictionary with background info of computed kpi
        
"""
def nr_assists(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
     
    # Filter out passes from events data
    mask_passes = df_events_player.eventName == 'Pass'
    mask_passes2 = df_events_player.eventName == 'Free Kick'
    df_passes = df_events_player.loc[mask_passes | mask_passes2]
    
    # Find number of events
    nr_of_events = len(df_passes)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for assists
        nr_assists = 0
        
        # Loop through all the passes
        for i, pass_i in df_passes.iterrows():
            
            # Loop through all the tags from that pass
            tag_list = []
            for tag in pass_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 301 == assist
            if (301 in tag_list):
                nr_assists += 1
        
        # Compute results, assists
        result_kpi = nr_assists
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################


""" Function which computes the KPI: Number of goal(s).

Description: 
    
    Input: df_events_player, player_minutes
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: result_kpi, info
            result_kpi - nr of goal(s)
            info - dictionary with background info of computed kpi
        
"""
def nr_goals(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
     
    # Filter out shots (and free kicks) from events data
    mask_shots = df_events_player.eventName == 'Shot'
    mask_shots2 = df_events_player.eventName == 'Free Kick'
    df_shots = df_events_player.loc[mask_shots | mask_shots2]
    
    # Find number of events
    nr_of_events = len(df_shots)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for goals
        nr_goals = 0
        
        # Loop through all the passes
        for i, shot_i in df_shots.iterrows():
            
            # Loop through all the tags from that pass
            tag_list = []
            for tag in shot_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 101 == goal
            if (101 in tag_list):
                nr_goals += 1
        
        # Compute results, goals
        result_kpi = nr_goals
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################


""" Function which computes the KPI: Number of dangerous ball loses.

Description: 
    
    Input: df_events_player, player_minutes
           df_events_player - dataframe for a players event in a match
           player_minutes- number of minutes played in that match
        
    Output: result_kpi, info
            result_kpi - nr of dangerous ball loses.
            info - dictionary with background info of computed kpi
        
"""
def danger_ball_loses(df_events_player, player_minutes):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    result_kpi_p90 = 0.0
     
    # Filter out events from events data
    mask1 = df_events_player.subEventName == 'Simple pass'
    mask2 = df_events_player.subEventName == 'Ground attacking duel'
    mask3 = df_events_player.subEventName == 'Touch'
    mask4 = df_events_player.subEventName == 'Head pass'
    mask5 = df_events_player.subEventName == 'Clearance'
    mask6 = df_events_player.subEventName == 'High pass'
    mask7 = df_events_player.subEventName == 'Smart pass'
    mask8 = df_events_player.subEventName == 'Ground loose ball duel'
    df_events = df_events_player.loc[mask1 | mask2 | mask3 | mask4 | mask5 | mask6 | mask7 | mask8]
    
    # Find number of events
    nr_of_events = len(df_events)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Events of that type exist
    else:
        
        # Variable for ball loses
        nr_ball_loses = 0
        
        # Loop through all the passes
        for i, event_i in df_events.iterrows():
            
            # Loop through all the tags
            tag_list = []
            for tag in event_i['tags']:
                tag_list.append(tag['id'])
            
            # tag 2001 == dangerous ball lost
            if (2001 in tag_list):
                nr_ball_loses += 1
        
        # Results 
        result_kpi = nr_ball_loses
        
        # Compute results p90
        result_kpi_p90 = round((nr_ball_loses / player_minutes) * 90, 2)
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events,
                'minutes_played': player_minutes}
    
    # Return the computed KPI-result
    return result_kpi, result_kpi_p90, info

# - End function
##############################################################################



""" Function which computes: Own goals, and gathers them in a df.

Description: 
    
    Input: df_events_All
           df_events_All - dataframe for all events
        
    Output: df_own_goals
            df_own_goals - df with all own goals
        
"""
def own_goals(df_events_All):
    
    # Initiate variables
    id_list = []
    
    # Loop trough all events
    for i, event_i in df_events_All.iterrows():
        
        # Loop through all tags
        tag_list = []
        for tag in event_i['tags']:
            tag_list.append(tag['id'])
        
        # tag 102 == own goal
        if (102 in tag_list):
            id_list.append(event_i.id)
    
    # Create df of own goals
    df_own_goals = df_events_All[df_events_All.id.isin(id_list)]
    
    # Return result
    return df_own_goals

# - End function
##############################################################################



""" Function which computes the KPI: Nr of yellow cards.

Description: 
    
    Input: 
           df_events_player - dataframe for a players event in a match
        
    Output: 
            result_kpi - nr of yellow cards
            info - dictionary with background info of computed kpi
        
"""
def yellow_cards(df_events_player):
    
    # Initiate variables for KPI-result
    result_kpi = 0
    
    # Filter out passes from events data
    mask_fouls = df_events_player.eventName == 'Foul'
    df_fouls = df_events_player.loc[mask_fouls]
    
    # Find number of events
    nr_of_events = len(df_fouls)
    
    # Check if there were any events of that type 
    if nr_of_events == 0:
        
        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events}
    
    # Events of that type exist
    else:
        
        # Variable for yellow cards
        nr_yellow_cards = 0
        
        # Loop trough all events
        for i, foul_i in df_fouls.iterrows():
            
            # Loop through all the tags
            tag_list = []
            for tag in foul_i['tags']:
                tag_list.append(tag['id'])
                
            # tag 1702 == yellow card
            if (1702 in tag_list):
                nr_yellow_cards += 1
                
            # tag 1702 == second yellow card
            if (1703 in tag_list):
                nr_yellow_cards += 1
        
        # Find results
        result_kpi = nr_yellow_cards

        # Dictionary with info 
        info = {'result': result_kpi,
                'nr_of_events': nr_of_events}
    
    # Return the computed KPI-result
    return result_kpi, info

# - End function
##############################################################################


