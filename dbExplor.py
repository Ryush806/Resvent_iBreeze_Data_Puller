# -*- coding: utf-8 -*-
__author__ = 'Ryan Boncheff'
__copyright__ = None
__credits__ = None
__license__ = None
__version__ = 'A001'
__maintainer__ =  'Ryan Boncheff'
__email__ = 'ryanboncheff@gmail.com'
__status__ = 'Alpha'

import pandas as pd
import sqlite3

path = r'C:\Users\rboncheff\Documents\iMatrix\PATIENT\000001\000001_patient.db'

# connects to the patient.db
con = sqlite3.connect(path)
cur = con.cursor()

sql = 'SELECT name FROM sqlite_master WHERE type=\'table\''
cur.execute(sql)
print('\nAvailable tables:\n')
print(cur.fetchall())

table = 'waveTable'

sql = f"PRAGMA table_info({table})"
cur.execute(sql)
info = cur.fetchall()
print(f'\nInformation for {table}:\n')
print(info)

labels = [i[1] for i in info]

sql = f"SELECT * from {table}"

cur.execute(sql)

data = cur.fetchall()
df = pd.DataFrame(data, columns = labels)

print(f'\nSample of unparsed {table} data:\n')
print(df.head())
print(df['date'].to_list())