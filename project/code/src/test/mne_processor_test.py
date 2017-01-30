#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue

from processor.mne_processor import MNEProcessor
from util.mne_util import MNEUtil
from mne.viz.utils import plt_show
from test.posdbos_test_factory import PoSDBoSTestFactory

class TestMNEProcessor(BaseTest):

    def setUp(self):
        self.queue = Queue()
        self.collector = PoSDBoSTestFactory.createDemoDataCollector(self.getData1024CSV(), self.queue)
        self.collector.collectData()
        self.processor = MNEProcessor()

    def test_all(self):
        window = self.queue.get()
        print window["AF3"]["value"]
        preProc, _ = self.processor.process(window)

    #def test_preProc(self):
    #    window = self.queue.get()
    #    preProc = self.processor.preProcessor.process(window)
    #    print preProc

if __name__ == "__main__":
    unittest.main()