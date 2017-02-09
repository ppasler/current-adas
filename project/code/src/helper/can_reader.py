'''
Created on 07.02.2017

@author: Paul Pasler
'''

import pandas as pd
import matplotlib.pyplot as plt
import datetime

def dateparse(time_in_secs):
    time_in_secs = time_in_secs/1000
    return datetime.datetime.fromtimestamp(float(time_in_secs))

experimentPath = "E:/thesis/experiment/"
filePath = "3/CAN.csv"

dtype= {"Time": float, "Signalname": str, "Value":float}
df = pd.read_csv(experimentPath+filePath, sep=";", dtype=dtype, parse_dates=["Time"], date_parser=dateparse)

group = df.groupby(["Signalname"])

signalnames = ["P_Steering_Angle", "P_Engine_Speed"]
signals = [group.get_group(signalname) for signalname in signalnames]

def plot():
    for signal in signals:
        signal.plot(title=signalname)
    plt.show()

def printDifference():
    for signal, name in zip(signals, signalnames):
        l = len(signal)
        perc = int(l * 0.25)
        awake = signal[0:perc]
        drowsy = signal[l-perc:l]
        print "%s: mean\t %f \t %f" %(name, awake.mean(), drowsy.mean())
        print "%s: var \t %f \t %f" %(name, awake.var(), drowsy.var())
        print "%s: std \t %f \t %f" %(name, awake.std(), drowsy.std())
        print "%s: std \t %f \t %f" %(name, signal[0:perc], signal[l-perc:l].energy())
printDifference()