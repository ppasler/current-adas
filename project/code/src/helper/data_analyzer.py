'''
Created on 07.02.2017

@author: Paul Pasler
'''

import pandas as pd
import matplotlib.pyplot as plt
import datetime
from config.config import ConfigProvider

def parseMilliseconds(timestamp):
        return parseSeconds(timestamp/1000)

def parseSeconds(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp))

def getStartStopPercent(df, s1=10, s2=20, s3=85, s4=95):
    length = int(len(df) / 100)
    return s1*length, s2*length, s3*length, s4*length


class Analyzer(object):

    def readCSV(self, filePath, sep, dtype, parse_dates, date_parser):
        return pd.read_csv(filePath, sep=sep, dtype=dtype, parse_dates=parse_dates, date_parser=date_parser)

    def splitStates(self, df, columns):
        s1, e1, s2, e2 = getStartStopPercent(df)
        awake, drowsy = df[s1:e1], df[s2:e2]
        awake = awake[columns].reset_index(drop=True)
        drowsy = drowsy[columns].reset_index(drop=True)
        return awake, drowsy

    def mergeColumns(self, awake, drowsy):
        ret = pd.concat([awake, drowsy], axis=1, ignore_index=True)
        columns = ["Awake_" + col for col in awake.columns] + ["Drowsy_" + col for col in awake.columns]
        ret.columns = columns
        return ret

    def mergeRows(self, dfs):
        return pd.concat(dfs, axis=0, ignore_index=True)

    def printDifference(self, df, column, name):
        awake, drowsy = self.splitStates(df, column)
        merge = self.mergeColumns(awake, drowsy)
        self.boxplot(merge, name)
        self.printStats(merge, name)

    def boxplot(self, df, name=""):
        fig, ax = plt.subplots()
        fig.suptitle(name, fontsize=20) 
        df.plot.box(ax=ax)

    def printStats(self, df, name=""):
        print "\n####################\n" + name + "\n####################\n"
        print df.describe()

class CANAnalyzer(Analyzer):

    def readCAN(self, filePath):
        dtype= {"Time": float, "Signalname": str, "Value":float}
        return self.readCSV(filePath, ";", dtype, ["Time"], parseMilliseconds)

    def groupCAN(self, df):
        return df.groupby(["Signalname"])
    
    def getSignals(self, group, signalnames):
        return [group.get_group(signalname) for signalname in signalnames]

    def printDifferences(self, signals, signalnames):
        for signal, name in zip(signals, signalnames):
            self.printDifference(signal, ["Value"], name)

class GyroAnalyzer(Analyzer):

    def readGyro(self, filePath):
        return self.readCSV(filePath, ",", None, ["Timestamp"], parseSeconds)

    def dropOtherColumns(self, df, keeps):
        drops = [i for i in range(0,len(df.columns)) if i not in keeps]
        return df.drop(df.columns[drops], axis=1)

    def normalizeGyro(self, df):
        config = ConfigProvider().getProcessingConfig()
        xGround = config.get("xGround")
        yGround = config.get("yGround")
        x = df["X"] - xGround
        y = df["Y"] - yGround
        df = pd.concat([x, y], axis=1, ignore_index=True)
        df.columns = ["X", "Y"]
        return df

experimentPath = "E:/thesis/experiment/"
ga = GyroAnalyzer()
ca = CANAnalyzer()

def analyseCAN():
    filePath = experimentPath + "3/CAN.csv"
    df = ca.readCAN(filePath)
    group = ca.groupCAN(df)

    signalnames = ["P_Steering_Angle", "P_Engine_Speed"]
    signals = ca.getSignals(group, signalnames)
    ca.printDifferences(signals, signalnames)

def analyseGyroList():
    probands = ConfigProvider().getExperimentConfig().get("probands")
    dfs = []
    for proband in probands:
        dfs.append(analyseGyro(proband))
    df = ga.mergeRows(dfs)
    print len(df)
    ga.printDifference(df, ["X", "Y"], "Gyro")

def analyseGyro(proband):
    filePath = experimentPath + proband + "/EEG.csv"
    df = ga.readGyro(filePath)
    keeps = [1, 13]
    df = ga.dropOtherColumns(df, keeps)
    df = ga.normalizeGyro(df)
    return df

analyseGyroList()
#df = analyseGyro("c")
#ga.printDifference(df, ["X", "Y"], "Gyro")

#analyseCAN()
plt.show()