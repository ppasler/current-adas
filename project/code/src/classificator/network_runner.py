#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''
import multiprocessing
import os
import time

from classificator.network_util import NetworkDataUtil, NetworkUtil
from config.config import ConfigProvider


scriptPath = os.path.dirname(os.path.abspath(__file__))

def testSeveral(start, end, name, convergence):
    threads = []
    for h in range(start, end):
        threads.append(multiprocessing.Process(target=testSingle, args=(h,name, convergence)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print "Done"

def testSingle(h, name, convergence):
    experimentDir = ConfigProvider().getExperimentConfig().get("filePath") + "test/"
    files = [experimentDir + "class.awake_full.csv", experimentDir + "class.drowsy_full.csv"]
    ndu = NetworkDataUtil(files)
    train, test = ndu.get()

    nu = NetworkUtil(ndu.getNInput(), 4)
    nu.train(train, convergence)
    nu.test()
    filename = name + "_" + str(h)
    nu.save(filename)

    data = ndu.get(False)
    results1, _ = nu.activate(data)
    f = open(os.path.dirname(os.path.abspath(__file__)) + "/../../data/" + filename +  ".nns", 'w')

    results, resArr = nu.activate(test)
    f.write("convergence: " + str(convergence) + "\n\n")
    f.write(nu.__str__() + "\n\n")
    f.write("  awk drsy res(%)\n")
    f.write(str(results1))
    f.write("  awk drsy res(%)\n")
    f.write(str(results))
    f.write("\n\nres;clazz;target\n")
    for line in resArr:
        f.write("%.2f;%.2f;%.2f\n" % tuple(line))
    f.close()
    
    ndu.get(False)

def loadSingle(fileName):
    files = [scriptPath + "/../../data/awake_full.csv", scriptPath + "/../../data/drowsy_full.csv"]
    ndu = NetworkDataUtil(files)
    data = ndu.get(False)

    nu = NetworkUtil(new=False, fileName=fileName)
    results, resArr = nu.activate(data)
    f = open(os.path.dirname(os.path.abspath(__file__)) + "/../../data/" + fileName +  "_.nns", 'w')

    f.write(nu.__str__() + "\n\n")
    f.write("  awk drsy res(%)\n")
    f.write(str(results))
    f.write("\n\nres;clazz;target\n")
    for line in resArr:
        f.write("%.2f;%.2f;%.2f\n" % tuple(line))
    f.close()

if __name__ == "__main__": # pragma: no cover
    name = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
    testSeveral(0, 4, name, False)
    #loadSingle("2016-08-23-19-14_3")
