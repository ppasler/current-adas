import os
import time

from util.eeg_table_util import EEGTableReader


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
        self.reader = EEGTableReader()
        self.filepath = scriptPath + "/../../examples/example_4096.csv"
        self.index = 0
        self._buildDataStructure()
        print "Using %d dummy datasets" % self.len

        
    def _readRawData(self):       
        rawData = self.reader.readData(self.filepath)
        self.len = len(rawData)
        return rawData

    def _readHeader(self):
        self.header = self.reader.readHeader(self.filepath)
        
        fields = self.header[:]
        fields.remove("Timestamp")
        fields.remove("Unknown")
        self.fields = filter(lambda x: not (x.startswith("Q")), fields)

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
        return EEGTablePacket(ret)

    def dequeue(self):
        '''get the current dummy data row'''
        row = self.data[self.index]
        row.sensors["Timestamp"] = time.time()
        self.index = (self.index + 1) % self.len
        return row

    def close(self):
        pass

class EEGTablePacket(object):
    '''Object for EEG data :see: EmotivPacket
    '''
    
    def __init__(self, data):
        self.sensors = data
        self.gyro_x = data["X"]["value"]
        self.gyro_y = data["Y"]["value"]
        self.old_model = True