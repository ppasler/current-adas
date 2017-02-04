#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 09.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import httplib
import json
import time
from posdbos.source.dummy_data_source import EEGTablePacket


class HttpEEGDataReceiver(object):
    '''
    Reads EEG raw data from Server
    '''

    def __init__(self, hostname, port, debug=False):
        self.connection = self._getConnection(hostname, port)
        if debug:
            self.connection.set_debuglevel(1)

    def _getConnection(self, hostname, port):
        return httplib.HTTPConnection(hostname + ':' + str(port))

    def getJsonResponse(self, response):
        return json.loads(response.read())

    def getHeader(self):
        self.connection.request("GET", "/header")
        response = self.connection.getresponse()
        return self.getJsonResponse(response)
        
    def getData(self):
        self.connection.request("GET", "/")
        response = self.connection.getresponse()
        return self.getJsonResponse(response)

    def dequeue(self):
        data = self.getData()
        return EEGTablePacket(data)