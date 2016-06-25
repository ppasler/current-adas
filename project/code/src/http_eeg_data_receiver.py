'''
Created on 09.05.2016

@author: Paul Pasler
'''

import httplib
import json
import time
from util.eeg_table_to_packet_converter import EEGTablePacket


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

if __name__ == "__main__":
    
    hostname, port = ("localhost", 9000)
    client = HttpEEGDataReceiver(hostname, port, True)
    
    print client.getHeader()
    time.sleep(3)
    
    print client.getData()
    time.sleep(3)
    
    print client.getData()