#!/usr/bin/python

import sys, os
import threading
from time import sleep

from data_collector import DataCollector
from emokit.emotiv import Emotiv
import matplotlib.pyplot as plt
import numpy as np

from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



class EEGSignalPlotter(object):

    def __init__(self, label, n=128, samplingRate=128.0):
        """This class plots EEG signals"""
        self.eeg_data = None
        self.label = label
        self.n = n
        self.samplingRate = samplingRate
        self.timeArray = self.getTimeArray(n, samplingRate)
        self.axRaw, self.axNorm, self.axAlpha, self.axTheta = self.initPlot()

    def update(self, data):
        row = np.array(data[self.label]["value"])
        if len(row) == self.n:
            self.eeg_data = row
            self.plotSignal()

    def configureFigure(self):
        #http://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python
        mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        mng.window.wm_geometry("+0+0")
        #http://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots-in-matplotlib
        plt.subplots_adjust(left=0.09, right=0.95, bottom=0.05, top=0.95, wspace=0.2, hspace=0.5)

    def getTimeArray(self, n, samplingRate):
        timeArray = np.arange(0, n, 1)
        timeArray = timeArray / samplingRate
        timeArray = timeArray * 1000 #scale to milliseconds
        return timeArray

    def initPlot(self):
        #http://stackoverflow.com/questions/332289/how-do-you-change-the-size-of-figures-drawn-with-matplotlib
        self.fig, ax = plt.subplots(4, figsize=(16, 9))
        axRaw, axNorm, axAlpha, axTheta = ax[0], ax[1], ax[2], ax[3]

        axRaw.set_ylabel('Amplitude')
        axRaw.set_xlabel('Time (ms)')

        axAlpha.set_ylabel("alpha (8-13Hz)")
        axTheta.set_ylabel("theta (4-8Hz)")

        self.configureFigure()

        plt.ion()
        plt.show()

        return axRaw, axNorm, axAlpha, axTheta

    def plotSignal(self):
        #self.fig.clf()
        print "update data"
        raw = self.eeg_data

        norm = SignalUtil().normalize(raw)
        self.plotRaw(raw, norm)
        self.plotAlphaChannel(norm)
        self.plotThetaChannel(norm)

        self.fig.canvas.draw()

    def plotRaw(self, raw, norm):
        self.axRaw.cla()
        self.axRaw.plot(self.timeArray, raw)
        self.axNorm.cla()
        self.axNorm.plot(self.timeArray, norm)

    def plotAlphaChannel(self, raw):
        chanName = "alpha"
        freqRange = EEGUtil().channel_ranges[chanName]
        filtered = SignalUtil().butterBandpassFilter(raw, freqRange[0], freqRange[1],  self.samplingRate)
        self.axAlpha.cla()
        self.axAlpha.plot(self.timeArray, filtered)

    def plotThetaChannel(self, raw):
        chanName = "theta"
        freqRange = EEGUtil().channel_ranges[chanName]
        filtered = SignalUtil().butterBandpassFilter(raw, freqRange[0], freqRange[1],  self.samplingRate)
        self.axTheta.cla()
        self.axTheta.plot(self.timeArray, filtered)

if __name__ == "__main__":
    print "STARTING STUFF"
    field = "F4"
    
    e = EEGSignalPlotter(field)
    collector = DataCollector(fields=[field])
    collector.setHandler(e.update)
    t = threading.Thread(target=collector.collectData)
    t.start()

    sleep(3)
    collector.close()
    t.join()
    print "ENDING STUFF" 
    #e.plotFFTSignals(eegData, ["F4"])


