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
        
        :param    float   fromTime:    time as unix timestamp 
        
        :return   int     the index of the given fromTime 
        '''
        data = self.getColumn(TIMESTAMP_STRING)
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)
        
        for i, time in enumerate(data):
            if time >= fromTime:
                return i

    def getColumn(self, columnName, offset=0, limit=-1, length=-1):
        '''
        get dataset from a certain column, either from offset to limit or till length
        if only column_name is specified, it returns the whole column
        if offset and length are both defined, length will be ignored
        
        :param     string column_name:   the name of the column
        :param     int    offset:        startindex of dataset
        :param     int    limit:         endpoint of dataset
        :param     int    length:        length of dataset
        
        :return    array  dataset for given column   
        '''
        
        if columnName not in self.header:
            return None

        if limit == -1:
            if  length == -1:
                limit = self.len
            else:
                limit = offset+length

        index = self.header.index(columnName)
        return self.data[:, index][offset:limit]      

    def getColumnByTime(self, columnName, fromTime, toTime):
        '''
        get dataset from a certain column, for a time interval (fromTime -> toTime)
             
        :param string    columnName:   the name of the column 
        :param float     fromTime:     start time of dataset as unix timestamp   
        :param float     toTime:       start time of dataset as unix timestamp
        
        :return array    dataset for given column   
        
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
        '''
        calcs the samplerate for the whole dataset based on the timestamp column   
        
        :return int    samplerate

        '''
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
    '''
    This class reads EEGTables created by emotiv.py
    '''

    def readHeader(self, file_path, delimiter=DEFAULT_DELIMITER):
        '''
        Reads the first row of the table to create a list of header values
        by default the delimiter for the csv table is ";"
        
        :param string   file_path
        :param string   delimiter   
        
        :return list    header column
        '''
        header = None
        with open(file_path, 'rb') as f:
            header = f.readline().strip().split(delimiter)
            
        return header

    def readData(self, filePath, delimiter=DEFAULT_DELIMITER):
        '''
        reads all rows of the table (except the first on) to create a 2D array of eeg values
        by default the delimiter for the csv table is ";"
        
        [
         ["timestamp_1", "val_1_1" ... "v_1_n"],
         ["timestamp_2", "val_2_1" ... "v_2_n"],
                ...
         ["timestamp_m", "val_m_1" ... "v_m_n"],
        ]
        
        :param string   filePath
        :param string   delimiter   
        
        :return array   data columns
        '''
        data = delete(genfromtxt(filePath, dtype=float, delimiter=delimiter), 0, 0)
        return data

    def readFile(self, filePath="", delimiter=DEFAULT_DELIMITER):
        '''
        reads the given file
        
        
        :param filePath:
        :param delimiter:
        '''
        if filePath == "":
            return None

        data = self.readData(filePath, delimiter)
        header = self.readHeader(filePath, delimiter)

        return EEGTableData(header, data, filePath)
    


if __name__ == "__main__":
    e = EEGTableReader()
    #eeg_data = e.readFile("example_full.csv")
    eeg_data = e.readFile("example_short.csv")
    print eeg_data.data
    from_index = eeg_data.getTimeIndex(1456820379.22)
    to_index = eeg_data.getTimeIndex(1456820379.27)
    print eeg_data.getColumn("F4", from_index, to_index)
    eeg_data.getTimeIndex(123)



    
