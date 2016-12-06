from datetime import datetime
import os, glob, csv
import time

TIMEZONE = 1
EPOCH = datetime(1970,1,1, hour=TIMEZONE)
print EPOCH
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

        for row in reader:  # process data lines
            row[timeIndex] = convertDate(row[timeIndex])
            writer.writerow(row)

        #http://stackoverflow.com/questions/19309834/how-write-csv-file-without-new-line-character-in-last-line
        fout.seek(-2, os.SEEK_END) # <---- 2 : len('\r\n')
        fout.truncate()
        print "took %.2fs for %s" % ((time.time() - start), filePath) 

def convertDate(dateString):
    if dateString == "":
        return ""
    return totimestamp(datetime.strptime(dateString, '%d/%m/%Y %H:%M:%S.%f'))

# http://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python
def totimestamp(dt):
    td = dt - EPOCH
    return td.total_seconds()

def processDir(filePath):
    os.chdir(filePath)
    files = getCSVFiles()
    for fileName in files:
        processCSVFile(fileName)

def doit():
    pathString = "%s/%s/"
    basepath = "E:/thesis/experiment"
    subjects = ["2/2016_12_01-17_38_16"]
    for subject in subjects:
        filePath = pathString % (basepath, subject)
        processDir(filePath)

if __name__ == "__main__":
    print "start..."
    doit()
    print "...finished"
