#!/usr/bin/python

from numpy import genfromtxt, delete, array

DEFAULT_DELIMITER = ";"

class EEGTableData(object):
    def __init__(self, header=None, data=None, file_path=""):
        self.file_path = file_path
        self.header = header
        self.data = data
        self.len = len(data)

    def setHeader(self, header):
        self.header = header

    def setData(self, data):
        self.data = data
        self.len = len(data)

    def getTimeIndex(self, from_time):
        for i, r in enumerate(self.data):
            date = r[0]
            if date >= from_time:
                return i

    def getColumn(self, column_name, offset=0, limit=-1, length=-1):
        if column_name not in self.header:
            return None

        if limit == -1:
            if  length == -1:
                limit = self.len
            else:
                limit = offset+length

        index = self.header.index(column_name)
        return self.data[:, index][offset:limit]      

    def getColumnByTime(self, column_name, from_time, to_time):
        from_index, to_index = 0, -1
        for i, r in enumerate(self.data):
            date = r[0]
            if date >= from_time and from_index == 0:
                from_index = i
            if date >= to_time:
                to_index = i
                break

        return self.getColumn(column_name, from_index, to_index)

        

        

    def __repr__(self):
        return "EEGTableData from '%s' len %d\nheader %s" % (self.file_path, self.len, self.header)

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

    print eeg_data

    print eeg_data.getColumn("F4", 2, 7)
    print eeg_data.getColumn("F4", 2, length=5)
    print eeg_data.getColumnByTime("F4", 1456820379.22, 1456820379.27)
    from_index = eeg_data.getTimeIndex(1456820379.22)
    to_index = eeg_data.getTimeIndex(1456820379.27)
    print eeg_data.getColumn("F4", from_index, to_index)



    
