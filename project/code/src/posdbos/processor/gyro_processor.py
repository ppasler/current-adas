#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''
from posdbos.util.signal_util import SignalUtil
from config.config import ConfigProvider

class GyroProcessor(object):
    def __init__(self):
        self.su = SignalUtil()
        self.windowSeconds = ConfigProvider().getCollectorConfig().get("windowSeconds")
        config = ConfigProvider().getProcessingConfig()
        self.xMax = config.get("xMax")
        self.yMax = config.get("yMax")

    def process(self, dto):
        xEnergy = self.su.energy(dto.getValue("X"))/self.windowSeconds
        yEnergy = self.su.energy(dto.getValue("Y"))/self.windowSeconds
        invalid = (xEnergy > self.xMax) or (yEnergy > self.yMax) 
        return dto.getData(), invalid