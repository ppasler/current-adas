#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 23.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

import threading
from time import sleep

from output.drowsiness_monitor import DrowsinessMonitor
from config.config import ConfigProvider


class TestDroswinessMonitor(BaseTest):

    def setUp(self):
        self.dm = DrowsinessMonitor()
        self.classes = ConfigProvider().getConfig("class")

    def test_run(self):
        dmThread = threading.Thread(target=self.dm.run)
        dmThread.start()
        
        for i in range(3):
            self.dm.setState(i%2, i%2)
            sleep(0.5)
    
        self.dm.close()
        dmThread.join()

    def test_setState_state(self):
        startState = self.dm.state
        self.assertEqual(startState, "awake")

        self.dm.setState(1)
        state = self.dm.state
        self.assertEqual(state, "drowsy")

        self.dm.setState(0)
        state = self.dm.state
        self.assertEqual(state, "awake")

        self.dm.setState(2)
        state = self.dm.state
        self.assertEqual(state, "awake")

    def test_setState_info(self):
        self.dm.setState(1, "hello")
        self.assertEqual(self.dm.info, "hello")

        self.dm.setState(0)
        self.assertEqual(self.dm.info, str(None))

if __name__ == "__main__":
    unittest.main()