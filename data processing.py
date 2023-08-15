# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 19:34:03 2023

@author: Shane
"""
#%pip install pybaseball;
import os
import re
import csv
import math
#import tweepy # %pip install tweepy
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import matplotlib.patches as patches
import seaborn as sns
from datetime import date, timedelta
import datetime as dt
#import statsapi # %pip install MLB-StatsAPI
#from pybaseball import statcast


'''
df is acquired by

data1 = statcast(start_dt="2018-01-01", end_dt="2022-12-31")
data1.to_csv('5 year raw download data', sep='\t',encoding='utf-8')

'''


df = pd.read_csv('5 year raw download data', sep='\t', encoding='utf-8')


#Cut down to just called pitches.
df = df.query("description in ('ball','called_strike')")

#drop X values in type
df = df[df.type != "X"]



def correct(df):
    #Checks if the pitch's z coord is below the top of the zone, above the bottom, and within the outside(positive val) and inside zone(negative)
    top = df["plate_z"]-.1225 < df["sz_top"]
    bot = df["plate_z"]+.1225 > df["sz_bot"]
    left = df["plate_x"]-.1225 < .708
    right = df["plate_x"]+.1225 > -.708

    if top and bot and left and right:
        #If the previous conditions are met, the pitch should be a strike, if it is called a ball, it is incorrect
        if df["type"] == "B":
            return "incorrect"
    #If top conditions are not met, the pitch should be called a ball, if not, it is incorrect.
    elif df["type"] == "S":
        return "incorrect"
    else: return "correct"
    
#Simulates marked incorrect pitches 10,000 times with margin of error for Hawkeye (.25 inches, .0208 feet) added in, if call is correct 95% of the time, it stands.
def simulate(df):
    #Create x and z arrays of 10,000 values between [-1,1], multiplied by .0208(.25inches to feet)
    x_values = (np.random.random_sample(1000) *2 - 1) * .0208
    z_values = (np.random.random_sample(1000) *2 - 1) * .0208
    pitch_coordinates = pd.DataFrame({"x": x_values, "z":z_values})

    #Create ball and strike counter
    balls = 0
    strikes = 0

    #Add z and x coords to the uniform dist
    pitch_coordinates["z"] = pitch_coordinates["z"] + df["plate_z"]
    pitch_coordinates["x"] = pitch_coordinates["x"] + df["plate_x"]

    #strikes is the amount of times the simulation resulted in a strike, balls is the amount of times the sim resulted in ball

    top = ((pitch_coordinates["z"]-.1225) < df["sz_top"])
    bot = ((pitch_coordinates["z"]+.1225) > df["sz_bot"])
    left = ((pitch_coordinates["x"]-.1225) < .708)
    right = ((pitch_coordinates["x"]+.1225) > -.708)

    strikes = len(pitch_coordinates[top & bot & left & right])
    balls = len(pitch_coordinates) - strikes

    #If the umpire calls strike, the probability the umpire is incorrect is the amount of simulated balls/total
    #If ump calls ball, the prob the ump is incorrect is amount of simulated strikes/total
    if df["type"] == "S":
        pi = balls/(balls + strikes)
    else:
        pi = strikes/(balls + strikes)

    #If the umpire is wrong 95% of the time compared to the simulation, we can conclude the call is incorrect
    if(pi >= .95):
        return "incorrect"
    else: return "correct"
    
#test if correct or incorrect call
df = df.dropna(subset=['plate_z', 'plate_x','sz_bot','sz_top'])
df["call"] = df.apply(correct, axis=1)

'''
#drop null values in call
df = df.dropna(subset=['call'])
'''

df["call"] = df.apply(simulate, axis=1)

df.to_csv('5 year raw download data with only called pitches and call type', sep='\t',encoding='utf-8')

