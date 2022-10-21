# Resvent_iBreeze_Data_Puller
Pulls and parses OSA/UARS data from the Resvent iBreeze PAP machine.
Currently (as of 2022-10-20), 3rd party PAP analysis programs like 
OSCAR do not support Resvent. This project was created as a stopgap
to allow Resvent users to access their rawdata until Oscar etc begin
supporting Resvent machines.

This program requires the user to use the iMatrix software to import
their PAP data from their SD card. It can be found online in various 
places. iMatrix lacks the ability to look at detailed data over multiple
days and does not report a significant amount of the data available in
the PAP SD card.

To use these programs, you will have to import your SD card into iMatrix
and then figure out where it stores your data on your computer.

On my system:
C:\Users\[me]\Documents\iMatrix\PATIENT\000001\000001_patient.db

Your path will probably be something similar.

There are five programs included. If you don't need to make any
changes (details below) and just want to get the data,
run fullSetPuller.py. Make sure to change dbPath and sdPath
to the correct paths for your data first.

These programs use the packages:  struct, pandas, and sqlite3

Make sure these modules are installed before running the code.
In terminal:
   pip install [package name]

In each of the following programs, you will have to change the
'path' variable to wherever your patient.db or SD card is 
located if you want to run them separately. The path variables
are located at the end of each program under:
if __name__ == '__main__':

- dbExplor.py

Lets you look through the various tables in the 
patient.db to explore what's there. Probably not super useful 
for most but I wanted to include it anyway.

- wavePuller.py

Grabs the very detailed pressure and flow readings.
It is sampled at a rate of 25 measurements per second.

Because of the level of detail, this script takes a long
time to run on the full dataset. I've included the variable
singleDate on line 28. If you want to pull the full dataset,
leave it as None. If you want to pull just one date, you can
change singleDate with the format 'yyyy-mm-dd'.

It creates two very large (multiple GB for my full data) csv files:
waveData_Pressure.csv contains date, timestamp, and pressure
waveData_Flow.csv contains date, timestamp, and flow

The size of both pressure and flow together is too big for pandas
to handle (at least so far as I know how to use it) so they have
to be split.

- detailPuller.py

Grabs the various respiratory parameters.
Pressure, IPAP, EPAP, Leak, Vt, MV, RR, Ti, IE, Spo2, PR
I don't have Spo2 or PR on my machine so I have left them out.
If you have them, add 9 and 10 to the tuple on line 48
Your machine calculates them at a rate of once every two seconds.

It will create detailsData.csv which contains:
date, timestamp, and each of the respiratory parameters

############
NOTE: For eventsPuller.py, you will have to change the 'path' 
variable to:
[path to SD card or a copy of it]\THERAPY\RECORD

For some reason, iMatrix doesn't store this data.
I guess it recalculate it from the machine data every time
even though it lives on the SD card.
############

- eventsPuller.py

Grabs the log of respiratory events (apnea, hypopnea, flow 
limitation, etc).

The program will search through all your records and grab all the
respiratory events as well as your usage time for each session.

eventsHistory.csv is created which contains:
Session_Start, Usage_sec, Timestamp, Category, Duration_sec
