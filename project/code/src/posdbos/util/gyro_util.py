#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 09.02.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from config.config import ConfigProvider


class GyroUtil(object):

    def __init__(self):
        """This class does signal processor with raw signals"""
        config = ConfigProvider().getProcessingConfig()
        self.xGround = config.get("xGround")
        self.yGround = config.get("yGround")

    def normalizeX(self, data):
        '''normalizes X values to zero

        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        return data - self.xGround

    def normalizeY(self, data):
        '''normalizes Y values to zero

        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        return data - self.yGround