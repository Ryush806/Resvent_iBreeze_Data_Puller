# -*- coding: utf-8 -*-
__author__ = 'Ryan Boncheff'
__copyright__ = None
__credits__ = None
__license__ = None
__version__ = 'A001'
__maintainer__ =  'Ryan Boncheff'
__email__ = 'ryanboncheff@gmail.com'
__status__ = 'Alpha'

import struct
import pandas as pd
import sqlite3

def detailsPuller(path):

    # detailTable column 'label' contains int rather than full description
    # I did some guessing for a while but then realized they're in  the same order
    # as they use on the STATS files on the SD card.
    # Also, I used a hex editor program that parsed the first few lines of the 
    # data into the same strings strings in the same order as well so I'm 
    # reasonably sure this is right.
    labelDict = {   
                    0   : 'Pressure',
                    1   : 'IPAP',
                    2   : 'EPAP',
                    3   : 'Leak',
                    4   : 'Vt',
                    5   : 'MV',
                    6   : 'RR',
                    7   : 'Ti',
                    8   : 'IE',
                    9   : 'Spo2',
                    10  : 'PR'
                }

    # after iMatrix reads the data, it inserts it into the patient specific db
    # sql stuff to get it pointed to the right spot
    con = sqlite3.connect(path)
    cur = con.cursor()

    # creates an empty dataframe to add each metric to
    dataSet = pd.DataFrame()

    # grabs each metric and adds it to the dataSet dataframe
    # I don't have blood pressure or pulsox so I left them out
    # They can be added to the tuple if you have the info
    for label in (0,1,2,3,4,5,6,7,8):

        labelStr = str(label)
        labelDesc = labelDict[label]

        # prints metric name to terminal to track where the program is
        print(labelDesc)

        # detailTable also contains columns unit and deviceID but since I was just
        # grabbing only my data I didn't include them
        sql = f"select label, realTime, date, frequency, realData \
                from detailTable \
                where label = {labelStr}\
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

            # adds the current record's measurements to the end of the metric dataframe
            if len(metric) == 0:
                metric = results
            else:
                metric = pd.concat([metric,results])

        # merges the metric specific dataframe with the final dataSet
        if len(dataSet) == 0:
            dataSet = metric
        else:
            dataSet = dataSet.merge(metric, how = 'outer', on = ['timestamp', 'date'])

    # writes the dataset to a csv for use elsewhere
    csvName = 'detailsData' + str(pd.datetime.now()) + '.csv'
    dataSet.to_csv(csvName)

if __name__ == '__main__':
    path = r'C:\Users\rboncheff\Documents\iMatrix\PATIENT\000001\000001_patient.db'
    detailsPuller(path)