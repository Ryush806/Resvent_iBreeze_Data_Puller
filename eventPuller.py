# -*- coding: utf-8 -*-
__author__ = 'Ryan Boncheff'
__copyright__ = 'Ryan Boncheff'
__credits__ = None
__license__ = 'GNU General Public License v3.0'
__version__ = 'A001'
__maintainer__ =  'Ryan Boncheff'
__email__ = 'ryanboncheff@gmail.com'
__status__ = 'Alpha'

'''
Grabs the event data from the EV files
Parses it and writes it to csv

I have no idea what the 'gd' column is
'''

import os
import pandas as pd

debug = False

def eventGrabber(logPath):
    '''
    A separate EV file is written for each therapy session so I wrote 
    a function to parse the individual file and call it for each file
    the program finds
    '''

    # opens and reads the file into a list
    with open(logPath, encoding = 'utf-8', errors = 'ignore') as f:
        lines = f.readlines()

    # every now and then there's an empty EV file so this exits the
    # function if that happens
    if len(lines) == 1:
        emptyDict =    {   
                    'cd' : [],
                    'Unix Timestamp' : [],
                    'Duration, sec' : [],
                    'gd' : []
                    }
        return pd.DataFrame(emptyDict)
    
    # I'm not a real programmer so I don't use real debugging :-)
    if debug: print('orig:\t',lines)

    # there's some goofy non utf-8 data at the beginning of each file
    # this gets rid of it
    while "ID=" not in lines[0]:
        lines = lines[1:]
    lines[0] = 'ID=' + lines[0].split('ID=')[1]
    if debug: print(lines)

    # goes through each line separates the data from the labels
    events = []
    for line in lines:
        line = line.split(',')
        tmpLine = []
        for el in line:
            if debug: print(el)
            if el == '\n':
                continue
            else:
                tmpLine.append(el.split('=')[1])
        events.append(tmpLine)

    #creates a dictionary of the events data that pandas can easily parse
    eventsDict =    {   
                    'cd' : [e[0] for e in events],
                    'Unix Timestamp' : [e[1] for e in events],
                    'Duration, sec' : [e[2] for e in events],
                    'gd' : [e[3] for e in events]
                    }

    events = pd.DataFrame(eventsDict)

    return events

def statGrabber(statPath):
    '''
    Grabs the start time and duration for each session

    Used in my data analysis (in Spotfire) to calculate
    events / hour indices
    '''

    # reads the data
    with open(statPath, encoding = 'utf-8', errors = 'ignore') as f:
        lines = f.readlines()

    #sometimes empty files so kicks it out of the function if so
    if len(lines) == 1:
        emptyDict =    {   
                    'cd' : [],
                    'Unix Timestamp' : [],
                    'Duration, sec' : [],
                    'gd' : [],
                    'Usage' : [],
                    'Start' : []
                    }
        return pd.DataFrame(emptyDict)

    
    # parses out the usage duration and start time for each sessions
    usage = [stat.split('=')[1].strip(' \n') for stat in lines if 'secUsed' in stat][0]
    start = [stat.split('=')[1].strip(' \n') for stat in lines if 'secStart' in stat][0]
    
    return usage, start       

def eventPuller(path):
    '''
    Grabs event data, start time, and usage
    
    Combines them into the format needed and writes to csv
    '''

    # goes through the file structure and gets all the needed files
    
    # folder for each month
    months = os.listdir(path)

    events = pd.DataFrame()

    # goes through each month file
    for month in months:
        
        monthPath = path + '\\' + month

        # folder for each day
        days = os.listdir(monthPath)

        monthly = pd.DataFrame()

        # goes through each day
        for day in days:

            dayPath = monthPath + '\\' + day

            # gets the file names that contain the events and stats data
            eventFiles = [file for file in os.listdir(dayPath) if file[0:2] == 'EV']
            statFiles = [file for file in os.listdir(dayPath) if file == 'STAT']

            daily = pd.DataFrame()

            # goes through each event file and combines the data
            # into one dataframe
            for log in eventFiles:
                
                logPath = dayPath + '\\' + log
                if debug: print(logPath)

                if len(daily) == 0:
                    daily = eventGrabber(logPath)
                else:
                    daily = pd.concat([daily,eventGrabber(logPath)])

            # goes through each stat file and adds the start time
            # and usage stats to the dataframe
            for stat in statFiles:
                statPath = dayPath + '\\' + stat
                if debug: print(statPath)
                usage, start = statGrabber(statPath)
                daily['Usage'] = usage
                daily['Start'] = start


            if len(monthly) == 0:
                monthly = daily
            else:
                monthly = pd.concat([monthly,daily])

        if len(events) == 0:
            events = monthly
        else:
            events = pd.concat([events,monthly])

    # dictionary for labelling the events
    # this part could maybe help you as the IDs
    # are just int 
    # I got these associations from comparing iMatrix
    # to the EV files by timestamp
    catID = {
                '1' : 'Usage, sec',
                '2' : 'Unix Start',
                '17' : 'Obstructive Apnea',
                '18' : 'Central Apnea',
                '19' : 'Hypopnea',
                '20' : 'Flow Limitation',
                '21' : 'RERA',
                '22' : 'Periodic Breathing',
                '23' : 'Snore',
            }

    #formatting and labelling and dealing with weird time offset that I don't understand...
    events = events.dropna()
    events['Category'] = events['cd'].apply(lambda x: catID[x])
    #time comes in wrong. don't know how to fix. manually added  hours to get it right
    events['Timestamp'] = pd.to_datetime(events['Unix Timestamp'], unit = 's') + pd.Timedelta(8, 'h')
    # events['Timestamp'] = events['Timestamp'].dt.tz_localize(tz = 'Asia/Shanghai', ambiguous = 'infer').dt.tz_localize(tz = None)
    events['Start'] = pd.to_datetime(events['Start'], unit = 's') + pd.Timedelta(8, 'h')    #dont know why these hours are different...
    # events['Start'] = events['Start'].dt.tz_localize(tz = 'Asia/Shanghai', ambiguous = 'infer').dt.tz_localize(tz = None)

    events = events[['Start','Usage','Timestamp','Category','Duration, sec']]
    events = events.rename(columns = {'Start':'Session_Start',
                                      'Usage':'Usage_sec',
                                      'Duration, sec':'Duration_sec'})

    resultPath = 'eventsHistory' + str(pd.datetime.now()) + '.csv'

    events.to_csv(resultPath)

if __name__ == '__main__':
    path = r'C:\Users\rboncheff\Desktop\APAP\THERAPY\RECORD'
    eventPuller(path)
