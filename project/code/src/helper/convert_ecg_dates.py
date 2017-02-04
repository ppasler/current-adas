import os, glob, csv
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from util.date_converter import DateConverter

def getCSVFiles():
    return glob.glob("*.csv")

def processCSVFile(filePath):
    with open(filePath, 'rb') as fin, open("proc_" + filePath, 'wb+') as fout:
        start = time.time()
        reader = csv.reader(fin, skipinitialspace=True)
        writer = csv.writer(fout)

        #write header
        header = next(reader)
        timeIndex = header.index("Time")
        header[timeIndex] = "Timestamp"
        writer.writerow(header)

        converter = DateConverter('%d/%m/%Y %H:%M:%S.%f', 1)
        for row in reader:  # process data lines
            row[timeIndex] = converter.convertDate(row[timeIndex])
            writer.writerow(row)

        #http://stackoverflow.com/questions/19309834/how-write-csv-file-without-new-line-character-in-last-line
        fout.seek(-2, os.SEEK_END) # <---- 2 : len('\r\n')
        fout.truncate()
        print "took %.2fs for %s" % ((time.time() - start), filePath) 

def processDir(filePath):
    os.chdir(filePath)
    files = getCSVFiles()
    for fileName in files:
        processCSVFile(fileName)

def doit():
    pathString = "%s/%s/"
    basepath = "E:/thesis/experiment"
    subjects = ["1/2016-12-05_13_58"]#, "2/2016-12-01_17-38"]
    for subject in subjects:
        filePath = pathString % (basepath, subject)
        processDir(filePath)

if __name__ == "__main__":
    print "start..."
    doit()
    print "...finished"
