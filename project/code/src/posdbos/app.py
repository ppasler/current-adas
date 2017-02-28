#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Empty
import logging
import threading
from time import time, sleep
from config.config import ConfigProvider


class PoSDBoS(object):

    def stop(self):
        self.running = False

    def close(self):
        self.running = False
        self.dc.close()
        self.dp.close()
        if hasattr(self, "dm"):
            self.dm.close()
        logging.info("closing app")

    def join(self):
        self.dct.join()
        self.dpt.join()

    def start(self):
        logging.info("starting app")
        self.dct = threading.Thread(target=self.dc.collectData)
        self.dct.start()
        self.dpt = threading.Thread(target=self.dp.processData)
        self.dpt.start()

    def run(self):
        self.start()
        dmt = threading.Thread(target=self.dm.run)
        dmt.start()
        features = []
        total = 0
        start = time()
        classes = []
        while self.running and dmt.is_alive():
            try:
                #awake = 0, drowsy = 1
                data = self.extractedQueue.get(timeout=5)
                features.append(data)
                clazz = self.nn.activate(data, True)
                classes.append(clazz)
                self.setState(clazz)
                total += 1
            except Empty:
                logging.info("Needed %.2fs for %d windows; awake: %d; drowsy: %d" % (time() - start, total, total-sum(classes), sum(classes)))
                self.stop()
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                logging.exception(e.message)
                self.close()

        while dmt.is_alive():
            try:
                sleep(1)
            except KeyboardInterrupt:
                self.close()
        #self.writeFeature(c)
        self.close()
        self.join()
        dmt.join()
        logging.info("Done")

    def setState(self, clazz):
        self.classified[clazz] += 1
        self.dm.setState(clazz)

    def runAndSave(self, filePath):
        self.start()
        features = []
        total = 0
        start = time()
        cleanExit = True
        while self.running:
            try:
                #awake = 0, drowsy = 1
                data = self.extractedQueue.get(timeout=5)
                features.append(data)
                total += 1
            except Empty:
                logging.info("Needed %.2fs for %d windows" % (time() - start, total))
                self.stop()
            except KeyboardInterrupt:
                cleanExit = False
                self.close()
            except Exception as e:
                cleanExit = False
                logging.exception(e.message)
                self.close()

        if cleanExit:
            logging.info("wrote it %s" % filePath)
            self.writeFeature(features, filePath)
        self.close()
        self.join()

        logging.info("done")

    def writeFeature(self, data, filePath):
        header = []
        start = 4
        end = start + len(data[0])/6
        for field in ConfigProvider().getCollectorConfig().get("eegFields"):
            header.extend([str(x) + "Hz" + field for x in range(start, end)])
        self.fileUtil.saveCSV(filePath, data, header)