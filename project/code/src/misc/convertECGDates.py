from datetime import datetime
import os, glob, csv
import time


EPOCH = datetime(1970,1,1)

def getCSVFiles():
    return glob.glob("*.csv")

def processCSVFile(filePath):
    with open(filePath, 'rb') as fin, open("proc_" + filePath, 'wb+') as fout:
        start = time.time()
        reader = csv.reader(fin)
        writer = csv.writer(fout)

        #write header
        header = next(reader).replace("Time", "Timestamp")
        writer.writerow(header)

        for row in reader:  # process data lines
            writer.writerow([convertDate(row[0])] + row[1:])

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

if __name__ == "__main__":
    print "start..."

    pathString = "%s/%s/"
    basepath = "E:/thesis/experiment"
    subjects = ["2/2016_12_01-17_38_16"]
    for subject in subjects:
        filePath = pathString % (basepath, subjects[0])
        processDir(filePath)

    print "...finished"
