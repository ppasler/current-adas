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

from posdbos.classificator.network_util import NetworkDataUtil, NetworkUtil
from config.config import ConfigProvider

import numpy as np
np.set_printoptions(precision=1, formatter={'float':lambda x: str(int(round(x)))})

scriptPath = os.path.dirname(os.path.abspath(__file__))

def trainSeveral(start, end, name, convergence):
    threads = []
    for h in range(start, end):
        threads.append(multiprocessing.Process(target=trainSingle, args=(h,name, convergence)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def trainSingle(h, name, convergence):
    experimentDir = ConfigProvider().getExperimentConfig().get("filePath")
    files = [experimentDir + "test/awakes_proc_new8.csv", experimentDir + "test/drowsies_proc_new8.csv"]
    #files = [experimentDir + "mp/awakes_full_norm_proc_4.csv", experimentDir + "mp/drowsies_full_norm_proc_4.csv"]
    ndu = NetworkDataUtil(files)
    train, test = ndu.get()

    nu = NetworkUtil(ndu.getNInput(), 1)
    nu.train(train, convergence)
    nu.test()
    fileName = name + "_" + str(h)
    nu.save(fileName)

    data = ndu.get(False, False)
    writeResults(nu, data, fileName, files, convergence, test)

def loadSingle(fileName):
    #files = [scriptPath + "/../../../data/awake_full.csv", scriptPath + "/../../../data/drowsy_full.csv"]
    experimentDir = ConfigProvider().getExperimentConfig().get("filePath")
    files = [experimentDir + "test/awakes_proc_new4.csv", experimentDir + "test/drowsies_proc_new4.csv"]

    ndu = NetworkDataUtil(files)
    data = ndu.get(False)
    nu = NetworkUtil(new=False, fileName=fileName)

    writeResults(nu, data, fileName, files)

def writeResults(nu, data, fileName, dataFiles, convergence=None, test=None):
    results1, _ = nu.activate(data)
    
    with open(scriptPath + "/../../../data/" + fileName +  ".nns", 'w') as f: 
        if test is not None:
            f.write("convergence: " + str(convergence) + "\n\n")
        f.write("files: " + ",".join(dataFiles) + "\n\n")

        f.write(nu.__str__() + "\n\n")
        f.write("  awk drsy res(%)\n")
        f.write(str(results1) + "\n")

        if test is not None:
            results, resArr = nu.activate(test)
            f.write(str(results))
            f.write("\n\nres;clazz;target\n")
            for line in resArr:
                f.write("%.2f;%.2f;%.2f\n" % tuple(line))

if __name__ == "__main__": # pragma: no cover
    name = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
    start = time.time()
    print "start %f" % start
    trainSeveral(0, 4, name, False)
    end = time.time()
    print "end %f (%fs)" % (end, end-start)
    #loadSingle("2017-02-26-11-17_0")
