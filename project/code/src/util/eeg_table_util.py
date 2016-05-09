import os
from numpy import genfromtxt, delete
import time


scriptPath = os.path.dirname(os.path.abspath(__file__))

class EEGTableToPacketUtil(object):
    '''
    Util for EPOC dummy data 
    
    Converts CSV style data to a emotiv object

    CSV
    Timestamp;       F3;    X;  ... QF3
    1459760953.863;  -58.0  -1; ... 6.0 
    
    emotiv
    {
        "Timestamp": 1459760953.863,
        "F3" :{
            "value":   -58.0,
            "quality": 6.0,
        }
        ...
    
    }
    '''
    
    def __init__(self):
        self.index = 0
        self._buildDataStructure()
        print "Using %d dummy datasets" % self.len

    
    def _getDataPath(self):
        return scriptPath + "/../../examples/example_4096.csv" 
        
    def _readRawData(self):       
        rawData = delete(genfromtxt(self._getDataPath(), dtype=float, delimiter=";"), 0, 0)
        self.len = len(rawData)
        return rawData

    def _readHeader(self):
        with open(self._getDataPath(), 'rb') as f:
            self.header = f.readline().strip().split(";")
        
        fields = self.header[:]
        fields.remove("Timestamp")
        fields.remove("Unknown")
        self.fields = filter(lambda x: not (x.startswith("Q")), fields)
        print self.header
        print self.fields
        

    def _buildDataStructure(self):
        self._readHeader()
        rawData = self._readRawData()

        data = []
        
        for raw in rawData:
            data.append(self._buildRow(raw))
        
        self.data = data   
                
    def _buildRow(self, row):
        ret = {}
        for h in self.fields:
            value = row[self.header.index(h)]
            quality = row[self.header.index("Q" + h)]
            ret[h] = {
                "value": value,
                "quality": int(quality)   
            }
        return ret    

    def get(self):
        '''get the current dummy data row'''
        row = self.data[self.index]
        row["Timestamp"] = time.time()
        self.index = (self.index + 1) % self.len
        return EEGTablePacket(row)

class EEGTablePacket(object):
    '''Object for EEG data :see: EmotivPacket
    '''
    
    def __init__(self, data):
        self.sensors = data
        self.gyro_x = data["X"]["value"]
        self.gyro_y = data["Y"]["value"]
        self.old_model = True