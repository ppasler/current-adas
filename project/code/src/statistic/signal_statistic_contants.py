#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from collections import OrderedDict
import os


TITLE = "Statistics for %s's EEG Signal"

SIGNALS_KEY = "signals"
GENERAL_KEY = "general"
RAW_KEY = "raw"
QUALITY_KEY = "quality"

TIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
DURATION_FORMAT_STRING = "%M:%S"

MAX_TYPE = "max"
MIN_TYPE = "min"
MEAN_TYPE = "mean"
AGGREGATION_TYPE = "aggregation"

METHOD = "method"

def initFields():
    return OrderedDict({
        "max": _initField(MAX_TYPE), 
        "min": _initField(MIN_TYPE), 
        "mean": _initField(MEAN_TYPE),
        "std": _initField(MEAN_TYPE),
        "var": _initField(MEAN_TYPE),
        "zeros": _initField(AGGREGATION_TYPE),
        "seq": _initField(AGGREGATION_TYPE),
        "out": _initField(AGGREGATION_TYPE)
    })

def _initField(typ, method=None):
    return {"type": typ,
             "method": method}

STAT_FIELDS = initFields()


def getNewFileName(filePath, fileExtension, suffix=None):
    fileName, _ = os.path.splitext(filePath)
    if suffix:
        fileName += suffix
    return "%s.%s" % (fileName, fileExtension)