'''
Created on 07.02.2017

@author: Paul Pasler
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

from config.config import ConfigProvider

DROWSY_SUF = "_D"
AWAKE_SUF = "_A"

lined, fig = None, None

def onpick(event):
    # on the pick event, find the orig line corresponding to the
    # legend proxy line, and toggle the visibility
    legline = event.artist
    origline = lined[legline]
    vis = not origline.get_visible()
    origline.set_visible(vis)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled
    if vis:
        legline.set_alpha(1.0)
    else:
        legline.set_alpha(0.2)
    fig.canvas.draw()


def parseMilliseconds(timestamp):
        return parseSeconds(timestamp/1000)

def parseSeconds(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp))

def getStartStopPercent(df, s1=10, s2=20, s3=85, s4=95):
    length = int(len(df) / 100)
    return s1*length, s2*length, s3*length, s4*length

def addTime(time, delta):
    return time + np.timedelta64(delta, "m")

def getStartStopTime(df, s1=10, e1=15, s2=37, e2=42):
    start = df["Time"].values[0]
    return addTime(start, s1), addTime(start, e1), addTime(start, s2), addTime(start, e2)

class Analyzer(object):

    def __init__(self):
        self.config = ConfigProvider()
        exConfig = self.config.getExperimentConfig()
        self.experimentPath = exConfig.get("filePath")
        self.probands = exConfig.get("probands")
        self.lengths = []

    def readCSV(self, filePath, sep, dtype, parse_dates=None, date_parser=None):
        return pd.read_csv(filePath, sep=sep, dtype=dtype, parse_dates=parse_dates, date_parser=date_parser)

    def mergeColumns(self, awake, drowsy):
        df = pd.concat([awake, drowsy], axis=1, ignore_index=True)
        columns = [col + AWAKE_SUF for col in awake.columns] + [col + DROWSY_SUF for col in awake.columns]
        df.columns = columns
        return self.sortColumns(df)

    def concatRows(self, dfs):
        self.lengths = [len(df) for df in dfs]
        return pd.concat(dfs, axis=0, ignore_index=True)

    def sortColumns(self, df):
        return df.reindex_axis(sorted(df.columns), axis=1)

    def dropOtherColumns(self, df, keeps):
        columns = df.columns.values
        keeps = np.where(np.in1d(columns, keeps))[0]
        drops = np.delete(np.arange(0, len(columns)), keeps)
        return df.drop(df.columns[drops], axis=1)

    def splitAndMerge(self, df):
        columns = self.dataField
        if type(columns) != list:
            columns = [columns]
        awake, drowsy = self.splitStates(df, columns)
        return self.mergeColumns(awake, drowsy)

    def showDifference(self, merge, name):
        self.boxplot(merge, name)
        #self.plot(merge, name)
        self.printStats(merge, name)

    def plot(self, df, name=""):
        global lined, fig
        fig, ax = plt.subplots()
        fig.suptitle(name, fontsize=20) 

        lines = []
        for column in df:
            line, = ax.plot(df[column])
            lines.append(line)
        leg = ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        leg.get_frame().set_alpha(0.4)

        lined = dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline
        fig.canvas.mpl_connect('pick_event', onpick)

        l = 0
        print self.lengths
        for length in self.lengths:
            l += length
            plt.axvline(x=l, color='r', linestyle='dashed')

    def boxplot(self, df, name=""):
        fig, ax = plt.subplots()
        fig.suptitle(name, fontsize=20) 
        df.plot.box(ax=ax)

    def printStats(self, df, name=""):
        print "\n####################\n" + name + "\n####################\n"
        print df.describe()
        print "energy\t" + "\t".join([str(x) for x in (df**2).sum(axis=0).values])
        print df.quantile([0.01, 0.05, 0.1, 0.2, 0.5, 0.80, 0.90, 0.95, 0.99])

    def resetIndex(self, df):
        return df.reset_index(drop=True)

class CANAnalyzer(Analyzer):

    def __init__(self):
        super(CANAnalyzer, self).__init__()
        self.fields = ["P_Steering_Angle", "P_Engine_Speed"]
        self.dataField = "Value"
        self.dateField = "Time"
        self.descField = "Signalname"

    def read(self, filePath):
        dtype= {self.dateField: float, self.descField: str, self.dataField:float}
        return self.readCSV(filePath, ";", dtype, [self.dateField], parseMilliseconds)

    def groupCAN(self, df):
        return df.groupby([self.descField])
    
    def getSignals(self, group):
        return [group.get_group(signalname) for signalname in self.fields]

    def analyse(self, proband):
        filePath = self.experimentPath + proband + "/CAN.csv"
        df = self.read(filePath)
        group = self.groupCAN(df)
    
        signals = self.getSignals(group)
        self.showDifferences(signals, self.fields)
        return signals

    def buildDf(self, dfs):
        retDfs = []
        for df, field in zip(dfs, self.fields):
            retDf = self.dropOtherColumns(df, [self.dateField, self.dataField])
            retDf = self.resetIndex(retDf)
            retDf.columns = [self.dateField, field]
            retDfs.append(retDf)
        return retDfs

    def showDifferences(self, signals, signalnames):
        for signal, name in zip(signals, signalnames):
            merge = self.splitAndMerge(signal)
            self.showDifference(merge, name)

    def splitStates(self, df, columns):
        s1, e1, s2, e2 = getStartStopTime(df)
        awake, drowsy = self.getDateRange(df, s1, e1), self.getDateRange(df, s2, e2)
        awake = self.resetIndex(awake[columns])
        drowsy = self.resetIndex(drowsy[columns])
        return awake, drowsy

    def getDateRange(self, df, start, stop):
        return df[(df[self.dateField] > start) & (df[self.dateField] < stop)]


class EmotivAnalyzer(Analyzer):

    def __init__(self, fileName, hasTime):
        super(EmotivAnalyzer, self).__init__()
        self.fileName = fileName
        self.hasTime = hasTime
        self.dateField = "Timestamp"

    def read(self, filePath):
        if self.hasTime:
            return self.readCSV(filePath, ",", None, [self.dateField], parseSeconds)
        else:
            return self.readCSV(filePath, ",", None)

    def buildDf(self, proband):
        filePath = self.experimentPath + proband + "/" + self.fileName + ".csv"
        df = self.read(filePath)
        return self.dropOtherColumns(df, self.fields)

    def splitStates(self, df, columns):
        s1, e1, s2, e2 = getStartStopPercent(df)
        awake, drowsy = df[s1:e1], df[s2:e2]
        awake = awake[columns].reset_index(drop=True)
        drowsy = drowsy[columns].reset_index(drop=True)
        return awake, drowsy

    def analyseMerge(self, probands):
        awakes, drowsies = [], []
        for proband in probands:
            df = self.buildDf(proband)
            awake, drowsy = self.splitStates(df, self.fields)
            awakes.append(awake)
            drowsies.append(drowsy)
        a = self.concatRows(awakes)
        d = self.concatRows(drowsies)
        merge = self.mergeColumns(a, d)
        self.showDifference(merge, "%s %s:%s" % (self.name, "merge", ",".join(probands) ))

class GyroAnalyzer(EmotivAnalyzer):

    def __init__(self, fileName="Gyro", hasTime=True):
        super(GyroAnalyzer, self).__init__(fileName, hasTime)
        self.name = "Gyro"
        self.fields = self.config.getEmotivConfig().get("gyroFields")
        self.dataField = self.fields
        self.xGround = self.config.getProcessingConfig().get("xGround")
        self.yGround = self.config.getProcessingConfig().get("yGround")

    def normalizeGyro(self, df):
        x = df["X"] - self.xGround
        y = df["Y"] - self.yGround
        df = pd.concat([x, y], axis=1, ignore_index=True)
        df.columns = self.fields
        return df

    def analyse(self, proband):
        df = self.buildDf(proband)
        df = self.normalizeGyro(df)
        merge = self.splitAndMerge(df)
        self.showDifference(merge, "%s %s" % (self.name, proband))
        return merge

class EEGAnalyzer(EmotivAnalyzer):

    def __init__(self, fileName="EEG", hasTime=True):
        super(EEGAnalyzer, self).__init__(fileName, hasTime)
        self.name = "EEG"
        self.fields = self.config.getCollectorConfig().get("eegFields")
        #self.fields = self.config.getEmotivConfig().get("eegFields")
        self.dataField = self.fields

    def analyse(self, proband):
        df = self.buildDf(proband)
        merge = self.splitAndMerge(df)
        self.showDifference(merge, "%s %s" % (self.name, proband))
        return merge

probands = ConfigProvider().getExperimentConfig().get("probands")
nProbands = ["1", "2"]
oProbands = ["a", "b", "c", "e"]
ea = GyroAnalyzer("EEGNormed", False)
#for proband in probands:
#    ea.analyse(proband)
ea.analyseMerge(probands)
#ea.analyseMerge(nProbands)
#ea.analyseMerge(oProbands)
#CANAnalyzer().analyse("3")
plt.show()