'''
seen at: `UCI EEG Dataset <https://archive.ics.uci.edu/ml/datasets/EEG+Database>`_
'''
import sys, os
import time

import numpy as np


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class EEGDataSetConverter(object):
    
    def __init__(self, fileName):
        self.fileName = fileName
        self.data = None
        self.header = []
    
    def _getData(self):
        raw = np.genfromtxt(self.fileName, delimiter=" ",  dtype="|S5")
        return np.delete(raw, [0,2], axis=1)

    def _buildDummyTimestamp(self):
        now = time.time()
        x = 1/256.0
        return np.arange(now, now+1, x)

    
    def readFile(self):
        raw = self._getData()

        rows = []
        l = 256
        for i in range(0, len(raw), l):
            self.header.append(raw[i][0]) 
            rows.append(raw[i:i+l,1].astype(float))
        
        self.header.insert(0, "Timestamp")
        rows.insert(0, self._buildDummyTimestamp())
        self.data = np.array(rows)

    def saveFile(self, data):
        np.savetxt(self.fileName + ".csv", self.data.transpose(), delimiter=";", header=";".join(self.header), fmt="%1.3f", comments='')

if __name__ == "__main__":
    c = EEGDataSetConverter("co2a0000364.rd.018")
    data = c.readFile()
    c.saveFile(data)
    c._buildDummyTimestamp()
    
