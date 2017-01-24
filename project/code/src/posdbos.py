#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Empty
import os
import threading
from time import time, sleep
from config.config import ConfigProvider


scriptPath = os.path.dirname(os.path.abspath(__file__))

class PoSDBoS(object):

    def stop(self):
        self.running = False

    def close(self):
        self.running = False
        self.fe.close()
        self.dm.close()

    def start(self):
        self.fet = threading.Thread(target=self.fe.start)
        self.fet.start()

    def run(self):
        self.start()
        dmt = threading.Thread(target=self.dm.run)
        dmt.start()
        features = []
        total = 0
        start = time()
        c = []
        while self.running and dmt.is_alive():
            try:
                #awake = 0, drowsy = 1
                data = self.extractedQueue.get(timeout=1)
                features.append(data)
                clazz = self.nn.activate(data, True)
                c.append([clazz, clazz])
                self.setState(clazz)
                total += 1
            except Empty:
                print "Needed %.2fs for %d windows" % (time() - start, total) 
                self.stop()
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                print e.message
                self.close()


        while dmt.is_alive():
            try:
                sleep(1)
            except KeyboardInterrupt:
                self.close()
        #self.writeFeature(c)
        self.close()
        self.fet.join()
        dmt.join()
        print "done"

    def setState(self, clazz):
        self.classified[clazz] += 1
        if self.curClass == clazz:
            self.classCount += 1
        else:
            self.curClass = clazz
            self.classCount = 0

        info = "class %d row (%s)" % (clazz, str(self.classCount))
        if clazz == 1 and self.classCount >= self.drowsyMinCount:
            self.dm.setState(clazz, info)
            self.found += 1
        elif clazz == 0 and self.classCount >= self.awakeMinCount:
            self.dm.setState(clazz, info)


    def runAndSave(self, filePath):
        self.start()
        features = []
        total = 0
        start = time()
        while self.running:
            try:
                #awake = 0, drowsy = 1
                data = self.extractedQueue.get(timeout=1)
                features.append(data)
                total += 1
            except Empty:
                print "Needed %.2fs for %d windows" % (time() - start, total) 
                self.stop()
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                print e.message
                self.close()

        self.writeFeature(features, filePath)
        self.close()
        self.fet.join()
        print "done"

    def writeFeature(self, data, filePath):
        #filePath = scriptPath + "/../data/" + "drowsy_full_.csv"

        header = []
        start = 4
        end = start + len(data[0])/6
        for field in ConfigProvider().getCollectorConfig().get("fields"):
            header.extend([str(x) + "Hz" + field for x in range(start, end)])
        self.fileUtil.saveCSV(filePath, data, header)