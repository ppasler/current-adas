#!/usr/bin/python

from numpy import genfromtxt, delete, shape

DEFAULT_DELIMITER = ";" # default delimiter for CSV file
TIMESTAMP_STRING = "Timestamp" # key which specifies the unix timestamp of the data

class EEGTableData(object):
    def __init__(self, header=None, data=None, file_path=""):
        self.file_path = file_path
        self.header = header
        self.data = data
        if data is not None:
            self.len = len(data)

    def setHeader(self, header):
        self.header = header

    def setData(self, data):
        self.data = data
        self.len = len(data)

    def getTimeIndex(self, fromTime):
        '''
        get the index for the given fromTime
        if fromTime < min(timestamp) return 0
        if fromTime > max(timestamp) return len(data)
        
        :param    float    fromTime:    time as unix timestamp 
        
        :return   returns the index of the given fromTime 
        '''
        data = self.getColumn(TIMESTAMP_STRING)
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)
        
        for i, time in enumerate(data):
            if time >= fromTime:
                return i

    def getColumn(self, column_name, offset=0, limit=-1, length=-1):
        '''
        get dataset from a certain column, either from offset to limit or till length
        if only column_name is specified, it returns the whole column
        if offset and length are both defined, length will be ignored
        
        :param string column_name:   the name of the column
        :param int    offset:        startindex of dataset
        :param int    limit:         endpoint of dataset
        :param int    length:        length of dataset
        '''
        
        if column_name not in self.header:
            return None

        if limit == -1:
            if  length == -1:
                limit = self.len
            else:
                limit = offset+length

        index = self.header.index(column_name)
        return self.data[:, index][offset:limit]      

    def getColumnByTime(self, columnName, fromTime, toTime):
        '''
        get dataset from a certain column, for a time interval (fromTime -> toTime)
             
        :param string    columnName:   the name of the column 
        :param float     fromTime:     start time of dataset as unix timestamp   
        :param float     toTime:       start time of dataset as unix timestamp
        
        :raise ValueError if time could not be found in dataset 
        '''
        fromIndex, toIndex = -1, -1

        if fromTime > toTime:
            fromTime, toTime = self._switchTime(fromTime, toTime)
        
        data = self.getColumn(TIMESTAMP_STRING)
        
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)

        if not self._timeInData(data, toTime):
            raise ValueError('could not find %f in data' % toTime)

        for i, time in enumerate(data):
            if time >= fromTime and fromIndex == -1:
                fromIndex = i
            if time >= toTime:
                toIndex = i
                break

        return self.getColumn(columnName, fromIndex, toIndex)

    def getSampleRate(self):
        data = self.getColumn(TIMESTAMP_STRING)
        duration = data[self.len-1] - data[0]
        return self.len / duration  

    def _switchTime(self, time1, time2):
        return time2, time1
        

    def _timeInData(self, data, time):
        return (min(data) <= time <= max(data))

    def __repr__(self):
        return "EEGTableData from '%s' shape %s\nheader %s" % (self.file_path, shape(self.data), self.header)

class EEGTableReader(object):

    def __init__(self):
        """This class reads EEGTables"""

    def readHeader(self, file_path, delimiter=DEFAULT_DELIMITER):
        header = None
        with open(file_path, 'rb') as f:
            header = f.readline().strip().split(delimiter)
        return header

    def readData(self, file_path, delimiter=DEFAULT_DELIMITER):
        data = delete(genfromtxt(file_path, dtype=float, delimiter=delimiter), 0, 0)
        return data

    def readFile(self, file_path="", delimiter=DEFAULT_DELIMITER):
        if file_path == "":
            return None

        data = self.readData(file_path)
        header = self.readHeader(file_path)

        return EEGTableData(header, data, file_path)
    


if __name__ == "__main__":
    e = EEGTableReader()
    #eeg_data = e.readFile("example_full.csv")
    eeg_data = e.readFile("example_short.csv")
    print eeg_data.data
    from_index = eeg_data.getTimeIndex(1456820379.22)
    to_index = eeg_data.getTimeIndex(1456820379.27)
    print eeg_data.getColumn("F4", from_index, to_index)
    eeg_data.getTimeIndex(123)



    
