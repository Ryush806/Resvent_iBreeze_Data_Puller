# -*- coding: utf-8 -*-
__author__ = 'Ryan Boncheff'
__copyright__ = 'Ryan Boncheff'
__credits__ = None
__license__ = 'GNU General Public License v3.0'
__version__ = 'A001'
__maintainer__ =  'Ryan Boncheff'
__email__ = 'ryanboncheff@gmail.com'
__status__ = 'Alpha'

import struct
import pandas as pd
import sqlite3
import datetime

def wavePuller(path):

    # waveTable column 'label' contains int rather than full description
    # labelDict defines their full description for labelling
    labelDict = {   
                    0   : 'Pressure',
                    1   : 'Flow'
                }

    # after iMatrix reads the data, it inserts it into the patient specific db
    # sql stuff to get it pointed to the right spot
    con = sqlite3.connect(path)
    cur = con.cursor()

    # singleDate = None will pull the entire dataset
    # singleDate = '2022-08-01' will pull only 2022-08-01
    singleDate = None

    # grabs each metric and creates a waveData_metric csv 
    # note that this is different than with detailTable algo
    # waveTable contains too much data for pandas to handle it
    # so csv's are written record by record
    for label in (0,1):

        labelStr = str(label)
        labelDesc = labelDict[label]

        # prints metric name to terminal to track where the program is
        print(labelDesc)

        # detailTable also contains columns unit and deviceID but since I was just
        # grabbing only my data I didn't include them
        if singleDate is None:
            sql = f"select label, realTime, date, frequency, realData \
                    from waveTable \
                    where label = {labelStr}\
                    ;"
        else:
            sql = f"select label, realTime, date, frequency, realData \
                    from waveTable \
                    where label = {labelStr} and date = '{singleDate}'\
                    ;"

        # executes query and loads data
        cur.execute(sql)
        sqlData = cur.fetchall()
        data = pd.DataFrame(sqlData, columns = ['label', 'realTime', 'date', 'frequency', 'realData'])

        # covert the string dates/timestamps to datetimes
        data['realTime'] = pd.to_datetime(data['realTime'])
        data['date'] = pd.to_datetime(data['date'])

        # creates an empty dataframe to add the data to
        metric = pd.DataFrame()

        # loops through all the records and adds the data to the metric dataframe
        for i,rec in data.iterrows(): 

            # frequency is the number of samples per second
            # mine is 0.5 (meaning every two seconds) but I think you can change
            # that on the machine so I included a way to calculate the timestep
            timeStep = str((1 / rec['frequency']) *1) + 'S'

            # each measurement is a float, so 4 bytes each
            # list comprehension below loops through the blob in chunks of 4 bytes
            # unpacks the float and appends it to the recData list
            # the result is a list of all the measurements contained in the blob        
            recData = [struct.unpack('f',rec['realData'][i:(i+4)])[0] for i in range(0,len(rec['realData']),4)]
            
            # creates an empty dataframe to add 
            # the measurements, date, and timestamp
            results = pd.DataFrame()

            # populates date column with the data from the record
            results['date'] = [rec['date'] for i in range(len(recData))]
            
            # populates the timestamp column with a range of:
            # the (original time + timeStep) * length of the measurements
            results['timestamp'] = pd.date_range(rec['realTime'], periods = len(recData), freq = timeStep)
            
            #populates the metric (dynamically labeled) column with the measurements
            results[str(labelDict[rec['label']])] = recData

            # writes the dataset to a csv for use elsewhere
            csvName = 'waveData_' + labelDesc + str(datetime.datetime.now())+ '.csv'
            
            # Clean the file name
            csvName = csvName.replace(':', '_')
            csvName = csvName.replace('/', '-')
            
            results.to_csv(csvName, mode = 'a', index = False)

if __name__ == '__main__':
    path = r'C:\Users\rboncheff\Documents\iMatrix\PATIENT\000001\000001_patient.db'
    wavePuller(path)
