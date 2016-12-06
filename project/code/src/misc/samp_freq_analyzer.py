#!/usr/bin/env python -W ignore::DeprecationWarning
# based on: http://martinos.org/mne/dev/auto_tutorials/plot_ica_from_raw.html

import os, collections

from util.signal_table_util import TableFileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

def main():
    filepath = "E:/thesis/experiment/2/"
    eegFileName = filepath + "2016-12-01-17-50_EEG.csv"
    eegData = TableFileUtil().readEEGFile(eegFileName)
    print "SampRate: %.2f" % eegData.getSamplingRate()
    timeData = eegData.getTime().astype(int)
    timeCount = collections.Counter(timeData)
    print timeCount
    print len(timeCount.values()) - len([x for x in timeCount.values() if x > 128])

if __name__ == "__main__":
    main()
