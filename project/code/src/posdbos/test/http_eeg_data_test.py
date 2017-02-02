#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import threading

from base_test import *  # @UnusedWildImport
from posdbos.network.http_data_provider import HttpEEGDataProvider
from posdbos.network.http_data_receiver import HttpEEGDataReceiver
from posdbos.source.dummy_data_source import DummyPacketSource


HOST = "localhost"
PORT = 1337

class TestHttpEEGData(BaseTest):


    def setUp(self):
        source = DummyPacketSource()
        source.convert()

        self.provider = HttpEEGDataProvider(HOST, PORT, source)
        self.receiver = HttpEEGDataReceiver(HOST, PORT)

        self.pThread = threading.Thread(target=self.provider.run)
        self.pThread.start()

    def test_run(self):

        header = self.receiver.getHeader()

        fetchNum = 1
        data = []
        for _ in range(fetchNum):
            data.append(self.receiver.getData())

        self.provider.stop()
        self.pThread.join(2)

        self.assertTrue(len(header) > 0)
        self.assertTrue(len(data) == fetchNum)

if __name__ == '__main__':
    unittest.main()